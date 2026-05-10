import discord

class BaseRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def toggle_role(self, interaction: discord.Interaction, role_id: int):
        role = interaction.guild.get_role(role_id)
        if not role:
            return await interaction.response.send_message("❌ Nie znaleziono roli.", ephemeral=True)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Usunięto rolę {role.mention}", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Nadano rolę {role.mention}", ephemeral=True)

class RoleViewAll(BaseRoleView):
    def __init__(self, role_tiktok_id, role_promocje_id):
        super().__init__()
        self.role_tiktok_id = role_tiktok_id
        self.role_promocje_id = role_promocje_id

    @discord.ui.button(label="Ping Promocje", style=discord.ButtonStyle.blurple, emoji="🎁", custom_id="role_promo_all")
    async def promocje(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, self.role_promocje_id)

    @discord.ui.button(label="Ping TikTok", style=discord.ButtonStyle.gray, emoji="🎬", custom_id="role_tiktok_all")
    async def tiktok(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, self.role_tiktok_id)

class RoleViewPromo(BaseRoleView):
    def __init__(self, role_promocje_id):
        super().__init__()
        self.role_promocje_id = role_promocje_id

    @discord.ui.button(label="Ping Promocje", style=discord.ButtonStyle.blurple, emoji="🎁", custom_id="role_promo_single")
    async def promocje(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, self.role_promocje_id)

class RoleViewTikTok(BaseRoleView):
    def __init__(self, role_tiktok_id):
        super().__init__()
        self.role_tiktok_id = role_tiktok_id

    @discord.ui.button(label="Ping TikTok", style=discord.ButtonStyle.gray, emoji="🎬", custom_id="role_tiktok_single")
    async def tiktok(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, self.role_tiktok_id)
