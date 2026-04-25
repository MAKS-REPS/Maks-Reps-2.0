import discord
from discord import app_commands
from discord.ext import commands
import os

# TWOJE DOTYCHCZASOWE IMPORTY
from welcome import handle_welcome
from roles import RoleView

# NOWE IMPORTY Z giveaway.py
from giveaway import GiveawayView, parse_time, run_giveaway_logic

# --- KONFIGURACJA ---
WELCOME_CHANNEL_ID = 1457756805173084309
REQUIRED_ROLE_ID = 1457769309735485450 
ROLE_TIKTOK_ID = 1469838172916551775
ROLE_PROMOCJE_ID = 1457769670060019767
MAKS_BLUE = 0x3498db

intents = discord.Intents.all()

class MaksBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Rejestracja widoków ról (Twój stary kod)
        self.add_view(RoleView(ROLE_TIKTOK_ID, ROLE_PROMOCJE_ID))
        
        # DODANE: Rejestracja widoku giveaway
        self.add_view(GiveawayView())
        
        await self.tree.sync()
        print(f"Zalogowano jako {self.user}")

bot = MaksBot()

@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, MAKS_BLUE)

@bot.tree.command(name="panel", description="Wysyła wybrany panel")
async def panel(interaction: discord.Interaction, typ: str):
    # Twoja stara logika panelu...
    pass

# --- NOWA KOMENDA GIVEAWAY ---
@bot.tree.command(name="givcreate", description="Tworzy nowy giveaway")
@app_commands.describe(
    tytul="Tytuł konkursu",
    opis="Opis wymagań i nagrody",
    czas="Czas trwania (np. 10m, 1h, 1d)",
    zwyciezcy="Liczba wygranych osób",
    kolor="Kolor paska w HEX (np. #5865F2)"
)
async def givcreate(
    interaction: discord.Interaction, 
    tytul: str, 
    opis: str, 
    czas: str, 
    zwyciezcy: int, 
    kolor: str = "#3498db"
):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Brak uprawnień!", ephemeral=True)

    sekundy = parse_time(czas)
    if not sekundy:
        return await interaction.response.send_message("Zły format czasu (np. 1h, 30m)!", ephemeral=True)

    # Odpalenie logiki z pliku giveaway.py
    await run_giveaway_logic(interaction, tytul, opis, sekundy, zwyciezcy, kolor, MAKS_BLUE)

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
