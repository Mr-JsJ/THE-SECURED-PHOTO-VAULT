from .csvfile import csv_access
import os
import csv
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.contrib import messages
from .face_detection import detect_and_crop_faces 
from .tag import get_image_tag
from io import BytesIO

#UPLOAD OF IMAGES#

def upload(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return HttpResponseBadRequest("User not authenticated")

    if request.method == 'POST':
        images = request.FILES.getlist('images')
        if not images:
            messages.error(request, 'No images were uploaded.')
            return render(request, 'upload.html')

        user_images_dir = os.path.join(settings.IMAGES_VAULT, f'{user_id}SVPimages')
        os.makedirs(user_images_dir, exist_ok=True)
        
        face_images_dir = os.path.join(user_images_dir, 'faces')
        os.makedirs(face_images_dir, exist_ok=True)

        csv_file_path = os.path.join(settings.META_DATA, f'SPV{user_id}.csv')

        try:
            with open(csv_file_path, mode='a', newline='') as csvfile:
                fieldnames = ['image_name', 'public_key', 'private_key', 'tags', 'date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                for image in images:
                    image_name = os.path.basename(image.name)
                    image_data = image.read()

                    # Generate ECC key pair
                    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
                    public_key = private_key.public_key()

                    public_key_bytes = public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )

                    shared_key = private_key.exchange(ec.ECDH(), public_key)

                    salt = os.urandom(16)
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=salt,
                        iterations=100000,
                        backend=default_backend()
                    )
                    symmetric_key = kdf.derive(shared_key)

                    iv = os.urandom(16)
                    cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())

                    # Encrypt main image
                    main_padder = padding.PKCS7(algorithms.AES.block_size).padder()
                    padded_image_data = main_padder.update(image_data) + main_padder.finalize()

                    main_encryptor = cipher.encryptor()
                    ciphertext = main_encryptor.update(padded_image_data) + main_encryptor.finalize()

                    encrypted_image_path = os.path.join(user_images_dir, f'{image_name}.bin')
                    with open(encrypted_image_path, 'wb') as f:
                        f.write(salt + iv + ciphertext)

                    private_key_bytes = private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )

                    auto_tag = get_image_tag(image)

                    image_metadata = {
                        'image_name': f'{image_name}.bin',
                        'public_key': public_key_bytes.decode('utf-8'),
                        'private_key': private_key_bytes.decode('utf-8'),
                        'tags': auto_tag,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    writer.writerow(image_metadata)

                    # Detect faces and crop face_detection.py
                    face_images = detect_and_crop_faces(image_data)
                    for i, face_image in enumerate(face_images):
                        face_image_name = f"{image_name}_face_{i}.bin"
                        face_encrypted_image_path = os.path.join(face_images_dir, face_image_name)

                        # Encrypt each cropped face image separately
                        face_padder = padding.PKCS7(algorithms.AES.block_size).padder()
                        face_padded_data = face_padder.update(face_image) + face_padder.finalize()

                        face_encryptor = cipher.encryptor()
                        face_ciphertext = face_encryptor.update(face_padded_data) + face_encryptor.finalize()

                        with open(face_encrypted_image_path, 'wb') as f:
                            f.write(salt + iv + face_ciphertext)

                        face_metadata = {
                            'image_name': face_image_name,
                            'public_key': public_key_bytes.decode('utf-8'),
                            'private_key': private_key_bytes.decode('utf-8'),
                            'tags': 'face',
                            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        writer.writerow(face_metadata)

            messages.success(request, 'Images uploaded and encrypted successfully with face images extracted!')

        except IOError as e:
            messages.error(request, f"An error occurred while processing the upload: {str(e)}")
            return render(request, 'upload.html')

    return render(request, 'upload.html')


#DECRPTION OF ENCRYPTED IMAGES#

from PIL import Image
import io

def decrypt_image(user_id, image_name, private_key_pem, public_key_pem):
    encrypted_image_path = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages', image_name)
    
    # Remove the '.bin' extension for the decrypted file
    decrypted_image_name = os.path.splitext(image_name)[0]  # Remove file extension
    decrypted_image_path = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages', 'decrypted', decrypted_image_name)
    decrypted_face_path = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages', 'decrypted', 'faces')

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
    os.makedirs(decrypted_face_path, exist_ok=True)  # Ensure the face directory exists
    
    # Save the decrypted main image
    with open(decrypted_image_path, 'wb') as f:
        f.write(image_data)

    print(f"Decrypted image saved to: {decrypted_image_path}")

    # Decrypt corresponding face images
    face_images_dir = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages', 'faces')
    face_images = [f for f in os.listdir(face_images_dir) if f.startswith(decrypted_image_name)]

    for i, face_image in enumerate(face_images):
        encrypted_face_path = os.path.join(face_images_dir, face_image)
        decrypted_face_image_path = os.path.join(decrypted_face_path, f"{decrypted_image_name}_face_{i}.png")  # Change the extension to your desired format

        with open(encrypted_face_path, 'rb') as f:
            salt = f.read(16)
            iv = f.read(16)
            ciphertext = f.read()

        cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        try:
            padded_face_data = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            face_data = unpadder.update(padded_face_data) + unpadder.finalize()

            # Use PIL to save the face image in a specific format
            image = Image.open(io.BytesIO(face_data))
            image.save(decrypted_face_image_path, format='PNG')  # Save as PNG or specify any other format

            print(f"Decrypted face image saved to: {decrypted_face_image_path}")

        except ValueError as e:
            print(f"Decryption of face {face_image} failed: {e}")
