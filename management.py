import os
import subprocess
import sys

import discord
from discord import app_commands
from discord.ext import commands

from utils import storage
from utils.embeds import error, success, warn


def owner_only():
    async def predicate(ctx: commands.Context) -> bool:
        if ctx.author.id != ctx.bot.kurucu_id:
            await ctx.send(embed=error("Yetki Yok", "Bu komut yalnızca bot sahibi tarafından kullanılabilir."))
            return False
        return True
    return commands.check(predicate)


PER_PAGE = 8


class SunucuListesiView(discord.ui.View):
    def __init__(self, author_id: int, guilds: list[discord.Guild]):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guilds = guilds
        self.page = 0
        self.max_page = max(0, (len(guilds) - 1) // PER_PAGE) if guilds else 0
        self._sync_buttons()

    def _sync_buttons(self) -> None:
        self.prev_btn.disabled = self.page <= 0
        self.next_btn.disabled = self.page >= self.max_page or not self.guilds

    def _guild_line(self, index: int, guild: discord.Guild) -> str:
        owner = guild.owner
        owner_name = str(owner)[:24] if owner else "Bilinmiyor"
        name = guild.name[:36] + ("…" if len(guild.name) > 36 else "")
        return f"**{index}.** {name} – `{guild.member_count or 0}` üye\n*{owner_name}*"

    def build_embed(self) -> discord.Embed:
        total_members = sum(g.member_count or 0 for g in self.guilds)
        embed = success(
            "Sunucu Listesi",
            f"**{len(self.guilds)}** sunucuda, toplam **{total_members:,}** üye.",
        )

        if not self.guilds:
            embed.add_field(name="Sunucular", value="Kayıt yok.", inline=False)
        else:
            start = self.page * PER_PAGE
            chunk = self.guilds[start:start + PER_PAGE]
            lines = [self._guild_line(start + i + 1, g) for i, g in enumerate(chunk)]
            embed.add_field(name="Sunucular", value="\n".join(lines), inline=False)

        embed.set_footer(text=f"Rainbow 5.0 · Sayfa {self.page + 1}/{self.max_page + 1}")
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                embed=error("Yetki Yok", "Bu menüyü yalnızca komutu kullanan kişi yönetebilir."),
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Önceki", style=discord.ButtonStyle.secondary, emoji="◀️")
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        self._sync_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Sonraki", style=discord.ButtonStyle.secondary, emoji="▶️")
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = min(self.max_page, self.page + 1)
        self._sync_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


class Management(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="restart", aliases=["yenidenbaslat"], description="Botu yeniden başlatır.")
    @owner_only()
    async def restart(self, ctx: commands.Context):
        await ctx.send(embed=success("Yeniden Başlatılıyor", "Bot birkaç saniye içinde tekrar açılacak."))
        subprocess.Popen(
            [sys.executable] + sys.argv,
            cwd=os.getcwd(),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
        await self.bot.close()

    @commands.hybrid_command(name="prefix", aliases=["önek"], description="Sunucu prefixini değiştirir.")
    @app_commands.guild_only()
    @app_commands.describe(yeni_prefix="Yeni prefix")
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx: commands.Context, yeni_prefix: str):
        yeni_prefix = yeni_prefix.strip()
        if not yeni_prefix:
            return await ctx.send(embed=error("Geçersiz Prefix", "Boş bir prefix kullanılamaz."))
        if len(yeni_prefix) > 5:
            return await ctx.send(embed=error("Geçersiz Prefix", "Prefix en fazla 5 karakter olabilir."))

        storage.set_prefix(ctx.guild.id, yeni_prefix)
        await ctx.send(embed=success(
            "Prefix Güncellendi",
            f"Bu sunucunun yeni prefixi: `{yeni_prefix}`\n"
            f"Örnek: `{yeni_prefix}yardım`",
        ))

    @commands.hybrid_command(name="sunucularim", aliases=["sunucularım", "sunucular", "guilds"], description="Botun bulunduğu sunucuları listeler.")
    @owner_only()
    async def sunucularim(self, ctx: commands.Context):
        guilds = sorted(self.bot.guilds, key=lambda g: g.member_count or 0, reverse=True)
        view = SunucuListesiView(ctx.author.id, guilds)
        message = await ctx.send(embed=view.build_embed(), view=view)
        view.message = message

    @commands.hybrid_command(name="botkapat", aliases=["shutdown", "kapat"], description="Botu kapatır.")
    @owner_only()
    async def botkapat(self, ctx: commands.Context):
        await ctx.send(embed=warn("Kapatılıyor", "Bot kapatılıyor."))
        await self.bot.close()

    async def cog_command_error(self, ctx: commands.Context, error_: commands.CommandError):
        if isinstance(error_, commands.MissingPermissions):
            await ctx.send(embed=error("Yetki Eksik", "Bu komutu kullanmak için Sunucuyu Yönet iznine ihtiyacın var."))
        else:
            raise error_


async def setup(bot: commands.Bot):
    await bot.add_cog(Management(bot))
