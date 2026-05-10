import discord
from discord import app_commands
from discord.ext import commands
import os

# --- IMPORTY TWOICH MODUŁÓW ---
from welcome import handle_welcome
from dm import send_welcome_dm
from roles import RoleViewAll, RoleViewPromo, RoleViewTikTok
from tickets import TicketView
from giveaway import GiveawayView, parse_time, run_giveaway_logic
from embeds import setup_embed_command
from moderation import setup_moderation
from verify import VerifyView, setup_verify  # Import systemu weryfikacji

# --- KONFIGURACJA ---
WELCOME_CHANNEL_ID = 1457756805173084309
REQUIRED_ROLE_ID = 1457769309735485450 
VERIFY_ROLE_ID = 1457768582770331805 # Twoja rola weryfikacyjna
MAKS_BLUE = 0x3498db

ROLE_TIKTOK_ID = 1469838172916551775
ROLE_PROMOCJE_ID = 1457769670060019767

intents = discord.Intents.all()

class MaksBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Rejestracja widoków dla trwałości przycisków (Persistence)
        self.add_view(RoleViewAll(ROLE_TIKTOK_ID, ROLE_PROMOCJE_ID))
        self.add_view(RoleViewPromo(ROLE_PROMOCJE_ID))
        self.add_view(RoleViewTikTok(ROLE_TIKTOK_ID))
        
        # Widoki systemowe
        self.add_view(TicketView())
        self.add_view(GiveawayView())
        self.add_view(VerifyView(VERIFY_ROLE_ID)) # Rejestracja przycisku weryfikacji
        
        # Inicjalizacja komend modułowych
        await setup_embed_command(self, REQUIRED_ROLE_ID, MAKS_BLUE)
        await setup_moderation(self)
        await setup_verify(self) # Rejestracja grupy /verification
        
        # Synchronizacja komend slash
        await self.tree.sync()
        print(f"✅ Bot {self.user} gotowy. Wszystkie systemy załadowane.")

bot = MaksBot()

@bot.event
async def on_ready():
    print(f"🚀 Zalogowano jako: {bot.user}")

# --- POWITANIA ---
@bot.event
async def on_member_join(member):
    # 1. Powitanie na kanale serwera
    await handle_welcome(member, WELCOME_CHANNEL_ID, MAKS_BLUE)
    
    # 2. Wiadomość prywatna (DM) z linkami
    await send_welcome_dm(member, MAKS_BLUE)

# --- KOMENDA /PANEL (ROLE I TICKETY) ---
@bot.tree.command(name="panel", description="Wybierz typ panelu do wysłania")
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety (Pomoc/Dostęp)", value="tickets"),
    app_commands.Choice(name="Role: Wszystko", value="roles_all"),
    app_commands.Choice(name="Role: Tylko Promocje", value="roles_promo"),
    app_commands.Choice(name="Role: Tylko Filmy (TikTok)", value="roles_tiktok")
])
async def panel(interaction: discord.Interaction, typ: app_commands.Choice[str]):
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)

    val = typ.value

    if val == "tickets":
        embed = discord.Embed(
            title="🚨 MAKS REPS × CENTRUM POMOCY", 
            description="**Wybierz kategorię z menu poniżej, aby utworzyć zgłoszenie.**", 
            color=MAKS_BLUE
        )
        await interaction.response.send_message(embed=embed, view=TicketView())
    
    elif val == "roles_all":
        embed = discord.Embed(
            title="☀️ MAKS REPS × WYBIERZ PINGI",
            description="🎁 **Ping Promocje**\n→ Otrzymuj powiadomienia o promocjach!\n\n🎬 **Ping TikTok**\n→ Otrzymuj powiadomienia z tiktoka!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=RoleViewAll(ROLE_TIKTOK_ID, ROLE_PROMOCJE_ID))

    elif val == "roles_promo":
        embed = discord.Embed(
            title="☀️ MAKS.R3PS X PROMOCJE",
            description="🎁 **Ping Promocje**\n→ Otrzymuj powiadomienia o promocjach!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=RoleViewPromo(ROLE_PROMOCJE_ID))

    elif val == "roles_tiktok":
        embed = discord.Embed(
            title="☀️ MAKS.R3PS X FILMY",
            description="🎬 **Ping TikTok**\n→ Otrzymuj powiadomienia z tiktoka!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=RoleViewTikTok(ROLE_TIKTOK_ID))

# --- KOMENDA /GIVCREATE ---
@bot.tree.command(name="givcreate", description="Tworzy nowy giveaway")
@app_commands.describe(
    tytul="Wpisz tytuł", opis="Wpisz zasady", czas="Np. 1h", zwyciezcy="Liczba osób", kolor="HEX"
)
async def givcreate(interaction: discord.Interaction, tytul: str, opis: str, czas: str, zwyciezcy: int, kolor: str = "#3498db"):
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)

    sekundy = parse_time(czas)
    if not sekundy:
        return await interaction.response.send_message("❌ Błędny format czasu.", ephemeral=True)

    await run_giveaway_logic(interaction, tytul, opis, sekundy, zwyciezcy, kolor, MAKS_BLUE)

# --- URUCHOMIENIE ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
