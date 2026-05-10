import discord
from discord import app_commands
from discord.ext import commands
import datetime

# --- KONFIGURACJA UPRAWNIEŃ ---
# ID ról, które mogą używać moderacji (Owner, Moderator, Support)
ALLOWED_ROLES = [1457769309735485450, 1457769440883118253, 1457779377092821196]

def has_mod_role(interaction: discord.Interaction):
    return any(role.id in ALLOWED_ROLES for role in interaction.user.roles)

class Moderation(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name="mod", description="Komendy moderacyjne")
        self.bot = bot

    async def check_hierarchy(self, interaction: discord.Interaction, target: discord.Member) -> bool:
        """Sprawdza, czy moderator ma prawo wykonać akcję na danym użytkowniku."""
        # 1. Nie można ukarać samego siebie
        if target.id == interaction.user.id:
            await interaction.response.send_message("❌ Nie możesz ukarać samego siebie!", ephemeral=True)
            return False
            
        # 2. Nie można ukarać właściciela serwera
        if target.id == interaction.guild.owner_id:
            await interaction.response.send_message("❌ Nie możesz ukarać właściciela serwera!", ephemeral=True)
            return False

        # 3. Sprawdzenie pozycji ról (Moderator musi być wyżej w hierarchii niż cel)
        if interaction.user.top_role.position <= target.top_role.position:
            await interaction.response.send_message("❌ Nie masz wystarczająco wysokiej rangi, aby ukarać tę osobę!", ephemeral=True)
            return False
            
        return True

    async def send_mod_embed(self, interaction: discord.Interaction, title: str, user: discord.Member, reason: str, duration: str = None):
        """Generuje i wysyła embed moderacyjny na wzór Twojego zdjęcia."""
        embed = discord.Embed(
            title=title,
            color=discord.Color.red(), # Czerwony pasek
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="👤 Użytkownik", value=f"{user.name}\n({user.id})", inline=False)
        embed.add_field(name="🛡️ Moderator", value=f"{interaction.user.name}", inline=False)
        
        if duration:
            embed.add_field(name="🕒 Czas", value=f"`{duration}`", inline=False)
            
        embed.add_field(name="📝 Powód", value=f"{reason}", inline=False)
        
        embed.set_thumbnail(url=user.display_avatar.url) # Miniaturka awatara
        embed.set_footer(text="Maks Reps 2.0") # Nowa stopka
        
        if not interaction.response.is_done():
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="ban", description="Banuje użytkownika")
    @app_commands.describe(uzytkownik="Użytkownik do zbanowania", powod="Powód bana")
    async def ban(self, interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak powodu"):
        if not has_mod_role(interaction):
            return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)
        
        if not await self.check_hierarchy(interaction, uzytkownik):
            return
        
        try:
            await uzytkownik.ban(reason=powod)
            await self.send_mod_embed(interaction, "🔨 Użytkownik został zbanowany", uzytkownik, powod)
        except Exception as e:
            await interaction.response.send_message(f"❌ Wystąpił błąd: {e}", ephemeral=True)

    @app_commands.command(name="kick", description="Wyrzuca użytkownika z serwera")
    async def kick(self, interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak powodu"):
        if not has_mod_role(interaction):
            return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)
        
        if not await self.check_hierarchy(interaction, uzytkownik):
            return
        
        try:
            await uzytkownik.kick(reason=powod)
            await self.send_mod_embed(interaction, "👢 Użytkownik został wyrzucony", uzytkownik, powod)
        except Exception as e:
            await interaction.response.send_message(f"❌ Wystąpił błąd: {e}", ephemeral=True)

    @app_commands.command(name="timeout", description="Mytuje użytkownika na określony czas")
    @app_commands.describe(minuty="Czas wyciszenia w minutach")
    async def timeout(self, interaction: discord.Interaction, uzytkownik: discord.Member, minuty: int, powod: str = "Brak powodu"):
        if not has_mod_role(interaction):
            return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)
        
        if not await self.check_hierarchy(interaction, uzytkownik):
            return
        
        try:
            duration = datetime.timedelta(minutes=minuty)
            await uzytkownik.timeout(duration, reason=powod)
            await self.send_mod_embed(interaction, "🔇 Użytkownik został wyciszony", uzytkownik, powod, f"{minuty}m")
        except Exception as e:
            await interaction.response.send_message(f"❌ Wystąpił błąd: {e}", ephemeral=True)

    @app_commands.command(name="clear", description="Usuwa wiadomości z kanału")
    async def clear(self, interaction: discord.Interaction, ilosc: int):
        if not has_mod_role(interaction):
            return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=ilosc)
        await interaction.followup.send(f"✅ Usunięto {len(deleted)} wiadomości.", ephemeral=True)

async def setup_moderation(bot: commands.Bot):
    bot.tree.add_command(Moderation(bot))
