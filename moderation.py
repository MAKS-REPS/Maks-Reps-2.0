import discord
from discord import app_commands
from discord.ext import commands
import datetime

# --- KONFIGURACJA UPRAWNIEŃ ---
ALLOWED_ROLES = [1457769309735485450, 1457769440883118253, 1457779377092821196]

def has_mod_role(interaction: discord.Interaction):
    return any(role.id in ALLOWED_ROLES for role in interaction.user.roles)

# --- WIDOKI Z PRZYCISKAMI ---

class UnbanView(discord.ui.View):
    def __init__(self, user_id: int, user_name: str):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.user_name = user_name

    @discord.ui.button(label="Odbanuj", style=discord.ButtonStyle.green, emoji="🔓")
    async def unban_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_mod_role(interaction):
            return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)
        
        await interaction.guild.unban(discord.Object(id=self.user_id))
        await interaction.response.edit_message(content=f"✅ Użytkownik **{self.user_name}** został odbanowany.", embed=None, view=None)

class UntimeoutView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=60)
        self.member = member

    @discord.ui.button(label="Usuń Timeout", style=discord.ButtonStyle.green, emoji="🔊")
    async def untimeout_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_mod_role(interaction):
            return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)
        
        await self.member.timeout(None)
        await interaction.response.edit_message(content=f"✅ Timeout dla **{self.member.name}** został usunięty.", embed=None, view=None)

# --- KLASA MODERACJI ---

class Moderation(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name="mod", description="Komendy moderacyjne")
        self.bot = bot

    async def check_hierarchy(self, interaction: discord.Interaction, target: discord.Member) -> bool:
        if target.id == interaction.user.id:
            await interaction.response.send_message("❌ Nie możesz ukarać samego siebie!", ephemeral=True)
            return False
        if target.id == interaction.guild.owner_id:
            await interaction.response.send_message("❌ Nie możesz ukarać właściciela!", ephemeral=True)
            return False
        if interaction.user.top_role.position <= target.top_role.position:
            await interaction.response.send_message("❌ Masz zbyt niską rangę!", ephemeral=True)
            return False
        return True

    # --- KOMENDY KARANIA ---

    @app_commands.command(name="ban", description="Banuje użytkownika")
    async def ban(self, interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak powodu"):
        if not has_mod_role(interaction) or not await self.check_hierarchy(interaction, uzytkownik): return
        await uzytkownik.ban(reason=powod)
        await self.send_mod_embed(interaction, "🔨 Ban", uzytkownik, powod)

    @app_commands.command(name="timeout", description="Wycisza użytkownika")
    async def timeout(self, interaction: discord.Interaction, uzytkownik: discord.Member, minuty: int, powod: str = "Brak powodu"):
        if not has_mod_role(interaction) or not await self.check_hierarchy(interaction, uzytkownik): return
        await uzytkownik.timeout(datetime.timedelta(minutes=minuty), reason=powod)
        await self.send_mod_embed(interaction, "🔇 Timeout", uzytkownik, powod, f"{minuty}m")

    # --- KOMENDY SPRAWDZANIA (CHECK) ---

    @app_commands.command(name="check", description="Sprawdza aktywne kary")
    @app_commands.choices(typ=[
        app_commands.Choice(name="Bany", value="ban"),
        app_commands.Choice(name="Timeouty", value="timeout")
    ])
    async def check(self, interaction: discord.Interaction, typ: str):
        if not has_mod_role(interaction):
            return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)

        if typ == "ban":
            bans = [entry async for entry in interaction.guild.bans(limit=10)]
            if not bans:
                return await interaction.response.send_message("Czysto! Nikt nie ma bana.", ephemeral=True)
            
            await interaction.response.send_message("Ostatnie 10 banów:", ephemeral=True)
            for entry in bans:
                view = UnbanView(entry.user.id, entry.user.name)
                await interaction.followup.send(f"👤 **{entry.user.name}** (ID: {entry.user.id})\n📝 Powód: {entry.reason}", view=view, ephemeral=True)

        elif typ == "timeout":
            members = [m for m in interaction.guild.members if m.is_timed_out()]
            if not members:
                return await interaction.response.send_message("Nikt nie ma obecnie timeouta.", ephemeral=True)
            
            await interaction.response.send_message("Osoby z timeoutem:", ephemeral=True)
            for m in members:
                view = UntimeoutView(m)
                time_left = m.timed_out_until - discord.utils.utcnow()
                minuty = int(time_left.total_seconds() // 60)
                await interaction.followup.send(f"👤 **{m.name}**\n⏳ Pozostało: ok. {minuty} min", view=view, ephemeral=True)

    # --- POMOCNICZE ---

    async def send_mod_embed(self, interaction: discord.Interaction, title: str, user: discord.Member, reason: str, duration: str = None):
        embed = discord.Embed(title=title, color=discord.Color.red(), timestamp=datetime.datetime.now())
        embed.add_field(name="👤 Użytkownik", value=f"{user.name} ({user.id})", inline=False)
        embed.add_field(name="🛡️ Moderator", value=f"{interaction.user.name}", inline=False)
        if duration: embed.add_field(name="🕒 Czas", value=f"`{duration}`", inline=False)
        embed.add_field(name="📝 Powód", value=f"{reason}", inline=False)
        embed.set_footer(text="Maks Reps 2.0")
        if not interaction.response.is_done(): await interaction.response.send_message(embed=embed)
        else: await interaction.followup.send(embed=embed)

async def setup_moderation(bot: commands.Bot):
    bot.tree.add_command(Moderation(bot))
