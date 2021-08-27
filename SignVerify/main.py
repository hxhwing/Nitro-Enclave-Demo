""" Nitro Enclave and Attestation integration with KMS Sample """

import base64
import json
import socket
import ecdsa
import hashlib
import binascii
from Crypto.Cipher import AES
from kms import NitroKms

ENCLAVE_PORT = 5000

"""Client-side AES encryption"""

def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)  # return bytes

# Use client-side AES to encrypt plain text
def encrypt(key, text):
    aes = AES.new(add_to_16(key), AES.MODE_ECB)  # Initialize encryption method
    encrypt_aes = aes.encrypt(add_to_16(text))  # Execute Encryption, return bytes
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # return base64 encoded string
    return encrypted_text

# Use client-side AES to decrypt encrypted text
def decrypt(key, text):
    aes = AES.new(add_to_16(key), AES.MODE_ECB)  # Initialize decryption method
    base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))  # Execute Decryption, return bytes
    decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')  # return base64 encoded string
    return decrypted_text


"""Run the nitro enclave application."""

def main():
    # Bind and listen on vsock.
    vsock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM) # pylint:disable=no-member
    vsock.bind((socket.VMADDR_CID_ANY, ENCLAVE_PORT)) # pylint:disable=no-member
    vsock.listen()

    # Initialize a KMS class
    nitro_kms = NitroKms()
    print('Listening...')

    while True:
        conn, _addr = vsock.accept()
        print('Received new connection')
        payload = conn.recv(4096)

        # Load the JSON data provided over vsock
        try:
            client_request = json.loads(payload.decode())
        except Exception as exc: # pylint:disable=broad-except
            msg = f'Exception ({type(exc)}) while loading JSON data: {str(exc)}'
            content = {
                'success': False,
                'error': msg
            }
            conn.send(str.encode(json.dumps(content)))
            conn.close()
            continue
        # Get AWS Credential from Socket
        kms_credentials = client_request['credential']
        # Get AWS KMS Key ID from Socket
        # key_id = client_request['keyid']
        # Get User ID from Socket
        # user_id = client_request['userid']

        # Get data stored in DynamoDB from Socket
        data = client_request['data']
        
        # Get encrypted datakey from Socket
        encrypted_datakey = data['encrypted_datakey']

        # Get encrypted privatekey from Socket
        encrypted_privatekey = data['encrypted_privatekey']

        # Get message to be signed from Socket
        message = client_request['message']

        # Set environment variables
        nitro_kms.set_region('ap-northeast-1')
        nitro_kms.set_credentials(kms_credentials)
        
        # Decrypt encrypted data_key by KMS Decrypt API with attestation
        datakey = nitro_kms.kms_decrypt(encrypted_datakey)  # Key metadata included in Ciphertextblob, return bytes
        plain_datakey = base64.b64encode(datakey).decode('utf-8') # bytes to string

        # Decrypt private_key with plain data key
        private_key = decrypt(plain_datakey, encrypted_privatekey) # Input datakey string and encrypted string

        # Convert private key to ECDSA signing key
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1, hashfunc = hashlib.sha256)

        # Sign message using private_key
        bmessage = bytes(message, 'utf-8') 
        content = sk.sign(bmessage)  #Signature in bytes

        # Return Signed message
        print('Signed Message: ' + binascii.hexlify(content).decode('utf-8'))
        
        # Send out returned data to Socket
        # conn.send(str.encode(json.dumps(content)))
        conn.send(content) # Bytes
        conn.close()
        print('Closed connection')

if __name__ == '__main__':
    main()
