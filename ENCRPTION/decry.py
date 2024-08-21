import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Load the private key for decryption
private_key_path = 'C:/Users/jsjji/OneDrive/Desktop/git/MCA-MINI PROJECT/THE-SECURED-PHOTO-VAULT/ENCRPTION/private_key.pem'
with open(private_key_path, 'rb') as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )

# Load the public key for decryption
public_key_path = 'C:/Users/jsjji/OneDrive/Desktop/git/MCA-MINI PROJECT/THE-SECURED-PHOTO-VAULT/ENCRPTION/public_key.pem'
with open(public_key_path, 'rb') as f:
    public_key = serialization.load_pem_public_key(
        f.read(),
        backend=default_backend()
    )

# Load the encrypted image
encrypted_image_path = 'C:/Users/jsjji/OneDrive/Desktop/git/MCA-MINI PROJECT/THE-SECURED-PHOTO-VAULT/ENCRPTION/EIMAGES/encrypted_image.bin'
with open(encrypted_image_path, 'rb') as f:
    salt = f.read(16)
    iv = f.read(16)
    ciphertext = f.read()

# Derive the symmetric key from the shared key
shared_key = private_key.exchange(ec.ECDH(), public_key)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=default_backend()
)
symmetric_key = kdf.derive(shared_key)

# Decrypt the image using AES
cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())
decryptor = cipher.decryptor()

# Remove padding after decryption
padded_image_data = decryptor.update(ciphertext) + decryptor.finalize()
unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
image_data = unpadder.update(padded_image_data) + unpadder.finalize()

# Save the decrypted image
decrypted_image_path = 'C:/Users/jsjji/OneDrive/Desktop/git/MCA-MINI PROJECT/THE-SECURED-PHOTO-VAULT/ENCRPTION/DIMAGES/decrypted_image.png'
with open(decrypted_image_path, 'wb') as f:
    f.write(image_data)
