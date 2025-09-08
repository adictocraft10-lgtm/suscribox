# Bot de Ventas de Modelos 3D para Discord

Este es un bot de Discord diseñado para automatizar la venta de modelos 3D (o cualquier archivo digital) directamente en tu servidor. Gestiona un inventario, permite a los usuarios buscar y comprar modelos, y facilita al administrador la entrega de los archivos una vez confirmado el pago.

## Características

- **Catálogo de Modelos**: Muestra todos los modelos disponibles con el comando `!catalogo`.
- **Búsqueda Inteligente**: Los usuarios pueden buscar modelos por nombre con `!buscar`.
- **Carrito de Compras**: Sistema de carrito persistente para cada usuario (`!agregar`, `!ver_carrito`, `!vaciar_carrito`).
- **Proceso de Compra**: El comando `!comprar` inicia el checkout, enviando al usuario el total y la información de pago por DM.
- **Notificaciones para Admins**: Notifica en un canal privado cuando un usuario genera un nuevo pedido.
- **Entrega Semi-Automática**: Un administrador confirma el pago con `!confirmar_pago`, y el bot automáticamente comprime los archivos y los envía al usuario por DM.
- **Manejo de Archivos Grandes**: Si los archivos del pedido superan el límite de Discord (25 MB), el bot notifica al usuario y al admin para coordinar una entrega manual.

## Instalación y Configuración

Sigue estos pasos para poner en marcha el bot.

### 1. Prerrequisitos

- Python 3.7 o superior.
- Una cuenta de bot de Discord con su **token**. Puedes crear uno en el [Portal de Desarrolladores de Discord](https://discord.com/developers/applications).
- Asegúrate de que tu bot tenga los siguientes **Privileged Gateway Intents** activados en el portal de desarrolladores:
  - `SERVER MEMBERS INTENT`
  - `MESSAGE CONTENT INTENT`

### 2. Clonar o Descargar el Proyecto

Obtén los archivos del proyecto, que son:
- `discord_bot.py`
- `requirements.txt`
- `.env` (que crearás a continuación)
- `README.md` (este archivo)

### 3. Instalar Dependencias

Abre una terminal en la carpeta del proyecto y ejecuta el siguiente comando para instalar las librerías necesarias:
```bash
pip install -r requirements.txt
```

### 4. Configurar las Variables de Entorno

Crea un archivo llamado `.env` en la misma carpeta que `discord_bot.py`. Este archivo contendrá toda la configuración secreta del bot. **Nunca compartas este archivo.**

Copia y pega el siguiente contenido en tu archivo `.env` y rellena los valores:

```ini
# El token secreto de tu bot de Discord.
DISCORD_TOKEN="AQUI_VA_EL_TOKEN_DE_TU_BOT"

# La ruta COMPLETA a la carpeta que contiene las carpetas de tus modelos.
# Ejemplo en Windows: C:\Users\TuUsuario\Desktop\Modelos3D
# Ejemplo en Linux: /home/TuUsuario/Modelos3D
MODEL_PATH="AQUI_VA_LA_RUTA_A_TUS_MODELOS"

# La ruta COMPLETA al archivo de texto con los precios.
# Ejemplo en Windows: C:\Users\TuUsuario\Desktop\precios.txt
PRICES_FILE="AQUI_VA_LA_RUTA_A_TU_ARCHIVO_DE_PRECIOS"

# El ID del canal de Discord donde quieres recibir las notificaciones de nuevos pedidos.
# Para obtener el ID, activa el Modo Desarrollador en Discord, haz clic derecho en el canal y selecciona "Copiar ID del canal".
ADMIN_CHANNEL_ID="AQUI_VA_EL_ID_DEL_CANAL_DE_ADMIN"

# Tu correo de PayPal que se mostrará a los usuarios para el pago.
PAYPAL_EMAIL="tu_correo@ejemplo.com"

# El nombre EXACTO del rol que tiene permiso para confirmar pagos (ej: "Dueño", "Admin").
# Es sensible a mayúsculas y minúsculas.
OWNER_ROLE_NAME="Dueño"
```

### 5. Estructura de Archivos

- **Carpeta de Modelos**: El bot espera que cada modelo esté en su propia subcarpeta dentro de la ruta que especificaste en `MODEL_PATH`. El nombre de la carpeta debe ser el nombre del modelo.
  ```
  Modelos3D/
  ├── Noir Paladin/
  │   ├── modelo.fbx
  │   └── textura.png
  └── Samurai Dragon/
      ├── dragon.obj
      └── readme.txt
  ```
- **Archivo de Precios**: El archivo `precios.txt` debe tener una línea por cada modelo, con el formato `Nombre del Modelo = Precio`.
  ```
  Noir Paladin = 15 USD
  Samurai Dragon = 20 USD
  ```

## Cómo Ejecutar el Bot

Una vez que hayas configurado todo, simplemente ejecuta el siguiente comando en tu terminal:
```bash
python3 discord_bot.py
```
Si todo está configurado correctamente, verás el mensaje "--- Iniciando Bot de Discord ---" y "Bot conectado como [NombreDeTuBot]" en la consola. El bot estará online y listo para recibir comandos.

## Lista de Comandos

### Comandos para Usuarios

- `!catalogo`: Muestra una lista de todos los modelos disponibles.
- `!buscar <nombre>`: Busca modelos que contengan el `<nombre>` especificado.
- `!agregar <nombre_completo>`: Añade un modelo al carrito. Requiere el nombre exacto.
- `!ver_carrito`: Muestra los artículos en tu carrito y el precio total.
- `!vaciar_carrito`: Limpia todos los artículos de tu carrito.
- `!comprar`: Inicia el proceso de pago. Recibirás un DM con los detalles.

### Comandos para Administradores

- `!confirmar_pago @usuario`: (Requiere el rol `OWNER_ROLE_NAME`). Confirma que el pago del `@usuario` ha sido recibido, comprime los archivos de su pedido y se los envía por DM.
