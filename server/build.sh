#!/bin/bash
FILE=kms-demo.eif
if [ -f "$FILE" ]; then
    rm $FILE
fi
#docker rmi -f $(docker images -a -q)
docker rmi kms-demo:latest
pkill vsock-proxy


docker build -t kms-demo:latest .
nitro-cli build-enclave --docker-uri kms-demo:latest  --output-file kms-demo.eif > EnclaveImage.log

vsock-proxy 8000 kms.ap-northeast-1.amazonaws.com 443 &

nitro-cli run-enclave --cpu-count 2 --memory 2900 --eif-path kms-demo.eif --debug-mode
nitro-cli console --enclave-id $(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")