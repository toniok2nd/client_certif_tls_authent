#!/usr/bin/env python3
"""
generate_certs.py

Usage example:
  python generate_certs.py \
    --ca-dir ca --server-dir server --client-dir client \
    --ca-name MyCA --server-name MyServer --client-name MyClient \
    --client-p12-pass secret --days 365 --client-alt-names client.local,alt.example \
    --keysize 4096
"""

import argparse
import subprocess
import os
import sys
import textwrap

# ANSI color codes
CSI = "\033["
RESET = CSI + "0m"
BOLD = CSI + "1m"
GREEN = CSI + "32m"
YELLOW = CSI + "33m"
RED = CSI + "31m"
CYAN = CSI + "36m"

def c(text, color):
    return f"{color}{text}{RESET}"

def run(cmd, capture_output=False):
    print(c("✨ +", CYAN), " ".join(cmd))
    try:
        if capture_output:
            return subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(c("❌ Command failed:", RED), e, file=sys.stderr)
        if getattr(e, "stdout", None):
            print(c("stdout:", YELLOW), e.stdout, file=sys.stderr)
        if getattr(e, "stderr", None):
            print(c("stderr:", YELLOW), e.stderr, file=sys.stderr)
        sys.exit(e.returncode)

def write_san_config(path, common_name, alt_names):
    """
    Writes a SAN config for a certificate with CN=common_name and alt_names list.
    alt_names should be a list of DNS names (strings). If empty, only CN will be set.
    """
    alt_lines = []
    for i, name in enumerate(alt_names, start=1):
        alt_lines.append(f"DNS.{i} = {name}")
    alt_section = "\n".join(alt_lines) if alt_lines else ""
    content = textwrap.dedent(f"""\
        [ req ]
        distinguished_name = req_distinguished_name
        req_extensions = req_ext
        prompt = no

        [ req_distinguished_name ]
        CN = {common_name}

        [ req_ext ]
        subjectAltName = @alt_names

        [ alt_names ]
        {alt_section}
        """)
    with open(path, "w") as f:
        f.write(content)
    print(c("📝 Wrote SAN config:", GREEN), path)

def ask_clean(path):
    """If path exists, ask user whether to remove it. Returns True if removed or didn't exist, False if kept."""
    if not os.path.exists(path):
        return True
    while True:
        reply = input(c(f"⚠️  File exists: {path}. Remove it? [y/N]: ", YELLOW)).strip().lower()
        if reply in ("y", "yes"):
            try:
                os.remove(path)
                print(c("🗑️  Removed:", GREEN), path)
                return True
            except Exception as e:
                print(c("❌ Could not remove", RED), f"{path}: {e}", file=sys.stderr)
                return False
        if reply in ("n", "no", ""):
            print(c("📌 Keeping:", CYAN), path)
            return False
        print(c("Please answer y or n.", YELLOW))

