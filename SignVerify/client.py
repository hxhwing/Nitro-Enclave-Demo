import binascii
import sys
import socket
import requests
import json
import base64
import subprocess
import boto3
import ecdsa
import hashlib

"""
How to use this?
python3 client.py <enclave-id> <userid> <'Message to be signed'>
e.g.:
python3 client.py 15 u005 'Message to be signed'
"""

def get_aws_session_token():
    """
    Get the AWS credential from EC2 instance metadata
    """
    r = requests.get("http://169.254.169.254/latest/meta-data/iam/security-credentials/")
    instance_profile_name = r.text

    r = requests.get("http://169.254.169.254/latest/meta-data/iam/security-credentials/%s" % instance_profile_name)
    response = r.json()

    credential = {
        'aws_access_key_id' : response['AccessKeyId'],
        'aws_secret_access_key' : response['SecretAccessKey'],
        'aws_session_token' : response['Token']
    }

    return credential

def main():
    # Get EC2 instance metedata
    credential = get_aws_session_token()

    # Create a vsock socket object
    s = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)

    # Get CID from command line parameter
    cid = int(sys.argv[1])

    # # Get KMS KeyID 
    # keyid = sys.argv[2]

    # Get UserID 
    userid = sys.argv[2]

    # Get message to be signed 
    message = sys.argv[3]

    # The port should match the server running in enclave
    port = 5000

    # Get item from DynamoDB
    ddb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    table = ddb.Table('UserToken')
    try:
        Item = table.get_item(Key={'userid': userid})
    except Exception as error:
        print('Item not found from DynamoDB')

    # Get public_key from DynamoDB
    public_key = Item['Item']['publickey']
    # Generate Verifying key from existing Public Key(string)
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256) # the default is sha1

    # Connect to the server
    s.connect((cid, port))

    # Send AWS credential and KMS KeyID to the server running in enclave
    s.send(str.encode(json.dumps({
        'credential': credential,
        'userid': userid,
        'data': Item['Item'],
        'message': message
    })))

    # receive data from the server (byte)
    response = s.recv(65536)

    #plaintext = base64.b64decode(response['Plaintext']).decode()
    print('Signed Message: ' + binascii.hexlify(response).decode('utf-8'))
    
    # Get signed message from Enclave, and verify the signing with Verifying key(public_key)
    bmessage = bytes(message, 'utf-8') 
    if vk.verify(response, bmessage): # True
        print('Signed message verified by public key: True')
    else:
        print('Signed message verified by public key: False')

    # close the connection
    s.close()

if __name__ == '__main__':
    main()