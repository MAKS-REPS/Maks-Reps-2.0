import discord
from discord.ext import commands
from discord import app_commands
import datetime
import asyncio
import random
import re
import os  # Dodane do obsługi zmiennych środowiskowych

# --- KONFIGURACJA ---
# Pobieranie tokenu z Railway Variables
TOKEN = os.getenv("DISCORD_TOKEN")
BONUS_ROLE_ID = 1497656242615746721

# Pamięć podręczna dla zakończonych giveawayów
ended_giveaways = {}

class GiveawayBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronizacja komend przy każdym restarcie (ważne na Railway)
        await self.tree.sync()
        print(f"✅ Zalogowano jako {self.user} i zsynchronizowano komendy.")

bot = GiveawayBot()

# --- WIDOK PRZYCISKU 🎉 ---
class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.entries = []

    @discord.ui.button(emoji="🎉", style=discord.ButtonStyle.blurple, custom_id="persistent_giv_btn")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.entries:
            return await interaction.response.send_message("Już bierzesz udział w tym konkursie!", ephemeral=True)
        
        self.entries.append(interaction.user.id)
        embed = interaction.message.embeds[0]
        
        found_field = False
        for i, field in enumerate(embed.fields):
            if field.name == "Entries":
                embed.set_field_at(i, name="Entries", value=str(len(self.entries)), inline=True)
                found_field = True
                break
        
        if not found_field:
            embed.add_field(name="Entries", value=str(len(self.entries)), inline=True)

        await interaction.message.edit(embed=embed)
        await interaction.response.send_message("Pomyślnie dołączyłeś do losowania!", ephemeral=True)

# --- LOGIKA CZASU ---
def parse_time(time_str):
    pos = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    match = re.match(r"(\d+)([smhd])", time_str.lower())
    if match:
        return int(match.group(1)) * pos[match.group(2)]
    return None

# --- GŁÓWNA LOGIKA LOSOWANIA ---
async def run_giveaway_logic(interaction, tytul, opis, sekundy, zwyciezcy, kolor_hex):
    try:
        color_val = int(kolor_hex.replace("#", ""), 16)
    except:
        color_val = 0x5865F2

    end_time = datetime.datetime.now() + datetime.timedelta(seconds=sekundy)
    timestamp = int(end_time.timestamp())

    embed = discord.Embed(
        title=tytul,
        description=opis.replace("\\n", "\n"), 
        color=discord.Color(color_val)
    )
    
    embed.add_field(name="Ends:", value=f"<t:{timestamp}:R> (<t:{timestamp}:f>)", inline=False)
    embed.add_field(name="Hosted by:", value=interaction.user.mention, inline=True)
    embed.add_field(name="Winners:", value=str(zwyciezcy), inline=True)
    embed.add_field(name="Entries", value="0", inline=True)
    embed.set_footer(text=f"Dzisiaj o {datetime.datetime.now().strftime('%H:%M')}")

    view = GiveawayView()
    await interaction.response.send_message(content="🎉 **GIVEAWAY** 🎉", embed=embed, view=view)
    msg = await interaction.original_response()

    await asyncio.sleep(sekundy)

    if not view.entries:
        end_embed = embed.copy()
        end_embed.description = f"Zakończono! Nikt nie wziął udziału w: **{tytul}**"
        end_embed.color = discord.Color.red()
        await msg.edit(embed=end_embed, view=None)
        return

    # Przygotowanie puli (uwzględniając bonusową rolę)
    pool = []
    guild = interaction.guild
    for user_id in view.entries:
        pool.append(user_id) 
        member = guild.get_member(user_id)
        if member and any(r.id == BONUS_ROLE_ID for r in member.roles):
            pool.append(user_id) 

    # Zapisujemy do pamięci dla /greroll
    ended_giveaways[msg.id] = {"pool": pool, "tytul": tytul}

    # Losowanie
    winners_list = []
    num_winners = min(zwyciezcy, len(set(view.entries)))
    
    while len(winners_list) < num_winners:
        chosen = random.choice(pool)
        if chosen not in winners_list:
            winners_list.append(chosen)

    winner_mentions = ", ".join([f"<@{w}>" for w in winners_list])

    end_embed = embed.copy()
    end_embed.description = f"Zakończono! Nagroda: **{tytul}**"
    end_embed.clear_fields()
    end_embed.add_field(name="Winners:", value=winner_mentions, inline=False)
    end_embed.add_field(name="Entries", value=str(len(view.entries)), inline=True)
    end_embed.color = discord.Color.red()

    await msg.edit(embed=end_embed, view=None)
    await interaction.followup.send(f"🎉 Gratulacje {winner_mentions}! Wygraliście: **{tytul}**!")

# --- KOMENDY SLASH ---

@bot.tree.command(name="gstart", description="Uruchamia nowy giveaway")
async def gstart(interaction: discord.Interaction, tytul: str, czas: str, zwyciezcy: int = 1, opis: str = "Kliknij 🎉 aby dołączyć!", kolor: str = "#5865F2"):
    sekundy = parse_time(czas)
    if not sekundy:
        return await interaction.response.send_message("❌ Błędny czas! Przykład: `10m`, `1h`, `1d`.", ephemeral=True)
    
    await run_giveaway_logic(interaction, tytul, opis, sekundy, zwyciezcy, kolor)

@bot.tree.command(name="greroll", description="Ponownie losuje zwycięzcę")
@app_commands.describe(message_id="ID wiadomości zakończonego konkursu", ilosc="Ilu nowych zwycięzców?")
async def greroll(interaction: discord.Interaction, message_id: str, ilosc: int = 1):
    try:
        msg_id = int(message_id)
    except:
        return await interaction.response.send_message("❌ To nie jest poprawne ID wiadomości.", ephemeral=True)

    if msg_id not in ended_giveaways:
        return await interaction.response.send_message("❌ Nie mam tego konkursu w pamięci. (Restart bota czyści pamięć).", ephemeral=True)

    data = ended_giveaways[msg_id]
    pool = data["pool"]
    
    new_winners = []
    num_to_draw = min(ilosc, len(set(pool)))

    while len(new_winners) < num_to_draw:
        winner = random.choice(pool)
        if winner not in new_winners:
            new_winners.append(winner)

    mentions = ", ".join([f"<@{w}>" for w in new_winners])
    await interaction.response.send_message(f"🔄 **REROLL!** Nowy zwycięzca: {mentions}! 🎉")

# Uruchomienie bota
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ BŁĄD: Nie znaleziono zmiennej DISCORD_TOKEN w Railway Variables!")
