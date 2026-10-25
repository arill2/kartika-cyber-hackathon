package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"log"
	"net"
	"strings"
	"time"
)

// decoySpec mendefinisikan satu listener umpan.
type decoySpec struct {
	name    string // "fake-ssh"
	port    int
	service string
	tier    int
	banner  []byte
	// respond dipanggil untuk setiap chunk data; mengembalikan balasan opsional.
	respond func(data []byte) []byte
	ot      bool
}

func modbusBanner() []byte {
	// MBAP header (transaction=1, proto=0, len=3, unit=1) + FC3 exception.
	return []byte{0x00, 0x01, 0x00, 0x00, 0x00, 0x03, 0x01, 0x83, 0x02}
}

func mysqlBanner() []byte {
	version := "5.7.42-0ubuntu0.18.04.1"
	p := []byte{0x0a}
	p = append(p, []byte(version)...)
	p = append(p, 0x00)
	p = append(p, 0x01, 0x00, 0x00, 0x00)       // thread id
	p = append(p, []byte("abcdefgh")...)        // auth-plugin-data-part-1
	p = append(p, 0x00)                         // filler
	p = append(p, 0xff, 0xf7)                   // capability lower
	p = append(p, 0x21)                         // charset
	p = append(p, 0x02, 0x00)                   // status
	p = append(p, 0xff, 0x81)                   // capability upper
	p = append(p, 0x15)                         // auth data len
	p = append(p, make([]byte, 10)...)          // reserved
	p = append(p, []byte("ijklmnopqrst")...)    // auth-plugin-data-part-2
	p = append(p, 0x00)
	hdr := []byte{byte(len(p)), byte(len(p) >> 8), byte(len(p) >> 16), 0x00}
	return append(hdr, p...)
}

func defaultSpecs(cfg Config) []decoySpec {
	return []decoySpec{
		{
			name: "fake-ssh", port: cfg.PortSSH, service: "ssh", tier: 2,
			banner: []byte("SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1\r\n"),
		},
		{
			name: "fake-mysql", port: cfg.PortMySQL, service: "mysql", tier: 2,
			banner: mysqlBanner(),
		},
		{
			name: "fake-redis", port: cfg.PortRedis, service: "redis", tier: 2,
			respond: func(data []byte) []byte {
				if len(data) == 0 {
					return nil
				}
				up := strings.ToUpper(string(data))
				switch {
				case strings.Contains(up, "PING"):
					return []byte("+PONG\r\n")
				case strings.Contains(up, "INFO"):
					return []byte("$0\r\n\r\n")
				default:
					return []byte("-ERR unknown command\r\n")
				}
			},
		},
		{name: "fake-rdp", port: cfg.PortRDP, service: "rdp", tier: 2},
		{name: "fake-smb", port: cfg.PortSMB, service: "smb", tier: 2},
		{name: "fake-hmi", port: cfg.PortHMI, service: "hmi", tier: 2, ot: true,
			respond: func(data []byte) []byte {
				return []byte("HTTP/1.1 200 OK\r\nServer: BOOTP-HMI/2.4\r\nContent-Length: 0\r\n\r\n")
			}},
		{
			name: "decoy-modbus", port: cfg.PortModbus, service: "modbus", tier: 2, ot: true,
			banner: modbusBanner(),
		},
	}
}

func startDecoyPorts(specs []decoySpec, send func(Event)) {
	for _, spec := range specs {
		go serveDecoy(spec, send)
	}
}

// listenWithFallback mencoba port utama; bila gagal (mis. port < 1024 tanpa
// privilege) turun ke port+10000 agar sensor tetap aktif.
func listenWithFallback(port int) (net.Listener, int, error) {
	ln, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
	if err == nil {
		return ln, port, nil
	}
	if port < 1024 {
		alt := port + 10000
		if ln2, err2 := net.Listen("tcp", fmt.Sprintf(":%d", alt)); err2 == nil {
			return ln2, alt, nil
		}
	}
	return nil, port, err
}

func serveDecoy(spec decoySpec, send func(Event)) {
	ln, actual, err := listenWithFallback(spec.port)
	if err != nil {
		log.Printf("[agent] decoy %s TIDAK aktif di :%d: %v", spec.name, spec.port, err)
		return
	}
	log.Printf("[agent] decoy %-14s listening :%d", spec.name, actual)
	for {
		conn, err := ln.Accept()
		if err != nil {
			time.Sleep(50 * time.Millisecond)
			continue
		}
		go handleDecoyConn(conn, spec, actual, send)
	}
}

