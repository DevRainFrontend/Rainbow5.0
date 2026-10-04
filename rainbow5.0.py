import asyncio
import logging
import os
import sys

import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

from utils import storage
from utils.embeds import base_embed, error
from utils.help_builder import get_help_response
from utils.help_data import PREFIX, all_commands

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("rainbow")

TOKEN = os.getenv("DISCORD_TOKEN")
KURUCU_ID = int(os.getenv("KURUCU_ID", "0"))

if not TOKEN:
    print("DISCORD_TOKEN .env dosyasında bulunamadı.")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True

EXTENSIONS = (
    "cogs.moderation",
    "cogs.management",
    "cogs.tools",
)


class RainbowBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=storage.DEFAULT_PREFIX,
            intents=intents,
            help_command=None,
            case_insensitive=True,
        )
        self.kurucu_id = KURUCU_ID

    async def setup_hook(self):
        for ext in EXTENSIONS:
            try:
                await self.load_extension(ext)
                log.info("Yüklendi: %s", ext)
            except Exception as e:
                log.error("Yüklenemedi %s: %s", ext, e)

    async def get_prefix(self, message: discord.Message):
        prefix = storage.get_prefix(message.guild.id) if message.guild else storage.DEFAULT_PREFIX
        return commands.when_mentioned_or(prefix)(self, message)

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        await self.process_commands(message)


bot = RainbowBot()

STATUSES = (
    "🌈 Rainbow5.0 Yayında",
    "⚡ Rainbow Hızıyla",
    "🛡️ Moderasyon Tam Tıkır",
    "✅ Rainbow Aktif",
)
STATUS_INTERVAL = 30
_status_index = 0


async def _apply_status():
    global _status_index
    await bot.change_presence(
        activity=discord.Game(name=STATUSES[_status_index]),
        status=discord.Status.online,
    )
    _status_index = (_status_index + 1) % len(STATUSES)


@tasks.loop(seconds=STATUS_INTERVAL)
async def rotate_status():
    await _apply_status()


@rotate_status.before_loop
async def before_rotate_status():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    log.info("Rainbow 5.0 hazır – %s | %s sunucu", bot.user, len(bot.guilds))
    log.info("Prefix: %s | Prefix komutları için Message Content Intent gerekli", storage.DEFAULT_PREFIX)

    if not rotate_status.is_running():
        await _apply_status()
        rotate_status.start()

    try:
        synced = await bot.tree.sync()
        log.info("%s slash komut senkronize edildi", len(synced))
    except Exception as e:
        log.error("Slash senkronizasyon hatası: %s", e)


@bot.hybrid_command(name="yardim", aliases=["yardım", "help", "y", "h"], description="Rainbow 5.0 komut listesini veya komut detayını gösterir.")
@app_commands.describe(komut="Detayını görmek istediğin komut adı")
async def yardim(ctx: commands.Context, komut: str = None):
    prefix = ctx.prefix
    if ctx.interaction and ctx.guild:
        prefix = storage.get_prefix(ctx.guild.id)
    embed = get_help_response(komut, prefix=prefix)
    await ctx.send(embed=embed)


@yardim.autocomplete("komut")
async def komut_autocomplete(interaction: discord.Interaction, current: str):
    choices = []
    query = current.lower()
    for cmd in all_commands():
        name = cmd["name"]
        if not query or query in name.lower():
            choices.append(app_commands.Choice(name=name, value=name))
    return choices[:25]


@bot.hybrid_command(name="ping", description="Bot gecikmesini gösterir.")
async def ping(ctx: commands.Context):
    latency = round(bot.latency * 1000)
    await ctx.send(embed=base_embed("Ping", f"Gecikme: **{latency}** ms"))


@bot.event
async def on_command_error(ctx: commands.Context, error_: commands.CommandError):
    if isinstance(error_, commands.CommandNotFound):
        return
    if isinstance(error_, commands.CheckFailure):
        return
    log.exception("Komut hatası [%s]: %s", ctx.command, error_)
    if ctx.command:
        await ctx.send(embed=error(
            "Beklenmeyen Hata",
            f"Bir sorun oluştu. `{ctx.prefix}yardım {ctx.command.name}` ile kullanımı kontrol et.",
        ))


async def main():
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
