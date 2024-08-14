import os
import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Specify the directory containing the encrypted images
image_folder = "path_to_your_folder"

# Load the private key
with open('private_key.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

# Load the keys dictionary from the JSON file
json_file_path = os.path.join(image_folder, 'encryption_keys.json')
with open(json_file_path, 'r') as json_file:
    keysofimage = json.load(json_file)

# Process each encrypted image in the folder
for filename in os.listdir(image_folder):
    if filename.startswith('encrypted_') and filename.endswith('.bin'):
        encrypted_image_path = os.path.join(image_folder, filename)
        original_image_name = filename[len('encrypted_'):-4]  # Extract the original image name

        # Load the encrypted image
        with open(encrypted_image_path, 'rb') as f:
            salt = f.read(16)
            iv = f.read(16)
            ciphertext = f.read()

        # Retrieve the corresponding symmetric key from the JSON file
        symmetric_key_hex = keysofimage.get(original_image_name)
        if symmetric_key_hex is None:
            print(f"No key found for {original_image_name}")
            continue

        symmetric_key = bytes.fromhex(symmetric_key_hex)

        # Decrypt the image using AES
        cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Remove padding after decryption
        padded_image_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        image_data = unpadder.update(padded_image_data) + unpadder.finalize()

        # Save the decrypted image
        decrypted_image_path = os.path.join(image_folder, f"decrypted_{original_image_name}")
        with open(decrypted_image_path, 'wb') as f:
            f.write(image_data)

        print(f"Decrypted and saved: {decrypted_image_path}")

print("Decryption complete.")