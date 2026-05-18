import discord
from discord import app_commands
from discord.ext import commands
import os
import random # Potrzebne do losowania w reroll

# --- IMPORTY TWOICH MODUŁÓW ---
from welcome import handle_welcome
from roles import RoleViewAll, RoleViewPromo, RoleViewTikTok
from tickets import TicketView
# ZAKTUALIZOWANY IMPORT (dodano giveaway_cache)
from giveaway import GiveawayView, parse_time, run_giveaway_logic, giveaway_cache 
from embeds import setup_embed_command
from moderation import setup_moderation
from verify import VerifyView, setup_verify
from antiscam import setup_antiscam

# --- KONFIGURACJA ---
WELCOME_CHANNEL_ID = 1457756805173084309
REQUIRED_ROLE_ID = 1457769309735485450 
VERIFY_ROLE_ID = 1457768582770331805
MAKS_BLUE = 0x3498db

ROLE_TIKTOK_ID = 1469838172916551775
ROLE_PROMOCJE_ID = 1457769670060019767

intents = discord.Intents.all()

class MaksBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # 1. Rejestracja widoków dla trwałości przycisków (Persistence)
        self.add_view(RoleViewAll(ROLE_TIKTOK_ID, ROLE_PROMOCJE_ID))
        self.add_view(RoleViewPromo(ROLE_PROMOCJE_ID))
        self.add_view(RoleViewTikTok(ROLE_TIKTOK_ID))
        self.add_view(TicketView())
        self.add_view(GiveawayView())
        self.add_view(VerifyView(VERIFY_ROLE_ID))
        
        # 2. Inicjalizacja komend i systemów modułowych
        # WAŻNE: Funkcja setup_embed_command teraz obsługuje opcję zdjęć
        await setup_embed_command(self, REQUIRED_ROLE_ID, MAKS_BLUE)
        await setup_moderation(self)
        await setup_verify(self)
        await setup_antiscam(self)
        
        # 3. Synchronizacja komend slash z Discordem
        await self.tree.sync()
        print(f"✅ Maks Reps 2.0: Wszystkie systemy (w tym Anti-Scam i Reroll) są online.")

bot = MaksBot()

@bot.event
async def on_ready():
    # Ustawienie statusu bota
    activity = discord.Activity(type=discord.ActivityType.watching, name="Maks.R3ps")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"🚀 Zalogowano jako: {bot.user}")

# --- POWITANIA ---
@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, MAKS_BLUE)

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
        return await interaction.response.send_message("❌ Brak uprawnień administracyjnych.", ephemeral=True)

    val = typ.value

    if val == "tickets":
        embed = discord.Embed(
            title="🚨 MAKS REPS × CENTRUM POMOCY", 
            description="**Wybierz kategorię z menu poniżej, aby utworzyć zgłoszenie.**", 
            color=MAKS_BLUE
        )
        embed.set_footer(text="Maks Reps 2.0")
        await interaction.response.send_message(embed=embed, view=TicketView())
    
    elif val == "roles_all":
        embed = discord.Embed(
            title="☀️ MAKS REPS × WYBIERZ PINGI",
            description="🎁 **Ping Promocje**\n→ Otrzymuj powiadomienia o promocjach!\n\n🎬 **Ping TikTok**\n→ Otrzymuj powiadomienia z tiktoka!",
            color=discord.Color.red()
        )
        embed.set_footer(text="Maks Reps 2.0")
        await interaction.response.send_message(embed=embed, view=RoleViewAll(ROLE_TIKTOK_ID, ROLE_PROMOCJE_ID))

    elif val == "roles_promo":
        embed = discord.Embed(
            title="☀️ MAKS.R3PS X PROMOCJE",
            description="🎁 **Ping Promocje**\n→ Otrzymuj powiadomienia o promocjach!",
            color=discord.Color.red()
        )
        embed.set_footer(text="Maks Reps 2.0")
        await interaction.response.send_message(embed=embed, view=RoleViewPromo(ROLE_PROMOCJE_ID))

    elif val == "roles_tiktok":
        embed = discord.Embed(
            title="☀️ MAKS.R3PS X FILMY",
            description="🎬 **Ping TikTok**\n→ Otrzymuj powiadomienia z tiktoka!",
            color=discord.Color.red()
        )
        embed.set_footer(text="Maks Reps 2.0")
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
        return await interaction.response.send_message("❌ Błędny format czasu (np. 10m, 1h, 1d).", ephemeral=True)

    await run_giveaway_logic(interaction, tytul, opis, sekundy, zwyciezcy, kolor, MAKS_BLUE)

# --- NOWA KOMENDA /GREROLL ---
@bot.tree.command(name="greroll", description="Losuje nowego zwycięzcę")
@app_commands.describe(message_id="Wklej ID wiadomości z zakończonym konkursem")
async def greroll(interaction: discord.Interaction, message_id: str):
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)

    try:
        msg_id = int(message_id)
    except ValueError:
        return await interaction.response.send_message("❌ Podaj poprawne ID wiadomości.", ephemeral=True)

    if msg_id not in giveaway_cache:
        return await interaction.response.send_message("❌ Nie znaleziono konkursu w pamięci.", ephemeral=True)

    data = giveaway_cache[msg_id]
    if not data["pool"]:
        return await interaction.response.send_message("❌ Brak uczestników do rozlosowania.", ephemeral=True)

    winner = random.choice(data["pool"])
    await interaction.response.send_message(f"🔄 **REROLL!** Nowy zwycięzca konkursu o **{data['tytul']}** to: <@{winner}>!")

# --- URUCHOMIENIE BOTA ---
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ BŁĄD: Nie znaleziono tokenu bota w zmiennych środowiskowych!")
