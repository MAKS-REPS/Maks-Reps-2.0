import discord
import datetime
import asyncio
import random
import re
import os
from discord.ext import commands
from discord import app_commands

# ID Twojej roli dającej 2x szansy
BONUS_ROLE_ID = 1497656242615746721

# Słownik do przechowywania uczestników zakończonych giveawayów (pod reroll)
giveaway_cache = {}

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

def parse_time(time_str):
    pos = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    match = re.match(r"(\d+)([smhd])", time_str.lower())
    if match:
        return int(match.group(1)) * pos[match.group(2)]
    return None

async def run_giveaway_logic(interaction, tytul, opis, sekundy, zwyciezcy, kolor_hex, default_color):
    try:
        color_val = int(kolor_hex.replace("#", ""), 16)
    except:
        color_val = default_color

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

    pool = []
    guild = interaction.guild
    for user_id in view.entries:
        pool.append(user_id) 
        member = guild.get_member(user_id)
        if member and any(r.id == BONUS_ROLE_ID for r in member.roles):
            pool.append(user_id) 

    # ZAPISUJEMY DANE DO CACHE (Dla komendy greroll)
    giveaway_cache[msg.id] = {"pool": pool, "tytul": tytul}

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

# --- SEKCOJA BOT SETUP ---

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="gstart", description="Uruchamia giveaway")
async def gstart(interaction: discord.Interaction, tytul: str, czas: str, zwyciezcy: int = 1, opis: str = "Kliknij 🎉 aby dołączyć!"):
    sekundy = parse_time(czas)
    if not sekundy:
        return await interaction.response.send_message("Błędny czas!", ephemeral=True)
    await run_giveaway_logic(interaction, tytul, opis, sekundy, zwyciezcy, "#5865F2", 0x5865f2)

# --- NOWA KOMENDA GREROLL ---

@bot.tree.command(name="greroll", description="Losuje nową osobę z zakończonego konkursu")
@app_commands.describe(message_id="ID wiadomości z zakończonym konkursem")
async def greroll(interaction: discord.Interaction, message_id: str):
    try:
        msg_id = int(message_id)
    except ValueError:
        return await interaction.response.send_message("Musisz podać poprawne ID wiadomości (same cyfry).", ephemeral=True)

    if msg_id not in giveaway_cache:
        return await interaction.response.send_message("Nie znaleziono tego konkursu w pamięci bota (mogło minąć zbyt dużo czasu lub bot był restartowany).", ephemeral=True)

    data = giveaway_cache[msg_id]
    pool = data["pool"]
    tytul = data["tytul"]

    if not pool:
        return await interaction.response.send_message("Brak uczestników do rozlosowania.", ephemeral=True)

    new_winner = random.choice(pool)
    
    await interaction.response.send_message(f"🔄 **REROLL!** Nowy zwycięzca konkursu o **{tytul}** to: <@{new_winner}>! Gratulacje!")

bot.run(os.getenv("DISCORD_TOKEN"))
