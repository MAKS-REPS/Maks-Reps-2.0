import discord
from discord import app_commands
from discord.ext import commands
import os

# --- IMPORTY TWOICH MODUŁÓW ---
from welcome import handle_welcome
# Importujemy wszystkie 3 klasy widoków z roles.py
from roles import RoleViewAll, RoleViewPromo, RoleViewTikTok
from tickets import TicketView
from giveaway import GiveawayView, parse_time, run_giveaway_logic
from embeds import setup_embed_command

# --- KONFIGURACJA ---
WELCOME_CHANNEL_ID = 1457756805173084309
REQUIRED_ROLE_ID = 1457769309735485450 
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
        
        self.add_view(TicketView())
        self.add_view(GiveawayView())
        
        # INICJALIZACJA KOMENDY EMBED
        await setup_embed_command(self, REQUIRED_ROLE_ID, MAKS_BLUE)
        
        await self.tree.sync()
        print(f"✅ Bot {self.user} gotowy. Wszystkie systemy załadowane.")

bot = MaksBot()

@bot.event
async def on_ready():
    print(f"🚀 Zalogowano jako: {bot.user}")

# --- POWITANIA ---
@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, MAKS_BLUE)

# --- KOMENDA /PANEL ---
@bot.tree.command(name="panel", description="Wybierz typ panelu do wysłania")
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety (Pomoc/Dostęp)", value="tickets"),
    app_commands.Choice(name="Role: Wszystko", value="roles_all"),
    app_commands.Choice(name="Role: Tylko Promocje", value="roles_promo"),
    app_commands.Choice(name="Role: Tylko Filmy (TikTok)", value="roles_tiktok")
])
async def panel(interaction: discord.Interaction, typ: app_commands.Choice[str]):
    # Sprawdzanie uprawnień
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

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
