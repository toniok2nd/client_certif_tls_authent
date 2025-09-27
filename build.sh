#!/bin/bash

# Variables
CA_DIR="ca"
SERVER_DIR="server"
CLIENT_DIR="client"
CA_NAME="MyCA"
SERVER_NAME="MyServer"
CLIENT_NAME="MyClient"
CA_KEY="ca.key"
CA_CERT="ca.crt"
SERVER_KEY="server.key"
SERVER_CSR="server.csr"
SERVER_CERT="server.crt"
CLIENT_KEY="client.key"
CLIENT_CSR="client.csr"
CLIENT_CERT="client.crt"
CLIENT_P12_PASS="secret"
DAYS=365
SAN_CONFIG=$SERVER_DIR/san.cnf

# Create OpenSSL configuration file for SAN
cat <<EOF > $SAN_CONFIG
[ req ]
distinguished_name = req_distinguished_name
req_extensions = req_ext
prompt = no

[ req_distinguished_name ]
CN = $SERVER_NAME

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = $SERVER_NAME
EOF


# Create directories
mkdir -p $CA_DIR $SERVER_DIR $CLIENT_DIR

# Generate CA key
openssl genpkey -algorithm RSA -out $CA_DIR/$CA_KEY -pkeyopt rsa_keygen_bits:2048

# Generate CA certificate
openssl req -x509 -new -nodes -key $CA_DIR/$CA_KEY -sha256 -days $DAYS -out $CA_DIR/$CA_CERT -subj "/CN=$CA_NAME"

# Generate server key
openssl genpkey -algorithm RSA -out $SERVER_DIR/$SERVER_KEY -pkeyopt rsa_keygen_bits:2048

# Generate server CSR
openssl req -new -key $SERVER_DIR/$SERVER_KEY -out $SERVER_DIR/$SERVER_CSR -config $SAN_CONFIG

# Generate server certificate signed by CA
openssl x509 -req -in $SERVER_DIR/$SERVER_CSR -CA $CA_DIR/$CA_CERT -CAkey $CA_DIR/$CA_KEY -CAcreateserial -out $SERVER_DIR/$SERVER_CERT -days $DAYS -sha256 -extfile $SAN_CONFIG -extensions req_ext


# Generate client key
openssl genpkey -algorithm RSA -out $CLIENT_DIR/$CLIENT_KEY -pkeyopt rsa_keygen_bits:2048

# Generate client CSR
openssl req -new -key $CLIENT_DIR/$CLIENT_KEY -out $CLIENT_DIR/$CLIENT_CSR -subj "/CN=$CLIENT_NAME"

# Generate client certificate signed by CA
openssl x509 -req -in $CLIENT_DIR/$CLIENT_CSR -CA $CA_DIR/$CA_CERT -CAkey $CA_DIR/$CA_KEY -CAcreateserial -out $CLIENT_DIR/$CLIENT_CERT -days $DAYS -sha256

# Generate client certificate in p12 format for firefox
openssl pkcs12 -export -out $CLIENT_DIR/client.p12 -inkey $CLIENT_DIR/$CLIENT_KEY -in $CLIENT_DIR/$CLIENT_CERT -name "Client Certificate" -passout pass:$CLIENT_P12_PASS


echo "CA certificate and keys generated in $CA_DIR"
echo "Server certificate and keys generated in $SERVER_DIR"
echo "Client certificate and keys generated in $CLIENT_DIR"

