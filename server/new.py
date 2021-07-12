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
session = botocore.session.get_session()
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
    region_name = "ap-northeast-1"
    session1 = boto3.session.Session(aws_access_key_id='',aws_secret_access_key='',region_name=region_name)

    kms_client = session1.client('kms')
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
    """Encrypts and then decrypts a string under an AWS KMS customer master key (CMK).
    :param str key_arn: Amazon Resource Name (ARN) of the AWS KMS CMK
    :param bytes source_plaintext: Data to encrypt
    :param botocore_session: existing botocore session instance
    :type botocore_session: botocore.session.Session
    """
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
    print("Starting server...")
    
    # Create a vsock socket object
    out=create_cmk()
    print(str.encode(str(out)),type(str.encode(str(out))))
    
    # while True:
        
        
    #     keyid = "arn:aws:kms:ap-northeast-1:196375779214:key/2e6e1837-23af-4ddb-b588-c4beacdf5468"
    #     print(keyid)
        
    #     try:
            
    #         source_plaintext=b'123456'
    #         ciphertext,plaintext=cycle_string(keyid, source_plaintext,session)
    #         #print(ciphertext,plaintext)
          

    #     except:
    #         print("down")
    #     # Close the connection
    #     break
       

if __name__ == '__main__':
    main()
