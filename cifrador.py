import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend

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
    nombre_archivo_descifrado = f"{nombre_base}_descifrado{extension}"

    ruta_archivo_descifrado = os.path.join("archivos", nombre_archivo_descifrado)
    with open(ruta_archivo_descifrado, 'wb') as f:
        f.write(datos_descifrados)

    print(f"Archivo descifrado guardado como: {ruta_archivo_descifrado}")
    return ruta_archivo_descifrado


# EJEMPLO CIFRADO
nombre_archivo = input("Introduce el nombre del archivo a cifrar (en la carpeta 'archivos'): ")
archivo_cifrado = cifrar_archivo(nombre_archivo)

# EJEMPLO DESCIFRADO

nombre_original = os.path.basename(nombre_archivo)  # Extraer el nombre del archivo original

clave_simetrica = leer_clave_para_archivo(os.path.basename(nombre_original)) # Obtener la clave correspondiente
descifrar_archivo(os.path.basename(archivo_cifrado), clave_simetrica)

