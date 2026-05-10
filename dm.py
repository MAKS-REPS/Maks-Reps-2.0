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
    
    # DODAJ TĘ LINIJKĘ:
    embed.set_footer(text="Maks Reps 2.0")

    try:
        await member.send(embed=embed, view=WelcomeDMView())
    except discord.Forbidden:
        print(f"❌ Nie udało się wysłać DM do {member.name}.")
