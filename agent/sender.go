package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"sync"
	"time"
)

// Sender mengirim event ke collector dengan:
//   - channel in-memory (non-blocking untuk caller),
//   - spool file lokal (JSONL) sebagai buffer bila collector down,
//   - retry dengan backoff (docs/02-arsitektur.md -> Reliability).
type Sender struct {
	cfg    Config
	client *http.Client
	ch     chan Event
	spool  string

	mu           sync.Mutex
	dropped      int
	sentOK       int
	spoolBacklog int
}

func NewSender(cfg Config) *Sender {
	spool := filepath.Join(filepath.Dir(cfg.DecoyDir), "spool.jsonl")
	_ = os.MkdirAll(filepath.Dir(spool), 0o700)
	return &Sender{
		cfg: cfg,
		client: &http.Client{
			Timeout: 6 * time.Second,
		},
		ch:    make(chan Event, 4096),
		spool: spool,
	}
}

// Emit menaruh event di antrean. Tidak pernah memblokir pemanggil.
func (s *Sender) Emit(ev Event) {
	if ev.TS == "" {
		ev.TS = nowRFC3339()
	}
	if ev.AgentID == "" {
		ev.AgentID = s.cfg.AgentID
	}
	select {
	case s.ch <- ev:
	default:
		// antrean penuh -> langsung tulis ke spool agar tidak hilang
		s.appendSpool(ev)
	}
}

func (s *Sender) appendSpool(ev Event) {
	s.mu.Lock()
	s.dropped++
	s.mu.Unlock()

	f, err := os.OpenFile(s.spool, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o600)
	if err != nil {
		log.Printf("[agent] gagal buka spool: %v", err)
		return
	}
	defer f.Close()
	line, _ := json.Marshal(ev)
	_, _ = f.Write(append(line, '\n'))
}

func (s *Sender) Run() {
	// Pengirim utama
	go func() {
		for ev := range s.ch {
			if !s.post(ev) {
				s.appendSpool(ev)
			}
		}
	}()
	// Penguras spool berkala
	go func() {
		t := time.NewTicker(10 * time.Second)
		for range t.C {
			s.flushSpool()
		}
	}()
	// Heartbeat + ringkasan
	go func() {
		t := time.NewTicker(30 * time.Second)
		for range t.C {
			s.mu.Lock()
			log.Printf("[agent] terkirim=%d spool-dari-antrean=%d", s.sentOK, s.dropped)
			s.mu.Unlock()
		}
	}()
}

func (s *Sender) post(ev Event) bool {
	body, _ := json.Marshal(ev)
	req, err := http.NewRequest(http.MethodPost, s.cfg.CoreURL+"/api/ingest", bytes.NewReader(body))
	if err != nil {
		return false
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Polaris-Token", s.cfg.Token)
	resp, err := s.client.Do(req)
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		s.mu.Lock()
		s.sentOK++
		s.mu.Unlock()
		return true
	}
	return false
}

// flushSpool mencoba mengirim ulang event yang tersimpan di spool.
func (s *Sender) flushSpool() {
	data, err := os.ReadFile(s.spool)
	if err != nil || len(data) == 0 {
		return
	}
	lines := bytes.Split(bytes.TrimSpace(data), []byte("\n"))
	remaining := make([][]byte, 0, len(lines))
	for _, ln := range lines {
		if len(bytes.TrimSpace(ln)) == 0 {
			continue
		}
		var ev Event
		if err := json.Unmarshal(ln, &ev); err != nil {
			continue
		}
		if !s.post(ev) {
			remaining = append(remaining, ln)
		}
	}
	s.mu.Lock()
	s.spoolBacklog = len(remaining)
	s.mu.Unlock()

	if len(remaining) == 0 {
		_ = os.Remove(s.spool)
		return
	}
	out := bytes.Join(remaining, []byte("\n"))
	out = append(out, '\n')
	if err := os.WriteFile(s.spool, out, 0o600); err != nil {
		log.Printf("[agent] gagal tulis ulang spool: %v", err)
	}
}

func (s *Sender) Stats() string {
	s.mu.Lock()
	defer s.mu.Unlock()
	return fmt.Sprintf("sent=%d backlog=%d spooled=%d", s.sentOK, s.spoolBacklog, s.dropped)
}
