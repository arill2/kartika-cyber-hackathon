#!/usr/bin/env python3
"""Credential spray ke decoy SSH, pola yang sama dihasilkan hydra/medusa.

Setiap koneksi mengirim banner klien SSH lalu sejumlah upaya autentikasi.
Karena umpan tidak menyelesaikan key-exchange dan tidak memiliki akun nyata,
tidak ada akses yang diberikan, namun setiap percobaan terekam POLARIS.
"""
import socket
import sys
import time

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 2222
tries = int(sys.argv[3]) if len(sys.argv) > 3 else 6

users = [b"admin", b"root", b"operator"]
pwds = [b"admin", b"123456", b"password", b"toor", b"hmi2024"]

sent = 0
for i in range(tries):
    try:
        s = socket.create_connection((host, port), timeout=3)
        s.settimeout(2)
        s.sendall(b"SSH-2.0-libssh_0.12.2\r\n")
        try:
            s.recv(256)  # banner server
        except socket.timeout:
            pass
        # payload KEXINIT palsu (cukup untuk merekam niat autentikasi)
        s.sendall(b"\x00\x00\x00\x2c\x0a\x14" + b"\x00" * 30)
        time.sleep(0.15)
        s.close()
        sent += 1
    except OSError as exc:
        print(f"  try#{i + 1} gagal: {exc}", file=sys.stderr)
    if i < len(users) and i < len(pwds):
        print(f"  try#{i + 1}: ssh {users[i].decode()}@{host}:{port} pass={pwds[i].decode()}")
    time.sleep(0.2)

print(f"selesai: {sent}/{tries} koneksi auth ke {host}:{port}")
