import discord
from discord.ext import commands
import requests
import urllib.parse
import os

# Konfiguracja
TOKEN = os.getenv('DISCORD_TOKEN')
# Upewnij się, że ten link prowadzi dokładnie do Twojej strony na GitHubie
BASE_SITE_URL = "https://maks-reps.github.io/Maks-Reps/"
API_URL = "https://api.xms4192.workers.dev/qc?url="

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class QCView(discord.ui.View):
    def __init__(self, photos, original_url):
        super().__init__(timeout=None)
        self.photos = photos
        self.original_url = original_url
        self.current_page = 0
        
        # Przycisk More QC! - generuje link, który Twoja strona odczyta przez init()
        encoded_url = urllib.parse.quote(original_url)
        full_url = f"{BASE_SITE_URL}?url={encoded_url}"
        self.add_item(discord.ui.Button(label="More QC!", style=discord.ButtonStyle.link, url=full_url))

    def create_embed(self):
        embed = discord.Embed(title="Maks Reps | QC Finder", color=0xff0000)
        embed.set_image(url=self.photos[self.current_page])
        embed.set_footer(text=f"Zdjęcie {self.current_page + 1}/{len(self.photos)}")
        return embed

    @discord.ui.button(label="⬅️ Poprzednie", style=discord.ButtonStyle.gray)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Następne ➡️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.photos) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    platforms = ["weidian.com", "taobao.com", "1688.com", "kakobuy.com", "usfans.com"]
    if any(p in message.content for p in platforms):
        raw_url = message.content.strip()
        try:
            r = requests.get(f"{API_URL}{urllib.parse.quote(raw_url)}")
            data = r.json()
            photos = []
            def extract(obj):
                if isinstance(obj, str) and (obj.startswith("http") or obj.startswith("//")):
                    if any(ext in obj.lower() for ext in [".jpg", ".png", ".webp"]):
                        photos.append("https:" + obj if obj.startswith("//") else obj)
                elif isinstance(obj, dict): [extract(v) for v in obj.values()]
                elif isinstance(obj, list): [extract(i) for i in obj]
            
            extract(data)
            photos = list(dict.fromkeys(photos))

            if photos:
                view = QCView(photos, raw_url)
                await message.reply(embed=view.create_embed(), view=view)
        except: pass

bot.run(TOKEN)
