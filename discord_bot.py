import discord
from discord.ext import commands
import os
import uuid
import zipfile
import shutil
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# --- Declaración de variables globales ---
# Estas se llenarán más tarde, dependiendo del modo de ejecución
DISCORD_TOKEN = None
MODEL_PATH = None
PRICES_FILE = None
ADMIN_CHANNEL_ID = 0
PAYPAL_EMAIL = None
OWNER_ROLE_NAME = None

# Configurar los intents del bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

# Inicializar el bot
bot = commands.Bot(command_prefix='!', intents=intents)

# --- Funciones de Carga de Datos ---

def load_inventory():
    """Escanea el directorio de modelos y carga los nombres en la memoria."""
    global model_inventory
    try:
        if not MODEL_PATH or not os.path.isdir(MODEL_PATH):
            print(f"Error: La ruta de modelos (MODEL_PATH) '{MODEL_PATH}' no es válida o no está configurada en .env")
            model_inventory = []
            return

        # Usamos list comprehension para obtener los nombres de las carpetas
        model_inventory = [item.name for item in os.scandir(MODEL_PATH) if item.is_dir()]
        print(f"Inventario cargado: {len(model_inventory)} modelos encontrados.")
        # print(model_inventory) # Descomentar para depuración
    except Exception as e:
        print(f"Ocurrió un error al cargar el inventario: {e}")
        model_inventory = []

