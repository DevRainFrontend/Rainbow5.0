from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands

from utils import storage
from utils.checks import bot_can_act, can_manage_role, can_moderate
from utils.embeds import error, success, warn
from utils.parsers import parse_duration

MAX_TIMEOUT = timedelta(days=28)


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not ctx.guild:
            await ctx.send(embed=error("Hata", "Bu komut yalnızca sunucularda kullanılabilir."))
            return False
        return True

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not storage.is_blacklisted(member.guild.id, member.id):
            return
        try:
            await member.ban(reason="Karaliste")
        except discord.Forbidden:
            pass

    @commands.hybrid_command(name="kick", aliases=["at"], description="Kullanıcıyı sunucudan atar.")
    @app_commands.guild_only()
    @app_commands.describe(member="Atılacak kullanıcı", reason="Sebep")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Belirtilmedi"):
        if not can_moderate(ctx.author, member):
            return await ctx.send(embed=error("Yetki Hatası", "Bu kullanıcıyı atamazsın."))
        if not bot_can_act(ctx.guild, member):
            return await ctx.send(embed=error("Yetki Hatası", "Bu kullanıcıyı atacak yetkim yok."))

        await member.kick(reason=f"{ctx.author}: {reason}")
        await ctx.send(embed=success(
            "Kullanıcı Atıldı",
            f"**{member}** sunucudan atıldı.\n**Sebep:** {reason}",
        ))

    @commands.hybrid_command(name="ban", description="Kullanıcıyı sunucudan yasaklar.")
    @app_commands.guild_only()
    @app_commands.describe(member="Yasaklanacak kullanıcı", reason="Sebep")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Belirtilmedi"):
        if not can_moderate(ctx.author, member):
            return await ctx.send(embed=error("Yetki Hatası", "Bu kullanıcıyı yasaklayamazsın."))
        if not bot_can_act(ctx.guild, member):
            return await ctx.send(embed=error("Yetki Hatası", "Bu kullanıcıyı yasaklayacak yetkim yok."))

        await member.ban(reason=f"{ctx.author}: {reason}")
        await ctx.send(embed=success(
            "Kullanıcı Yasaklandı",
            f"**{member}** yasaklandı.\n**Sebep:** {reason}",
        ))

    @commands.hybrid_command(name="unban", description="Kullanıcının yasağını kaldırır.")
    @app_commands.guild_only()
    @app_commands.describe(user="Kullanıcı adı veya ID")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, *, user: str):
        banned = [entry async for entry in ctx.guild.bans()]
        target = None

        for ban_entry in banned:
            if str(ban_entry.user) == user or str(ban_entry.user.id) == user:
                target = ban_entry.user
                break

        if not target:
            return await ctx.send(embed=error("Bulunamadı", "Bu kullanıcı yasaklı değil veya bulunamadı."))

        try:
            await ctx.guild.unban(target)
        except discord.NotFound:
            return await ctx.send(embed=error("Bulunamadı", "Bu kullanıcı yasaklı değil."))
        await ctx.send(embed=success("Yasak Kaldırıldı", f"**{target}** kullanıcısının yasağı kaldırıldı."))

    @commands.hybrid_command(name="idban", description="Kullanıcı ID'si ile yasaklar.")
    @app_commands.guild_only()
    @app_commands.describe(user_id="Kullanıcı ID", reason="Sebep")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def idban(self, ctx: commands.Context, user_id: int, *, reason: str = "Belirtilmedi"):
        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            return await ctx.send(embed=error("Bulunamadı", "Geçerli bir kullanıcı ID'si gir."))

        await ctx.guild.ban(user, reason=f"{ctx.author}: {reason}")
        await ctx.send(embed=success(
            "Kullanıcı Yasaklandı",
            f"**{user}** (`{user_id}`) yasaklandı.\n**Sebep:** {reason}",
        ))

    @commands.hybrid_command(name="idunban", description="Kullanıcı ID'si ile yasağı kaldırır.")
    @app_commands.guild_only()
    @app_commands.describe(user_id="Kullanıcı ID")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def idunban(self, ctx: commands.Context, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            return await ctx.send(embed=error("Bulunamadı", "Geçerli bir kullanıcı ID'si gir."))

        try:
            await ctx.guild.unban(user)
        except discord.NotFound:
            return await ctx.send(embed=error("Bulunamadı", "Bu kullanıcı yasaklı değil."))
        await ctx.send(embed=success(
            "Yasak Kaldırıldı",
            f"**{user}** (`{user_id}`) kullanıcısının yasağı kaldırıldı.",
        ))

    @commands.hybrid_command(name="mute", aliases=["sustur"], description="Kullanıcıyı belirli süre susturur.")
    @app_commands.guild_only()
    @app_commands.describe(member="Susturulacak kullanıcı", duration="Süre (örn. 5m, 1h, 2d)", reason="Sebep")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, duration: str, *, reason: str = "Belirtilmedi"):
        if not can_moderate(ctx.author, member):
            return await ctx.send(embed=error("Yetki Hatası", "Bu kullanıcıyı susturamazsın."))
        if not bot_can_act(ctx.guild, member):
            return await ctx.send(embed=error("Yetki Hatası", "Bu kullanıcıyı susturacak yetkim yok."))

        delta = parse_duration(duration)
        if not delta or delta.total_seconds() < 60:
            return await ctx.send(embed=error("Geçersiz Süre", "Örnek: `5m`, `1h`, `2d` (en az 1 dakika)."))
        if delta > MAX_TIMEOUT:
            return await ctx.send(embed=error("Geçersiz Süre", "En fazla 28 gün susturulabilir."))

        until = discord.utils.utcnow() + delta
        await member.timeout(until, reason=f"{ctx.author}: {reason}")
        await ctx.send(embed=success(
            "Kullanıcı Susturuldu",
            f"**{member}** `{duration}` süreyle susturuldu.\n**Sebep:** {reason}",
        ))

    @commands.hybrid_command(name="unmute", aliases=["susturmakaldir"], description="Kullanıcının susturmasını kaldırır.")
    @app_commands.guild_only()
    @app_commands.describe(member="Susturması kaldırılacak kullanıcı")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        if not bot_can_act(ctx.guild, member):
            return await ctx.send(embed=error("Yetki Hatası", "Bu kullanıcının susturmasını kaldıramam."))

        await member.timeout(None, reason=f"{ctx.author}: Susturma kaldırıldı")
        await ctx.send(embed=success("Susturma Kaldırıldı", f"**{member}** artık konuşabilir."))

    @commands.hybrid_command(name="lock", aliases=["kilitle"], description="Kanalı kilitler.")
    @app_commands.guild_only()
    @app_commands.describe(reason="Kilitleme sebebi")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lock(self, ctx: commands.Context, *, reason: str = "Kanal kilitlendi"):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
        await ctx.send(embed=warn("Kanal Kilitlendi", f"Bu kanal kilitlendi.\n**Sebep:** {reason}"))

    @commands.hybrid_command(name="unlock", aliases=["kilitac"], description="Kanal kilidini açar.")
    @app_commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unlock(self, ctx: commands.Context):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(embed=success("Kanal Açıldı", "Kanal kilidi kaldırıldı, herkes yazabilir."))

    @commands.hybrid_command(name="slowmode", aliases=["yavasmod"], description="Kanal yavaş modunu ayarlar.")
    @app_commands.guild_only()
    @app_commands.describe(seconds="Saniye (0 = kapalı)")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx: commands.Context, seconds: int):
        if seconds < 0 or seconds > 21600:
            return await ctx.send(embed=error("Geçersiz Değer", "0 ile 21600 arasında bir değer gir."))

        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await ctx.send(embed=success("Yavaş Mod", "Yavaş mod kapatıldı."))
        else:
            await ctx.send(embed=success("Yavaş Mod", f"Yavaş mod **{seconds}** saniye olarak ayarlandı."))

    @commands.hybrid_command(name="sil", aliases=["temizle", "purge"], description="Belirtilen sayıda mesajı siler.")
    @app_commands.guild_only()
    @app_commands.describe(amount="Silinecek mesaj sayısı (1-100)")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def sil(self, ctx: commands.Context, amount: int):
        if amount < 1 or amount > 100:
            return await ctx.send(embed=error("Geçersiz Sayı", "1 ile 100 arasında bir sayı gir."))

        if ctx.interaction:
            await ctx.defer(ephemeral=True)

        deleted = await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(embed=success("Mesajlar Silindi", f"**{len(deleted) - 1}** mesaj silindi."))
        if not ctx.interaction:
            await msg.delete(delay=5)

    @commands.hybrid_command(name="rolver", aliases=["addrole"], description="Kullanıcıya rol verir.")
    @app_commands.guild_only()
    @app_commands.describe(member="Kullanıcı", role="Verilecek rol")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def rolver(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if not can_manage_role(ctx.author, role):
            return await ctx.send(embed=error("Yetki Hatası", "Bu rolü veremezsin."))
        if role >= ctx.guild.me.top_role:
            return await ctx.send(embed=error("Yetki Hatası", "Bu rolü veremem."))
        if role in member.roles:
            return await ctx.send(embed=warn("Zaten Var", f"**{member}** zaten **{role.name}** rolüne sahip."))

        await member.add_roles(role, reason=f"{ctx.author}")
        await ctx.send(embed=success("Rol Verildi", f"**{member}** kullanıcısına **{role.name}** rolü verildi."))

    @commands.hybrid_command(name="rolal", aliases=["removerole"], description="Kullanıcıdan rol alır.")
    @app_commands.guild_only()
    @app_commands.describe(member="Kullanıcı", role="Alınacak rol")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def rolal(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if not can_manage_role(ctx.author, role):
            return await ctx.send(embed=error("Yetki Hatası", "Bu rolü alamazsın."))
        if role >= ctx.guild.me.top_role:
            return await ctx.send(embed=error("Yetki Hatası", "Bu rolü alamam."))
        if role not in member.roles:
            return await ctx.send(embed=warn("Rol Yok", f"**{member}** bu role sahip değil."))

        await member.remove_roles(role, reason=f"{ctx.author}")
        await ctx.send(embed=success("Rol Alındı", f"**{member}** kullanıcısından **{role.name}** rolü alındı."))

    @commands.hybrid_command(name="karaliste", description="Kullanıcıyı karalisteye alır.")
    @app_commands.guild_only()
    @app_commands.describe(member="Kullanıcı", reason="Sebep")
    @commands.has_permissions(ban_members=True)
    async def karaliste(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Belirtilmedi"):
        if not can_moderate(ctx.author, member):
            return await ctx.send(embed=error("Yetki Hatası", "Bu kullanıcıyı karalisteye alamazsın."))
        if storage.is_blacklisted(ctx.guild.id, member.id):
            return await ctx.send(embed=warn("Zaten Kayıtlı", "Bu kullanıcı zaten karalistede."))

        storage.add_blacklist(ctx.guild.id, member.id)

        try:
            await member.ban(reason=f"Karaliste: {reason} ({ctx.author})")
        except discord.Forbidden:
            pass

        await ctx.send(embed=success(
            "Karalisteye Alındı",
            f"**{member}** karalisteye eklendi.\n**Sebep:** {reason}",
        ))

    @commands.hybrid_command(name="karalistecikar", description="Kullanıcıyı karalisteden çıkarır.")
    @app_commands.guild_only()
    @app_commands.describe(member="Kullanıcı")
    @commands.has_permissions(ban_members=True)
    async def karalistecikar(self, ctx: commands.Context, member: discord.Member):
        if not storage.remove_blacklist(ctx.guild.id, member.id):
            return await ctx.send(embed=warn("Kayıt Yok", "Bu kullanıcı karalistede değil."))

        await ctx.send(embed=success("Karalisteden Çıkarıldı", f"**{member}** karalisteden kaldırıldı."))

    @commands.hybrid_command(name="karalistekontrol", description="Karaliste durumunu kontrol eder.")
    @app_commands.guild_only()
    @app_commands.describe(member="Kullanıcı")
    @commands.has_permissions(ban_members=True)
    async def karalistekontrol(self, ctx: commands.Context, member: discord.Member):
        if storage.is_blacklisted(ctx.guild.id, member.id):
            await ctx.send(embed=warn("Karaliste", f"**{member}** karalistede kayıtlı."))
        else:
            await ctx.send(embed=success("Temiz", f"**{member}** karalistede değil."))

    @commands.hybrid_command(name="uyariver", aliases=["uyarıver", "warn"], description="Kullanıcıya uyarı verir.")
    @app_commands.guild_only()
    @app_commands.describe(member="Kullanıcı", reason="Uyarı sebebi")
    @commands.has_permissions(moderate_members=True)
    async def uyariver(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        if member.bot:
            return await ctx.send(embed=error("Hata", "Botlara uyarı verilemez."))
        if not can_moderate(ctx.author, member):
            return await ctx.send(embed=error("Yetki Hatası", "Bu kullanıcıya uyarı veremezsin."))

        count = storage.add_warning(ctx.guild.id, member.id, ctx.author.id, reason)
        roles = storage.get_warning_roles(ctx.guild.id)
        role_id = roles.get(str(count))

        if role_id:
            role = ctx.guild.get_role(role_id)
            if role and role < ctx.guild.me.top_role:
                await member.add_roles(role, reason=f"Uyarı {count}")

        await ctx.send(embed=warn(
            "Uyarı Verildi",
            f"**{member}** kullanıcısına uyarı verildi.\n"
            f"**Toplam:** {count}\n**Sebep:** {reason}",
        ))

        try:
            await member.send(embed=warn(
                f"{ctx.guild.name} – Uyarı",
                f"Sana bir uyarı verildi.\n**Sebep:** {reason}\n**Toplam uyarı:** {count}",
            ))
        except discord.Forbidden:
            pass

    @commands.hybrid_command(name="uyarirolayarla", aliases=["uyarırolayarla"], description="Uyarı seviyesine rol ayarlar.")
    @app_commands.guild_only()
    @app_commands.describe(level="Uyarı seviyesi", role="Rol")
    @commands.has_permissions(manage_roles=True)
    async def uyarirolayarla(self, ctx: commands.Context, level: int, role: discord.Role):
        if level < 1:
            return await ctx.send(embed=error("Geçersiz Seviye", "Seviye 1 veya üzeri olmalı."))

        storage.set_warning_role(ctx.guild.id, level, role.id)
        await ctx.send(embed=success(
            "Uyarı Rolü Ayarlandı",
            f"**{level}.** uyarı seviyesi için rol: **{role.name}**",
        ))

    @commands.hybrid_command(name="uyarisifirla", aliases=["uyarısıfırla"], description="Kullanıcının uyarılarını sıfırlar.")
    @app_commands.guild_only()
    @app_commands.describe(member="Kullanıcı")
    @commands.has_permissions(moderate_members=True)
    async def uyarisifirla(self, ctx: commands.Context, member: discord.Member):
        count = storage.reset_warnings(ctx.guild.id, member.id)
        if count == 0:
            return await ctx.send(embed=warn("Kayıt Yok", f"**{member}** için kayıtlı uyarı yok."))

        roles = storage.get_warning_roles(ctx.guild.id)
        for role_id in roles.values():
            role = ctx.guild.get_role(role_id)
            if role and role in member.roles:
                await member.remove_roles(role, reason="Uyarılar sıfırlandı")

        await ctx.send(embed=success("Uyarılar Sıfırlandı", f"**{member}** için **{count}** uyarı silindi."))

    @commands.hybrid_command(name="uyariliste", description="Sunucudaki tüm uyarıları listeler.")
    @app_commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def uyariliste(self, ctx: commands.Context):
        all_warnings = storage.get_warnings(ctx.guild.id)
        if not all_warnings:
            return await ctx.send(embed=warn("Kayıt Yok", "Bu sunucuda kayıtlı uyarı bulunmuyor."))

        lines = []
        for user_id, warnings in all_warnings.items():
            member = ctx.guild.get_member(int(user_id))
            name = str(member) if member else f"`{user_id}`"
            lines.append(f"{name} – **{len(warnings)}** uyarı")

        embed = success("Uyarı Listesi", "")
        chunk = ""
        for line in lines:
            if len(chunk) + len(line) > 900:
                embed.add_field(name="\u200b", value=chunk, inline=False)
                chunk = ""
            chunk += line + "\n"
        if chunk:
            embed.add_field(name="\u200b", value=chunk, inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="uyari", aliases=["uyarı", "uyarilar", "warnings"], description="Kullanıcının uyarılarını gösterir.")
    @app_commands.guild_only()
    @app_commands.describe(member="Kullanıcı")
    @commands.has_permissions(moderate_members=True)
    async def uyari(self, ctx: commands.Context, member: discord.Member):
        warnings = storage.get_user_warnings(ctx.guild.id, member.id)
        if not warnings:
            return await ctx.send(embed=warn("Kayıt Yok", f"**{member}** için kayıtlı uyarı yok."))

        lines = []
        for w in warnings:
            mod = ctx.guild.get_member(w["moderator_id"])
            mod_name = str(mod) if mod else f"`{w['moderator_id']}`"
            lines.append(f"**#{w['count']}** – {w['reason']} (*{mod_name}*)")

        embed = warn(f"{member} – Uyarılar", f"Toplam: **{len(warnings)}**")
        embed.add_field(name="Kayıtlar", value="\n".join(lines), inline=False)
        await ctx.send(embed=embed)

    async def cog_command_error(self, ctx: commands.Context, error_: commands.CommandError):
        if isinstance(error_, commands.MissingPermissions):
            await ctx.send(embed=error("Yetki Eksik", "Bu komutu kullanmak için gerekli izinlere sahip değilsin."))
        elif isinstance(error_, commands.BotMissingPermissions):
            await ctx.send(embed=error("Bot Yetkisi", "Bu işlemi yapmak için botun gerekli izinleri yok."))
        elif isinstance(error_, commands.MissingRequiredArgument):
            await ctx.send(embed=error(
                "Eksik Argüman",
                f"Kullanım hatalı. `{ctx.prefix}yardım {ctx.command.name}` ile detaylara bak.",
            ))
        elif isinstance(error_, commands.MemberNotFound):
            await ctx.send(embed=error("Bulunamadı", "Kullanıcı bulunamadı."))
        elif isinstance(error_, commands.RoleNotFound):
            await ctx.send(embed=error("Bulunamadı", "Rol bulunamadı."))
        elif isinstance(error_, commands.BadArgument):
            await ctx.send(embed=error("Geçersiz Argüman", "Girdiğin değer geçersiz."))
        else:
            raise error_


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
