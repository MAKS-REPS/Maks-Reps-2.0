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

intents = discord.Intents.all()

class MaksBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Rejestrujemy widoki (Persistent Views), aby przyciski i menu 
        # działały zawsze, nawet po restarcie bota.
        self.add_view(RoleView())
        self.add_view(TicketView())
        self.add_view(GiveawayView())
        
        # Synchronizacja komend slash (/)
        await self.tree.sync()
        print(f"✅ Zsynchronizowano komendy dla {self.user}")

bot = MaksBot()

@bot.event
async def on_ready():
    print(f"🚀 Bot {bot.user} jest online i gotowy do pracy!")

# --- POWITANIA ---
@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, MAKS_BLUE)

# --- KOMENDA /PANEL (TICKETY I ROLE) ---
@bot.tree.command(name="panel", description="Wysyła wybrany panel (Tickety lub Role)")
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety (Pomoc/Dostęp)", value="tickets"),
    app_commands.Choice(name="Role (Pingi)", value="roles")
])
async def panel(interaction: discord.Interaction, typ: str):
    # Sprawdzanie, czy użytkownik ma rolę administracyjną
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Nie masz uprawnień do wysyłania paneli.", ephemeral=True)

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
        await interaction.response.send_message(embed=embed, view=RoleView())

# --- KOMENDA /GIVCREATE (GIVEAWAY) ---
@bot.tree.command(name="givcreate", description="Tworzy nowy giveaway")
@app_commands.describe(
    tytul="Tytuł konkursu",
    opis="Opis wymagań i nagrody",
    czas="Czas trwania (np. 10m, 1h, 1d)",
    zwyciezcy="Liczba wygranych osób",
    kolor="Kolor paska w HEX (np. #3498db)"
)
async def givcreate(
    interaction: discord.Interaction, 
    tytul: str, 
    opis: str, 
    czas: str, 
    zwyciezcy: int, 
    kolor: str = "#3498db"
):
    # Sprawdzanie uprawnień
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Nie masz uprawnień do tworzenia giveawayów.", ephemeral=True)

    # Przeliczanie czasu
    sekundy = parse_time(czas)
    if not sekundy:
        return await interaction.response.send_message("❌ Błędny format czasu! Użyj np. 10m, 2h lub 1d.", ephemeral=True)

    # Wywołanie logiki z pliku giveaway.py
    await run_giveaway_logic(interaction, tytul, opis, sekundy, zwyciezcy, kolor, MAKS_BLUE)

# --- URUCHOMIENIE BOTA ---
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ BŁĄD: Nie znaleziono tokenu bota w zmiennych środowiskowych!")
