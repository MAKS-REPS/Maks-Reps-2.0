import discord

# --- KONFIGURACJA LINKÓW ---
DISCORD_LINK = "https://discord.gg/26U4v4h5Ea"
USFANS_LINK = "https://www.usfans.com/register?ref=7ZDX3M"
SPREADSHEET_LINK = "https://docs.google.com/spreadsheets/d/1ig6hVp-Jt3GeK__kzoqRLL99d0nI2QwmVsDM6-P1YY4/edit?usp=drivesdk"

class WelcomeDMView(discord.ui.View):
    def __init__(self):
        # timeout=None, aby przycisk był trwały (choć w DM to mniej istotne)
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Server Info", url=DISCORD_LINK, style=discord.ButtonStyle.link))

async def send_welcome_dm(member, color):
    embed = discord.Embed(
        title="Witaj na serwerze Maks.R3ps!",
        description=(
            f"💎 **Link do discorda**\n"
            f"➡️ [Discord]({DISCORD_LINK})\n\n"
            f"💸 **Odbierz darmowy kupon na -40% na start w USFans**\n"
            f"➡️ [Link do rejestracji na USFans]({USFANS_LINK})\n\n"
            f"📰 **Spreadsheet z ponad 1000+ itemkami:**\n"
            f"➡️ [Spreadsheet]({SPREADSHEET_LINK})"
        ),
        color=color
    )

    try:
        await member.send(embed=embed, view=WelcomeDMView())
    except discord.Forbidden:
        print(f"❌ Nie udało się wysłać DM do {member.name} (zablokowane wiadomości prywatne).")
