import os
import json
import base64
import shared_objects
# from Crypto.PublicKey import RSA
# from Crypto import Random
# from Crypto.Cipher import PKCS1_OAEP
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def generate_keys():
    # Create private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    # Create public key
    public_key = private_key.public_key()

    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ), public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def encrypt_message(a_message , publickey):
   pass


def decrypt_message(encoded_encrypted_msg, pr_key_pem):
    rsa_private_key = PKCS1_OAEP.new(RSA.importKey(pr_key_pem))
    decrypted = rsa_private_key.decrypt(base64.b64decode(encoded_encrypted_msg))
    return decrypted


def verify_password(pr_key_pem, username, encrypted_password):
    r = {"status": 0, "message": "", "valid": False, "profile": {}}
    stored_password = decrypt_message(encrypted_password, pr_key_pem).decode('utf-8')
    # load user profile which contains the password
    user_profile_directory = os.path.join(
        shared_objects.root, shared_objects.config["users"]["path"], username.lower())
    if os.path.exists(user_profile_directory) and os.path.isdir(user_profile_directory):
        password_file_path = os.path.join(user_profile_directory, "password")
        if os.path.exists(password_file_path):
            password_file = open(password_file_path, "r")
            password = password_file.read()
            password_file.close()
            if password == stored_password:
                r["valid"] = True
                # load user profile
                r["profile"]["username"] = username
                profile_info_path = os.path.join(user_profile_directory, "profile")
                if os.path.exists(profile_info_path):
                    profile_info_file = open(profile_info_path, "r")
                    r["profile"]["info"] = json.load(profile_info_file)
                    profile_info_file.close()
                else:
                    r["profile"]["info"] = {}
            else:
                r["message"] = "Password is incorrect!"
        else:
            shared_objects.log.warning("user password file not found: {}".format(password_file_path))
    else:
        shared_objects.log.warning("user profile path not found: {}".format(user_profile_directory))

    return r

