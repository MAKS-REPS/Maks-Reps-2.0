import discord
from discord.ext import commands
import os

class InviteTrackerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Słownik do przechowywania zaproszeń: {guild_id: {invite_code: uses}}
        self.invites = {}

    async def cog_load(self):
        for guild in self.bot.guilds:
            try:
                self.invites[guild.id] = await guild.invites()
            except discord.Forbidden:
                print(f"⚠️ Brak uprawnień do pobrania zaproszeń na serwerze: {guild.name}")
            except Exception as e:
                print(f"❌ Błąd ładowania zaproszeń dla {guild.name}: {e}")

    def find_invite_by_code(self, invite_list, code):
        for inv in invite_list:
            if inv.code == code:
                return inv
        return None

    @commands.Cog.listener()
    def on_invite_create(self, invite):
        if invite.guild.id not in self.invites:
            self.invites[invite.guild.id] = []
        self.invites[invite.guild.id].append(invite)

    @commands.Cog.listener()
    def on_invite_delete(self, invite):
        if invite.guild.id in self.invites:
            self.invites[invite.guild.id] = [inv for inv in self.invites[invite.guild.id] if inv.code != invite.code]

    @commands.Cog.listener()
    async def on_member_join(self, member):
        ALLOWED_CHANNEL_ID = 1483135652815179898
        guild = member.guild
        
        channel = guild.get_channel(ALLOWED_CHANNEL_ID)
        if not channel:
            return

        old_invites = self.invites.get(guild.id, [])
        try:
            new_invites = await guild.invites()
        except discord.Forbidden:
            return
            
        self.invites[guild.id] = new_invites

        inviter = None
        used_invite = None

        for new_inv in new_invites:
            old_inv = self.find_invite_by_code(old_invites, new_inv.code)
            if old_inv and new_inv.uses > old_inv.uses:
                used_invite = new_inv
                inviter = new_inv.inviter
                break
        
        if not used_invite:
            for new_inv in new_invites:
                old_inv = self.find_invite_by_code(old_invites, new_inv.code)
                if not old_inv and new_inv.uses > 0:
                    used_invite = new_inv
                    inviter = new_inv.inviter
                    break

        total_invites = 0
        if inviter:
            for inv in new_invites:
                if inv.inviter and inv.inviter.id == inviter.id:
                    total_invites += inv.uses

        embed = discord.Embed(color=0x2ecc71)
        
        # Formatowanie bez wzmianek (używamy czystego tekstu member.name / inviter.name)
        if inviter and used_invite:
            embed.title = "📥 NOWE ZAPROSZENIE"
            embed.description = (
                f"👤 Użytkownik **{member.name}** dołączył do serwera.\n\n"
                f"📌 Zaproszony przez: **{inviter.name}**\n"
                f"📊 Łączna liczba zaproszeń użytkownika: **{total_invites}**"
            )
        else:
            embed.title = "📥 NOWE DOŁĄCZENIE"
            embed.description = f"👤 Użytkownik **{member.name}** dołączył do serwera, ale nie udało się ustalić zaproszenia."
            
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID Użytkownika: {member.id}")
        
        await channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(InviteTrackerCog(bot))
