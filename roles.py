import discord

class RoleView(discord.ui.View):
    def __init__(self, role_tiktok_id, role_promocje_id):
        # timeout=None sprawia, że przyciski są trwałe (persistent)
        super().__init__(timeout=None)
        self.role_tiktok_id = role_tiktok_id
        self.role_promocje_id = role_promocje_id

    async def toggle_role(self, interaction: discord.Interaction, role_id: int):
        role = interaction.guild.get_role(role_id)
        
        # Zabezpieczenie na wypadek, gdyby rola nie istniała
        if not role:
            return await interaction.response.send_message("❌ Nie znaleziono tej roli na serwerze.", ephemeral=True)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Usunięto rolę {role.mention}", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Nadano rolę {role.mention}", ephemeral=True)

    @discord.ui.button(label="Ping Promocje", style=discord.ButtonStyle.blurple, emoji="🎁", custom_id="role_promocje")
    async def promocje(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, self.role_promocje_id)

    @discord.ui.button(label="Ping TikTok", style=discord.ButtonStyle.gray, emoji="🎬", custom_id="role_tiktok")
    async def tiktok(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, self.role_tiktok_id)
