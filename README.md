# Sistema cliente-servidor cifrado

[![Tecnologías](https://skillicons.dev/icons?i=py)](https://skillicons.dev)

Distribución segura de contenidos con tres piezas: un servidor de contenidos, un servidor de licencias y un cliente, con firma digital RSA y cifrado simétrico AES.

![Sistema cliente-servidor cifrado](docs/preview.jpg)

## Qué hace

- El servidor de contenidos lista los ficheros disponibles y los envía cifrados con AES.
- El cliente firma su petición con RSA y el servidor de licencias le entrega la clave para descifrar.
- Las imágenes descargadas llevan una marca de agua con el usuario.

## Cómo ejecutarlo

```bash
pip install cryptography pillow

# Cada uno en una terminal
python servidor_licencias.py
python servidor_contenidos_simple.py
python cliente.py
```

## Contenido

| Fichero | Qué es |
|---|---|
| `servidor_contenidos_simple.py` | Servidor de contenidos |
| `servidor_licencias.py` | Servidor de licencias |
| `cliente.py` | Cliente |
| `cifrador.py` | Cifrado y descifrado de ficheros con AES |
| `archivos/, descargas/` | Contenidos de ejemplo y descargas del cliente |
| `claves.txt` | Clave de ejemplo de los contenidos de prueba |

---

Proyecto del Grado en Tecnología Digital y Multimedia (UPV). Forma parte de mi [portfolio](https://quique-such.github.io/portafolio/).
