import os
import random
import discord
from discord.ext import commands

# The complete list with your exact fractional probability odds ('weight') configured
GUINEVERE_CHARACTERS = [
    # --- GODLY (Purple) - 1/22 chance each ---
    {"name": "Princess Guinevere", "rarity": "🌌 Godly", "color": 0x9400D3, "image": "https://placehold.co", "weight": 1},
    {"name": "Olivia Park (flashback)", "rarity": "🌌 Godly", "color": 0x9400D3, "image": "https://placehold.co", "weight": 1},
    {"name": "Orville", "rarity": "🌌 Godly", "color": 0x9400D3, "image": "https://placehold.co", "weight": 1},

    # --- LEGENDARY (Blue) - 3/22 chance each ---
    {"name": "Kid Andi", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://placehold.co", "weight": 3},
    {"name": "Kid Frankie", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://placehold.co", "weight": 3},
    {"name": "Gwen", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://placehold.co", "weight": 3},
    {"name": "Sir Arthur", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://placehold.co", "weight": 3},
    {"name": "Olivia Park", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://placehold.co", "weight": 3},
    {"name": "Krash", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://placehold.co", "weight": 3},
    {"name": "Armend", "rarity": "👑 Legendary", "color": 0x00FFFF, "image": "https://placehold.co", "weight": 3},

    # --- RARE (Pink/Blue) - 8/22 chance each ---
    {"name": "Andi", "rarity": "⭐ Rare", "color": 0xFF69B4, "image": "https://placehold.co", "weight": 8},
    {"name": "Frankie", "rarity": "⭐ Rare", "color": 0xFF69B4, "image": "https://placehold.co", "weight": 8},
    {"name": "Sparky", "rarity": "⭐ Rare", "color": 0x00FFFF, "image": "https://placehold.co", "weight": 8},
    {"name": "Patience", "rarity": "⭐ Rare", "color": 0xFF69B4, "image": "https://placehold.co", "weight": 8},

    # --- COMMON (Red) - 20/22 chance each ---
    {"name": "Space cat", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://placehold.co", "weight": 20},
    {"name": "Space penguin", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://placehold.co", "weight": 20},
    {"name": "Space tapir", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://placehold.co", "weight": 20},
    {"name": "Star pups", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://placehold.co", "weight": 20},
    {"name": "Nurse 1", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://placehold.co", "weight": 20},
    {"name": "Nurse 2", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://placehold.co", "weight": 20},
    {"name": "Nurse 3", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://placehold.co", "weight": 20},
    {"name": "Reggie", "rarity": "⚪ Common", "color": 0xFF0000, "image": "https://placehold.co", "weight": 20}
]

user_gacha_backpack = {}

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def roll(ctx):
    user_id = ctx.author.id

    # 1. Pull the fractional weights from our character data list
    weights = [char["weight"] for char in GUINEVERE_CHARACTERS]
    
    # 2. Spin the wheel using your custom relative ratio setup
    # random.choices returns a list, so we extract the single item with [0]
    picked = random.choices(GUINEVERE_CHARACTERS, weights=weights, k=1)[0]

    if user_id not in user_gacha_backpack:
        user_gacha_backpack[user_id] = []
    user_gacha_backpack[user_id].append(picked['name'])

    embed = discord.Embed(
        title="✨ GACHA ROLL SUCCESS! ✨",
        description=f"**{ctx.author.name}** rolled the wheel of Park Planet!",
        color=picked['color']
    )
    embed.add_field(name="Character Obtained", value=f"**{picked['name']}**", inline=False)
    embed.add_field(name="Rarity Rank", value=picked['rarity'], inline=True)
    
    embed.set_image(url=picked['image'])
    embed.set_footer(text="Keep rolling to collect all characters!")

    await ctx.send(embed=embed)

@roll.error
async def roll_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ **{ctx.author.name}**, you're rolling too fast! Please wait **{error.retry_after:.1f}** seconds.")
