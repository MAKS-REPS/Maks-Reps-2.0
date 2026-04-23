# --- POPRAWKA DLA PYTHON 3.13 (audioop) ---
try:
    import audioop
except ImportError:
    try:
        import audioop_lts as audioop
        import sys
        sys.modules["audioop"] = audioop
    except ImportError:
        print("⚠️ Uwaga: Brak audioop-lts. Jeśli bot crashuje, dodaj go do requirements.txt")

import discord
from discord.ext import commands
import re
import os
import requests
import urllib.parse
from urllib.parse import urlparse, parse_qs, unquote, quote

# --- KONFIGURACJA AFILIACJI ---
AFF_KAKOBUY = "maksr3ps"
AFF_USFANS = "DJPZ6T"
AFF_ACBUY = "KV2WLD"

# --- ID KANAŁÓW ---
CH_LINKS = 1495473429086863481  # Kanał: linki-afiliacyjne
CH_QC = 1457766095531278529     # Kanał: qc-finder

# --- KONFIGURACJA QC ---
BASE_SITE_URL = "https://maks-reps.github.io/Maks-Reps/"
API_URL = "https://api.xms4192.workers.dev/qc?url="

# --- EMOJI ---
EMOJI_USFANS = "<:USFANS:1465100695022866453>"
EMOJI_ACBUY = "<:ACBUY:1465100840640577637>"
EMOJI_KAKOBUY = "<:kakobuy:1496931499017113642>"
EMOJI_WEIDIAN = "<:weidian:1496931587047030825>"
EMOJI_TAOBAO = "<:taobao:1496931560371388466>"
EMOJI_1688 = "<:1688:1496931547541012601>"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- FUNKCJE POMOCNICZE ---

def clean_url(url):
    """Wyciąga czysty link Weidian/Taobao z linków agentów."""
    decoded = unquote(url)
    match = re.search(r'(?:url|link|item_id|itemID)=([^&]+)', decoded)
    if match and "http" in match.group(1):
        return unquote(match.group(1))
    return url

def extract_product_info(url):
    full_url = clean_url(url)
    p_id = None
    params = parse_qs(urlparse(full_url).query)
    id_list = params.get('id') or params.get('itemId') or params.get('infoId') or params.get('item_id')
    
    if id_list: p_id = id_list[0]
    else:
        id_match = re.search(r'(?:id|itemID|item_id)=(\d+)', full_url, re.IGNORECASE)
        if id_match: p_id = id_match.group(1)

    platform = "taobao"
    emoji = EMOJI_TAOBAO
    if "weidian.com" in full_url:
        platform, emoji = "weidian", EMOJI_WEIDIAN
    elif "1688.com" in full_url:
        platform, emoji = "1688", EMOJI_1688
        
    return p_id, platform, emoji

# --- WIDOKI (INTERFEJSY) ---

class QCView(discord.ui.View):
    def __init__(self, photos, original_url):
        super().__init__(timeout=300)
        self.photos = photos
        self.original_url = original_url
        self.current_page = 0
        encoded_url = quote(original_url, safe='')
        full_url = f"{BASE_SITE_URL}?url={encoded_url}"
        self.add_item(discord.ui.Button(label="Więcej QC na stronie", style=discord.ButtonStyle.link, url=full_url))

    def create_embed(self):
        embed = discord.Embed(title="📸 Maks Reps | QC Finder", color=0xff0000)
        embed.set_image(url=self.photos[self.current_page])
        embed.set_footer(text=f"Zdjęcie {self.current_page + 1}/{len(self.photos)}")
        return embed

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.gray)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else: await interaction.response.defer()

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.photos) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else: await interaction.response.defer()

# --- EVENTY ---

@bot.event
async def on_ready():
    print(f'✅ Bot połączony jako {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot: return

    # --- LOGIKA DLA KANAŁU Z LINKAMI ---
    if message.channel.id == CH_LINKS:
        urls = re.findall(r'(https?://\S+)', message.content)
        if not urls: return
        
        p_id, platform, platform_emoji = extract_product_info(urls[0])
        if p_id:
            raw_url = f"https://item.{platform}.com/item.htm?id={p_id}"
            if platform == "weidian": raw_url = f"https://weidian.com/item.html?itemID={p_id}"
            
            encoded_raw = quote(raw_url, safe='')
            link_kako = f"https://www.kakobuy.com/item/details?url={encoded_raw}&affcode={AFF_KAKOBUY}"
            link_usfans = f"https://www.usfans.com/item/details?url={encoded_raw}&affcode={AFF_USFANS}"
            link_acbuy = f"https://www.allchinabuy.com/en/page/buy/?url={encoded_raw}&partnercode={AFF_ACBUY}"

            embed = discord.Embed(description="🔗 **Twoje przekonwertowane linki:**", color=0x2b2d31)
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="KakoBuy", url=link_kako, emoji=EMOJI_KAKOBUY))
            view.add_item(discord.ui.Button(label="USFans", url=link_usfans, emoji=EMOJI_USFANS))
            view.add_item(discord.ui.Button(label="ACBuy", url=link_acbuy, emoji=EMOJI_ACBUY))
            view.add_item(discord.ui.Button(label="RAW Link", url=raw_url, emoji=platform_emoji))
            await message.reply(embed=embed, view=view)

    # --- LOGIKA DLA KANAŁU QC ---
    elif message.channel.id == CH_QC:
        urls = re.findall(r'(https?://\S+)', message.content)
        if not urls: return
        
        target_url = clean_url(urls[0])
        if any(p in target_url for p in ["weidian", "taobao", "1688", "tmall"]):
            status_msg = await message.reply("🔍 Pobieram zdjęcia QC...")
            try:
                r = requests.get(f"{API_URL}{quote(target_url, safe='')}", timeout=15)
                data = r.json()
                
                photos = []
                def find_imgs(obj):
                    if isinstance(obj, str) and (obj.startswith("http") or obj.startswith("//")):
                        if any(ext in obj.lower() for ext in [".jpg", ".png", ".webp", ".jpeg"]):
                            photos.append(obj if obj.startswith("http") else "https:" + obj)
                    elif isinstance(obj, dict): [find_imgs(v) for v in obj.values()]
                    elif isinstance(obj, list): [find_imgs(i) for i in obj]
                
                find_imgs(data)
                photos = [p for p in list(dict.fromkeys(photos)) if len(p) > 30]

                if photos:
                    view = QCView(photos, target_url)
                    await status_msg.edit(content=None, embed=view.create_embed(), view=view)
                else:
                    await status_msg.edit(content="❌ Nie znaleziono zdjęć QC w bazie.")
            except:
                await status_msg.edit(content="⚠️ Błąd bazy danych QC.")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
