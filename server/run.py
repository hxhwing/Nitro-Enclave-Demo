import socket
import json
import subprocess
#import random
import os
import botocore
import boto3
import ast
import aws_encryption_sdk
from aws_encryption_sdk import CommitmentPolicy
import subprocess
import random
print('start new')

def create_cmk(desc='Customer Master Key'):
    """Create a KMS Customer Master Key
    The created CMK is a Customer-managed key stored in AWS KMS.
    :param desc: key description
    :return Tuple(KeyId, KeyArn) where:
        KeyId: AWS globally-unique string ID
        KeyArn: Amazon Resource Name of the CMK
    :return Tuple(None, None) if error
    """

    # Create CMK
    
    region_name = "us-east-1"
    session = botocore.session.get_session()
    kms_client = session.client('kms')
    # try:
    source_plaintext=random.randint(000000,999999)
    source_plaintext=str(source_plaintext)
    source_plaintext=str.encode(source_plaintext)
    #response = kms_client.create_key(Description=desc)
    #print(response)
    #response['KeyMetadata']['KeyId']
    ciphertext = kms_client.encrypt(Plaintext=source_plaintext, KeyId='',EncryptionAlgorithm='SYMMETRIC_DEFAULT')
    print((ciphertext['CiphertextBlob']))
    cycled_plaintext = kms_client.decrypt(CiphertextBlob=ciphertext['CiphertextBlob'], KeyId='',EncryptionAlgorithm='SYMMETRIC_DEFAULT')
    print(cycled_plaintext['Plaintext'].decode())
    # except:
    #     print("down")
    #     return None, None

    # Return the key ID and ARN
    #return response['KeyMetadata']['KeyId'], response['KeyMetadata']['Arn']
    return {
        'Plaintext':source_plaintext,
        'Ciphertext': ciphertext['CiphertextBlob'],
        'Decrypted text': cycled_plaintext['Plaintext'].decode()
    }

def cycle_string(key_arn, source_plaintext, botocore_session=None):
    

    # Set up an encryption client with an explicit commitment policy. If you do not explicitly choose a
    # commitment policy, REQUIRE_ENCRYPT_REQUIRE_DECRYPT is used by default.
    client = aws_encryption_sdk.EncryptionSDKClient(commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT)

    # Create an AWS KMS master key provider
    kms_kwargs = dict(key_ids=[key_arn])
    if botocore_session is not None:
        kms_kwargs["botocore_session"] = botocore_session
    master_key_provider = aws_encryption_sdk.StrictAwsKmsMasterKeyProvider(**kms_kwargs)

    # Encrypt the plaintext source data
    ciphertext, encryptor_header = client.encrypt(source=source_plaintext, key_provider=master_key_provider)

    # Decrypt the ciphertext
    cycled_plaintext, decrypted_header = client.decrypt(source=ciphertext, key_provider=master_key_provider)
    return ciphertext.decode('utf-8', errors="ignore"),cycled_plaintext.decode('utf-8', errors="ignore")



def main():
    while True:
        print("Starting server...")
        os.environ["AWS_ACCESS_KEY_ID"]=""
        os.environ["AWS_SECRET_ACCESS_KEY"]=""
        #os.environ["AWS_SESSION_TOKEN"]=
        os.environ["AWS_DEFAULT_REGION"]='ap-northeast-1'
        botocore_session=botocore.session.get_session()
        key_arn=""
        source_plaintext=b'12345'
        # Create a vsock socket object
        out=cycle_string(key_arn, source_plaintext, botocore_session)
        print(out)
       

if __name__ == '__main__':
    main()