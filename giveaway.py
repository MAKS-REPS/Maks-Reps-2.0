import discord
import datetime
import asyncio
import random
import re

# ID roli dającej 2x szansy na wygraną
BONUS_ROLE_ID = 1497656242615746721

class GiveawayView(discord.ui.View):
    def __init__(self):
        # Ustawiamy timeout na None i podajemy custom_id w przycisku, 
        # aby bot pamiętał o nim po restarcie.
        super().__init__(timeout=None)
        self.entries = []

    @discord.ui.button(emoji="🎉", style=discord.ButtonStyle.blurple, custom_id="giveaway_join_btn")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.entries:
            return await interaction.response.send_message("Już bierzesz udział w tym giveawayu!", ephemeral=True)
        
        self.entries.append(interaction.user.id)
        await interaction.response.send_message("Dołączyłeś do konkursu! Powodzenia!", ephemeral=True)

def parse_time(time_str):
    pos = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    match = re.match(r"(\d+)([smhd])", time_str.lower())
    if match:
        return int(match.group(1)) * pos[match.group(2)]
    return None

async def run_giveaway_logic(interaction, tytul, opis, sekundy, zwyciezcy, kolor_hex, default_color):
    # Konwersja koloru podanego w HEX (np. #5865f2)
    try:
        color_val = int(kolor_hex.replace("#", ""), 16)
    except:
        color_val = default_color

    end_time = datetime.datetime.now() + datetime.timedelta(seconds=sekundy)
    timestamp = int(end_time.timestamp())

    # Formatowanie opisu - naśladujemy wygląd ze screena
    pelny_opis = f"{opis}\n\n**Konta mają być nowe, na dowód należy wysłać ssa po założeniu (przykład poniżej) / brak spełnienia któregoś z wymagań = ponowne losowanie**"

    embed = discord.Embed(
        title=tytul,
        description=pelny_opis,
        color=discord.Color(color_val)
    )
    # Dodawanie formatowania czasu, organizatora i liczby zwycięzców
    embed.add_field(name="Ends:", value=f"<t:{timestamp}:R> (<t:{timestamp}:f>)", inline=False)
    embed.add_field(name="Hosted by:", value=interaction.user.mention, inline=False)
    # Wartość Entries na start to 0, zaktualizujemy ją w logach lub na końcu (Discord rate limits zabraniają edycji po każdym kliknięciu)
    embed.add_field(name="Entries:", value="Trwa zbieranie...", inline=True)
    embed.add_field(name="Winners:", value=str(zwyciezcy), inline=True)
    embed.set_footer(text=f"Dziś o {datetime.datetime.now().strftime('%H:%M')}")

    view = GiveawayView()
    await interaction.response.send_message(content="🎉 **GIVEAWAY START** 🎉", embed=embed, view=view)
    msg = await interaction.original_response()

    # Oczekiwanie na koniec czasu
    await asyncio.sleep(sekundy)

    # Po upływie czasu pobieramy ostateczną listę uczestników
    if not view.entries:
        return await interaction.followup.send(f"Giveaway **{tytul}** zakończony. Brak uczestników!")

    # LOGIKA WAG (2x Szansa dla roli)
    pool = []
    guild = interaction.guild
    
    # Przechodzimy przez unikalne ID uczestników
    for user_id in set(view.entries):
        pool.append(user_id) # 1. Normalny los
        
        # Próba pobrania obiektu użytkownika z serwera, aby sprawdzić role
        member = guild.get_member(user_id)
        if member and any(r.id == BONUS_ROLE_ID for r in member.roles):
            pool.append(user_id) # 2. Drugi los dla posiadacza roli (zwiększa szansę o 100%)

    # Losowanie zwycięzców bez duplikatów
    winners_list = []
    num_winners = min(zwyciezcy, len(set(view.entries)))
    
    while len(winners_list) < num_winners:
        chosen = random.choice(pool)
        if chosen not in winners_list:
            winners_list.append(chosen)

    winner_mentions = ", ".join([f"<@{w}>" for w in winners_list])

    # Aktualizacja Embedu po zakończeniu
    end_embed = embed.copy()
    end_embed.clear_fields()
    end_embed.add_field(name="Zwycięzcy:", value=winner_mentions, inline=False)
    end_embed.add_field(name="Entries:", value=str(len(set(view.entries))), inline=False)
    end_embed.color = discord.Color.dark_grey()

    await msg.edit(content="🎉 **GIVEAWAY ZAKOŃCZONY** 🎉", embed=end_embed, view=None)
    await interaction.followup.send(f"Gratulacje {winner_mentions}! Wygraliście: **{tytul}**!")
