import discord
from discord import app_commands
from discord.ext import commands
import datetime

# --- KONFIGURACJA UPRAWNIEŃ ---
ALLOWED_ROLES = [1457769309735485450, 1457769440883118253, 1457779377092821196]

def has_mod_role(interaction: discord.Interaction):
    return any(role.id in ALLOWED_ROLES for role in interaction.user.roles)

class Moderation(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name="mod", description="Komendy moderacyjne")
        self.bot = bot

    async def send_mod_embed(self, interaction: discord.Interaction, title: str, user: discord.Member, reason: str, duration: str = None):
        embed = discord.Embed(
            title=title,
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="👤 Użytkownik", value=f"{user.name}\n({user.id})", inline=False)
        embed.add_field(name="🛡️ Moderator", value=f"{interaction.user.name}", inline=False)
        
        if duration:
            embed.add_field(name="🕒 Czas", value=f"`{duration}`", inline=False)
            
        embed.add_field(name="📝 Powód", value=f"{reason}", inline=False)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Maks Reps Bot")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="Banuje użytkownika")
    @app_commands.describe(uzytkownik="Kogo zbanować", powod="Dlaczego")
    async def ban(self, interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak powodu"):
        if not has_mod_role(interaction):
            return await interaction.response.send_message("❌ Nie masz uprawnień do tej komendy.", ephemeral=True)
        
        try:
            await uzytkownik.ban(reason=powod)
            await self.send_mod_embed(interaction, "🔨 Użytkownik został zbanowany", uzytkownik, powod)
        except Exception as e:
            await interaction.response.send_message(f"❌ Błąd: {e}", ephemeral=True)

    @app_commands.command(name="kick", description="Wyrzuca użytkownika")
    async def kick(self, interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak powodu"):
        if not has_mod_role(interaction):
            return await interaction.response.send_message("❌ Nie masz uprawnień do tej komendy.", ephemeral=True)
        
        try:
            await uzytkownik.kick(reason=powod)
            await self.send_mod_embed(interaction, "👢 Użytkownik został wyrzucony", uzytkownik, powod)
        except Exception as e:
            await interaction.response.send_message(f"❌ Błąd: {e}", ephemeral=True)

    @app_commands.command(name="timeout", description="Wycisza użytkownika (timeout)")
    @app_commands.describe(uzytkownik="Kogo wyciszyć", minuty="Na ile minut", powod="Dlaczego")
    async def timeout(self, interaction: discord.Interaction, uzytkownik: discord.Member, minuty: int, powod: str = "Brak powodu"):
        if not has_mod_role(interaction):
            return await interaction.response.send_message("❌ Nie masz uprawnień do tej komendy.", ephemeral=True)
        
        try:
            duration = datetime.timedelta(minutes=minuty)
            await uzytkownik.timeout(duration, reason=powod)
            await self.send_mod_embed(interaction, "🔇 Użytkownik został wyciszony", uzytkownik, powod, f"{minuty}m")
        except Exception as e:
            await interaction.response.send_message(f"❌ Błąd: {e}", ephemeral=True)

    @app_commands.command(name="clear", description="Usuwa określoną liczbę wiadomości")
    async def clear(self, interaction: discord.Interaction, ilosc: int):
        if not has_mod_role(interaction):
            return await interaction.response.send_message("❌ Nie masz uprawnień.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=ilosc)
        await interaction.followup.send(f"✅ Usunięto {len(deleted)} wiadomości.", ephemeral=True)

async def setup_moderation(bot: commands.Bot):
    bot.tree.add_command(Moderation(bot))
