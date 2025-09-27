socat -v OPENSSL-LISTEN:9090,cert=server/server.crt,key=server/server.key,cafile=ca/ca.crt,verify=1,fork,reuseaddr \
        TCP:localhost:8080

