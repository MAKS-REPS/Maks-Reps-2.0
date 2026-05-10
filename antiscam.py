import discord
from discord.ext import commands
import re

# Rozszerzona lista zakazanych fraz
SCAM_KEYWORDS = [
    "free nitro", "discord-nitro", "steam-gift", "gift-card", 
    "giveaway-nitro", "dlscord", "nitro-free", "get-nitro",
    "check my bio", "check bio", "look at my bio" # Nowe frazy anty-scam
]

# ID kanału, na który trafią logi o usunięciu (ustaw ten, gdzie chcesz widzieć raporty)
LOGS_CHANNEL_ID = 1457756805173084309 

class AntiScam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignoruj wiadomości od botów i od Ciebie (Ownera)
        if message.author.bot or message.author.id == message.guild.owner_id:
            return

        # Sprawdzanie małych liter, aby ominąć próby ukrycia frazy (np. ChEcK mY BiO)
        content = message.content.lower()

        # 1. Wykrywanie linków zaproszeń (Discord Invites)
        invite_pattern = r"(discord\.gg/|discord\.com/invite/)"
        
        # 2. Sprawdzanie czy wiadomość zawiera zakazane słowa lub linki
        is_scam = any(word in content for word in SCAM_KEYWORDS)
        is_invite = re.search(invite_pattern, content)

        if is_scam or is_invite:
            try:
                # Pobranie treści przed usunięciem do logów
                saved_content = message.content
                await message.delete()
                
                # Krótkie ostrzeżenie dla użytkownika
                warn_msg = await message.channel.send(
                    f"⚠️ {message.author.mention}, Twoja wiadomość została usunięta automatycznie (Anty-Scam/Reklama)."
                )
                await warn_msg.delete(delay=5)

                # Wysyłanie szczegółowego logu dla administracji
                log_channel = self.bot.get_channel(LOGS_CHANNEL_ID)
                if log_channel:
                    embed = discord.Embed(
                        title="🚨 FILTR ANTY-SCAM",
                        description=f"Wykryto i usunięto wiadomość od {message.author.mention}",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Treść wiadomości:", value=f"```{saved_content}```", inline=False)
                    embed.add_field(name="Powód:", value="Użycie zakazanej frazy (np. scam/bio) lub linku do zaproszenia", inline=False)
                    embed.set_footer(text="Maks Reps 2.0")
                    await log_channel.send(embed=embed)

            except discord.Forbidden:
                # Jeśli bot nie ma uprawnień do usuwania wiadomości
                print(f"❌ BRAK UPRAWNIEŃ: Bot nie może usuwać wiadomości na kanale {message.channel.name}")

async def setup_antiscam(bot):
    await bot.add_cog(AntiScam(bot))
