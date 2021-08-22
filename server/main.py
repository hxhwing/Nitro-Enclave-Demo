"""Enclave NitroPepper application."""

import base64
import json
import socket
import bcrypt

from bcrypt import _bcrypt
from kms import NitroKms

ENCLAVE_PORT = 5000

def main():
    """Run the nitro enclave application."""
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
            # parent_app_data = json.loads(payload.decode())
            # kms_credentials = parent_app_data['kms_credentials']
            # kms_region = parent_app_data['kms_region']
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
        kms_credentials = client_request['credential']
        key_id = client_request['keyid']
        nitro_kms.set_region('ap-northeast-1')
        nitro_kms.set_credentials(kms_credentials)

        plaintext = nitro_kms.kms_generate_random(16)
        datakey = nitro_kms.kms_generate_data_key(16, key_id)

        plaintext_for_recipient_b64 = plaintext['CiphertextForRecipient']
        TobeEncrypted = base64.b64decode(plaintext_for_recipient_b64)

        ciphertext = nitro_kms.kms_encrypt(TobeEncrypted, key_id)
        decrypt = nitro_kms.kms_decrypt(ciphertext['CiphertextBlob'])

        content = {
            'Plaintext': base64.b64encode(TobeEncrypted).decode('utf-8'),
            'Ciphertext': ciphertext['CiphertextBlob'],
            'Decrypted': base64.b64encode(decrypt).decode('utf-8')
        }
        print(content)

        # if 'action' in parent_app_data:
        #     if parent_app_data['action'] == 'generate_hash_and_pepper':
        #         content = process_generate_hash_and_pepper(nitro_kms, parent_app_data)
        #     elif parent_app_data['action'] == 'validate_credentials':
        #         content = process_validate_credentials(nitro_kms, parent_app_data)
        #     else:
        #         content = {
        #             'success': False,
        #             'error': f"Unknown action: {parent_app_data['action']}"
        #         }

        # else:
        #     content = {
        #         'success': False,
        #         'error': 'No action provided'
        #     }

        conn.send(str.encode(json.dumps(content)))
        conn.close()
        print('Closed connection')



if __name__ == '__main__':
    main()
