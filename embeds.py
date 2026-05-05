import discord
from discord import app_commands

async def setup_embed_command(bot, REQUIRED_ROLE_ID, MAKS_BLUE):
    @bot.tree.command(name="embed", description="Wysyła spersonalizowany komunikat w ramce (Embed)")
    @app_commands.describe(
        tytul="Nagłówek wiadomości",
        opis="Treść (możesz oznaczać role używając <@&ID_ROLI>)",
        kolor="Kolor paska HEX (np. #ff0000 lub zostaw puste)"
    )
    async def create_embed(interaction: discord.Interaction, tytul: str, opis: str, kolor: str = None):
        # Sprawdzenie uprawnień
        if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
            return await interaction.response.send_message("❌ Brak uprawnień do używania tej komendy.", ephemeral=True)

        # Logika koloru
        if kolor:
            try:
                hex_str = kolor.replace("#", "")
                embed_color = int(hex_str, 16)
            except ValueError:
                return await interaction.response.send_message("❌ Błędny format koloru HEX!", ephemeral=True)
        else:
            embed_color = MAKS_BLUE

        # Obsługa formatowania:
        # 1. Zamiana \n na prawdziwe nowe linie
        # 2. Discord sam zamieni <@&ID> na nazwę roli w opisie
        format_opis = opis.replace("\\n", "\n")
        
        new_embed = discord.Embed(
            title=tytul,
            description=format_opis,
            color=embed_color
        )
        
        # Tutaj dodałem Twój znaczek:
        new_embed.set_footer(text=f"Wysłane przez: {interaction.user.display_name} • Made By Maks.R3ps")

        # Wysłanie potwierdzenia (widoczne tylko dla Ciebie)
        await interaction.response.send_message("✅ Embed wysłany!", ephemeral=True)
        
        # Wysłanie właściwego embeda na kanał
        await interaction.channel.send(embed=new_embed)
