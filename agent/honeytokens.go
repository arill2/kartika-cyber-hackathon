package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"syscall"
	"time"
	"unsafe"
)

// honeytokenFile adalah satu berkas umpan.
type honeytokenFile struct {
	path    string
	content func(canary, beacon string) string
}

func fileSpecs(dir string, beacons map[string]string) []honeytokenFile {
	return []honeytokenFile{
		{filepath.Join(dir, ".env"), func(c, b string) string {
			return fmt.Sprintf(`# INTERNAL - DO NOT COMMIT
APP_ENV=production
DB_HOST=10.10.4.21
DB_USER=app_rw
DB_PASS=S3cr3t-%s
REDIS_URL=redis://10.10.4.22:6379/0
AWS_ACCESS_KEY_ID=AKIA%s
AWS_SECRET_ACCESS_KEY=%s
VAULT_TOKEN=%s
# ops? monitoring sync
HEALTH_WEBHOOK=%s
`, c, strings.ToUpper(c[:8]), c, c, b)
		}},
		{filepath.Join(dir, "credentials.txt"), func(c, b string) string {
			return fmt.Sprintf("admin : Adm1n@2024-%s\nroot : r00t-%s\nsvc_backup : B4ckup-%s\n", c, c, c)
		}},
		{filepath.Join(dir, "backup_db.sql"), func(c, b string) string {
			return fmt.Sprintf("-- prod dump\nCREATE TABLE users(...);\nINSERT INTO users VALUES ('admin','$2y$10$%s');\n-- token: %s\n", c, b)
		}},
		{filepath.Join(dir, "vault-token.txt"), func(c, b string) string {
			return fmt.Sprintf("hvs.%s\n", c)
		}},
		{filepath.Join(dir, "id_rsa_backup"), func(c, b string) string {
			return fmt.Sprintf("-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXkt%s\n-----END OPENSSH PRIVATE KEY-----\n", c)
		}},
		{filepath.Join(dir, "passwords.xlsx"), func(c, b string) string {
			return fmt.Sprintf("POLARIS-HONEYTOKEN,%s\nservice,user,password\nVPN,admin,Vpn-%s\nOT-HMI,operator,hmi-%s\n", b, c, c)
		}},
		{filepath.Join(dir, ".aws", "credentials"), func(c, b string) string {
			return fmt.Sprintf("[default]\naws_access_key_id = AKIA%s\naws_secret_access_key = %s\n", strings.ToUpper(c[:8]), c)
		}},
		{filepath.Join(dir, ".aws", "config"), func(c, b string) string {
			return fmt.Sprintf("[profile prod]\nregion = ap-southeast-3\nrole_arn = arn:aws:iam::000000000000:role/honeytoken-%s\n", c)
		}},
		{filepath.Join(dir, "wp-config.php.bak"), func(c, b string) string {
			return fmt.Sprintf("<?php\ndefine('DB_PASSWORD', '%s');\ndefine('AUTH_KEY', '%s');\n", c, b)
		}},
		{filepath.Join(dir, "k8s-prod.yaml"), func(c, b string) string {
			return fmt.Sprintf("apiVersion: v1\nkind: Secret\nmetadata:\n  name: prod-secret\nstringData:\n  token: \"%s\"\n", c)
		}},
	}
}

func randCanary() string {
	b := make([]byte, 16)
	now := time.Now().UnixNano()
	for i := range b {
		b[i] = byte((now >> (uint(i) * 3)) ^ int64(i*37+11))
	}
	const hexd = "0123456789abcdef"
	out := make([]byte, len(b)*2)
	for i, x := range b {
		out[i*2] = hexd[x>>4]
		out[i*2+1] = hexd[x&0x0f]
	}
	return string(out)
}

// setupHoneytokens menanam berkas umpan lalu memulai watch inotify.
// Watch baru dipasang SETELAH berkas ditulis agar panen event palsu dari
// aktivitas agent sendiri tidak terjadi.
func setupHoneytokens(cfg Config, send func(Event)) {
	dir := cfg.DecoyDir
	_ = os.MkdirAll(dir, 0o755)
	_ = os.MkdirAll(filepath.Join(dir, ".aws"), 0o755)
	_ = os.MkdirAll(filepath.Join(dir, ".git"), 0o755)

	canary := env("POLARIS_CANARY", randCanary())
	// beacon token ber-prefix "cred-" -> diklasifikasi canary_cred_used (T1)
	beaconURL := cfg.BeaconBase + "/cred-" + canary

	written := map[string]string{} // path -> sha256
	for _, spec := range fileSpecs(dir, nil) {
		content := spec.content(canary, beaconURL)
		if err := os.WriteFile(spec.path, []byte(content), 0o644); err != nil {
			log.Printf("[agent] gagal tanam honeytoken %s: %v", spec.path, err)
			continue
		}
		sum := sha256.Sum256([]byte(content))
		written[spec.path] = hex.EncodeToString(sum[:])
	}
	// tambahan: .git/config umpan
	gitcfg := filepath.Join(dir, ".git", "config")
	_ = os.WriteFile(gitcfg, []byte("[remote \"origin\"]\n\turl = git@10.10.4.9:payroll/hr-system.git\n"), 0o644)
	sum := sha256.Sum256([]byte("git-conf"))
	written[gitcfg] = hex.EncodeToString(sum[:])

	log.Printf("[agent] %d honeytoken files ditanam di %s", len(written), dir)
	log.Printf("[agent] canary value  : %s", canary)
	log.Printf("[agent] beacon (T1)   : %s", beaconURL)

	go watchFiles(dir, written, send)
}

