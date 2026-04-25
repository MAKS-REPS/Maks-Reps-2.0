import discord
from discord import app_commands
from discord.ext import commands
import os

# --- KONFIGURACJA ---
WELCOME_CHANNEL_ID = 1457756805173084309
REQUIRED_ROLE_ID = 1457769309735485450 
ID_KATEGORII_TICKETOW = 1486842150661656767
MAKS_BLUE = 0x3498db

# ID RÓL DO PINGÓW
ROLE_TIKTOK_ID = 1469838172916551775
ROLE_PROMOCJE_ID = 1457769670060019767

intents = discord.Intents.all()

# --- SEKCJA 1: TICKETY ---
class TicketMenu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="POMOC Z ZAMÓWIENIEM", description="Kliknij, jeśli potrzebujesz pomocy z zamówieniem", emoji="🛒"),
            discord.SelectOption(label="PROBLEM Z SHIPPINGIEM", description="Kliknij, jeśli masz problem z shippingiem", emoji="🚛"),
            discord.SelectOption(label="PROBLEM Z BOTEM", description="Kliknij, aby zgłosić problem z botem", emoji="🤖"),
        ]
        super().__init__(
            placeholder="❌ Nie wybrano żadnej z kategorii", 
            min_values=1, 
            max_values=1, 
            options=options, 
            custom_id="persistent_ticket_select"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(ID_KATEGORII_TICKETOW)
        admin_role = guild.get_role(REQUIRED_ROLE_ID)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)
        }
        channel = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", category=category, overwrites=overwrites)
        
        embed = discord.Embed(
            title="🎫 MAKS REPS × TICKET", 
            description=f"Witaj {interaction.user.mention}!\nWybrałeś: **{self.values[0]}**.\nZaraz ktoś z administracji Ci pomoże.", 
            color=MAKS_BLUE
        )
        await channel.send(content=f"{interaction.user.mention} | {admin_role.mention}", embed=embed)
        await interaction.response.send_message(f"✅ Otwarto ticket: {channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketMenu())

# --- SEKCJA 2: AUTO-ROLE (PINGI) ---
class RoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ping Promocje", style=discord.ButtonStyle.blurple, emoji="🎁", custom_id="role_promocje")
    async def promocje_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_PROMOCJE_ID)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Usunięto rolę {role.mention}", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Nadano rolę {role.mention}", ephemeral=True)

    @discord.ui.button(label="Ping TikTok", style=discord.ButtonStyle.gray, emoji="🎬", custom_id="role_tiktok")
    async def tiktok_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_TIKTOK_ID)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Usunięto rolę {role.mention}", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Nadano rolę {role.mention}", ephemeral=True)

# --- BOT SETUP ---
class MaksBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(TicketView())
        self.add_view(RoleView())
        await self.tree.sync()

bot = MaksBot()

@bot.event
async def on_ready():
    print(f"✅ Bot Maks Reps online!")

# --- POWITANIA (MAKS REPS) ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        count = member.guild.member_count
        embed = discord.Embed(
            title="👋 Maks Reps × WITAMY",
            description=(
                f"• 🤱 × Witaj {member.mention} na **Maks Reps**\n"
                f"• 👥 × Jesteś **{count} osobą** na naszym serwerze!\n"
                f"• ✨ × Liczymy, że zostaniesz z nami na dłużej!"
            ),
            color=MAKS_BLUE
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# --- KOMENDA /PANEL ---
@bot.tree.command(name="panel", description="Wybierz typ panelu do wysłania")
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety (Pomoc)", value="tickets"),
    app_commands.Choice(name="Role (Pingi)", value="roles")
])
async def panel(interaction: discord.Interaction, typ: str):
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)
        return

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

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
