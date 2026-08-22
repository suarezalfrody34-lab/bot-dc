import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("Falta DISCORD_TOKEN en el archivo .env")

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

TEMP_PREFIX = "🔊・"


@bot.event
async def on_ready():
    print(f"Conectado como {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_voice_state_update(member, before, after):

    # ============================================================
    # 1. SI ALGUIEN SALE DE UN CANAL TEMPORAL Y QUEDA VACÍO,
    #    ELIMINARLO.
    # ============================================================

    if before.channel and before.channel.name.startswith(TEMP_PREFIX):

        if len(before.channel.members) == 0:

            try:
                channel_name = before.channel.name

                await before.channel.delete(
                    reason="Canal temporal vacío"
                )

                print(f"🗑️ Canal eliminado: {channel_name}")

            except discord.NotFound:
                pass

            except discord.Forbidden:
                print("❌ No tengo permiso para eliminar canales.")

            except discord.HTTPException as error:
                print(f"❌ Error eliminando canal: {error}")

    # ============================================================
    # 2. SI NO ENTRÓ A NINGÚN CANAL, TERMINAR.
    # ============================================================

    if after.channel is None:
        return

    # ============================================================
    # 3. SI ENTRÓ A UN CANAL TEMPORAL, NO CREAR OTRO.
    #
    #    Así pueden entrar varias personas al mismo canal.
    # ============================================================

    if after.channel.name.startswith(TEMP_PREFIX):
        return

    # ============================================================
    # 4. SI NO CAMBIÓ DE CANAL, NO HACER NADA.
    # ============================================================

    if before.channel == after.channel:
        return

    # ============================================================
    # 5. CREAR EL CANAL TEMPORAL.
    # ============================================================

    guild = member.guild
    source_channel = after.channel

    try:

        new_channel = await guild.create_voice_channel(
            name=f"{TEMP_PREFIX}{member.display_name}",
            category=source_channel.category,
            reason="Crear canal temporal"
        )

        print(
            f"🆕 Canal creado para {member.display_name}: "
            f"{new_channel.name}"
        )

        # Mover al usuario al nuevo canal.
        await member.move_to(
            new_channel,
            reason="Mover al usuario a su canal temporal"
        )

    except discord.Forbidden:

        print("❌ El bot no tiene suficientes permisos.")

    except discord.HTTPException as error:

        print(f"❌ Error de Discord: {error}")


bot.run(TOKEN)
