import socket
from cryptography.hazmat.backends import default_backend
import requests
import json
import subprocess
import boto3
import base64
import random
import botocore
import botocore.session
import os
import aws_encryption_sdk
from aws_encryption_sdk import CommitmentPolicy
def cycle_string(key_arn, source_plaintext, botocore_session=None):
    """Encrypts and then decrypts a string under a KMS customer master key (CMK).
    :param str key_arn: Amazon Resource Name (ARN) of the KMS CMK
    :param bytes source_plaintext: Data to encrypt
    :param botocore_session: existing botocore session instance
    :type botocore_session: botocore.session.Session
    """
    # Set up an encryption client with an explicit commitment policy. Note that if you do not explicitly choose a
    # commitment policy, REQUIRE_ENCRYPT_REQUIRE_DECRYPT is used by default.
    client = aws_encryption_sdk.EncryptionSDKClient(commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT)

    # Create a KMS master key provider
    kms_kwargs = dict(key_ids=[key_arn])
    if botocore_session is not None:
        kms_kwargs["botocore_session"] = botocore_session
    master_key_provider = aws_encryption_sdk.StrictAwsKmsMasterKeyProvider(**kms_kwargs)

    # Encrypt the plaintext source data
    ciphertext, encryptor_header = client.encrypt(source=source_plaintext, key_provider=master_key_provider)

    # Decrypt the ciphertext
    cycled_plaintext, decrypted_header = client.decrypt(source=ciphertext, key_provider=master_key_provider)
    print(ciphertext.decode('utf-8', errors="ignore"),cycled_plaintext.decode('utf-8', errors="ignore"))
    return [ciphertext.decode('utf-8', errors="ignore"),cycled_plaintext.decode('utf-8', errors="ignore")]

def set_config(credential):
    os.environ["AWS_ACCESS_KEY_ID"]=credential['access_key_id']
    os.environ["AWS_SECRET_ACCESS_KEY"]=credential['secret_access_key']
    os.environ["AWS_SESSION_TOKEN"]=credential['token']
    os.environ["AWS_DEFAULT_REGION"]='ap-northeast-1'

def aws_api_call(credential, key_arn):
    """
    Make AWS API call using credential obtained from parent EC2 instance
    """
    #print(type(keyid))
    keyid=key_arn.split('/')[1]
    set_config(credential)
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
    #ciphertext = client.encrypt(Plaintext=source_plaintext, KeyId=keyid,EncryptionAlgorithm='SYMMETRIC_DEFAULT')
    get=cycle_string(key_arn=key_arn, source_plaintext=source_plaintext, botocore_session=botocore.session.Session())
    keyid=key_arn
    #cycled_plaintext = client.decrypt(CiphertextBlob=ciphertext['CiphertextBlob'], KeyId=keyid,EncryptionAlgorithm='SYMMETRIC_DEFAULT')
    #cycled_plaintext = client.decrypt(CiphertextBlob=ciphertext, KeyId=keyid,EncryptionAlgorithm='SYMMETRIC_DEFAULT')

    # print(cycled_plaintext)
    # str_cipher=base64.b64encode(ciphertext['CiphertextBlob'])
    # print(str_cipher.decode('utf-8'),type(str_cipher.decode('utf-8')))
    # Call the standalone kmstool through subprocess
    # proc = subprocess.Popen(
    #     [
    #         "/app/kmstool_enclave_cli",
    #         "--region", "ap-northeast-1",
    #         "--proxy-port", "8000",
    #         "--aws-access-key-id", "%s" % credential['access_key_id'],
    #         "--aws-secret-access-key", "%s" % credential['secret_access_key'],
    #         "--aws-session-token", "%s" % credential['token'],
    #         "--ciphertext", "%s" % str_cipher.decode('utf-8'),
    #     ],
    #     stdout=subprocess.PIPE
    # )

    # result = proc.communicate()[0]
    # print(result)
    
    # Return some data from API response
    result={
        'Plaintext':source_plaintext,
        'Ciphertext': get[0],
        'Encrypted-CLI':get[1]}
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
