package main

import (
	"log"
	"os"
	"os/signal"
	"runtime"
	"syscall"
)

const banner = `
  ____   ___  _        _    ____  ___ ____
 |  _ \ / _ \| |      / \  |  _ \|_ _/ ___|
 | |_) | | | | |     / _ \ | |_) || |\___ \
 |  __/| |_| | |___ / ___ \|  _ < | | ___) |
 |_|    \___/|_____/_/   \_\_| \_\___|____/
        POLARIS Agent: Decoy & Honeytoken Sensor
`

func main() {
	log.SetFlags(log.Ltime)
	cfg := loadConfig()

	log.Print(banner)
	log.Printf("[agent] id=%s core=%s decoy-dir=%s", cfg.AgentID, cfg.CoreURL, cfg.DecoyDir)

	sender := NewSender(cfg)
	sender.Run()

	emit := sender.Emit

	// 1) honeytoken files + inotify
	setupHoneytokens(cfg, emit)

	// 2) decoy ports (IT + OT) + port spray
	startDecoyPorts(defaultSpecs(cfg), emit)
	startBarePorts(cfg.ExtraPorts, emit)

	// 3) web decoy
	go startWebDecoy(cfg, emit)

	log.Printf("[agent] siap. runtime=%s/%s goroutines=%d", runtime.GOOS, runtime.GOARCH, runtime.NumGoroutine())

	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
	<-sig
	log.Printf("[agent] shutdown (%s). umpan tetap tertinggal di %s", sender.Stats(), cfg.DecoyDir)
}
