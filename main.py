import discord
from discord.ext import commands
from threading import Thread
import logging
from dotenv import load_dotenv
import os
from flask import Flask

load_dotenv()

# ================== KEEP ALIVE ==================
app = Flask(__name__)

@app.route('/')
def home():
    return "Discord Bot is Running! ✅"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

Thread(target=run_flask, daemon=True).start()


token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler("discord.log", encoding="utf-8", mode="w")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ======================
# READY
# ======================

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")

# ======================
# SESIUNE (CLEANER)
# ======================

@bot.command()
async def sesiune(ctx, ora, locatie="Greenville parcare"):

    msg = f"""
❗ **SESIUNE GVRF ÎN DESFĂȘURARE** ❗

⏰ Ora: {ora}
🏠 Locație: {locatie}
👮 Host: {ctx.author.mention}

📌 Minim 10 reacții pentru participare
@everyone
"""

    message = await ctx.send(msg)
    await message.add_reaction("✅")

# ======================
# WARN SYSTEM (SAFE + CLEAN)
# ======================

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="Nespecificat"):

    guild = ctx.guild

    warn1 = discord.utils.get(guild.roles, name="Warn 1")
    warn2 = discord.utils.get(guild.roles, name="Warn 2")
    warn3 = discord.utils.get(guild.roles, name="Warn 3")

    if not warn1 or not warn2 or not warn3:
        return await ctx.send("❌ Lipsesc rolurile Warn 1 / 2 / 3")

    if warn2 in member.roles:
        await member.remove_roles(warn2)
        await member.add_roles(warn3)
        level = 3

    elif warn1 in member.roles:
        await member.remove_roles(warn1)
        await member.add_roles(warn2)
        level = 2

    else:
        await member.add_roles(warn1)
        level = 1

    embed = discord.Embed(
        title=f"⚠️ WARN {level}",
        color=discord.Color.orange()
    )

    embed.add_field(name="👤 User", value=member.mention, inline=False)
    embed.add_field(name="📌 Motiv", value=reason, inline=False)
    embed.add_field(name="👮 Moderator", value=ctx.author.mention, inline=False)

    await ctx.send(embed=embed)

    try:
        await member.send(embed=embed)
    except:
        pass

# ======================
# REGISTER (IMPROVED UX)
# ======================

@bot.command()
async def register(ctx, *, data):

    if not ctx.message.attachments:
        return await ctx.send("❌ Atașează o poză a mașinii.")

    try:
        nume, marca, model, an = [x.strip() for x in data.split("|")]
    except:
        return await ctx.send("❌ Format: nume | marca | model | an")

    poza = ctx.message.attachments[0].url

    embed = discord.Embed(
        title="🚗 Mașină înregistrată",
        color=discord.Color.green()
    )

    embed.add_field(name="👤 Nume", value=nume, inline=True)
    embed.add_field(name="🚘 Marcă", value=marca, inline=True)
    embed.add_field(name="🚗 Model", value=model, inline=True)
    embed.add_field(name="📅 An", value=an, inline=True)

    embed.set_image(url=poza)
    embed.set_footer(text=f"Înregistrat de {ctx.author}")

    await ctx.send(embed=embed)

# ======================
# RUN
# ======================

bot.run(token, log_handler=handler, log_level=logging.INFO)