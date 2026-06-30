import socket
import os
from PIL import Image, ImageDraw, ImageFont
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend

# Configuración del servidor
HOST = '127.0.0.1'  # Dirección IP del servidor
PORT = 12345  # Puerto en el que escuchará el servidor

# Función para verificar y crear la carpeta de archivos
def verificar_carpeta_archivos():
    # Nombre de la carpeta donde estarán los archivos
    carpeta_archivos = "archivos"
    
    # Si no existe la carpeta, crearla y mostrar un mensaje
    if not os.path.exists(carpeta_archivos):
        os.makedirs(carpeta_archivos)
        print(f"La carpeta '{carpeta_archivos}' ha sido creada.")
        print("Por favor, coloque archivos en la carpeta antes de iniciar el servidor.")
        return False
    else:
        archivos = os.listdir(carpeta_archivos)
        if not archivos:
            print(f"La carpeta '{carpeta_archivos}' está vacía. Por favor, coloque archivos en ella.")
            return False
        return True

# Función para enviar la lista de archivos disponibles
def listar_archivos(conexion):
    carpeta_descargas = "archivos"
    archivos = os.listdir(carpeta_descargas)
    archivos_disponibles = '\n'.join(archivos)  # Crear una lista separada por saltos de línea
    conexion.send(archivos_disponibles.encode())  # Enviar la lista de archivos


# def agregar_marca_agua(nombre_archivo, usuario):
#     # Verificar si el archivo es una foto
#     if nombre_archivo.lower().endswith((".jpeg", ".jpg", ".png")):
#         print ("Vamos a añadir la marca de agua")
#         ruta_archivo = os.path.join("archivos", nombre_archivo)
#         print ("Ruta archivo", ruta_archivo)
#         
#         # Si el archivo contiene '_cifrado', descifrarlo antes de proceder
#         if "_cifrado" in nombre_archivo:
#             print ("Tenemos que descifrar el archivo")
#             clave_simetrica = leer_clave_para_archivo(ruta_archivo)
#             print ("Clave simétrica", clave_simetrica)
# 
#             if clave_simetrica:
#                 nombre_base, extension = os.path.splitext(nombre_archivo)
#                 ruta_archivo_descifrado = nombre_base.replace("_cifrado", "") + extension
#                 ruta_descifrado = os.path.join("archivos", ruta_archivo_descifrado)
#                 descifrar_archivo(nombre_archivo, clave_simetrica)
#                 ruta_archivo = ruta_descifrado
#                 print ("Ruta archivo", ruta_archivo)
# 
#         try:
#             # Verifica que la imagen se pueda abrir antes de agregar la marca de agua
#             with Image.open(ruta_archivo) as img:
#                 img.verify()  # Esto lanzará una excepción si la imagen está corrupta
# 
#             # Abrir la imagen nuevamente para modificarla
#             with Image.open(ruta_archivo).convert("RGB") as imagen:
#                 # Crear un objeto de dibujo
#                 dibujo = ImageDraw.Draw(imagen)
# 
#                 # Texto y fuente de la marca de agua
#                 texto = usuario
#                 try:
#                     fuente = ImageFont.truetype("arial.ttf", 36)  # Cambia el tamaño según lo necesario
#                 except IOError:
#                     fuente = ImageFont.load_default()
# 
#                 # Calcular la posición para la marca de agua (esquina inferior derecha)
#                 x1, y1, x2, y2 = dibujo.textbbox((20, 20), texto, font=fuente)
#                 ancho_texto = x2 - x1
#                 alto_texto = y2 - y1
#                 posicion = (imagen.width - ancho_texto - 10, imagen.height - alto_texto - 10)
#                 
#                 transparencia = 128  # Transparencia (0 = invisible, 255 = opaco)
# 
#                 pixel_central = imagen.getpixel((imagen.width - 1, imagen.height - 1))
#                 brillo = sum(pixel_central[:3]) // 3  # Promedio R, G, B
#                 color_texto = (255, 255, 255, transparencia) if brillo < 128 else (0, 0, 0, transparencia)
# 
#                 # Aplicar la marca de agua
#                 dibujo.text(posicion, texto, font=fuente, fill=color_texto)  # Color blanco
# 
#                 # Guardar la imagen con marca de agua
#                 nombre_base, extension = os.path.splitext(nombre_archivo)
#                 nueva_ruta = os.path.join("archivos", f"{nombre_base}{extension}") # imagen guardada con la marca de agua
#                 print ("Nueva ruta", nueva_ruta)
#                 imagen.save(nueva_ruta)
# 
#                 print(f"Imagen con marca de agua guardada como: {nueva_ruta}")
# 
#                 # Cifrar la imagen después de agregar la marca de agua
#                 # NO ESTÁ ENTRANDO AQUÍ
#                 if "_cifrado" in nombre_archivo:
#                     print ("Ciframos la imagen con la marca de agua puesta")
#                     cifrar_archivo(nueva_ruta)
# 
# 
#         except Exception as e:
#             print(f"Error al abrir la imagen descargada o al agregar la marca de agua: {e}")
#     else:
#         print("El archivo no es una imagen soportada. No se aplicará la marca de agua.")


