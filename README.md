# generate files 
```bash
python generate_file.py -h
usage: generate_file.py [-h] [--ca-dir CA_DIR] [--server-dir SERVER_DIR] [--client-dir CLIENT_DIR]
                        [--ca-name CA_NAME] [--server-name SERVER_NAME] [--client-name CLIENT_NAME]
                        [--ca-key CA_KEY] [--ca-cert CA_CERT] [--server-key SERVER_KEY]
                        [--server-csr SERVER_CSR] [--server-cert SERVER_CERT]
                        [--client-key CLIENT_KEY] [--client-csr CLIENT_CSR]
                        [--client-cert CLIENT_CERT] [--client-p12-pass CLIENT_P12_PASS]
                        [--days DAYS] [--client-alt-names CLIENT_ALT_NAMES] [--keysize KEYSIZE]

Generate CA, server and client certs using OpenSSL

options:
  -h, --help            show this help message and exit
  --ca-dir CA_DIR
  --server-dir SERVER_DIR
  --client-dir CLIENT_DIR
  --ca-name CA_NAME
  --server-name SERVER_NAME
  --client-name CLIENT_NAME
  --ca-key CA_KEY
  --ca-cert CA_CERT
  --server-key SERVER_KEY
  --server-csr SERVER_CSR
  --server-cert SERVER_CERT
  --client-key CLIENT_KEY
  --client-csr CLIENT_CSR
  --client-cert CLIENT_CERT
  --client-p12-pass CLIENT_P12_PASS
  --days DAYS
  --client-alt-names CLIENT_ALT_NAMES
                        Comma-separated list of additional DNS names for the client certificate
                        (e.g. client.local,alt.example).
  --keysize KEYSIZE     RSA key size in bits for generated private keys (default: 2048).
```

# serve a file
```bash
python serve_file.py --file "client/client.p12"  --password PASSWORD_FOR_FILE
```

# serve public with ngrok
```bash
ngrok http https://localhost:7860
```
