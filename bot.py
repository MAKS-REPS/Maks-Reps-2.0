import discord
from discord import app_commands
from discord.ext import commands
import os

# --- KONFIGURACJA ---
WELCOME_CHANNEL_ID = 1457756805173084309
REQUIRED_ROLE_ID = 1457769309735485450 
ID_KATEGORII_TICKETOW = 0 # Tu wkleisz ID, które bot Ci poda
MAKS_BLUE = 0x3498db

intents = discord.Intents.all()

class TicketMenu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="DOSTĘP", description="Kliknij, aby uzyskać pomoc z dostępem", emoji="🔑"),
            discord.SelectOption(label="POMOC Z ZAMÓWIENIEM", description="Pomoc z Twoim zamówieniem", emoji="🛒"),
            discord.SelectOption(label="POMOC Z SHIPEM", description="Problemy z przesyłką/shippingiem", emoji="🚛"),
        ]
        super().__init__(placeholder="❌ Nie wybrano żadnej z kategorii", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(ID_KATEGORII_TICKETOW)
        admin_role = guild.get_role(REQUIRED_ROLE_ID)

        if not category:
            await interaction.response.send_message("❌ Błąd: ID Kategorii w kodzie jest błędne! Użyj komendy !id, aby je sprawdzić.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)
        }

        channel = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", category=category, overwrites=overwrites)
        
        embed = discord.Embed(title="🎫 MAKS REPS × TICKET", description=f"Witaj {interaction.user.mention}!\nOpisz swój problem.", color=MAKS_BLUE)
        await channel.send(content=f"{interaction.user.mention} | {admin_role.mention}", embed=embed)
        await interaction.response.send_message(f"✅ Otwarto ticket: {channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketMenu())

class MaksBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents) # Prefiks dla komendy !id

    async def setup_hook(self):
        self.add_view(TicketView())
        await self.tree.sync()

bot = MaksBot()

# --- NOWA KOMENDA DO SPRAWDZANIA ID ---
@bot.command()
async def id(ctx):
    # Sprawdza czy kanał jest w kategorii
    if ctx.channel.category:
        category_name = ctx.channel.category.name
        category_id = ctx.channel.category.id
        await ctx.send(f"📂 Jesteś w kategorii: **{category_name}**\n🆔 Jej ID to: `{category_id}`\n\nSkopiuj ten numer i wklej do kodu w miejsce `ID_KATEGORII_TICKETOW`.")
    else:
        await ctx.send("❌ Ten kanał nie należy do żadnej kategorii!")

# --- POWITANIA ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="👋 Maks Reps × WITAMY", color=MAKS_BLUE)
        embed.description = f"• 👶 × Witaj {member.mention} na **Maks Reps**\n• 👥 × Jesteś **{member.guild.member_count} osobą**!"
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# --- KOMENDA /PANEL ---
@bot.tree.command(name="panel", description="Wysyła panel ticketów")
async def panel(interaction: discord.Interaction):
    if interaction.user.get_role(REQUIRED_ROLE_ID) is None:
        await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)
        return
    embed = discord.Embed(title="🚨 MAKS REPS × CENTRUM POMOCY", description="Wybierz kategorię poniżej.", color=MAKS_BLUE)
    await interaction.response.send_message(embed=embed, view=TicketView())

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
