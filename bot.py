import discord
from discord.ext import commands
import requests
import urllib.parse
import os
import re

# --- KONFIGURACJA ---
TOKEN = os.getenv('DISCORD_TOKEN')
ALLOWED_CHANNEL_ID = 1457766095531278529 
BASE_SITE_URL = "https://maks-reps.github.io/Maks-Reps/"
API_URL = "https://api.xms4192.workers.dev/qc?url="

# Intents są kluczowe - muszą być włączone w Developer Portal!
intents = discord.Intents.all() 
bot = commands.Bot(command_prefix="!", intents=intents)

class QCView(discord.ui.View):
    def __init__(self, photos, original_url):
        super().__init__(timeout=None)
        self.photos = photos
        self.original_url = original_url
        self.current_page = 0
        
        encoded_url = urllib.parse.quote(original_url)
        full_url = f"{BASE_SITE_URL}?url={encoded_url}"
        self.add_item(discord.ui.Button(label="More QC!", style=discord.ButtonStyle.link, url=full_url))

    def create_embed(self):
        embed = discord.Embed(title="Maks Reps | Quality Checks", color=0xff0000)
        embed.set_image(url=self.photos[self.current_page])
        embed.set_footer(text=f"Zdjęcie {self.current_page + 1}/{len(self.photos)}")
        return embed

    @discord.ui.button(label="⬅️ Poprzednie", style=discord.ButtonStyle.gray)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Następne ➡️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.photos) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()

@bot.event
async def on_ready():
    print(f"✅ BOT STATUS: ONLINE")
    print(f"✅ ZALOGOWANO JAKO: {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.channel.id != ALLOWED_CHANNEL_ID: return

    urls = re.findall(r'(https?://\S+)', message.content)
    if not urls: return
    
    raw_url = urls[0]
    # Lista obsługiwanych platform
    if any(p in raw_url for p in ["weidian.com", "taobao.com", "1688.com", "kakobuy.com", "usfans.com", "allchinabuy.com"]):
        try:
            r = requests.get(f"{API_URL}{urllib.parse.quote(raw_url)}", timeout=10)
            data = r.json()
            
            photos = []
            def extract(obj):
                if isinstance(obj, str) and (obj.startswith("http") or obj.startswith("//")):
                    if any(ext in obj.lower() for ext in [".jpg", ".png", ".webp", ".jpeg"]):
                        photos.append("https:" + obj if obj.startswith("//") else obj)
                elif isinstance(obj, dict): [extract(v) for v in obj.values()]
                elif isinstance(obj, list): [extract(i) for i in obj]
            
            extract(data)
            photos = list(dict.fromkeys(photos))

            if photos:
                view = QCView(photos, raw_url)
                await message.reply(embed=view.create_embed(), view=view)
        except Exception as e:
            print(f"BŁĄD API: {e}")

# Railway wymaga czasami zbindowania portu, choć bot go nie używa
if __name__ == "__main__":
    if not TOKEN:
        print("❌ BŁĄD: Brak DISCORD_TOKEN w zmiennych środowiskowych!")
    else:
        bot.run(TOKEN)
