#!/bin/bash
FILE=GenerateToken-demo.eif
if [ -f "$FILE" ]; then
    rm $FILE
fi
#docker rmi -f $(docker images -a -q)
docker rmi GenerateToken-demo:latest
pkill vsock-proxy


docker build -t GenerateToken-demo:latest .
nitro-cli build-enclave --docker-uri GenerateToken-demo:latest  --output-file GenerateToken-demo.eif > EnclaveImage.log

vsock-proxy 8000 kms.ap-northeast-1.amazonaws.com 443 &

nitro-cli run-enclave --cpu-count 2 --memory 2900 --eif-path GenerateToken-demo.eif --debug-mode
nitro-cli console --enclave-id $(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")