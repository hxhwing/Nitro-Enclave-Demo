import socket
import requests
import json
import subprocess
import boto3
import base64
import random

def aws_api_call(credential, keyid):
    """
    Make AWS API call using credential obtained from parent EC2 instance
    """
    print(type(keyid))
    client = boto3.client(
        'kms',
        region_name = 'ap-northeast-1',
        aws_access_key_id = credential['access_key_id'],
        aws_secret_access_key = credential['secret_access_key'],
        aws_session_token = credential['token']
    )
    source_plaintext=random.randint(000000,999999)
    print(source_plaintext)
    source_plaintext=str(source_plaintext)
    source_plaintext=str.encode(source_plaintext)
    #source_plaintext="Hello, KMS\!"
    ciphertext = client.encrypt(Plaintext=source_plaintext, KeyId=keyid,EncryptionAlgorithm='SYMMETRIC_DEFAULT')
    # cycled_plaintext = client.decrypt(CiphertextBlob=ciphertext['CiphertextBlob'], KeyId=keyid,EncryptionAlgorithm='SYMMETRIC_DEFAULT')
    # print(cycled_plaintext)
    str_cipher=base64.b64encode(ciphertext['CiphertextBlob'])
    print(str_cipher.decode('utf-8'),type(str_cipher.decode('utf-8')))
    # Call the standalone kmstool through subprocess
    proc = subprocess.Popen(
        [
            "/app/kmstool_enclave_cli",
            "--region", "ap-northeast-1",
            "--proxy-port", "8000",
            "--aws-access-key-id", "%s" % credential['access_key_id'],
            "--aws-secret-access-key", "%s" % credential['secret_access_key'],
            "--aws-session-token", "%s" % credential['token'],
            "--ciphertext", "%s" % str_cipher.decode('utf-8'),
        ],
        stdout=subprocess.PIPE
    )

    result = proc.communicate()[0]
    print(result)
    
    # Return some data from API response
    result={
        'Plaintext':source_plaintext,
        'Ciphertext': str_cipher.decode('utf-8'),
        'Encrypted-Plaintext': (base64.b64decode(result)).decode(),
    }
    return result

def main():
    print("Starting server...")
    
    # Create a vsock socket object
    s = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)

    # Listen for connection from any CID
    cid = socket.VMADDR_CID_ANY

    # The port should match the client running in parent EC2 instance
    port = 5000

    # Bind the socket to CID and port
    s.bind((cid, port))

    # Listen for connection from client
    s.listen()

    while True:
        c, addr = s.accept()

        # Get data sent from parent instance
        payload = c.recv(65536)
        client_request = json.loads(payload.decode())

        credential = client_request['credential']
        ciphertext = client_request['ciphertext']

        # Get data from AWS API call
        content = aws_api_call(credential, str(ciphertext))
        print(content)
        # Send the response back to parent instance
        c.send(str.encode(str(content)))

        # Close the connection
        c.close() 

if __name__ == '__main__':
    main()
