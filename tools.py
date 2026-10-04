import asyncio
import io
import os

import aiohttp
import discord
import qrcode
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from utils import storage
from utils.calculator import calculate
from utils.embeds import base_embed, error, success, warn
from utils.image import remove_background

load_dotenv()


class Tools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _restore_nick(self, member: discord.Member, afk_data: dict) -> None:
        original = afk_data.get("original_nick")
        try:
            if original is not None:
                await member.edit(nick=original or None)
            elif member.nick and member.nick.startswith("[AFK] "):
                await member.edit(nick=member.nick[6:][:32] or None)
        except discord.Forbidden:
            pass

    async def _is_prefix_command(self, message: discord.Message) -> bool:
        prefixes = await self.bot.get_prefix(message)
        if isinstance(prefixes, str):
            prefixes = [prefixes]
        return any(message.content.startswith(p) for p in prefixes)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        try:
            is_command = await self._is_prefix_command(message)

            afk_data = storage.get_afk(message.author.id)
            if afk_data:
                storage.clear_afk(message.author.id)
                await self._restore_nick(message.author, afk_data)
                if not is_command:
                    await message.channel.send(
                        embed=success("AFK Kaldırıldı", f"Tekrar hoş geldin, **{message.author.display_name}**."),
                        delete_after=8,
                    )

            if self.bot.user in message.mentions or is_command:
                return

            for user in message.mentions:
                if user.bot:
                    continue
                afk = storage.get_afk(user.id)
                if not afk:
                    continue
                reason = afk.get("reason", "AFK")
                await message.channel.send(
                    embed=warn(
                        f"{user.display_name} – AFK",
                        f"**{user.mention}** şu an AFK.\n**Sebep:** {reason}",
                    ),
                    delete_after=12,
                )
        except Exception:
            pass

    @commands.hybrid_command(name="qr", description="Metinden QR kod oluşturur.")
    @app_commands.describe(metin="QR koda dönüştürülecek metin")
    async def qr(self, ctx: commands.Context, *, metin: str):
        if len(metin) > 500:
            return await ctx.send(embed=error("Çok Uzun", "Metin en fazla 500 karakter olabilir."))

        if ctx.interaction:
            await ctx.defer()

        def _make_qr():
            img = qrcode.make(metin)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            return buf

        buf = await asyncio.to_thread(_make_qr)
        embed = base_embed("QR Kod", f"**İçerik:** {metin[:200]}")
        embed.set_image(url="attachment://qr.png")
        await ctx.send(embed=embed, file=discord.File(buf, filename="qr.png"))

    @commands.hybrid_command(name="hesapla", aliases=["calc", "hesap"], description="Matematiksel ifade hesaplar.")
    @app_commands.describe(ifade="Hesaplanacak ifade")
    async def hesapla(self, ctx: commands.Context, *, ifade: str):
        try:
            result = calculate(ifade)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            await ctx.send(embed=success("Sonuç", f"`{ifade}` = **{result}**"))
        except (ValueError, SyntaxError, ZeroDivisionError, TypeError, OverflowError):
            await ctx.send(embed=error("Hesaplanamadı", "Geçerli bir matematik ifadesi gir."))

    @commands.hybrid_command(name="afk", description="AFK moduna geçer.")
    @app_commands.guild_only()
    @app_commands.describe(sebep="AFK sebebi")
    async def afk(self, ctx: commands.Context, *, sebep: str = "AFK"):
        if len(sebep) > 100:
            return await ctx.send(embed=error("Çok Uzun", "Sebep en fazla 100 karakter olabilir."))

        original_nick = ctx.author.nick
        storage.set_afk(ctx.author.id, sebep, original_nick)

        if not (ctx.author.nick and ctx.author.nick.startswith("[AFK]")):
            try:
                base = ctx.author.nick or ctx.author.display_name
                await ctx.author.edit(nick=f"[AFK] {base}"[:32])
            except discord.Forbidden:
                pass

        await ctx.send(embed=success(
            "AFK Modu",
            f"AFK moduna geçtin.\n**Sebep:** {sebep}",
        ))

    @commands.hybrid_command(name="davet", aliases=["invite", "davetlink"], description="Botun davet linkini paylaşır.")
    async def davet(self, ctx: commands.Context):
        perms = discord.Permissions(
            manage_channels=True,
            manage_messages=True,
            manage_roles=True,
            kick_members=True,
            ban_members=True,
            moderate_members=True,
        )
        url = discord.utils.oauth_url(self.bot.user.id, permissions=perms)
        embed = base_embed(
            "Davet Linki",
            f"Rainbow 5.0'ı sunucuna eklemek için [buraya tıkla]({url}).",
        )
        embed.add_field(name="Link", value=url, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="arkaplansil", aliases=["removebg", "bgkaldir"], description="Resmin arka planını kaldırır.")
    @app_commands.describe(gorsel="İşlenecek görsel")
    async def arkaplansil(self, ctx: commands.Context, gorsel: discord.Attachment = None):
        attachment = gorsel

        if not attachment and ctx.message:
            if ctx.message.attachments:
                attachment = ctx.message.attachments[0]
            elif ctx.message.reference:
                try:
                    ref = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                    if ref.attachments:
                        attachment = ref.attachments[0]
                except (discord.NotFound, discord.Forbidden):
                    pass

        if not attachment:
            return await ctx.send(embed=error(
                "Görsel Gerekli",
                "Bir görsel ekle veya görsel içeren bir mesaja yanıt ver.",
            ))

        content_type = attachment.content_type or ""
        if not content_type.startswith("image/"):
            return await ctx.send(embed=error("Geçersiz Dosya", "Yalnızca görsel dosyaları desteklenir."))

        if attachment.size > 8 * 1024 * 1024:
            return await ctx.send(embed=error("Dosya Çok Büyük", "Görsel en fazla 8 MB olabilir."))

        processing = None
        if ctx.interaction:
            await ctx.defer()
        else:
            processing = await ctx.send(embed=base_embed("İşleniyor", "Arka plan kaldırılıyor, biraz bekle..."))

        try:
            data = await attachment.read()
            result = await remove_background(data)

            embed = success("Arka Plan Kaldırıldı", "İşlem tamamlandı.")
            embed.set_image(url="attachment://nobg.png")
            file = discord.File(io.BytesIO(result), filename="nobg.png")

            if processing:
                await processing.delete()
            await ctx.send(embed=embed, file=file)
        except ImportError:
            err = error("Paket Eksik", "`rembg` yüklü değil. `pip install -r requirements.txt` çalıştır.")
            if processing:
                await processing.edit(embed=err)
            else:
                await ctx.send(embed=err)
        except ValueError as e:
            err = error("Dosya Çok Büyük", str(e))
            if processing:
                await processing.edit(embed=err)
            else:
                await ctx.send(embed=err)
        except Exception:
            err = error("Hata", "Görsel işlenirken bir sorun oluştu. Farklı bir görsel dene.")
            if processing:
                await processing.edit(embed=err)
            else:
                await ctx.send(embed=err)

    @commands.hybrid_command(name="havadurumu", aliases=["weather", "hava"], description="Şehir için hava durumu gösterir.")
    @app_commands.describe(sehir="Şehir adı")
    async def havadurumu(self, ctx: commands.Context, *, sehir: str):
        api_key = os.getenv("WEATHER_API_KEY", "")
        if not api_key:
            return await ctx.send(embed=error("Yapılandırma", "Hava durumu API anahtarı ayarlanmamış."))

        if ctx.interaction:
            await ctx.defer()

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": sehir,
            "appid": api_key,
            "units": "metric",
            "lang": "tr",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 404:
                        return await ctx.send(embed=error("Bulunamadı", f"`{sehir}` için sonuç bulunamadı."))
                    if resp.status != 200:
                        return await ctx.send(embed=error("API Hatası", "Hava durumu alınamadı."))
                    data = await resp.json()
        except aiohttp.ClientError:
            return await ctx.send(embed=error("Bağlantı Hatası", "Hava durumu servisine ulaşılamadı."))

        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        desc = data["weather"][0]["description"].capitalize()
        city = data["name"]
        country = data["sys"]["country"]
        icon = data["weather"][0]["icon"]

        embed = base_embed(f"{city}, {country}", desc)
        embed.set_thumbnail(url=f"https://openweathermap.org/img/wn/{icon}@2x.png")
        embed.add_field(name="Sıcaklık", value=f"{temp:.1f}°C", inline=True)
        embed.add_field(name="Hissedilen", value=f"{feels:.1f}°C", inline=True)
        embed.add_field(name="Nem", value=f"%{humidity}", inline=True)
        embed.add_field(name="Rüzgar", value=f"{wind} m/s", inline=True)
        await ctx.send(embed=embed)

    async def cog_command_error(self, ctx: commands.Context, error_: commands.CommandError):
        if isinstance(error_, commands.MissingPermissions):
            await ctx.send(embed=error("Yetki Eksik", "Bu komut için gerekli izinlere sahip değilsin."))
        elif isinstance(error_, commands.BotMissingPermissions):
            await ctx.send(embed=error("Bot Yetkisi", "Botun bu işlem için gerekli izinleri yok."))
        elif isinstance(error_, commands.MissingRequiredArgument):
            await ctx.send(embed=error(
                "Eksik Argüman",
                f"`{ctx.prefix}yardım {ctx.command.name}` ile kullanımı görebilirsin.",
            ))
        else:
            raise error_


async def setup(bot: commands.Bot):
    await bot.add_cog(Tools(bot))
