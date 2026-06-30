import os
import socket
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
from PIL import Image, ImageDraw, ImageFont

# Configuración del cliente
HOST = "127.0.0.1"  # Dirección IP del servidor
PUERTO = 12345  # Puerto al que se conecta al servidor de contenidos
PUERTO_LIC = 8000  # Puerto al que se conecta al servidor de licencias

# Función para generar claves RSA para el cliente
def generar_claves_cliente():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key

# Función para firmar un mensaje con la clave privada del cliente
def firmar_mensaje(mensaje, private_key):
    firma = private_key.sign(
        mensaje,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return firma

# Función para enviar el nombre del archivo cifrado y su firma
def enviar_nombre_y_firma(socket_licencias, encrypted_file_name, private_key, public_key):
    try:
        # Firmar el mensaje
        firma = firmar_mensaje(encrypted_file_name, private_key)
        print(f"\t Firma generada")

        # Serializar la clave pública
        public_key_serialized = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Enviar el nombre del archivo cifrado
        socket_licencias.send(encrypted_file_name)
        print("\t Nombre del archivo cifrado enviado")

        # Enviar la firma
        socket_licencias.send(firma)
        print("\t Firma enviada")

        # Enviar la clave pública del cliente
        socket_licencias.send(public_key_serialized)
        print("\t Clave pública cliente enviada")
    except Exception as e:
        print(f"\t Error al enviar nombre y firma: {e}")

def agregar_marca_agua(nombre_archivo, usuario):
    ruta_archivo = os.path.join("descargas", nombre_archivo)

    try:
        # Abrir la imagen
        with Image.open(ruta_archivo).convert("RGB") as imagen:
            # Crear un objeto de dibujo
            dibujo = ImageDraw.Draw(imagen)

            # Texto y fuente de la marca de agua
            texto = usuario
            try:
                fuente = ImageFont.truetype("arial.ttf", 36)  # Cambia el tamaño según lo necesario
            except IOError:
                fuente = ImageFont.load_default()

            # Calcular la posición para la marca de agua (esquina inferior derecha)
            x1, y1, x2, y2 = dibujo.textbbox((0, 0), texto, font=fuente)
            ancho_texto = x2 - x1
            alto_texto = y2 - y1
            posicion = (imagen.width - ancho_texto - 10, imagen.height - alto_texto - 10)

            # Aplicar la marca de agua
            dibujo.text(posicion, texto, font=fuente, fill=(255, 255, 255))  # Color blanco

            # Guardar la imagen con marca de agua
            nombre_base, extension = os.path.splitext(nombre_archivo)
            nueva_ruta = os.path.join("descargas", f"{nombre_base}{extension}")
            imagen.save(nueva_ruta)

            print(f"\t Imagen con marca de agua guardada como: {nueva_ruta}")

    except Exception as e:
        print(f"Error al agregar marca de agua: {e}")


# Función para verificar y crear la carpeta de descargas
def verificar_carpeta_descargas():
    carpeta_descargas = "descargas"
    if not os.path.exists(carpeta_descargas):
        os.makedirs(carpeta_descargas)
        print(f"\t La carpeta '{carpeta_descargas}' ha sido creada para almacenar los archivos descargados.")
    return carpeta_descargas


# Función para recibir la clave pública del servidor de licencias
def recibir_clave_publica(socket_cliente):
    public_pem = socket_cliente.recv(2048)  # Tamaño suficiente para la clave pública
    print("\t Clave pública recibida.")
    # Cargar la clave pública
    return serialization.load_pem_public_key(public_pem)


# Función para descifrar datos con AES
def descifrar_datos_aes(data, key):
    iv = data[:16]  # Extraer el IV de los primeros 16 bytes
    encrypted_data = data[16:]  # Resto son los datos cifrados
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    
    # Descifrar los datos
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    
    # Quitar padding de los datos descifrados
    unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = unpadder.update(padded_data) + unpadder.finalize()
    return decrypted_data

# Función para descifrar un archivo
def descifrar_archivo(nombre_archivo_cifrado, clave_simetrica):
    ruta_archivo_cifrado = os.path.join("descargas", nombre_archivo_cifrado)
    
    # Verificar si el archivo cifrado existe
    if not os.path.exists(ruta_archivo_cifrado):
        print(f"\t El archivo {ruta_archivo_cifrado} no existe.")
        return

    # Leer el archivo cifrado
    with open(ruta_archivo_cifrado, 'rb') as f:
        iv = f.read(16)  # Leer los primeros 16 bytes para el IV
        datos_cifrados = f.read()  # Leer el resto de los datos cifrados

    # Crear el descifrador con AES en modo CBC
    cipher = Cipher(algorithms.AES(clave_simetrica), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Descifrar los datos
    datos_descifrados_padded = decryptor.update(datos_cifrados) + decryptor.finalize()
    
    # Remover PKCS7 Padding
    unpadder = PKCS7(128).unpadder()
    datos_descifrados = unpadder.update(datos_descifrados_padded) + unpadder.finalize()

    # Eliminar el sufijo "_cifrado" del nombre del archivo
    nombre_base, extension = os.path.splitext(nombre_archivo_cifrado)
    nombre_base = nombre_base.replace("_cifrado", "")  # Eliminar "_cifrado"
    nombre_archivo_descifrado = f"{nombre_base}_descifrado{extension}"

    ruta_archivo_descifrado = os.path.join("descargas", nombre_archivo_descifrado)
    with open(ruta_archivo_descifrado, 'wb') as f:
        f.write(datos_descifrados)

    print(f"\t Archivo descifrado guardado como: {ruta_archivo_descifrado}")
    
# Función para recibir el archivo y gestionar claves
def recibir_archivo(socket_cliente, usuario):
    verificar_carpeta_descargas()

    # Recibe el nombre del archivo
    nombre_archivo = socket_cliente.recv(1024).decode()
    
    if nombre_archivo == 'Archivo no encontrado.':
        print(nombre_archivo)
        return
    print(f'\t Descargando el archivo: {nombre_archivo}')
    

    # Abrir el archivo en modo escritura binaria
    with open(os.path.join('descargas', nombre_archivo), 'wb') as file:
        while True:
            data = socket_cliente.recv(1024)
            if data.endswith(b'FINAL_ARCHIVO'):  # Verificar el fin de archivo
                file.write(data[:-len(b'FINAL_ARCHIVO')])  # Escribir solo los datos útiles
                break
            file.write(data)
    print(f'\t Archivo {nombre_archivo} descargado exitosamente.')

    # Si el archivo está cifrado, conectarse al servidor de licencias
    if "_cifrado" in nombre_archivo:
        print(f"Conexión al servidor de licencias para obtener la clave del archivo.")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_licencias:
            socket_licencias.connect((HOST, PUERTO_LIC))

            # Recibir la clave pública del servidor
            public_key = recibir_clave_publica(socket_licencias)

            # Generar clave simétrica
            symmetric_key = os.urandom(32)  # Clave AES de 256 bits
            print("\t Clave simétrica generada")

            # Cifrar la clave simétrica con la clave pública
            encrypted_symmetric_key = public_key.encrypt(
                symmetric_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            socket_licencias.send(encrypted_symmetric_key)
            print(f"\t Clave simétrica cifrada")

            # Generar claves del cliente
            client_private_key, client_public_key = generar_claves_cliente()

            # Cifrar el nombre del archivo con AES
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv))
            encryptor = cipher.encryptor()

            # Aplicar padding al nombre del archivo
            padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()
            padded_file_name = padder.update(nombre_archivo.encode()) + padder.finalize()
            encrypted_file_name = iv + encryptor.update(padded_file_name) + encryptor.finalize()

            # Enviar el nombre del archivo cifrado y su firma
            enviar_nombre_y_firma(socket_licencias, encrypted_file_name, client_private_key, client_public_key)

            # Recibir la clave del archivo cifrada
            encrypted_file_key = socket_licencias.recv(1024)
            print(f"\t Clave del archivo cifrada recibida")

            # Descifrar la clave del archivo
            file_key = descifrar_datos_aes(encrypted_file_key, symmetric_key)
            print(f"\t Clave del archivo descifrada")

            # Descifrar el archivo con la clave recibida
            descifrar_archivo(nombre_archivo, file_key)
            print(f"\t Archivo descifrado exitosamente.")


# Función principal para iniciar el cliente
def iniciar_cliente():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
        socket_cliente.connect((HOST, PUERTO))

        usuario = input("Introduzca su nombre de usuario: ")
        socket_cliente.send(usuario.encode())
        
        while True:
            comando = input("Ingrese un comando (LISTAR, DESCARGAR <archivo> o SALIR): ").strip()
            try:
                socket_cliente.send(comando.encode())

                if comando.upper() == "SALIR":
                    print("Desconectando del servidor...")
                    break

                elif comando.upper() == "LISTAR":
                    respuesta = socket_cliente.recv(1024).decode()
                    print("\t Archivos disponibles:")
                    for archivo in respuesta.splitlines():
                        print(f"\t - {archivo}")

                elif comando.upper().startswith("DESCARGAR"):
                    _, nombre_archivo = comando.split(' ', 1)
                    recibir_archivo(socket_cliente, usuario)

                else:
                    print("\t Comando no reconocido. Intente de nuevo.")
            except ConnectionAbortedError:
                print("La conexión con el servidor fue cerrada inesperadamente.")
                break

# Iniciar el cliente
iniciar_cliente()

