import discord
from discord.ext import commands
import os

# 1. Konfiguracja uprawnień (Intents)
# Musisz je również włączyć w Discord Developer Portal!
intents = discord.Intents.default()
intents.members = True          # Pozwala widzieć, gdy ktoś dołącza
intents.message_content = True  # Pozwala botowi czytać treść wiadomości

bot = commands.Bot(command_prefix="!", intents=intents)

# 2. ID kanału, na którym mają pojawiać się powitania
WELCOME_CHANNEL_ID = 1457756805173084309

@bot.event
async def on_ready():
    print(f'✅ Bot Maks Reps jest online jako {bot.user}')

@bot.event
async def on_member_join(member):
    # Znajdź kanał o podanym ID
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    
    # Jeśli kanał istnieje, wyślij powitanie
    if channel:
        # Pobierz aktualną liczbę osób na serwerze
        member_count = member.guild.member_count
        
        # Tworzenie Embedu (wiadomość z kolorowym paskiem)
        embed = discord.Embed(
            title="👋 Maks Reps × WITAMY",
            description="",
            color=0x3498db  # Jasny niebieski (taki jak na Twoim screenie)
        )
        
        # Treść powitania
        embed.add_field(
            name="", 
            value=(
                f"• 👶 × Witaj {member.mention} na **Maks Reps**\n"
                f"• 👥 × Jesteś **{member_count} osobą** na naszym serwerze!\n"
                f"• ✨ × Liczymy, że zostaniesz z nami na dłużej!"
            ),
            inline=False
        )
        
        # Ikonka osoby (Avatar dołączającego) po prawej stronie
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Wysyłanie wiadomości z oznaczeniem użytkownika
        await channel.send(f"{member.mention}", embed=embed)

# 3. Pobieranie tokenu ze zmiennych środowiskowych Railway
token = os.getenv('DISCORD_TOKEN')

if token:
    bot.run(token)
else:
    print("❌ BŁĄD: Nie znaleziono tokenu DISCORD_TOKEN. Dodaj go w zakładce Variables na Railway!")
