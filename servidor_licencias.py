import os
import socket
import select
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import utils

HOST = "127.0.0.1"
PUERTO_LIC = 8000

# Crear socket y configurarlo
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PUERTO_LIC))
s.listen()

# Lista para almacenar los sockets de clientes
s_list = [s]

# Función para leer la clave del archivo
def leer_clave_para_archivo(nombre_archivo):
    archivo_claves = "claves.txt"
    nombre_archivo = nombre_archivo.replace("_cifrado", "")
    if not os.path.exists(archivo_claves):
        print("El archivo de claves no existe.")
        return None

    with open(archivo_claves, 'r') as f:
        for linea in f:
            if ':' in linea:
                archivo, clave = linea.strip().split(':')
                if archivo == os.path.basename(nombre_archivo):
                    return bytes.fromhex(clave)
    return None

# Verificar la firma del mensaje
def verificar_firma(mensaje, firma, public_key_pem):
    try:
        public_key = serialization.load_pem_public_key(public_key_pem)
        public_key.verify(
            firma,
            mensaje,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Firma verificada correctamente.")
        return True
    except Exception as e:
        print(f"Error al verificar la firma: {e}")
        return False

# Cifrar datos con AES
def cifrar_datos_aes(data, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data

# Generar claves RSA
def generar_claves():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_key, public_pem

# Descifrar clave simétrica
def descifrar_clave_simetrica(encrypted_symmetric_key, private_key):
    try:
        symmetric_key = private_key.decrypt(
            encrypted_symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print("Clave simétrica descifrada con éxito.")
        return symmetric_key
    except Exception as e:
        print(f"Error al descifrar la clave simétrica: {e}")
        return None

# Servidor principal
private_key, public_pem = generar_claves()
print(f"Servidor escuchando en {HOST}:{PUERTO_LIC}...")

while True:
    read_sockets, _, exception_sockets = select.select(s_list, [], [], 2)

    for notified_socket in read_sockets:
        if notified_socket == s:
            client_socket, client_address = s.accept()
            s_list.append(client_socket)
            print(f"Nueva conexión desde {client_address[0]}:{client_address[1]}")

            client_socket.send(public_pem)
            print(f"Clave pública enviada al cliente {client_address[0]}:{client_address[1]}")
        else:
            try:
                encrypted_symmetric_key = notified_socket.recv(256)
                print(f"Clave simétrica cifrada recibida: {encrypted_symmetric_key}")
                if encrypted_symmetric_key:
                    symmetric_key = descifrar_clave_simetrica(encrypted_symmetric_key, private_key)
                    if symmetric_key:
                        print(f"Clave simétrica descifrada: {symmetric_key.hex()}")
                        encrypted_file_name = notified_socket.recv(1024)
                        print(f"Nombre del archivo cifrado recibido: {encrypted_file_name}")
                        firma = notified_socket.recv(256)
                        client_public_key_pem = notified_socket.recv(1024)
                        print("Firma:",firma)

                        if not client_public_key_pem:
                            print("Clave pública del cliente no recibida.")
                            continue

                        if verificar_firma(encrypted_file_name, firma, client_public_key_pem):
                            iv, encrypted_name = encrypted_file_name[:16], encrypted_file_name[16:]
                            cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv))
                            decryptor = cipher.decryptor()

                            padded_file_name = decryptor.update(encrypted_name) + decryptor.finalize()
                            unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
                            file_name = unpadder.update(padded_file_name) + unpadder.finalize()
                            file_name = file_name.decode('utf-8')
                            print(f"Nombre del archivo descifrado: {file_name}")
                            
                            file_key = leer_clave_para_archivo(file_name)
                            
                            if file_key:
                                print(f"Clave encontrada para el archivo: {file_key.hex()}")                                
                                encrypted_file_key = cifrar_datos_aes(file_key, symmetric_key)
                                print(f"Clave del archivo cifrada: {encrypted_file_key}") 
                                notified_socket.send(encrypted_file_key)
                                print("Clave del archivo enviada.")
                                break
                            else:
                                print("Clave para el archivo no encontrada.")
                                break
                        else:
                            print("Firma no válida.")
                            break
                else:
                    s_list.remove(notified_socket)
            except Exception as e:
                print(f"Error: {e}")
                s_list.remove(notified_socket)

    for notified_socket in exception_sockets:
        s_list.remove(notified_socket)
