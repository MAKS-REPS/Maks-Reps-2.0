import discord
from discord import app_commands
from discord.ext import commands
import os

# --- IMPORTY TWOICH MODUŁÓW ---
from welcome import handle_welcome
from roles import RoleView
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
        # Rejestracja widoków dla trwałości (persistent views)
        self.add_view(RoleView(ROLE_TIKTOK_ID, ROLE_PROMOCJE_ID))
        self.add_view(TicketView())
        self.add_view(GiveawayView())
        
        # Inicjalizacja zewnętrznych komend
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

# --- KOMENDA /ID (NOWA) ---
@bot.tree.command(name="id", description="Pobiera ID wskazanego kanału, roli lub użytkownika")
@app_commands.describe(
    kanal="Wybierz kanał, którego ID chcesz uzyskać",
    rola="Wybierz rolę, której ID chcesz uzyskać",
    uzytkownik="Wybierz osobę, której ID chcesz uzyskać"
)
async def get_id(
    interaction: discord.Interaction, 
    kanal: discord.abc.GuildChannel = None, 
    rola: discord.Role = None, 
    uzytkownik: discord.Member = None
):
    # Sprawdzenie uprawnień
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)

    if kanal:
        await interaction.response.send_message(f"🆔 ID kanału **{kanal.name}**: `{kanal.id}`", ephemeral=True)
    elif rola:
        await interaction.response.send_message(f"🆔 ID roli **{rola.name}**: `{rola.id}`", ephemeral=True)
    elif uzytkownik:
        await interaction.response.send_message(f"🆔 ID użytkownika **{uzytkownik.name}**: `{uzytkownik.id}`", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Musisz wybrać jedną z opcji!", ephemeral=True)

# --- KOMENDA /PANEL ---
@bot.tree.command(name="panel", description="Wybierz typ panelu do wysłania")
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety (Pomoc/Dostęp)", value="tickets"),
    app_commands.Choice(name="Role (Pingi)", value="roles")
])
async def panel(interaction: discord.Interaction, typ: str):
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)

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
        await interaction.response.send_message(embed=embed, view=RoleView(ROLE_TIKTOK_ID, ROLE_PROMOCJE_ID))

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
