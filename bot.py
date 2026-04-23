# --- POPRAWKA DLA PYTHON 3.13 ---
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    import sys
    sys.modules["audioop"] = audioop

import discord
from discord.ext import commands
import re
import os
import requests
from urllib.parse import quote, unquote, urlparse, parse_qs

# --- KONFIGURACJA ---
TOKEN = os.getenv('DISCORD_TOKEN')
CH_QC_FINDER = 1457766095531278529  # ID kanału ze zdjęcia
MOJA_STRONA = "https://maks-reps.github.io/Maks-Reps/"

# API DO ZDJĘĆ
API_URL = "https://api.xms4192.workers.dev/qc?url="

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- KLASA GALERII (Widok z przyciskami) ---
class QCView(discord.ui.View):
    def __init__(self, photos, product_url):
        super().__init__(timeout=None)
        self.photos = photos
        self.product_url = product_url
        self.index = 0
        
        # Przycisk do Twojej strony
        encoded_url = quote(product_url, safe='')
        link_do_strony = f"{MOJA_STRONA}?url={encoded_url}"
        self.add_item(discord.ui.Button(label="Zobacz na mojej stronie", url=link_do_strony, style=discord.ButtonStyle.link))

    def create_embed(self):
        embed = discord.Embed(color=0x2b2d31)
        embed.set_author(name="Zdjęcie QC", icon_url=bot.user.avatar.url if bot.user.avatar else None)
        embed.description = f"Zdjęcie QC {self.index + 1}/{len(self.photos)}"
        embed.set_image(url=self.photos[self.index])
        embed.set_footer(text="Maks Reps • Automatyczny QC Finder")
        return embed

    @discord.ui.button(label="⬅️ Poprzednie", style=discord.ButtonStyle.gray)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index - 1) % len(self.photos)
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Następne ➡️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index + 1) % len(self.photos)
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

# --- FUNKCJA CZYSZCZĄCA LINKI ---
def get_raw_url(url):
    decoded = unquote(url)
    match = re.search(r'(?:url|link)=([^&]+)', decoded)
    if match:
        return match.group(1)
    return url

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot or message.channel.id != CH_QC_FINDER:
        return

    urls = re.findall(r'(https?://\S+)', message.content)
    if not urls:
        return

    raw_url = get_raw_url(urls[0])
    
    # Obsługujemy tylko chińskie platformy
    if any(x in raw_url for x in ["weidian", "taobao", "1688", "tmall"]):
        status_msg = await message.reply("🔍 Szukam zdjęć QC w bazie...")
        
        try:
            r = requests.get(f"{API_URL}{quote(raw_url, safe='')}", timeout=10)
            data = r.json()
            
            photos = []
            # Wyciąganie zdjęć z JSONa
            def find_imgs(obj):
                if isinstance(obj, str) and (obj.startswith("http") or obj.startswith("//")):
                    if any(ext in obj.lower() for ext in [".jpg", ".png", ".jpeg", ".webp"]):
                        photos.append(obj if obj.startswith("http") else "https:" + obj)
                elif isinstance(obj, dict): [find_imgs(v) for v in obj.values()]
                elif isinstance(obj, list): [find_imgs(i) for i in obj]
            
            find_imgs(data)
            photos = list(dict.fromkeys(photos)) # Usuń duplikaty

            if photos:
                view = QCView(photos, raw_url)
                await status_msg.edit(content=None, embed=view.create_embed(), view=view)
            else:
                await status_msg.edit(content="❌ Brak zdjęć QC dla tego przedmiotu.")
        except Exception as e:
            print(f"Błąd: {e}")
            await status_msg.edit(content="⚠️ Błąd serwera zdjęć. Spróbuj później.")

bot.run(TOKEN)
