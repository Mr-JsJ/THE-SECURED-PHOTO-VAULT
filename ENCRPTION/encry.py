import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Generate ECC key pair
private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
public_key = private_key.public_key()

# Serialize the public key to share with the sender
public_key_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Load the image to encrypt
image_path = 'C:/Users/jsjji/OneDrive/Desktop/git/MCA-MINI PROJECT/THE-SECURED-PHOTO-VAULT/ENCRPTION/ball.jpg'
with open(image_path, 'rb') as f:
    image_data = f.read()

# Generate a shared key using ECC
shared_key = private_key.exchange(ec.ECDH(), public_key)
print(shared_key)
# Derive a symmetric key from the shared key
salt = os.urandom(16)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=default_backend()
)
symmetric_key = kdf.derive(shared_key)

# Encrypt the image using AES
iv = os.urandom(16)
cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())
encryptor = cipher.encryptor()

# Padding the image data to be a multiple of the block size
padder = padding.PKCS7(algorithms.AES.block_size).padder()
padded_image_data = padder.update(image_data) + padder.finalize()

ciphertext = encryptor.update(padded_image_data) + encryptor.finalize()

# Save the encrypted image
encrypted_image_path = 'C:/Users/jsjji/OneDrive/Desktop/git/MCA-MINI PROJECT/THE-SECURED-PHOTO-VAULT/ENCRPTION/EIMAGES/encrypted_image.bin'
with open(encrypted_image_path, 'wb') as f:
    f.write(salt + iv + ciphertext)

# Save the private key and public key
private_key_path = 'C:/Users/jsjji/OneDrive/Desktop/git/MCA-MINI PROJECT/THE-SECURED-PHOTO-VAULT/ENCRPTION/private_key.pem'
public_key_path = 'C:/Users/jsjji/OneDrive/Desktop/git/MCA-MINI PROJECT/THE-SECURED-PHOTO-VAULT/ENCRPTION/public_key.pem'

with open(private_key_path, 'wb') as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

with open(public_key_path, 'wb') as f:
    f.write(public_key_bytes)
