import discord
from discord import app_commands
from discord.ext import commands
import os

# 1. Konfiguracja uprawnień (Intents)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True 

class MaksBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronizacja komend slash (/)
        await self.tree.sync()
        print("✅ Komendy Slash zsynchronizowane!")

bot = MaksBot()

# --- KONFIGURACJA ---
WELCOME_CHANNEL_ID = 1457756805173084309
REQUIRED_ROLE_ID = 1457769309735485450 # ID rangi, która może używać bota
MAKS_BLUE = 0x3498db

# --- SEKCJA 1: POWITANIA (Automatyczne) ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        count = member.guild.member_count
        embed = discord.Embed(
            title="👋 Maks Reps × WITAMY",
            description=f"• 👶 × Witaj {member.mention} na **Maks Reps**\n"
                        f"• 👥 × Jesteś **{count} osobą** na serwerze!\n"
                        f"• ✨ × Liczymy, że zostaniesz z nami na dłużej!",
            color=MAKS_BLUE
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# --- SEKCJA 2: GENERATOR EMBEDÓW (Tylko dla wybranej rangi) ---
@bot.tree.command(name="embed", description="Stwórz własną ramkę embed (tylko dla uprawnionych)")
@app_commands.describe(
    tytul="Nagłówek ramki",
    opis="Treść (użyj \\n dla nowej linii)",
    kolor="Wybierz: niebieski, czerwony, zielony, zloty"
)
async def create_embed(interaction: discord.Interaction, tytul: str, opis: str, kolor: str = "niebieski"):
    # Sprawdzanie czy użytkownik ma wymaganą rangę
    role = interaction.guild.get_role(REQUIRED_ROLE_ID)
    if role not in interaction.user.roles:
        await interaction.response.send_message(f"❌ Nie masz uprawnień! Musisz posiadać rangę {role.mention}, aby używać tej komendy.", ephemeral=True)
        return

    kolory = {
        "niebieski": discord.Color.blue(),
        "czerwony": discord.Color.red(),
        "zielony": discord.Color.green(),
        "zloty": discord.Color.gold()
    }
    
    wybrany_kolor = kolory.get(kolor.lower(), discord.Color.blue())

    embed = discord.Embed(
        title=tytul,
        description=opis.replace("\\n", "\n"),
        color=wybrany_kolor
    )
    
    # Wysyła embed na kanał, na którym wpisano komendę
    await interaction.response.send_message(embed=embed)

# --- URUCHOMIENIE ---
@bot.event
async def on_ready():
    print(f"---")
    print(f"✅ Bot {bot.user.name} działa poprawnie!")
    print(f"✅ Blokada rangi ID: {REQUIRED_ROLE_ID} aktywna.")
    print(f"---")

token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ BŁĄD: Brak tokenu DISCORD_TOKEN!")
