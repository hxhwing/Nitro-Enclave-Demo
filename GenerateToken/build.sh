#!/bin/bash
FILE=GenerateToken-demo.eif
if [ -f "$FILE" ]; then
    rm $FILE
fi

RunningEnclave=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
if [ -n "$RunningEnclave" ]; then
	nitro-cli terminate-enclave --enclave-id $(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID");
fi

#docker rmi -f $(docker images -a -q)
docker rmi generatetoken-demo:latest
pkill vsock-proxy


docker build -t generatetoken-demo:latest .
nitro-cli build-enclave --docker-uri generatetoken-demo:latest  --output-file GenerateToken-demo.eif > EnclaveImage.log

vsock-proxy 8000 kms.ap-northeast-1.amazonaws.com 443 &

nitro-cli run-enclave --cpu-count 2 --memory 2900 --enclave-cid 10 --eif-path GenerateToken-demo.eif --debug-mode
nitro-cli console --enclave-id $(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")