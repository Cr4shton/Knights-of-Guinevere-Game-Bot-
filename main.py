import os
import random
import asyncio
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask

# --- 🌐 EXTRA: FLASK WEB SERVER FOR RENDER FREE TIER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is online and awake!"

def run_flask():
    # This dynamically reads Render's requested system port
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    """Starts the web server on a separate background thread."""
    t = Thread(target=run_flask)
    t.start()
# --------------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True # CRUCIAL: Gives bot permission to read heart reacts
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 🚀 CHARACTER DATA ---
GUINEVERE_CHARACTERS = [
    # --- GODLY (Purple) ---
    {"name": "Princess Guinevere", "rarity": "🌌 Godly", "color": 0x9400D3, "image": "https://share.google", "weight": 1},
    {"name": "Olivia Park (flashback)", "rarity": "🌌 Godly", "color": 0x9400D3, "image": "https://share.google", "weight": 1},
    {"name": "Orville", "rarity": "🌌 Godly", "color": 0x9400D3, "image": "https://share.google", "weight": 1},

    # --- LEGENDARY (Blue) ---
    {"name": "Kid Andi", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google", "weight": 3},
    {"name": "Kid Frankie", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google", "weight": 3},
    {"name": "Gwen", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google", "weight": 3},
    {"name": "Sir Arthur", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google", "weight": 3},
    {"name": "Olivia Park", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google", "weight": 3},
    {"name": "Krash", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google", "weight": 3},
    {"name": "Armend", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google", "weight": 3},

    # --- RARE (Pink/Blue) ---
    {"name": "Andi", "rarity": "⭐ Rare", "color": 0xFF69B4, "image": "https://share.google", "weight": 8},
    {"name": "Frankie", "rarity": "⭐ Rare", "color": 0xFF69B4, "image": "https://share.google", "weight": 8},
    {"name": "Sparky", "rarity": "⭐ Rare", "color": 0x00FFFF, "image": "https://share.google", "weight": 8},
    {"name": "Patience", "rarity": "⭐ Rare", "color": 0xFF69B4, "image": "https://share.google", "weight": 8},

    # --- COMMON (Red) ---
    {"name": "Space cat", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google", "weight": 20},
    {"name": "Space penguin", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google", "weight": 20},
    {"name": "Space tapir", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google", "weight": 20},
    {"name": "Star pups", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google", "weight": 20},
    {"name": "Nurse 1", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google", "weight": 20},
    {"name": "Nurse 2", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google", "weight": 20},
    {"name": "Nurse 3", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google", "weight": 20},
    {"name": "Reggie", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google", "weight": 20}
]

user_gacha_backpack = {}
active_rolls = {}

def is_valid_discord_image(url: str) -> bool:
    clean_url = url.split('?')[0].lower()
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
    return url.startswith(('http://', 'https://')) and clean_url.endswith(valid_extensions)

@bot.event
async def on_ready():
    print(f"Game Bot is online as {bot.user.name}")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def roll(ctx):
    weights = [char["weight"] for char in GUINEVERE_CHARACTERS]
    picked = random.choices(GUINEVERE_CHARACTERS, weights=weights, k=1)[0]

    embed = discord.Embed(
        title="✨ A CHARACTER APPEARED! ✨",
        description="React with ❤️ within 15 seconds to claim them!",
        color=picked['color']
    )
    embed.add_field(name="Character Spotted", value=f"**{picked['name']}**", inline=False)
    embed.add_field(name="Rarity Rank", value=picked['rarity'], inline=True)
    
    if is_valid_discord_image(picked['image']):
        embed.set_image(url=picked['image'])
    else:
        embed.set_footer(text="⚠️ Image URL configuration is invalid. Must end in a standard photo format.")

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("❤️")

    active_rolls[msg.id] = {"character": picked, "claimed": False}

    await asyncio.sleep(15)
    if msg.id in active_rolls:
        if not active_rolls[msg.id]["claimed"]:
            del active_rolls[msg.id]
            try:
                embed.description = "⌛ Time's up! This character ran away."
                await msg.edit(embed=embed)
                await msg.clear_reactions()
            except discord.HTTPException:
                pass

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id or str(payload.emoji) != "❤️":
        return

    if payload.message_id in active_rolls:
        session = active_rolls[payload.message_id]
        if session["claimed"]:
            return
            
        session["claimed"] = True
        picked_char = session["character"]
        user_id = payload.user_id

        if user_id not in user_gacha_backpack:
            user_gacha_backpack[user_id] = []
        user_gacha_backpack[user_id].append(picked_char["name"])

        del active_rolls[payload.message_id]

        channel = bot.get_channel(payload.channel_id)
        if channel:
            user = await bot.fetch_user(user_id)
            await channel.send(f"🌟 **Character claimed!** {user.mention} added **{picked_char['name']}** ({picked_char['rarity']}) to their backpack!")

@bot.command()
async def backpack(ctx):
    user_id = ctx.author.id
    if user_id not in user_gacha_backpack or not user_gacha_backpack[user_id]:
        await ctx.send(f"🎒 {ctx.author.mention}, your backpack is empty! Use `!roll` to look for characters.")
        return

    inventory = user_gacha_backpack[user_id]
    summary = {}
    for item in inventory:
        summary[item] = summary.get(item, 0) + 1

    items_text = "\n".join([f"• **{name}** x{count}" for name, count in summary.items()])
    
    embed = discord.Embed(
        title=f"🎒 {ctx.author.name}'s Character Backpack",
        description=items_text,
        color=0x3498DB
    )
    await ctx.send(embed=embed)

@roll.error
async def roll_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Wait **{error.retry_after:.1f}** seconds before rolling again!")

# --- START CONFIGURATION ---
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    keep_alive() # Starts Flask web server right before launching the bot
    bot.run(TOKEN)
else:
    print("Bot Offline: No valid DISCORD_TOKEN was found.")
