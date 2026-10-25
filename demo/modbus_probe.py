#!/usr/bin/env python3
"""Probe Modbus/TCP ke decoy OT, meniru klien ICS membaca holding register.

Mengirim request Modbus FC03 (Read Holding Registers) lalu menampilkan balasan.
Semua lalu lintas ini direkam POLARIS sebagai decoy_ot_touch (ATT&CK for ICS).
"""
import socket
import struct
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 502

# MBAP: transaction=1, protocol=0, length=6, unit=1 | PDU: FC03, addr=0, qty=10
req = struct.pack(">HHHBBHH", 0x0001, 0x0000, 0x0006, 0x01, 0x03, 0x0000, 0x000A)
try:
    s = socket.create_connection((host, port), timeout=3)
    s.sendall(req)
    data = s.recv(256)
    print(f"modbus {host}:{port} -> {data.hex() if data else '(tanpa balasan)'}")
    s.close()
except OSError as exc:
    print(f"modbus {host}:{port} gagal: {exc}")
