import os
import csv
from datetime import datetime
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseBadRequest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from .csvfile import csv_access
from .tag import get_image_tag 

def upload(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return HttpResponseBadRequest("User not authenticated")

    if request.method == 'POST':
        images = request.FILES.getlist('images')
        if not images:
            messages.error(request, 'No images were uploaded.')
            return render(request, 'upload.html')

        # Directory where user's images will be stored
        user_images_dir = os.path.join(settings.IMAGES_VAULT, f'{user_id}SVPimages')
        os.makedirs(user_images_dir, exist_ok=True)

        # Path to the user's CSV file for metadata storage
        csv_file_path = os.path.join(settings.META_DATA, f'SPV{user_id}.csv')

        try:
            with open(csv_file_path, mode='a', newline='') as csvfile:
                fieldnames = ['image_name', 'public_key', 'private_key', 'tags', 'date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                for image in images:
                    # Ensure file name is safe
                    image_name = os.path.basename(image.name)
                    

                    # Load the image to encrypt
                    image_data = image.read()

                    # Generate ECC key pair
                    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
                    public_key = private_key.public_key()

                    # Serialize the public key to store in the CSV
                    public_key_bytes = public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )

                    # Generate a shared key using ECC
                    shared_key = private_key.exchange(ec.ECDH(), public_key)

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
                    encrypted_image_path = os.path.join(user_images_dir, f'{image_name}.bin')
                    with open(encrypted_image_path, 'wb') as f:
                        f.write(salt + iv + ciphertext)

                    # Save the private key
                    private_key_bytes = private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )

                    auto_tag = get_image_tag(image)#auto tad module

                    # Collect image metadata
                    image_metadata = {
                        'image_name': f'{image_name}.bin',
                        'public_key': public_key_bytes.decode('utf-8'),
                        'private_key': private_key_bytes.decode('utf-8'),
                        'tags': auto_tag,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    # Write metadata to the CSV file
                    writer.writerow(image_metadata)

            # Optionally, add a success message
            messages.success(request, 'Images uploaded and encrypted successfully!')

        except IOError as e:
            messages.error(request, f"An error occurred while processing the upload: {str(e)}")
            return render(request, 'upload.html')

    return render(request, 'upload.html')




def decrypt_image(user_id, image_name, private_key_pem, public_key_pem):
    encrypted_image_path = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages', image_name)
    
    # Remove the '.bin' extension for the decrypted file
    decrypted_image_name = os.path.splitext(image_name)[0]  # Remove file extension
    decrypted_image_path = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages', 'decrypted', decrypted_image_name)
    
    print(user_id, image_name, private_key_pem, public_key_pem)

    # Load the private key from the PEM string
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
        backend=default_backend()
    )

    # Load the public key from the PEM string
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode('utf-8'),
        backend=default_backend()
    )

    # Load the encrypted image
    with open(encrypted_image_path, 'rb') as f:
        salt = f.read(16)
        iv = f.read(16)
        ciphertext = f.read()

    # Generate the shared key using ECC
    shared_key = private_key.exchange(ec.ECDH(), public_key)

    # Derive the symmetric key from the shared key using PBKDF2
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

    try:
        # Decrypt the data and remove padding
        padded_image_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        image_data = unpadder.update(padded_image_data) + unpadder.finalize()
    except ValueError as e:
        print("Decryption failed: Invalid padding or corrupted ciphertext.")
        print(f"Error details: {e}")
        return

    # Ensure the decrypted directory exists
    os.makedirs(os.path.dirname(decrypted_image_path), exist_ok=True)
    
    # Save the decrypted image
    with open(decrypted_image_path, 'wb') as f:
        f.write(image_data)

    print(f"Decrypted image saved to: {decrypted_image_path}")



