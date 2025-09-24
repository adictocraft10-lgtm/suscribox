# Editor de Fotos con Marcos

Esta es una aplicación web simple que te permite agregar marcos, fotos, stickers y texto para crear composiciones personalizadas.

## Cómo usar

### 1. Requisitos

-   Tener Python 3 instalado en tu computadora. Puedes descargarlo desde [python.org](https://www.python.org/downloads/).

### 2. Iniciar la aplicación

1.  Abre una terminal o línea de comandos.
2.  Navega hasta la carpeta donde se encuentra este proyecto.
3.  Ejecuta el siguiente comando para iniciar el servidor web:

    ```bash
    python3 server.py
    ```

    Si tienes una versión más antigua de Python, puede que necesites usar `python` en lugar de `python3`.

4.  Abre tu navegador web y ve a la siguiente dirección: [http://localhost:8000](http://localhost:8000)

### 3. Añadir tus propios marcos y stickers

-   **Para añadir marcos:** Simplemente copia tus archivos de imagen (por ejemplo, `.png`, `.jpg`) en la carpeta `marcos`. Los marcos deben tener un área transparente en el medio para que la foto del usuario se pueda ver.
-   **Para añadir stickers:** Copia tus archivos de imagen en la carpeta `stickers`.

Los nuevos marcos y stickers aparecerán automáticamente en la galería la próxima vez que cargues la aplicación.

## Estructura del Proyecto

```
.
├── app/
│   ├── css/
│   │   └── style.css       # Estilos de la aplicación
│   ├── js/
│   │   └── script.js       # Lógica de la aplicación
│   └── index.html          # Página principal
├── marcos/                 # Pon tus marcos aquí
├── stickers/               # Pon tus stickers aquí
├── server.py               # Servidor web para ejecutar la app
└── README.md               # Este archivo
```