def load_prices():
    """Lee el archivo de precios y carga los datos en un diccionario."""
    global model_prices
    try:
        if not PRICES_FILE or not os.path.isfile(PRICES_FILE):
            print(f"Error: El archivo de precios (PRICES_FILE) '{PRICES_FILE}' no es válido o no está configurado en .env")
            model_prices = {}
            return

        with open(PRICES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if ' = ' in line:
                    name, price = line.strip().split(' = ', 1)
                    model_prices[name.lower()] = price # Guardamos en minúsculas para facilitar la búsqueda
        print(f"Precios cargados: {len(model_prices)} entradas encontradas.")
        # print(model_prices) # Descomentar para depuración
    except Exception as e:
        print(f"Ocurrió un error al cargar los precios: {e}")
        model_prices = {}

# Diccionarios en memoria para almacenar datos
model_inventory = []
model_prices = {}
user_carts = {} # {user_id: [model1, model2]}
active_orders = {} # {user_id: {"items": [], "total": 0.0, "order_id": ""}}

@bot.event
async def on_ready():
    """Se ejecuta cuando el bot se conecta a Discord."""
    print(f'Bot conectado como {bot.user}')
    # Cargar datos al iniciar
    load_inventory()
    load_prices()

# --- Comandos del Bot (se implementarán más adelante) ---

@bot.command(name='catalogo')
async def catalog(ctx):
    """Muestra todos los modelos disponibles en el inventario."""
    if not model_inventory:
        await ctx.send("El inventario de modelos está vacío o no se ha cargado correctamente.")
        return

    # Crear un embed para una bonita presentación
    embed = discord.Embed(
        title="Catálogo de Modelos 3D",
        description="Estos son todos los modelos que tenemos disponibles:",
        color=discord.Color.blue()
    )

    # Unir la lista de modelos en un solo string, cada uno en una nueva línea
    model_list_str = "\n- ".join(sorted(model_inventory))

    # Discord tiene un límite de 4096 caracteres para la descripción de un embed.
    # Si la lista es muy larga, la truncamos para evitar un error.
    if len(model_list_str) > 4000:
        model_list_str = model_list_str[:4000] + "\n\n*Y muchos más...*"

    embed.description = "- " + model_list_str
    embed.set_footer(text=f"Total: {len(model_inventory)} modelos. Usa `!buscar <nombre>` para ver el precio.")

    await ctx.send(embed=embed)

@bot.command(name='buscar')
async def search(ctx, *, query: str):
    """Busca un modelo por nombre en el inventario y muestra su precio."""
    if not query:
        await ctx.send("Por favor, escribe el nombre del modelo que quieres buscar. Ejemplo: `!buscar dragon`")
        return

    query = query.lower()
    matches = []

    # Buscamos modelos que contengan la consulta del usuario
    for model_name in model_inventory:
        if query in model_name.lower():
            # El precio se busca con la clave en minúsculas
            price = model_prices.get(model_name.lower(), "Precio no disponible")
            matches.append({'name': model_name, 'price': price})

    if not matches:
        embed = discord.Embed(
            title="Búsqueda sin Resultados",
            description=f"No encontré ningún modelo que contenga '{query}'.\nPrueba con otro término o usa `!catalogo` para ver todos los modelos.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Creamos un embed para mostrar los resultados
    embed = discord.Embed(
        title=f"Resultados de la Búsqueda para '{query}'",
        color=discord.Color.green()
    )

    description_lines = []
    for match in matches[:20]: # Limitar a 20 para no hacer un mensaje gigante
        description_lines.append(f"**{match['name']}**\nPrecio: `{match['price']}`")

    embed.description = "\n\n".join(description_lines)

    if len(matches) > 20:
        embed.set_footer(text=f"Mostrando los primeros 20 de {len(matches)} resultados.")
    else:
        embed.set_footer(text=f"Encontré {len(matches)} resultado(s).")

    await ctx.send(embed=embed)

@bot.command(name='agregar')
async def add_to_cart(ctx, *, model_name: str):
    """Añade un modelo al carrito de compras del usuario."""
    if not model_name:
        await ctx.send("Debes especificar el nombre del modelo a agregar. Ejemplo: `!agregar Noir Paladin`")
        return

    user_id = ctx.author.id
    query = model_name.lower()

    # Buscamos una coincidencia exacta del nombre del modelo (insensible a mayúsculas)
    found_model_name = None
    for inv_model in model_inventory:
        if inv_model.lower() == query:
            found_model_name = inv_model
            break

    if not found_model_name:
        await ctx.send(f"No pude encontrar el modelo exacto '{model_name}'.\nUsa `!buscar` para encontrar el nombre correcto y luego cópialo y pégalo aquí.")
        return

    # Si el usuario no tiene carrito, se crea uno
    if user_id not in user_carts:
        user_carts[user_id] = []

    # Evitar duplicados en el carrito
    if found_model_name in user_carts[user_id]:
        await ctx.send(f"El modelo '{found_model_name}' ya está en tu carrito. Usa `!ver_carrito` para revisar tu pedido.")
        return

    user_carts[user_id].append(found_model_name)

    embed = discord.Embed(
        title="✅ Modelo Añadido al Carrito",
        description=f"He añadido **{found_model_name}** a tu carrito.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Tienes {len(user_carts[user_id])} item(s) en el carrito. Usa `!ver_carrito` para revisar.")
    await ctx.send(embed=embed)

# --- Funciones de Ayuda ---
def parse_price(price_str: str) -> float:
    """Extrae el valor numérico de un string de precio (ej: '15.5 USD' -> 15.5)."""
    try:
        # Asume que el precio es el primer elemento del string
        return float(price_str.split()[0])
    except (ValueError, IndexError):
        return 0.0

@bot.command(name='ver_carrito')
async def view_cart(ctx):
    """Muestra el contenido del carrito de compras del usuario y el total."""
    user_id = ctx.author.id
    if user_id not in user_carts or not user_carts[user_id]:
        await ctx.send("Tu carrito de compras está vacío. Usa `!agregar <nombre_modelo>` para añadir items.")
        return

    cart_items = user_carts[user_id]
    total_price = 0.0

    embed = discord.Embed(
        title=f"🛒 Carrito de Compras de {ctx.author.name}",
        color=discord.Color.blue()
    )

    description_lines = []
    for item_name in cart_items:
        price_str = model_prices.get(item_name.lower(), "0 USD")
        item_price = parse_price(price_str)
        total_price += item_price
        description_lines.append(f"• **{item_name}** - `{price_str}`")

    embed.description = "\n".join(description_lines)
    embed.add_field(name="Total a Pagar", value=f"**`{total_price:.2f} USD`**", inline=False)
    embed.set_footer(text="Usa `!comprar` para proceder al pago o `!vaciar_carrito` para limpiarlo.")

    await ctx.send(embed=embed)

@bot.command(name='vaciar_carrito')
async def clear_cart(ctx):
    """Vacía el carrito de compras del usuario."""
    user_id = ctx.author.id
    if user_id in user_carts and user_carts[user_id]:
        user_carts.pop(user_id) # Eliminar la clave del carrito
        await ctx.send("🗑️ Tu carrito de compras ha sido vaciado.")
    else:
        await ctx.send("Tu carrito ya estaba vacío.")

@bot.command(name='comprar')
async def buy(ctx):
    """Inicia el proceso de compra, guarda el pedido y notifica al usuario y a los admins."""
    user_id = ctx.author.id
    if user_id not in user_carts or not user_carts[user_id]:
        await ctx.send("Tu carrito está vacío. ¡Añade algunos modelos con `!agregar` antes de comprar!")
        return

    cart_items = user_carts[user_id]
    total_price = sum(parse_price(model_prices.get(item.lower(), "0 USD")) for item in cart_items)

    # Generar un ID de pedido único y corto
    order_id = str(uuid.uuid4()).split('-')[0]

    # Guardar el pedido activo para la confirmación del admin
    active_orders[user_id] = {
        "items": list(cart_items), # Crear una copia
        "total": total_price,
        "order_id": order_id,
        "user": ctx.author
    }

    # Limpiar el carrito del usuario
    user_carts.pop(user_id)

    # --- Mensaje para el usuario (por DM) ---
    try:
        embed_user = discord.Embed(
            title="🧾 Tu Pedido está casi listo",
            description=f"¡Gracias! He registrado tu pedido con el ID: **`{order_id}`**",
            color=discord.Color.purple()
        )
        item_list_str = "\n".join([f"• {item}" for item in cart_items])
        embed_user.add_field(name="Resumen de tu pedido:", value=item_list_str, inline=False)
        embed_user.add_field(name="Total a Pagar:", value=f"**`{total_price:.2f} USD`**", inline=False)
        embed_user.add_field(
            name="Instrucciones de Pago",
            value=f"1. Realiza el pago a través de PayPal a: **`{PAYPAL_EMAIL}`**\n"
                  f"2. Envía una captura de pantalla del comprobante en este canal.\n"
                  f"3. Un administrador verificará tu pago y te entregará los modelos.",
            inline=False
        )
        embed_user.set_footer(text="Tu carrito ha sido vaciado. Contacta a un admin si tienes problemas.")

        await ctx.author.send(embed=embed_user)
        await ctx.send(f"{ctx.author.mention}, te he enviado los detalles de tu pedido y las instrucciones de pago por mensaje privado. ¡Revísalo!")

    except discord.Forbidden:
        await ctx.send(f"{ctx.author.mention}, no puedo enviarte mensajes privados. Por favor, habilita los DMs para poder enviarte los detalles del pedido.")
        # Devolver los items al carrito si no se pudo contactar
        user_carts[user_id] = cart_items
        active_orders.pop(user_id) # Cancelar el pedido
        return

    # --- Notificación para los administradores ---
    admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
    if admin_channel:
        embed_admin = discord.Embed(
            title=f"📢 Nuevo Pedido - ID: `{order_id}`",
            description=f"El usuario **{ctx.author.mention}** (`{ctx.author.name}`) ha iniciado una compra.",
            color=discord.Color.dark_orange()
        )
        item_list_str_admin = "\n".join([f"- {item}" for item in cart_items])
        embed_admin.add_field(name="Contenido del Pedido", value=item_list_str_admin, inline=False)
        embed_admin.add_field(name="Total del Pedido", value=f"`{total_price:.2f} USD`", inline=False)
        embed_admin.set_footer(text=f"Para confirmar y entregar, usa: !confirmar_pago @{ctx.author.name}")
        await admin_channel.send(embed=embed_admin)

@bot.command(name='confirmar_pago')
@commands.has_role(OWNER_ROLE_NAME)
async def confirm_payment(ctx, member: discord.Member):
    """Confirma el pago de un usuario y le entrega los archivos de su pedido."""
    user_id = member.id
    if user_id not in active_orders:
        await ctx.send(f"No he encontrado ningún pedido activo para {member.mention}.")
        return

    order = active_orders[user_id]
    order_id = order['order_id']
    items_to_zip = order['items']
    user_to_deliver = order['user']

    processing_msg = await ctx.send(f"⏳ Procesando pedido `{order_id}` para **{user_to_deliver.name}**. Creando archivo ZIP...")

    zip_path = f"./pedido_{order_id}.zip"
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for item_name in items_to_zip:
                item_folder_path = os.path.join(MODEL_PATH, item_name)
                if os.path.isdir(item_folder_path):
                    # Añadimos la carpeta y todo su contenido al zip
                    for root, _, files in os.walk(item_folder_path):
                        for file in files:
                            full_path = os.path.join(root, file)
                            # La ruta dentro del zip será relativa para mantener la estructura de carpetas
                            archive_path = os.path.relpath(full_path, MODEL_PATH)
                            zf.write(full_path, archive_path)
                else:
                    await ctx.send(f"⚠️ **Aviso:** No se encontró la carpeta para el modelo `{item_name}`. No se incluirá en la entrega.")

        file_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        if file_size_mb > 24: # Dejar un margen por si acaso
            await user_to_deliver.send(f"¡Hola! Tu pedido `{order_id}` está listo, pero los archivos son muy grandes ({file_size_mb:.2f} MB) para enviarlos por Discord. Un administrador se pondrá en contacto contigo para coordinar la entrega manual. ¡Gracias por tu paciencia!")
            await processing_msg.edit(content=f"⚠️ **Archivo demasiado grande** para el pedido `{order_id}` ({file_size_mb:.2f} MB). Se ha notificado al usuario para entrega manual.")
            return

        await user_to_deliver.send(
            f"🎉 ¡Gracias por tu compra! Aquí tienes tu pedido `{order_id}`.",
            file=discord.File(zip_path)
        )

        await processing_msg.edit(content=f"✅ **Entrega Completada**. El pedido `{order_id}` para {user_to_deliver.mention} ha sido entregado por DM.")
        active_orders.pop(user_id) # Eliminar solo si la entrega fue exitosa

    except discord.Forbidden:
        await processing_msg.edit(content=f"❌ **Error de entrega**: No pude enviar el DM a {user_to_deliver.mention}. Es posible que tenga los DMs desactivados. El pedido sigue activo para que puedas intentar la entrega manual.")
    except Exception as e:
        await processing_msg.edit(content=f"❌ **Error al procesar el pedido `{order_id}`:**\n`{e}`\nEl pedido sigue activo. Revisa los logs y realiza la entrega manual.")

    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

@confirm_payment.error
async def confirm_payment_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("⛔ No tienes permiso para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Debes mencionar al usuario al que quieres confirmar el pago. Ejemplo: `!confirmar_pago @usuario`")
    else:
        await ctx.send(f"Ha ocurrido un error inesperado: {error}")

# --- Punto de entrada principal ---
if __name__ == "__main__":
    # Asignar todas las variables de entorno necesarias para el bot
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    MODEL_PATH = os.getenv("MODEL_PATH")
    PRICES_FILE = os.getenv("PRICES_FILE")
    PAYPAL_EMAIL = os.getenv("PAYPAL_EMAIL")
    OWNER_ROLE_NAME = os.getenv("OWNER_ROLE_NAME")
    try:
        ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", 0))
    except (ValueError, TypeError):
        ADMIN_CHANNEL_ID = 0

    # Validar que las variables críticas estén presentes
    if not DISCORD_TOKEN or DISCORD_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Error: El token del bot (DISCORD_TOKEN) no está configurado correctamente en .env")
    elif not ADMIN_CHANNEL_ID:
        print("Error: El ID del canal de admin (ADMIN_CHANNEL_ID) no está configurado correctamente en .env")
    elif not OWNER_ROLE_NAME:
        print("Error: El rol de dueño (OWNER_ROLE_NAME) no está configurado en .env")
    elif not MODEL_PATH or not PRICES_FILE or not PAYPAL_EMAIL:
        print("Error: Revisa que MODEL_PATH, PRICES_FILE y PAYPAL_EMAIL estén configurados en .env")
    else:
        print("--- Iniciando Bot de Discord ---")
        bot.run(DISCORD_TOKEN)
