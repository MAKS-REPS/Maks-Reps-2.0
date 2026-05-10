import discord
from discord import app_commands
from discord.ext import commands

# --- KLASA BAZOWA DLA WIDOKÓW ---
class BaseRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def toggle_role(self, interaction: discord.Interaction, role_id: int):
        role = interaction.guild.get_role(role_id)
        
        if not role:
            return await interaction.response.send_message("❌ Nie znaleziono tej roli na serwerze.", ephemeral=True)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Usunięto rolę {role.mention}", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Nadano rolę {role.mention}", ephemeral=True)


# --- 1. WIDOK DLA WSZYSTKIEGO (POŁĄCZONY) ---
class WszystkoView(BaseRoleView):
    def __init__(self, role_tiktok_id: int, role_promocje_id: int):
        super().__init__()
        self.role_tiktok_id = role_tiktok_id
        self.role_promocje_id = role_promocje_id

    @discord.ui.button(label="Ping Promocje", style=discord.ButtonStyle.blurple, emoji="🎁", custom_id="role_promocje_all")
    async def promocje(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, self.role_promocje_id)

    @discord.ui.button(label="Ping TikTok", style=discord.ButtonStyle.gray, emoji="🎬", custom_id="role_tiktok_all")
    async def tiktok(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, self.role_tiktok_id)


# --- 2. WIDOK TYLKO DLA PROMOCJI ---
class PromocjeView(BaseRoleView):
    def __init__(self, role_promocje_id: int):
        super().__init__()
        self.role_promocje_id = role_promocje_id

    @discord.ui.button(label="Ping Promocje", style=discord.ButtonStyle.blurple, emoji="🎁", custom_id="role_promocje_single")
    async def promocje(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, self.role_promocje_id)


# --- 3. WIDOK TYLKO DLA TIKTOKA ---
class TikTokView(BaseRoleView):
    def __init__(self, role_tiktok_id: int):
        super().__init__()
        self.role_tiktok_id = role_tiktok_id

    @discord.ui.button(label="Ping TikTok", style=discord.ButtonStyle.gray, emoji="🎬", custom_id="role_tiktok_single")
    async def tiktok(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, self.role_tiktok_id)


# --- KOMENDA /PANEL ---
@app_commands.command(name="panel", description="Wysyła panel z przyciskami do wyboru ról")
@app_commands.choices(typ=[
    app_commands.Choice(name="Wszystko (Promocje + Filmy)", value="wszystko"),
    app_commands.Choice(name="Tylko Promocje", value="promocje"),
    app_commands.Choice(name="Tylko Filmy (TikTok)", value="filmy")
])
async def panel(interaction: discord.Interaction, typ: app_commands.Choice[str]):
    ROLE_PROMOCJE_ID = 111111111111111111  # Zmień na swoje ID
    ROLE_TIKTOK_ID = 222222222222222222    # Zmień na swoje ID

    embed_color = discord.Color.red()

    if typ.value == "wszystko":
        embed = discord.Embed(
            title="☀️ MAKS.R3PS × WYBIERZ PINGI",
            description="**🎁 Ping Promocje**\n→ Otrzymuj powiadomienia o promocjach!\n\n**🎬 Ping TikTok**\n→ Otrzymuj powiadomienia z tiktoka!",
            color=embed_color
        )
        view = WszystkoView(role_tiktok_id=ROLE_TIKTOK_ID, role_promocje_id=ROLE_PROMOCJE_ID)
        await interaction.response.send_message(embed=embed, view=view)

    elif typ.value == "promocje":
        embed = discord.Embed(
            title="☀️ MAKS.R3PS × PROMOCJE",
            description="**🎁 Ping Promocje**\n→ Otrzymuj powiadomienia o promocjach!",
            color=embed_color
        )
        view = PromocjeView(role_promocje_id=ROLE_PROMOCJE_ID)
        await interaction.response.send_message(embed=embed, view=view)

    elif typ.value == "filmy":
        embed = discord.Embed(
            title="☀️ MAKS.R3PS × FILMY",
            description="**🎬 Ping TikTok**\n→ Otrzymuj powiadomienia z tiktoka!",
            color=embed_color
        )
        view = TikTokView(role_tiktok_id=ROLE_TIKTOK_ID)
        await interaction.response.send_message(embed=embed, view=view)