def agregar_marca_agua(nombre_archivo, usuario):
    # Verificar si el archivo es una foto
    if nombre_archivo.lower().endswith((".jpeg", ".jpg", ".png")):
        ruta_archivo = os.path.join("archivos", nombre_archivo)
            
            
        try:
            # Verifica que la imagen se pueda abrir antes de agregar la marca de agua
            with Image.open(ruta_archivo) as img:
                img.verify()  # Esto lanzará una excepción si la imagen está corrupta

            # Abrir la imagen nuevamente para modificarla
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
                x1, y1, x2, y2 = dibujo.textbbox((20, 20), texto, font=fuente)
                ancho_texto = x2 - x1
                alto_texto = y2 - y1
                posicion = (imagen.width - ancho_texto - 10, imagen.height - alto_texto - 10)
                
                transparencia = 128  # Transparencia (0 = invisible, 255 = opaco)

                pixel_central = imagen.getpixel((imagen.width - 1, imagen.height - 1))
                brillo = sum(pixel_central[:3]) // 3  # Promedio R, G, B
                color_texto = (255, 255, 255, transparencia) if brillo < 128 else (0, 0, 0, transparencia)

                # Aplicar la marca de agua
                dibujo.text(posicion, texto, font=fuente, fill=color_texto)  # Color blanco

                # Guardar la imagen con marca de agua
                nombre_base, extension = os.path.splitext(nombre_archivo)
                nueva_ruta = os.path.join("archivos", f"{nombre_base}{extension}") # imagen guardada con la marca de agua
                print ("Nueva ruta", nueva_ruta)
                imagen.save(nueva_ruta)

                print(f"Imagen con marca de agua guardada como: {nueva_ruta}")

        except Exception as e:
            print(f"Error al abrir la imagen descargada o al agregar la marca de agua: {e}")
    else:
        print("El archivo no es una imagen soportada. No se aplicará la marca de agua.")


# Función para leer la clave de un archivo
def leer_clave_para_archivo(nombre_archivo):
    """
    Lee las claves del archivo de texto y devuelve la clave asociada al archivo solicitado.
    """
    archivo_claves = "claves.txt"
    
    if not os.path.exists(archivo_claves):
        print("El archivo de claves no existe.")
        return None
    
    with open(archivo_claves, 'r') as f:
        for linea in f:
            # Asegurarse de que la línea contiene dos elementos separados por ":"
            if ':' in linea:
                archivo, clave = linea.strip().split(':')
                if archivo == os.path.basename(nombre_archivo):  # Usar solo el nombre base
                    return bytes.fromhex(clave)
    
    # Si el archivo no existe en 'archivos/' y no está cifrado, imprimir el mensaje
    if os.path.exists(f"archivos/{nombre_archivo}") and "_cifrado" not in nombre_archivo:
        print(f"No se encontró una clave para el archivo {nombre_archivo}.")
        return None
    
    return None

