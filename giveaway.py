import discord
from discord import app_commands
import datetime
import asyncio
import random
import re

# ID Twojej roli dającej 2x szansy
BONUS_ROLE_ID = 1497656242615746721

# Prosty cache w pamięci bota (zniknie po restarcie bota)
# Klucz: message_id, Wartość: lista ID użytkowników
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

def pick_winners(entries, guild, num_winners):
    """Funkcja pomocnicza do losowania zwycięzców z uwzględnieniem bonusowej roli."""
    if not entries:
        return []
    
    pool = []
    for user_id in entries:
        pool.append(user_id) 
        member = guild.get_member(user_id)
        if member and any(r.id == BONUS_ROLE_ID for r in member.roles):
            pool.append(user_id) # Druga szansa

    winners_list = []
    actual_num_winners = min(num_winners, len(set(entries)))
    
    while len(winners_list) < actual_num_winners:
        chosen = random.choice(pool)
        if chosen not in winners_list:
            winners_list.append(chosen)
            
    return winners_list

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

    # Zapisujemy uczestników do cache, aby umożliwić /greroll
    giveaway_cache[msg.id] = view.entries

    if not view.entries:
        end_embed = embed.copy()
        end_embed.description = f"Zakończono! Nikt nie wziął udziału w: **{tytul}**"
        end_embed.color = discord.Color.red()
        await msg.edit(embed=end_embed, view=None)
        return

    winners_list = pick_winners(view.entries, interaction.guild, zwyciezcy)
    winner_mentions = ", ".join([f"<@{w}>" for w in winners_list])

    end_embed = embed.copy()
    end_embed.description = f"Zakończono! Nagroda: **{tytul}**"
    end_embed.clear_fields()
    end_embed.add_field(name="Winners:", value=winner_mentions, inline=False)
    end_embed.add_field(name="Entries", value=str(len(view.entries)), inline=True)
    end_embed.color = discord.Color.red()

    await msg.edit(embed=end_embed, view=None)
    await interaction.followup.send(f"🎉 Gratulacje {winner_mentions}! Wygraliście: **{tytul}**!")

# --- NOWA KOMENDA REROLL ---

@app_commands.command(name="greroll", description="Losuje nowego zwycięzcę zakońćzonego giveawayu")
@app_commands.describe(message_id="ID wiadomości z zakończonym giveawayem")
@app_commands.checks.has_permissions(manage_messages=True)
async def greroll(interaction: discord.Interaction, message_id: str):
    try:
        msg_id = int(message_id)
    except ValueError:
        return await interaction.response.send_message("Podaj poprawne ID wiadomości.", ephemeral=True)

    if msg_id not in giveaway_cache:
        return await interaction.response.send_message(
            "Nie znaleziono tego giveawayu w pamięci (mógł zostać zakończony przed restartem bota).", 
            ephemeral=True
        )

    entries = giveaway_cache[msg_id]
    if not entries:
        return await interaction.response.send_message("W tym konkursie nie było uczestników.", ephemeral=True)

    try:
        channel = interaction.channel
        msg = await channel.fetch_message(msg_id)
    except Exception:
        return await interaction.response.send_message("Nie udało się odnaleźć wiadomości na tym kanale.", ephemeral=True)

    # Pobieramy liczbę zwycięzców z oryginalnego embeda (jeśli się da)
    # W tym kodzie zakładamy, że reroll losuje 1 nową osobę lub tylu, ilu było w polu Winners.
    # Dla uproszczenia wylosujemy 1 nową osobę jako "rerolled winner".
    
    new_winner_id = pick_winners(entries, interaction.guild, 1)
    
    if not new_winner_id:
        return await interaction.response.send_message("Nie udało się wylosować zwycięzcy.", ephemeral=True)

    winner_mention = f"<@{new_winner_id[0]}>"
    
    await interaction.response.send_message(f"🎉 Nowy zwycięzca (reroll): {winner_mention}! Gratulacje!")
    await channel.send(f"Nowym zwycięzcą giveawayu (ID: {msg_id}) zostaje: {winner_mention}!")

# Nie zapomnij dodać komendy do drzewa bota (client.tree.add_command(greroll))
