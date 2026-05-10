import discord
from discord import app_commands

class VerifyView(discord.ui.View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, emoji="✅", custom_id="verify_permanent")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(self.role_id)
        
        if not role:
            return await interaction.response.send_message("❌ Błąd: Nie odnaleziono roli weryfikacyjnej.", ephemeral=True)

        if role in interaction.user.roles:
            return await interaction.response.send_message("ℹ️ Masz już dostęp!", ephemeral=True)

        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Weryfikacja pomyślna! Witaj na **Maks.R3ps**.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Bot ma za niskie uprawnienia (rola bota musi być nad rolą użytkownika).", ephemeral=True)

async def setup_verify(bot):
    # Tworzymy grupę komend /verification
    verification_group = app_commands.Group(name="verification", description="Zarządzanie weryfikacją")

    @verification_group.command(name="panel", description="Wysyła panel weryfikacyjny na wybrany kanał")
    @app_commands.describe(kanal="Kanał, na którym ma się pojawić weryfikacja")
    async def panel(interaction: discord.Interaction, kanal: discord.TextChannel):
        # Sprawdzenie czy to Ty (Owner)
        if interaction.user.id != interaction.guild.owner_id:
            return await interaction.response.send_message("❌ Brak dostępu.", ephemeral=True)

        role_id = 1457768582770331805 # Twoja rola

        embed = discord.Embed(
            title="🛡️ SYSTEM WERYFIKACJI",
            description=(
                "Aby odblokować dostęp do reszty serwera **Maks.R3ps**, "
                "kliknij poniższy przycisk.\n\n"
                "*Przystępując do serwera, akceptujesz regulamin.*"
            ),
            color=0x2ecc71
        )
        embed.set_footer(text="Maks Reps 2.0")
        
        await kanal.send(embed=embed, view=VerifyView(role_id))
        await interaction.response.send_message(f"✅ Panel został wysłany na {kanal.mention}", ephemeral=True)

    bot.tree.add_command(verification_group)
