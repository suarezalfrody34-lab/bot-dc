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


@bot.event
async def on_ready():
    print(f"Conectado como {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    # Solo actuamos cuando el usuario entra a un canal de voz.
    if before.channel is not None or after.channel is None:
        return

    source_channel = after.channel
    guild = member.guild

    # Crea el nuevo canal en la misma categoría del canal al que entró.
    new_channel = await guild.create_voice_channel(
        name=f"{member.display_name}",
        category=source_channel.category,
        reason=f"Canal temporal para {member}"
    )

    try:
        await member.move_to(new_channel, reason="Mover al usuario a su canal temporal")
    except (discord.Forbidden, discord.HTTPException):
        # Si no puede mover al usuario, elimina el canal que acabamos de crear.
        await new_channel.delete(reason="No se pudo mover al usuario")
        return


bot.run(TOKEN)
