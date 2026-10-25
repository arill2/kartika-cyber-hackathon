package main

import (
	"os"
	"strconv"
	"strings"
)

// Config menampung seluruh konfigurasi agent. Semua nilai dapat di-override
// lewat environment variable agar mudah di-deploy di satuan berbeda
// (lihat docs/06-tech-stack.md -> "Config via file/env").
type Config struct {
	AgentID    string
	CoreURL    string // contoh: http://127.0.0.1:8787
	Token      string // token autentikasi agent -> collector
	DecoyDir   string // lokasi honeytoken file
	WebPort    int    // port server web decoy (path + fake login)
	BeaconBase string // basis URL honeytoken (dibaca oleh payload umpan)

	// Port decoy (dapat di-override)
	PortSSH    int
	PortMySQL  int
	PortRedis  int
	PortRDP    int
	PortSMB    int
	PortHMI    int
	PortModbus int
	ExtraPorts []int // "port spray" - umpan ringan di banyak port sekaligus
}

func envInts(key, def string) []int {
	raw := env(key, def)
	var out []int
	for _, tok := range strings.Split(raw, ",") {
		tok = strings.TrimSpace(tok)
		if tok == "" {
			continue
		}
		if n, err := strconv.Atoi(tok); err == nil {
			out = append(out, n)
		}
	}
	return out
}

func env(key, def string) string {
	if v := strings.TrimSpace(os.Getenv(key)); v != "" {
		return v
	}
	return def
}

func envInt(key string, def int) int {
	if v := strings.TrimSpace(os.Getenv(key)); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			return n
		}
	}
	return def
}

func loadConfig() Config {
	home, _ := os.UserHomeDir()
	defDir := home + "/.polaris/decoy"
	if home == "" {
		defDir = os.TempDir() + "/polaris-decoy"
	}

	core := env("POLARIS_CORE_URL", "http://127.0.0.1:8787")
	return Config{
		AgentID:    env("POLARIS_AGENT_ID", "node-01"),
		CoreURL:    strings.TrimRight(core, "/"),
		Token:      env("POLARIS_TOKEN", "polaris-dev-token"),
		DecoyDir:   env("POLARIS_DECOY_DIR", defDir),
		WebPort:    envInt("POLARIS_WEB_PORT", 80),
		BeaconBase: env("POLARIS_BEACON_BASE", strings.TrimRight(core, "/")+"/beacon"),
		PortSSH:    envInt("POLARIS_PORT_SSH", 2222),
		PortMySQL:  envInt("POLARIS_PORT_MYSQL", 3306),
		PortRedis:  envInt("POLARIS_PORT_REDIS", 6379),
		PortRDP:    envInt("POLARIS_PORT_RDP", 3389),
		PortSMB:    envInt("POLARIS_PORT_SMB", 445),
		PortHMI:    envInt("POLARIS_PORT_HMI", 8080),
		PortModbus: envInt("POLARIS_PORT_MODBUS", 502),
		// Port spray: beragam port layanan populer yang mustahil tersentuh
		// operasi normal. Memperluas permukaan tipuan -> scanner mudah terbaca.
		ExtraPorts: envInts("POLARIS_EXTRA_PORTS",
			"21,23,25,135,139,443,1433,1521,2049,2375,5432,5900,5985,7001,8001,9000,9200,10000,11211,27017,5000,8443,1080,8888"),
	}
}
