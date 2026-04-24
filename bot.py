import discord
from discord import app_commands
from discord.ext import commands
import os

# Importy Twoich plików:
from welcome import handle_welcome
from roles import RoleView
# (W podobny sposób można wyciągnąć tickety)

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
        # Rejestrujemy widoki z innych plików
        self.add_view(RoleView(ROLE_TIKTOK_ID, ROLE_PROMOCJE_ID))
        await self.tree.sync()

bot = MaksBot()

@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, MAKS_BLUE)

@bot.tree.command(name="panel", description="Wysyła wybrany panel")
async def panel(interaction: discord.Interaction, typ: str):
    # Logika sprawdzania uprawnień i wysyłania widoków...
    pass

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
