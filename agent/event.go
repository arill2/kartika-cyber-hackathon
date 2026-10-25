package main

import "time"

// Event adalah unit telemetri yang dikirim agent ke collector.
// Skema JSON ini adalah kontrak antara agent (Go) dan collector (Python).
type Event struct {
	AgentID    string `json:"agent_id"`
	EventType  string `json:"event_type"`
	TS         string `json:"ts"`
	SrcIP      string `json:"src_ip"`
	SrcPort    int    `json:"src_port,omitempty"`
	DstPort    int    `json:"dst_port,omitempty"`
	Decoy      string `json:"decoy,omitempty"`
	Service    string `json:"service,omitempty"`
	Tier       int    `json:"tier"`
	Payload    string `json:"payload_printable,omitempty"`
	PayloadHex string `json:"payload_hex,omitempty"`
	UserAgent  string `json:"user_agent,omitempty"`
	Path       string `json:"http_path,omitempty"`
	Method     string `json:"http_method,omitempty"`
	Username   string `json:"username,omitempty"`
	Password   string `json:"password,omitempty"`
	Bytes      int    `json:"bytes,omitempty"`
	DurationMS int64  `json:"duration_ms,omitempty"`
	Token      string `json:"token,omitempty"`
	FilePath   string `json:"file_path,omitempty"`
	SHA256     string `json:"sha256,omitempty"`
	Detail     string `json:"detail,omitempty"`
}

// Tipe event yang dikenal engine (docs/04-engine-deteksi.md).
const (
	EvDecoyConn      = "decoy_connection"      // T2 - koneksi ke port umpan
	EvWebDecoy       = "web_decoy_hit"         // T2 - akses path umpan
	EvFileAccess     = "honeytoken_file_access" // T1 - berkas umpan dibaca
	EvCanaryUsed     = "canary_cred_used"      // T1 - kredensial umpan dipakai
	EvBeaconFetch    = "honeytoken_url_fetch"  // T1 - honeytoken URL di-fetch
	EvLoginAttempt   = "decoy_login_attempt"   // T2 - submit ke login palsu
	EvOTTouch        = "decoy_ot_touch"        // T2 - port OT/ICS disentuh
)

func nowRFC3339() string { return time.Now().UTC().Format(time.RFC3339Nano) }
