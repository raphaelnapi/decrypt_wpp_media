import base64
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='decrypt_media',
        description='Decrypt WhatsApp media files (.enc) using the media key.',
        usage='%(prog)s [input_file] [file_type] [media_key] [output_file]'
    )

    parser.add_argument(
        'input_file',
        help='Encrypted media file (.enc)'
    )

    parser.add_argument(
        'media_type',
        choices=['image', 'video', 'audio', 'document'],
        help='Type of media'
    )

    parser.add_argument(
        'media_key',
        help='Media key in hexadecimal string format'
    )

    parser.add_argument(
        'output_file',
        help='Output file name for decrypted media'
    )

    args = parser.parse_args()

    return args

def derive_media_keys(media_key_hexstr: str, media_type: str):
    infos = {
        'image': b'WhatsApp Image Keys',
        'video': b'WhatsApp Video Keys',
        'audio': b'WhatsApp Audio Keys',
        'document': b'WhatsApp Document Keys',
    }

    if media_type not in infos:
        raise ValueError('media_type deve ser: image, video, audio ou document')

    media_key = bytes.fromhex(media_key_hexstr)

    if len(media_key) != 32:
        raise ValueError(f'media_key deve ter 32 bytes, veio com {len(media_key)}')

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=112,
        salt=b'\x00' * 32,
        info=infos[media_type],
    )

    expanded = hkdf.derive(media_key)

    iv = expanded[0:16]
    cipher_key = expanded[16:48]
    mac_key = expanded[48:80]
    ref_key = expanded[80:112]

    return iv, cipher_key, mac_key, ref_key

def main():
    try:
        print(':: DECRYPT WHATSAPP MEDIA')
        print()

        args = parse_arguments()

        input_file = args.input_file
        media_type = args.media_type
        media_key = args.media_key
        output_file = args.output_file

        print('Input:', input_file)
        print('Type:', media_type)
        print('Key:', media_key)
        print('Output:', output_file)
        print()

        #deriva media_key
        iv, cipher_key, mac_key, ref_key = derive_media_keys(media_key, media_type)
        print('IV:', iv.hex())
        print('cipherKey:', cipher_key.hex())
        print('macKey:', mac_key.hex())

        with open(input_file, 'rb') as arq:
            enc_file_bytes = arq.read()

        ct = enc_file_bytes[:-10] #remove MAC

        cipher = Cipher(algorithm=algorithms.AES256(cipher_key), mode=modes.CBC(iv))
        decryptor = cipher.decryptor()

        pt_padded = decryptor.update(ct) + decryptor.finalize()

        #remove padding
        unpadder = PKCS7(128).unpadder()
        pt = unpadder.update(pt_padded) + unpadder.finalize()

        with open(output_file, 'wb') as output_file:
            output_file.write(pt)

        print()
        print('Decryption successful.')
    except Exception as e:
        print('Error: ', e)

if __name__ == '__main__':
    main()