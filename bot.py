import discord
from discord.ext import commands
import os

# Konfiguracja intencji
intents = discord.Intents.all() # Włączamy wszystkie, żeby nie było problemów

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CHANNEL_ID = 1457756805173084309

@bot.event
async def on_ready():
    print(f'---')
    print(f'✅ BOT MAKS REPS DZIAŁA!')
    print(f'✅ Zalogowano jako: {bot.user.name}')
    print(f'---')

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    
    if channel:
        member_count = member.guild.member_count
        
        embed = discord.Embed(
            title="👋 Maks Reps × WITAMY",
            color=0x3498db # Kolor niebieski
        )
        
        embed.add_field(
            name="", 
            value=f"• 👶 × Witaj {member.mention} na **Maks Reps**\n"
                  f"• 👥 × Jesteś **{member_count} osobą** na naszym serwerze!\n"
                  f"• ✨ × Liczymy, że zostaniesz z nami na dłużej!",
            inline=False
        )
        
        # Pobieranie awatara użytkownika
        avatar_url = member.display_avatar.url
        embed.set_thumbnail(url=avatar_url)
        
        await channel.send(f"{member.mention}", embed=embed)
    else:
        print(f"❌ BŁĄD: Nie znaleziono kanału o ID {WELCOME_CHANNEL_ID}")

# Pobieranie tokenu
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ BŁĄD: Brak zmiennej DISCORD_TOKEN w Railway!")
