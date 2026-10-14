import os
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True # CRUCIAL: Gives bot permission to read heart reacts
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 🚀 HOW TO ADD PHOTOS: ---
# Change the "https://..." links below to real image URLs from Google or a Wiki!
# Make sure the links end in .jpg or .png
GUINEVERE_CHARACTERS = [
    # --- GODLY (Purple) ---
    {"name": "Princess Guinevere", "rarity": "🌌 Godly", "color": 0x9400D3, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 1},
    {"name": "Olivia Park (flashback)", "rarity": "🌌 Godly", "color": 0x9400D3, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 1},
    {"name": "Orville", "rarity": "🌌 Godly", "color": 0x9400D3, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 1},

    # --- LEGENDARY (Blue) ---
    {"name": "Kid Andi", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 3},
    {"name": "Kid Frankie", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 3},
    {"name": "Gwen", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 3},
    {"name": "Sir Arthur", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 3},
    {"name": "Olivia Park", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 3},
    {"name": "Krash", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 3},
    {"name": "Armend", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 3},

    # --- RARE (Pink/Blue) ---
    {"name": "Andi", "rarity": "⭐ Rare", "color": 0xFF69B4, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 8},
    {"name": "Frankie", "rarity": "⭐ Rare", "color": 0xFF69B4, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 8},
    {"name": "Sparky", "rarity": "⭐ Rare", "color": 0x00FFFF, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 8},
    {"name": "Patience", "rarity": "⭐ Rare", "color": 0xFF69B4, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 8},

    # --- COMMON (Red) ---
    {"name": "Space cat", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 20},
    {"name": "Space penguin", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 20},
    {"name": "Space tapir", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 20},
    {"name": "Star pups", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 20},
    {"name": "Nurse 1", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 20},
    {"name": "Nurse 2", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 20},
    {"name": "Nurse 3", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 20},
    {"name": "Reggie", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://share.google/APSwmbYoxajhJKNKh", "weight": 20}
]

user_gacha_backpack = {}
active_rolls = {} # Tracks active message IDs to stop double-claim/double-roll bugs

@bot.event
async def on_ready():
    print(f"Game Bot is online as {bot.user.name}")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def roll(ctx):
    weights = [char["weight"] for char in GUINEVERE_CHARACTERS]
    picked = random.choices(GUINEVERE_CHARACTERS, weights=weights, k=1)[0] # Fixes Issue #1

    embed = discord.Embed(
        title="✨ A CHARACTER APPEARED! ✨",
        description="React with ❤️ within 15 seconds to claim them!",
        color=picked['color']
    )
    embed.add_field(name="Character Spotted", value=f"**{picked['name']}**", inline=False)
    embed.add_field(name="Rarity Rank", value=picked['rarity'], inline=True)
    embed.set_image(url=picked['image'])

    # Send the card and immediately add the heart reaction starter
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("❤️")

    # Store this roll session in memory
    active_rolls[msg.id] = {"character": picked, "claimed": False}

# --- 2: THE HEART REACTION CLAIM FUNCTION ---
@bot.event
async def on_raw_reaction_add(payload):
    # Ignore reactions made by the bot itself
    if payload.user_id == bot.user.id:
        return

    # Check if this message was a valid roll active session
    if payload.message_id in active_rolls:
        session = active_rolls[payload.message_id]
        
        # Check if the emoji used is a heart, and ensure nobody has claimed it yet
        if str(payload.emoji) == "❤️" and not session["claimed"]:
            session["claimed"] = True # Locks it instantly so nobody else can steal it
            picked_char = session["character"]
            user_id = payload.user_id
            
            # Fetch user object to print their name
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(user_id)
            
            # Save to inventory
            if user_id not in user_gacha_backpack:
                user_gacha_backpack[user_id] = []
            user_gacha_backpack[user_id].append(picked_char['name'])

            channel = bot.get_channel(payload.channel_id)
            await channel.send(f"🎉 **{member.name}** reacted first and claimed **{picked_char['name']}**!")
            
            # Clean up memory
            del active_rolls[payload.message_id]

@roll.error
async def roll_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ **{ctx.author.name}**, please wait **{error.retry_after:.1f}** seconds to roll again.")

bot.run(os.environ['DISCORD_TOKEN'])