// wellKnownService menebak nama layanan dari nomor port (untuk konteks alert).
var wellKnownService = map[int]string{
	21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 80: "http", 110: "pop3",
	135: "msrpc", 139: "netbios", 143: "imap", 443: "https", 445: "smb",
	587: "smtp", 993: "imaps", 995: "pop3s", 1080: "socks", 1433: "mssql",
	1521: "oracle", 2049: "nfs", 2375: "docker", 3306: "mysql", 3389: "rdp",
	5000: "http-alt", 5432: "postgres", 5601: "kibana", 5900: "vnc",
	5985: "winrm", 6379: "redis", 7001: "weblogic", 8000: "http-alt",
	8080: "hmi", 8443: "https-alt", 8888: "http-alt", 9000: "portainer",
	9200: "elasticsearch", 10000: "webmin", 11211: "memcached", 27017: "mongodb", 502: "modbus",
}

func serviceForPort(port int) string {
	if s, ok := wellKnownService[port]; ok {
		return s
	}
	return "unknown"
}

// startBarePorts membuka banyak listener ringan (port spray) - umpan minimum
// untuk memperluas deteksi scanner (docs/03 -> Decoy Ports).
func startBarePorts(ports []int, send func(Event)) {
	for _, p := range ports {
		go func(port int) {
			ln, actual, err := listenWithFallback(port)
			if err != nil {
				return
			}
			log.Printf("[agent] decoy port-spray listening :%d (%s)", actual, serviceForPort(actual))
			for {
				conn, err := ln.Accept()
				if err != nil {
					time.Sleep(50 * time.Millisecond)
					continue
				}
				go func(c net.Conn) {
					defer c.Close()
					start := time.Now()
					var srcIP string
					var srcPort int
					if ta, ok := c.RemoteAddr().(*net.TCPAddr); ok {
						srcIP, srcPort = ta.IP.String(), ta.Port
					}
					_ = c.SetReadDeadline(time.Now().Add(2 * time.Second))
					buf := make([]byte, 512)
					n, _ := c.Read(buf)
					send(Event{
						EventType: EvDecoyConn, SrcIP: srcIP, SrcPort: srcPort, DstPort: actual,
						Decoy: "decoy-port", Service: serviceForPort(actual), Tier: 2,
						Payload: sanitize(buf[:n], 200), PayloadHex: hex.EncodeToString(buf[:n]),
						Bytes: n, DurationMS: time.Since(start).Milliseconds(),
					})
				}(conn)
			}
		}(p)
	}
}

func handleDecoyConn(conn net.Conn, spec decoySpec, actualPort int, send func(Event)) {
	defer conn.Close()
	start := time.Now()

	var srcIP string
	var srcPort int
	if ta, ok := conn.RemoteAddr().(*net.TCPAddr); ok {
		srcIP = ta.IP.String()
		srcPort = ta.Port
	}

	if len(spec.banner) > 0 {
		_ = conn.SetWriteDeadline(time.Now().Add(2 * time.Second))
		_, _ = conn.Write(spec.banner)
	}

	// Deadline baca panjang: memberi ruang agar tool brute force (hydra/medusa)
	// dapat menyelesaikan beberapa percobaan auth sebelum koneksi ditutup,
	// sehingga pola brute force terekam utuh.
	_ = conn.SetReadDeadline(time.Now().Add(15 * time.Second))
	buf := make([]byte, 4096)
	total := 0
	var first []byte
	for {
		n, err := conn.Read(buf)
		if n > 0 {
			if first == nil {
				first = append([]byte{}, buf[:n]...)
			}
			total += n
			if spec.respond != nil {
				if resp := spec.respond(buf[:n]); len(resp) > 0 {
					_, _ = conn.Write(resp)
				}
			}
		}
		if err != nil {
			break
		}
		if total > 16384 {
			break
		}
	}

	evType := EvDecoyConn
	if spec.ot {
		evType = EvOTTouch
	}
	printable := sanitize(first, 256)
	sum := sha256.Sum256(first)

	send(Event{
		EventType:  evType,
		SrcIP:      srcIP,
		SrcPort:    srcPort,
		DstPort:    actualPort,
		Decoy:      spec.name,
		Service:    spec.service,
		Tier:       spec.tier,
		Payload:    printable,
		PayloadHex: hex.EncodeToString(first),
		Bytes:      total,
		DurationMS: time.Since(start).Milliseconds(),
		SHA256:     hex.EncodeToString(sum[:]),
	})
}

// sanitize mengubah bytes menjadi teks printable (redaksi byte non-cetak).
func sanitize(b []byte, max int) string {
	if len(b) > max {
		b = b[:max]
	}
	var sb strings.Builder
	for _, c := range b {
		if c >= 32 && c < 127 {
			sb.WriteByte(c)
		} else if c == '\n' || c == '\r' || c == '\t' {
			sb.WriteByte(' ')
		} else {
			sb.WriteByte('.')
		}
	}
	return strings.TrimSpace(sb.String())
}
