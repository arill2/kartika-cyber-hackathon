package main

import (
	"fmt"
	"log"
	"net"
	"net/http"
	"strings"
	"time"
)

// webDecoys adalah path yang hanya menarik bagi recon otomatis (docs/03).
var webDecoys = map[string]struct {
	status int
	body   string
}{
	"/.env":              {200, "APP_ENV=production\nDB_PASS=honey-3f9a2c\nS3_KEY=honey-token-do-not-use\n"},
	"/.git/config":       {200, "[core]\n\trepositoryformatversion = 0\n[remote \"origin\"]\n\turl = git@10.10.4.9:internal/payroll.git\n"},
	"/.aws/credentials":  {200, "[default]\naws_access_key_id = AKIAHONEYTOKEN01\naws_secret_access_key = honey/honeyhoney\n"},
	"/actuator/env":      {200, "{\"activeProfiles\":[\"prod\"],\"propertySources\":[{\"name\":\"systemEnvironment\"}]}\n"},
	"/actuator/heapdump": {200, "POLARIS-HONEYTOKEN heapdump placeholder\n"},
	"/server-status":     {200, "<h1>Apache Server Status</h1><p>Server Version: Apache/2.4.52 (Ubuntu)</p>\n"},
	"/.well-known/security.txt": {200, "Contact: mailto:soc@10.10.4.1\n"},
	"/api/v1/internal/users":    {200, "{\"users\":[{\"id\":1,\"user\":\"admin\",\"token\":\"honey-token-01\"}]}\n"},
}

// loginPaths menyajikan form login palsu; submit-nya dicatat (decoy_login_attempt).
var loginPaths = []string{"/wp-admin", "/phpmyadmin", "/adminer.php", "/manager/html", "/console", "/admin", "/login"}

func loginPage(path string) string {
	return fmt.Sprintf(`<!doctype html><html><head><title>%s</title>
<style>body{font-family:system-ui;background:#eef1f5;display:flex;height:100vh;align-items:center;justify-content:center}
form{background:#fff;padding:28px 32px;border-radius:8px;box-shadow:0 8px 30px rgba(0,0,0,.12);width:320px}
h2{margin:0 0 18px;font-size:18px}input{width:100%%;padding:9px 10px;margin:6px 0 14px;border:1px solid #cbd5e1;border-radius:6px;box-sizing:border-box}
button{width:100%%;padding:10px;background:#1e40af;color:#fff;border:0;border-radius:6px;cursor:pointer}</style></head>
<body><form method="POST" action="%s"><h2>%s &mdash; Sign in</h2>
<input name="username" placeholder="Username" required><input name="password" type="password" placeholder="Password" required>
<button type="submit">Login</button></form></body></html>`, path, path, strings.TrimPrefix(path, "/"))
}

func startWebDecoy(cfg Config, send func(Event)) {
	mux := http.NewServeMux()

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		ua := r.UserAgent()
		path := r.URL.Path

		if _, ok := webDecoys[path]; ok {
			d := webDecoys[path]
			send(Event{
				EventType: EvWebDecoy, SrcIP: clientIP(r), UserAgent: ua,
				Path: path, Method: r.Method, Tier: 2,
				DstPort: cfg.WebPort, Service: "http", Decoy: "web-decoy",
				Detail: "web decoy path diakses",
			})
			w.Header().Set("Server", "nginx/1.18.0 (Ubuntu)")
			w.WriteHeader(d.status)
			_, _ = w.Write([]byte(d.body))
			return
		}

		for _, lp := range loginPaths {
			if path == lp || strings.HasPrefix(path, lp+"/") {
				if r.Method == http.MethodPost {
					_ = r.ParseForm()
					send(Event{
						EventType: EvLoginAttempt, SrcIP: clientIP(r), UserAgent: ua,
						Path: path, Method: r.Method, Tier: 2, Service: "http",
						Decoy: "decoy-login", DstPort: cfg.WebPort,
						Username: r.FormValue("username"), Password: r.FormValue("password"),
						Detail: "kredensial disubmit ke login palsu",
					})
					http.Error(w, "Invalid credentials", http.StatusUnauthorized)
					return
				}
				send(Event{
					EventType: EvWebDecoy, SrcIP: clientIP(r), UserAgent: ua,
					Path: path, Method: r.Method, Tier: 2, Service: "http",
					Decoy: "decoy-login", DstPort: cfg.WebPort,
					Detail: "login decoy diakses",
				})
				w.Header().Set("Content-Type", "text/html; charset=utf-8")
				_, _ = w.Write([]byte(loginPage(path)))
				return
			}
		}

		if path == "/healthz" {
			_, _ = w.Write([]byte("ok\n"))
			return
		}

		// halaman portal internal palsu untuk "/"
		if path == "/" {
			w.Header().Set("Content-Type", "text/html; charset=utf-8")
			_, _ = w.Write([]byte("<html><title>Internal Portal</title><body><h1>Internal Portal</h1><p>Authorized personnel only.</p></body></html>"))
			return
		}
		http.NotFound(w, r)
	})

	port := cfg.WebPort
	addr := fmt.Sprintf(":%d", port)
	ln, err := net.Listen("tcp", addr)
	if err != nil {
		fallback := port + 1
		log.Printf("[agent] web decoy port %d gagal (%v); fallback ke %d", port, err, fallback)
		addr = fmt.Sprintf(":%d", fallback)
		ln, err = net.Listen("tcp", addr)
		if err != nil {
			log.Printf("[agent] web decoy TIDAK aktif: %v", err)
			return
		}
	}
	log.Printf("[agent] web decoy listening %s", addr)

	srv := &http.Server{Handler: mux, ReadHeaderTimeout: 5 * time.Second}
	if err := srv.Serve(ln); err != nil {
		log.Printf("[agent] web decoy berhenti: %v", err)
	}
}

func clientIP(r *http.Request) string {
	if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
		return strings.TrimSpace(strings.Split(xff, ",")[0])
	}
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr
	}
	return host
}
