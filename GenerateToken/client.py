import sys
import socket
import requests
import json
import base64
import subprocess
import boto3

"""
How to use this?
python3 client.py <KMS Key-id> <UserID>
e.g.:
python3 client.py alias/encalve u001
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
    # cid = int(sys.argv[1])

    # Get KMS KeyID 
    keyid = sys.argv[1]

    # Get UserID 
    userid = sys.argv[2]

    # The port should match the server running in enclave
    port = 5000

    # Connect to the server
    s.connect((cid, port))

    # Send AWS credential and KMS KeyID to the server running in enclave
    s.send(str.encode(json.dumps({
        'credential': credential,
        'keyid': keyid,
        'userid': userid
    })))

    # receive data from the server
    response = s.recv(65536).decode()

    #plaintext = base64.b64decode(response['Plaintext']).decode()
    print(response)

    # Write to DynamoDB
    ddb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    table = ddb.Table('UserToken')
    try:
        table.put_item(Item=json.loads(response))
        print('Write User Token to DynamoDB Successfully')
    except Exception as error:
        print(error)

    # close the connection
    s.close()

if __name__ == '__main__':
    main()