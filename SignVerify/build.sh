#!/bin/bash
FILE=SignVerify-demo.eif
if [ -f "$FILE" ]; then
    rm $FILE
fi
#docker rmi -f $(docker images -a -q)
docker rmi SignVerify-demo:latest
pkill vsock-proxy


docker build -t SignVerify-demo:latest .
nitro-cli build-enclave --docker-uri SignVerify-demo:latest  --output-file SignVerify-demo.eif > EnclaveImage.log

vsock-proxy 8000 kms.ap-northeast-1.amazonaws.com 443 &

nitro-cli run-enclave --cpu-count 2 --memory 2900 --eif-path SignVerify-demo.eif --debug-mode
nitro-cli console --enclave-id $(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")