func watchFiles(dir string, hashes map[string]string, send func(Event)) {
	fd, err := syscall.InotifyInit1(syscall.IN_CLOEXEC)
	if err != nil {
		log.Printf("[agent] inotify tidak tersedia, fallback polling: %v", err)
		go pollFiles(hashes, send)
		return
	}
	defer syscall.Close(fd)

	watchMask := uint32(syscall.IN_ACCESS | syscall.IN_OPEN | syscall.IN_MODIFY | syscall.IN_ATTRIB | syscall.IN_CLOSE_WRITE)
	dirs := []string{dir, filepath.Join(dir, ".aws"), filepath.Join(dir, ".git")}
	for _, d := range dirs {
		if _, err := syscall.InotifyAddWatch(fd, d, watchMask); err != nil {
			log.Printf("[agent] watch %s gagal: %v", d, err)
		}
	}
	log.Printf("[agent] inotify aktif pada %d direktori umpan", len(dirs))

	// dedupe: satu aksi (open+access+close) -> satu event
	var mu sync.Mutex
	last := map[string]time.Time{}
	buf := make([]byte, 64*1024)
	for {
		n, err := syscall.Read(fd, buf)
		if err != nil {
			if err == syscall.EINTR {
				continue
			}
			log.Printf("[agent] inotify read berhenti: %v", err)
			return
		}
		offset := 0
		for offset+syscall.SizeofInotifyEvent <= n {
			raw := (*syscall.InotifyEvent)(unsafe.Pointer(&buf[offset]))
			nameLen := int(raw.Len)
			name := ""
			if nameLen > 0 && offset+syscall.SizeofInotifyEvent+nameLen <= n {
				b := buf[offset+syscall.SizeofInotifyEvent : offset+syscall.SizeofInotifyEvent+nameLen]
				name = strings.TrimRight(string(b), "\x00")
			}
			offset += syscall.SizeofInotifyEvent + nameLen
			if name == "" {
				continue
			}
			// hiraukan file non-umpan
			if strings.HasSuffix(name, ".swp") || strings.HasPrefix(name, ".") && !strings.Contains(name, "env") &&
				name != "config" && name != "credentials" {
				// tetap proses .env / .aws/credentials / .git/config
				if !isInteresting(name) {
					continue
				}
			}
			if raw.Mask&syscall.IN_ISDIR != 0 {
				continue
			}
			full := filepath.Join(dir, name)
			// normalisasi untuk file di subdir
			if !fileExists(full) {
				full = filepath.Join(dir, ".aws", name)
				if !fileExists(full) {
					full = filepath.Join(dir, ".git", name)
				}
			}
			key := full + "|read"
			mu.Lock()
			if t, ok := last[key]; ok && time.Since(t) < 1200*time.Millisecond {
				mu.Unlock()
				continue
			}
			last[key] = time.Now()
			mu.Unlock()

			sum := hashes[full]
			send(Event{
				EventType: EvFileAccess,
				SrcIP:     "127.0.0.1", // akses lokal; di produksi difilter per-node
				FilePath:  full,
				SHA256:    sum,
				Tier:      1,
				Detail:    maskName(raw.Mask),
				Bytes:     int(raw.Len),
			})
		}
	}
}

func isInteresting(name string) bool {
	for _, s := range []string{"env", "credential", "config", "passwords", "vault", "backup", "id_rsa", "wp-config", "k8s"} {
		if strings.Contains(strings.ToLower(name), s) {
			return true
		}
	}
	return false
}

func fileExists(p string) bool {
	_, err := os.Stat(p)
	return err == nil
}

func maskName(mask uint32) string {
	var parts []string
	if mask&syscall.IN_ACCESS != 0 {
		parts = append(parts, "IN_ACCESS")
	}
	if mask&syscall.IN_OPEN != 0 {
		parts = append(parts, "IN_OPEN")
	}
	if mask&syscall.IN_MODIFY != 0 {
		parts = append(parts, "IN_MODIFY")
	}
	if mask&syscall.IN_ATTRIB != 0 {
		parts = append(parts, "IN_ATTRIB")
	}
	if mask&syscall.IN_CLOSE_WRITE != 0 {
		parts = append(parts, "IN_CLOSE_WRITE")
	}
	return strings.Join(parts, "+")
}

// pollFiles adalah fallback bila inotify tidak tersedia.
func pollFiles(hashes map[string]string, send func(Event)) {
	seen := map[string]time.Time{}
	t := time.NewTicker(2 * time.Second)
	for range t.C {
		for p := range hashes {
			st, err := os.Stat(p)
			if err != nil {
				continue
			}
			at := st.ModTime()
			if prev, ok := seen[p]; !ok || at.After(prev) {
				seen[p] = at
			}
		}
	}
}
