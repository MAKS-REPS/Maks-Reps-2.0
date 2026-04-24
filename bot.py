import discord
from discord import app_commands
from discord.ext import commands
import os

# --- KONFIGURACJA ---
WELCOME_CHANNEL_ID = 1457756805173084309
REQUIRED_ROLE_ID = 1457769309735485450 
ID_KATEGORII_TICKETOW = 0  # Tu wpiszesz ID po użyciu !id
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

        if ID_KATEGORII_TICKETOW == 0 or category is None:
            await interaction.response.send_message("❌ Błąd: ID kategorii nie jest ustawione w kodzie! Użyj !id na kanale w kategorii.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)
        }

        channel = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", category=category, overwrites=overwrites)
        embed = discord.Embed(title="🎫 MAKS REPS × TICKET", description=f"Witaj {interaction.user.mention}!\nOpisz swój problem, a administracja Ci pomoże.", color=MAKS_BLUE)
        await channel.send(content=f"{interaction.user.mention} | {admin_role.mention}", embed=embed)
        await interaction.response.send_message(f"✅ Otwarto ticket: {channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketMenu())

class MaksBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(TicketView())
        await self.tree.sync()

bot = MaksBot()

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
async def id(ctx):
    if ctx.channel.category:
        await ctx.send(f"📂 Kategoria: **{ctx.channel.category.name}**\n🆔 ID: `{ctx.channel.category.id}`")
    else:
        await ctx.send("❌ Ten kanał nie jest w kategorii!")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="👋 Maks Reps × WITAMY", color=MAKS_BLUE)
        embed.description = f"• 👶 × Witaj {member.mention} na **Maks Reps**\n• 👥 × Jesteś **{member.guild.member_count} osobą**!"
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

@bot.tree.command(name="panel", description="Wysyła panel ticketów")
async def panel(interaction: discord.Interaction):
    role = interaction.guild.get_role(REQUIRED_ROLE_ID)
    if role not in interaction.user.roles:
        await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)
        return
    embed = discord.Embed(title="🚨 MAKS REPS × CENTRUM POMOCY", description="Wybierz kategorię z menu poniżej.", color=MAKS_BLUE)
    await interaction.response.send_message(embed=embed, view=TicketView())

token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ Brak tokenu!")
