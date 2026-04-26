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
        # Rejestracja widoków, aby działały po restarcie bota
        self.add_view(RoleView(ROLE_TIKTOK_ID, ROLE_PROMOCJE_ID))
        self.add_view(TicketView())
        self.add_view(GiveawayView())
        
        await self.tree.sync()
        print(f"✅ Bot {self.user} gotowy. Komendy zsynchronizowane.")

bot = MaksBot()

@bot.event
async def on_ready():
    print(f"🚀 Systemy sprawne: Welcome, Roles, Tickets, Giveaway, Embeds.")

# --- POWITANIA ---
@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, MAKS_BLUE)

# --- NOWA KOMENDA /EMBED ---
@bot.tree.command(name="embed", description="Wysyła spersonalizowany komunikat w ramce (Embed)")
@app_commands.describe(
    tytul="Nagłówek wiadomości",
    opis="Treść wiadomości (użyj \\n dla nowej linii)",
    kolor="Kolor paska w formacie HEX (np. #ff0000 lub zostaw puste dla domyślnego)"
)
async def create_embed(interaction: discord.Interaction, tytul: str, opis: str, kolor: str = None):
    # Sprawdzenie uprawnień (tak samo jak w panelu i giveaway)
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Brak uprawnień do używania tej komendy.", ephemeral=True)

    # Logika koloru
    if kolor:
        try:
            # Zamiana HEX na int
            embed_color = int(kolor.replace("#", ""), 16)
        except ValueError:
            return await interaction.response.send_message("❌ Błędny format koloru HEX! Użyj np. #ff0000", ephemeral=True)
    else:
        embed_color = MAKS_BLUE

    # Tworzenie embeda
    # Zamiana \n wpisanego w komendzie na prawdziwy znak nowej linii
    format_opis = opis.replace("\\n", "\n")
    
    new_embed = discord.Embed(
        title=tytul,
        description=format_opis,
        color=embed_color
    )
    
    # Opcjonalnie: Stopka z informacją kto wysłał
    new_embed.set_footer(text=f"Wiadomość wysłana przez {interaction.user.display_name}")

    # Wysyłanie
    await interaction.response.send_message("✅ Embed wysłany!", ephemeral=True)
    await interaction.channel.send(embed=new_embed)

# --- KOMENDA /PANEL (TICKETY I ROLE) ---
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

# --- KOMENDA /GIVCREATE (GIVEAWAY) ---
@bot.tree.command(name="givcreate", description="Tworzy nowy, w pełni modyfikowalny giveaway")
@app_commands.describe(
    tytul="Wpisz tytuł (np. 7x 500CNY)",
    opis="Wpisz tutaj wszystkie zasady (użyj \\n dla nowej linii)",
    czas="Czas trwania (np. 1h, 30m, 1d)",
    zwyciezcy="Liczba wygranych osób",
    kolor="Kolor paska HEX (np. #3498db)"
)
async def givcreate(
    interaction: discord.Interaction, 
    tytul: str, 
    opis: str, 
    czas: str, 
    zwyciezcy: int, 
    kolor: str = "#3498db"
):
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Nie masz uprawnień do tworzenia konkursów.", ephemeral=True)

    sekundy = parse_time(czas)
    if not sekundy:
        return await interaction.response.send_message("❌ Błędny format czasu (użyj np. 1h, 30m, 1d).", ephemeral=True)

    await run_giveaway_logic(interaction, tytul, opis, sekundy, zwyciezcy, kolor, MAKS_BLUE)

# --- URUCHOMIENIE ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