# Función para cifrar un archivo
def cifrar_archivo(nombre_archivo):
    # Crear la carpeta si no existe
    os.makedirs("archivos", exist_ok=True)

    # Archivo donde se guardarán las claves
    archivo_claves = "claves.txt"

    # Verificar si el archivo ya está cifrado (si tiene '_cifrado' en el nombre)
    if "_cifrado" in nombre_archivo:
        print(f"Este archivo ya está cifrado: {nombre_archivo}")
        return None  # Termina la ejecución si ya está cifrado

    # Verificar si el archivo existe
    ruta_archivo = os.path.join("archivos", nombre_archivo)
    if not os.path.exists(ruta_archivo):
        print(f"El archivo {ruta_archivo} no existe.")
        return None

    # Leer el archivo
    with open(ruta_archivo, 'rb') as f:
        datos = f.read()

    # Generar una clave simétrica AES (256 bits)
    clave_simetrica = os.urandom(32)  # Clave AES-256
    iv = os.urandom(16)  # Vector de inicialización

    # Aplicar PKCS7 Padding
    padder = PKCS7(128).padder()  # Bloques de 128 bits (16 bytes)
    datos_padded = padder.update(datos) + padder.finalize()

    # Crear el cifrador con AES en modo CBC
    cipher = Cipher(algorithms.AES(clave_simetrica), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Cifrar los datos
    datos_cifrados = encryptor.update(datos_padded) + encryptor.finalize()

    # Guardar el archivo cifrado
    nombre_base, extension = os.path.splitext(nombre_archivo)
    nombre_archivo_cifrado = f"{nombre_base}_cifrado{extension}"
    ruta_archivo_cifrado = os.path.join("archivos", nombre_archivo_cifrado)
    with open(ruta_archivo_cifrado, 'wb') as f:
        f.write(iv + datos_cifrados)  # Almacenar IV + datos cifrados

    # Eliminar la clave asociada al archivo anterior del archivo de claves, si existe
    if os.path.exists(archivo_claves):
        with open(archivo_claves, 'r') as f:
            lineas = f.readlines()

        with open(archivo_claves, 'w') as f:
            for linea in lineas:
                if not linea.startswith(nombre_archivo + ":"):
                    f.write(linea)

    # Crear el archivo de claves si no existe
    if not os.path.exists(archivo_claves):
        with open(archivo_claves, 'w') as f:
            pass  # Solo crear el archivo vacío si no existe

    # Guardar la nueva clave en el archivo de texto (solo el nombre base del archivo)
    with open(archivo_claves, 'a') as f:
        f.write(f"{nombre_archivo}:{clave_simetrica.hex()}\n")

    print(f"Archivo cifrado guardado como: {ruta_archivo_cifrado}")
    return ruta_archivo_cifrado

# Función para descifrar un archivo
def descifrar_archivo(nombre_archivo_cifrado, clave_simetrica):
    ruta_archivo_cifrado = os.path.join("archivos", nombre_archivo_cifrado)
    
    # Verificar si el archivo cifrado existe
    if not os.path.exists(ruta_archivo_cifrado):
        print(f"El archivo {ruta_archivo_cifrado} no existe.")
        return

    # Leer el archivo cifrado
    with open(ruta_archivo_cifrado, 'rb') as f:
        iv = f.read(16)  # Leer los primeros 16 bytes para el IV
        datos_cifrados = f.read()  # Leer el resto de los datos cifrados
    
    print(f"Clave: {clave_simetrica.hex()}, IV: {iv.hex()}")  # Verificar clave e IV

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
    nombre_archivo_descifrado = f"{nombre_base}{extension}"

    ruta_archivo_descifrado = os.path.join("archivos", nombre_archivo_descifrado)
    with open(ruta_archivo_descifrado, 'wb') as f:
        f.write(datos_descifrados)

    print(f"Archivo descifrado guardado como: {ruta_archivo_descifrado}")
    return ruta_archivo_descifrado

# Función para enviar el archivo solicitado
def enviar_archivo(conexion, nombre_archivo):
    try:
        with open(os.path.join('archivos', nombre_archivo), 'rb') as file:
            # Enviar el nombre del archivo como confirmación
            conexion.send(nombre_archivo.encode())
            # Leer y enviar el archivo en bloques
            while chunk := file.read(1024):
                conexion.send(chunk)
        print(f'Archivo {nombre_archivo} enviado exitosamente.')
        # Enviar un marcador para indicar el fin de transmisión
        conexion.send(b'FINAL_ARCHIVO')
    except FileNotFoundError:
        conexion.send(b'Archivo no encontrado.')


def iniciar_servidor():
    if not verificar_carpeta_archivos():
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_servidor:
        socket_servidor.bind((HOST, PORT))
        socket_servidor.listen(5)
        print(f'Servidor escuchando en {HOST}:{PORT}...')

        while True:
            conexion, address = socket_servidor.accept()
            print(f'Conexión establecida con {address}')
            
            usuario = conexion.recv(1024).decode().strip()
            print(f'Usuario conectado: {usuario}')
            
            with conexion:
                while True:  # Mantener la conexión abierta mientras el cliente lo permita
                    try:
                        comando = conexion.recv(1024).decode().strip()
                        print(f'Comando recibido: {comando}')
                        
                        # Separar el comando principal y los argumentos
                        partes = comando.split(' ', 1)
                        comando_principal = partes[0].upper()  # Solo el comando principal en mayúsculas
                        nombre_archivo = partes[1] if len(partes) > 1 else None  # Argumento sin modificar
                        
                        if not comando_principal:  # Si el comando está vacío, cerrar la conexión
                            break
                        
                        if comando_principal == "SALIR":
                            print(f'Cliente {address} desconectado.\n')
                            break  # Salir del bucle interno, pero no cerrar el servidor

                        elif comando_principal == "LISTAR":
                            listar_archivos(conexion)

                        elif comando_principal == "DESCARGAR" and nombre_archivo:
                            print(f'Procesando solicitud de descarga: {nombre_archivo}')
                            
                            # Verificar si el archivo está cifrado
                            if "_cifrado" in nombre_archivo:
                                # Extraer el nombre original del archivo cifrado
                                nombre_original = os.path.basename(nombre_archivo).replace("_cifrado", "")
        
                                # Obtener la clave para el archivo cifrado
                                clave_simetrica = leer_clave_para_archivo(nombre_original)
                                
                                # Descifrar el archivo
                                archivo_descifrado = descifrar_archivo(os.path.basename(nombre_archivo), clave_simetrica)

                                # Agregar la marca de agua al archivo descifrado
                                agregar_marca_agua(os.path.basename(archivo_descifrado), usuario)

                                # Cifrar de nuevo el archivo con la marca de agua
                                archivo_cifrado_nuevo = cifrar_archivo(os.path.basename(archivo_descifrado))

                                # Enviar el archivo cifrado
                                enviar_archivo(conexion, os.path.basename(archivo_cifrado_nuevo))
                            else:
                                # Agregar la marca de agua
                                agregar_marca_agua(nombre_archivo, usuario)

                                # Enviar el archivo directamente
                                enviar_archivo(conexion, nombre_archivo)
                            
                        else:
                            conexion.send(b'Comando no reconocido. Intente de nuevo.')
                    except ConnectionResetError:
                        print(f'Conexión con {address} finalizada abruptamente.\n')
                        break

iniciar_servidor()