def main():
    p = argparse.ArgumentParser(description="Generate CA, server and client certs using OpenSSL")
    p.add_argument("--ca-dir", default="ca")
    p.add_argument("--server-dir", default="server")
    p.add_argument("--client-dir", default="client")
    p.add_argument("--ca-name", default="MyCA")
    p.add_argument("--server-name", default="MyServer")
    p.add_argument("--client-name", default="MyClient")
    p.add_argument("--ca-key", default="ca.key")
    p.add_argument("--ca-cert", default="ca.crt")
    p.add_argument("--server-key", default="server.key")
    p.add_argument("--server-csr", default="server.csr")
    p.add_argument("--server-cert", default="server.crt")
    p.add_argument("--client-key", default="client.key")
    p.add_argument("--client-csr", default="client.csr")
    p.add_argument("--client-cert", default="client.crt")
    p.add_argument("--client-p12-pass", default="secret")
    p.add_argument("--days", type=int, default=365)
    p.add_argument(
        "--client-alt-names",
        help="Comma-separated list of additional DNS names for the client certificate (e.g. client.local,alt.example).",
        default=""
    )
    p.add_argument(
        "--keysize",
        type=int,
        default=2048,
        help="RSA key size in bits for generated private keys (default: 2048)."
    )
    args = p.parse_args()

    # parse alt names into list, remove empty strings, strip whitespace
    client_alt_names = [s.strip() for s in args.client_alt_names.split(",") if s.strip()]

    server_san_config = os.path.join(args.server_dir, "san.cnf")
    client_san_config = os.path.join(args.client_dir, "san.cnf")

    # Create directories
    os.makedirs(args.ca_dir, exist_ok=True)
    os.makedirs(args.server_dir, exist_ok=True)
    os.makedirs(args.client_dir, exist_ok=True)

    # Files to potentially create
    files = [
        os.path.join(args.ca_dir, args.ca_key),
        os.path.join(args.ca_dir, args.ca_cert),
        os.path.join(args.server_dir, args.server_key),
        os.path.join(args.server_dir, args.server_csr),
        os.path.join(args.server_dir, args.server_cert),
        os.path.join(args.client_dir, args.client_key),
        os.path.join(args.client_dir, args.client_csr),
        os.path.join(args.client_dir, args.client_cert),
        os.path.join(args.client_dir, "client.p12"),
        server_san_config,
        client_san_config,
    ]

    # Ask for each existing file whether to remove it
    keep_map = {}
    for f in files:
        if os.path.exists(f):
            removed = ask_clean(f)
            keep_map[f] = not removed
        else:
            keep_map[f] = False

    # Create SAN configs (overwrite if user removed or not existing, otherwise skip)
    if not keep_map.get(server_san_config, False):
        write_san_config(server_san_config, args.server_name, [args.server_name])
    else:
        print(c("⏭️  Skipping overwrite of", CYAN), server_san_config)

    if not keep_map.get(client_san_config, False):
        write_san_config(client_san_config, args.client_name, [args.client_name] + client_alt_names)
    else:
        print(c("⏭️  Skipping overwrite of", CYAN), client_san_config)

    keysize_opt = str(args.keysize)
    print(c(f"🔐 Using RSA key size: {keysize_opt} bits", BOLD + CYAN))

    # Generate CA key (skip if user chose to keep existing)
    ca_key_path = os.path.join(args.ca_dir, args.ca_key)
    if not keep_map.get(ca_key_path, False):
        run([
            "openssl", "genpkey", "-algorithm", "RSA",
            "-out", ca_key_path,
            "-pkeyopt", f"rsa_keygen_bits:{keysize_opt}"
        ])
    else:
        print(c("⏭️  Skipping generation of", CYAN), ca_key_path)

    # Generate CA certificate
    ca_cert_path = os.path.join(args.ca_dir, args.ca_cert)
    if not keep_map.get(ca_cert_path, False):
        run([
            "openssl", "req", "-x509", "-new", "-nodes",
            "-key", ca_key_path,
            "-sha256", "-days", str(args.days),
            "-out", ca_cert_path,
            "-subj", f"/CN={args.ca_name}"
        ])
    else:
        print(c("⏭️  Skipping generation of", CYAN), ca_cert_path)

    # Generate server key
    server_key_path = os.path.join(args.server_dir, args.server_key)
    if not keep_map.get(server_key_path, False):
        run([
            "openssl", "genpkey", "-algorithm", "RSA",
            "-out", server_key_path,
            "-pkeyopt", f"rsa_keygen_bits:{keysize_opt}"
        ])
    else:
        print(c("⏭️  Skipping generation of", CYAN), server_key_path)

    # Generate server CSR
    server_csr_path = os.path.join(args.server_dir, args.server_csr)
    if not keep_map.get(server_csr_path, False):
        run([
            "openssl", "req", "-new",
            "-key", server_key_path,
            "-out", server_csr_path,
            "-config", server_san_config
        ])
    else:
        print(c("⏭️  Skipping generation of", CYAN), server_csr_path)

    # Generate server certificate signed by CA
    server_cert_path = os.path.join(args.server_dir, args.server_cert)
    if not keep_map.get(server_cert_path, False):
        run([
            "openssl", "x509", "-req",
            "-in", server_csr_path,
            "-CA", ca_cert_path,
            "-CAkey", ca_key_path,
            "-CAcreateserial",
            "-out", server_cert_path,
            "-days", str(args.days),
            "-sha256",
            "-extfile", server_san_config,
            "-extensions", "req_ext"
        ])
    else:
        print(c("⏭️  Skipping generation of", CYAN), server_cert_path)

    # Generate client key
    client_key_path = os.path.join(args.client_dir, args.client_key)
    if not keep_map.get(client_key_path, False):
        run([
            "openssl", "genpkey", "-algorithm", "RSA",
            "-out", client_key_path,
            "-pkeyopt", f"rsa_keygen_bits:{keysize_opt}"
        ])
    else:
        print(c("⏭️  Skipping generation of", CYAN), client_key_path)

    # Generate client CSR using client SAN config
    client_csr_path = os.path.join(args.client_dir, args.client_csr)
    if not keep_map.get(client_csr_path, False):
        run([
            "openssl", "req", "-new",
            "-key", client_key_path,
            "-out", client_csr_path,
            "-config", client_san_config
        ])
    else:
        print(c("⏭️  Skipping generation of", CYAN), client_csr_path)

    # Generate client certificate signed by CA (include SANs from client_san_config)
    client_cert_path = os.path.join(args.client_dir, args.client_cert)
    if not keep_map.get(client_cert_path, False):
        run([
            "openssl", "x509", "-req",
            "-in", client_csr_path,
            "-CA", ca_cert_path,
            "-CAkey", ca_key_path,
            "-CAcreateserial",
            "-out", client_cert_path,
            "-days", str(args.days),
            "-sha256",
            "-extfile", client_san_config,
            "-extensions", "req_ext"
        ])
    else:
        print(c("⏭️  Skipping generation of", CYAN), client_cert_path)

    # Generate client PKCS#12
    client_p12_path = os.path.join(args.client_dir, "client.p12")
    if not keep_map.get(client_p12_path, False):
        run([
            "openssl", "pkcs12", "-export",
            "-out", client_p12_path,
            "-inkey", client_key_path,
            "-in", client_cert_path,
            "-name", "Client Certificate",
            "-passout", f"pass:{args.client_p12_pass}"
        ])
    else:
        print(c("⏭️  Skipping generation of", CYAN), client_p12_path)

    print(c(f"✅ CA certificate and keys generated in {args.ca_dir}", GREEN))
    print(c(f"✅ Server certificate and keys generated in {args.server_dir}", GREEN))
    print(c(f"✅ Client certificate and keys generated in {args.client_dir}", GREEN))

if __name__ == "__main__":
    main()

