import discord
from discord import app_commands
from discord.ext import commands
import os

# --- IMPORTY TWOICH MODUŁÓW ---
from welcome import handle_welcome
from roles import RoleView
from tickets import TicketView
from giveaway import GiveawayView, parse_time, run_giveaway_logic

# --- KONFIGURACJA ---
WELCOME_CHANNEL_ID = 1457756805173084309
REQUIRED_ROLE_ID = 1457769309735485450 
MAKS_BLUE = 0x3498db

# ID RÓL DO PINGÓW (używane w RoleView)
ROLE_TIKTOK_ID = 1469838172916551775
ROLE_PROMOCJE_ID = 1457769670060019767

intents = discord.Intents.all()

class MaksBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # FIX: Przekazujemy ID ról do RoleView, aby uniknąć błędu TypeError
        self.add_view(RoleView(ROLE_TIKTOK_ID, ROLE_PROMOCJE_ID))
        
        # Rejestracja pozostałych widoków
        self.add_view(TicketView())
        self.add_view(GiveawayView())
        
        await self.tree.sync()
        print(f"✅ Bot zalogowany jako {self.user} i zsynchronizowany.")

bot = MaksBot()

@bot.event
async def on_ready():
    print(f"🚀 Wszystkie systemy (Welcome, Roles, Tickets, Giveaway) są gotowe!")

# --- POWITANIA ---
@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, MAKS_BLUE)

# --- KOMENDA /PANEL (TICKETY I ROLE) ---
@bot.tree.command(name="panel", description="Wybierz typ panelu do wysłania")
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety (Pomoc/Dostęp)", value="tickets"),
    app_commands.Choice(name="Role (Pingi)", value="roles")
])
async def panel(interaction: discord.Interaction, typ: str):
    # Sprawdzanie uprawnień (tylko osoby z rolą administratora/wymaganą)
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Brak uprawnień do tej komendy.", ephemeral=True)

    if typ == "tickets":
        embed = discord.Embed(
            title="🚨 MAKS REPS × CENTRUM POMOCY", 
            description="**Wybierz kategorię z menu poniżej, aby utworzyć zgłoszenie.**", 
            color=MAKS_BLUE
        )
        await interaction.response.send_message(embed=embed, view=TicketView())
    
    elif typ == "roles":
        embed = discord.Embed(
            title="☀️ MAKS REPS × WYBIERZ PINGI",
            description="🎁 **Ping Promocje**\n→ Otrzymuj powiadomienia o promocjach!\n\n🎬 **Ping TikTok**\n→ Otrzymuj powiadomienia z tiktoka!",
            color=discord.Color.red()
        )
        # Tutaj również przekazujemy ID przy wysyłaniu nowego panelu
        await interaction.response.send_message(embed=embed, view=RoleView(ROLE_TIKTOK_ID, ROLE_PROMOCJE_ID))

# --- KOMENDA /GIVCREATE (GIVEAWAY) ---
@bot.tree.command(name="givcreate", description="Tworzy nowy giveaway")
@app_commands.describe(
    tytul="Tytuł konkursu",
    opis="Nagroda i opis wymagań",
    czas="Czas trwania (np. 10m, 1h, 1d)",
    zwyciezcy="Liczba wygranych osób",
    kolor="Kolor paska HEX (np. #3498db)"
)
async def givcreate(interaction: discord.Interaction, tytul: str, opis: str, czas: str, zwyciezcy: int, kolor: str = "#3498db"):
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)

    sekundy = parse_time(czas)
    if not sekundy:
        return await interaction.response.send_message("❌ Błędny format czasu (użyj np. 1h, 30m).", ephemeral=True)

    await run_giveaway_logic(interaction, tytul, opis, sekundy, zwyciezcy, kolor, MAKS_BLUE)

# --- URUCHOMIENIE ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
