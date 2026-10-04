PREFIX = "r!"

CATEGORIES: dict[str, list[dict]] = {
    "Moderasyon": [
        {
            "name": "kick",
            "aliases": ["at"],
            "description": "Kullanıcıyı sunucudan atar.",
            "usage": f"{PREFIX}kick <@kullanıcı|id> [sebep]",
            "example": f"{PREFIX}kick @Ahmet kurallara uymadı",
            "permissions": "Üyeleri At",
        },
        {
            "name": "ban",
            "aliases": [],
            "description": "Kullanıcıyı sunucudan yasaklar.",
            "usage": f"{PREFIX}ban <@kullanıcı|id> [sebep]",
            "example": f"{PREFIX}ban @Ahmet spam",
            "permissions": "Üyeleri Yasakla",
        },
        {
            "name": "unban",
            "aliases": [],
            "description": "Kullanıcının yasağını kaldırır.",
            "usage": f"{PREFIX}unban <kullanıcı_adı#0000|id>",
            "example": f"{PREFIX}unban Ahmet#1234",
            "permissions": "Üyeleri Yasakla",
        },
        {
            "name": "idban",
            "aliases": [],
            "description": "Kullanıcı ID'si ile yasaklar.",
            "usage": f"{PREFIX}idban <id> [sebep]",
            "example": f"{PREFIX}idban 123456789012345678 reklam",
            "permissions": "Üyeleri Yasakla",
        },
        {
            "name": "idunban",
            "aliases": [],
            "description": "Kullanıcı ID'si ile yasağı kaldırır.",
            "usage": f"{PREFIX}idunban <id>",
            "example": f"{PREFIX}idunban 123456789012345678",
            "permissions": "Üyeleri Yasakla",
        },
        {
            "name": "mute",
            "aliases": ["sustur"],
            "description": "Kullanıcıyı belirli süre susturur.",
            "usage": f"{PREFIX}mute <@kullanıcı|id> <süre> [sebep]",
            "example": f"{PREFIX}mute @Ahmet 30m küfür",
            "permissions": "Üyeleri Sustur",
            "notes": "Süre: 5m, 1h, 2d gibi (dakika, saat, gün).",
        },
        {
            "name": "unmute",
            "aliases": ["susturmakaldir"],
            "description": "Kullanıcının susturmasını kaldırır.",
            "usage": f"{PREFIX}unmute <@kullanıcı|id>",
            "example": f"{PREFIX}unmute @Ahmet",
            "permissions": "Üyeleri Sustur",
        },
        {
            "name": "lock",
            "aliases": ["kilitle"],
            "description": "Kanalı kilitler, @everyone yazamaz.",
            "usage": f"{PREFIX}lock [sebep]",
            "example": f"{PREFIX}lock bakım çalışması",
            "permissions": "Kanalları Yönet",
        },
        {
            "name": "unlock",
            "aliases": ["kilitac"],
            "description": "Kanal kilidini açar.",
            "usage": f"{PREFIX}unlock",
            "example": f"{PREFIX}unlock",
            "permissions": "Kanalları Yönet",
        },
        {
            "name": "slowmode",
            "aliases": ["yavasmod"],
            "description": "Kanal yavaş modunu ayarlar.",
            "usage": f"{PREFIX}slowmode <saniye>",
            "example": f"{PREFIX}slowmode 5",
            "permissions": "Kanalları Yönet",
            "notes": "0 yazarak yavaş modu kapatabilirsin.",
        },
        {
            "name": "sil",
            "aliases": ["temizle", "purge"],
            "description": "Belirtilen sayıda mesajı siler.",
            "usage": f"{PREFIX}sil <1-100>",
            "example": f"{PREFIX}sil 25",
            "permissions": "Mesajları Yönet",
        },
        {
            "name": "rolver",
            "aliases": ["addrole"],
            "description": "Kullanıcıya rol verir.",
            "usage": f"{PREFIX}rolver <@kullanıcı|id> <@rol|rol_adı>",
            "example": f"{PREFIX}rolver @Ahmet @Üye",
            "permissions": "Rolleri Yönet",
        },
        {
            "name": "rolal",
            "aliases": ["removerole"],
            "description": "Kullanıcıdan rol alır.",
            "usage": f"{PREFIX}rolal <@kullanıcı|id> <@rol|rol_adı>",
            "example": f"{PREFIX}rolal @Ahmet @Üye",
            "permissions": "Rolleri Yönet",
        },
        {
            "name": "karaliste",
            "aliases": [],
            "description": "Kullanıcıyı karalisteye alır.",
            "usage": f"{PREFIX}karaliste <@kullanıcı|id> [sebep]",
            "example": f"{PREFIX}karaliste @Ahmet tekrarlayan ihlal",
            "permissions": "Üyeleri Yasakla",
            "notes": "Karalisteye alınan kullanıcı sunucuya giremez.",
        },
        {
            "name": "karalistecikar",
            "aliases": [],
            "description": "Kullanıcıyı karalisteden çıkarır.",
            "usage": f"{PREFIX}karalistecikar <@kullanıcı|id>",
            "example": f"{PREFIX}karalistecikar @Ahmet",
            "permissions": "Üyeleri Yasakla",
        },
        {
            "name": "karalistekontrol",
            "aliases": [],
            "description": "Kullanıcının karaliste durumunu kontrol eder.",
            "usage": f"{PREFIX}karalistekontrol <@kullanıcı|id>",
            "example": f"{PREFIX}karalistekontrol @Ahmet",
            "permissions": "Üyeleri Yasakla",
        },
        {
            "name": "uyarıver",
            "aliases": ["uyariver", "warn"],
            "description": "Kullanıcıya uyarı verir.",
            "usage": f"{PREFIX}uyarıver <@kullanıcı|id> <sebep>",
            "example": f"{PREFIX}uyarıver @Ahmet küfür",
            "permissions": "Üyeleri Yönet",
        },
        {
            "name": "uyarırolayarla",
            "aliases": ["uyarirolayarla"],
            "description": "Uyarı seviyesine karşılık gelen rolü ayarlar.",
            "usage": f"{PREFIX}uyarırolayarla <seviye> <@rol>",
            "example": f"{PREFIX}uyarırolayarla 3 @Uyarı3",
            "permissions": "Rolleri Yönet",
        },
        {
            "name": "uyarısıfırla",
            "aliases": ["uyarisifirla"],
            "description": "Kullanıcının uyarılarını sıfırlar.",
            "usage": f"{PREFIX}uyarısıfırla <@kullanıcı|id>",
            "example": f"{PREFIX}uyarısıfırla @Ahmet",
            "permissions": "Üyeleri Yönet",
        },
        {
            "name": "uyariliste",
            "aliases": [],
            "description": "Sunucudaki tüm uyarıları listeler.",
            "usage": f"{PREFIX}uyariliste",
            "example": f"{PREFIX}uyariliste",
            "permissions": "Üyeleri Yönet",
        },
        {
            "name": "uyarı",
            "aliases": ["uyari", "uyarilar", "warnings"],
            "description": "Kullanıcının uyarılarını gösterir.",
            "usage": f"{PREFIX}uyarı <@kullanıcı|id>",
            "example": f"{PREFIX}uyarı @kullanıcı",
            "permissions": "Üyeleri Yönet",
        },
    ],
    "Yönetim": [
        {
            "name": "restart",
            "aliases": ["yenidenbaslat"],
            "description": "Botu yeniden başlatır.",
            "usage": f"{PREFIX}restart",
            "example": f"{PREFIX}restart",
            "permissions": "Bot Sahibi",
        },
        {
            "name": "prefix",
            "aliases": ["önek"],
            "description": "Sunucu prefixini değiştirir.",
            "usage": f"{PREFIX}prefix <yeni_prefix>",
            "example": f"{PREFIX}prefix !",
            "permissions": "Sunucuyu Yönet",
            "notes": "Varsayılan prefix: r!",
        },
        {
            "name": "sunucularım",
            "aliases": ["sunucularim", "sunucular", "guilds"],
            "description": "Botun bulunduğu sunucuları listeler.",
            "usage": f"{PREFIX}sunucularım",
            "example": f"{PREFIX}sunucularım",
            "permissions": "Bot Sahibi",
        },
        {
            "name": "botkapat",
            "aliases": ["shutdown", "kapat"],
            "description": "Botu kapatır.",
            "usage": f"{PREFIX}botkapat",
            "example": f"{PREFIX}botkapat",
            "permissions": "Bot Sahibi",
        },
    ],
    "Araçlar": [
        {
            "name": "qr",
            "aliases": [],
            "description": "Metinden QR kod oluşturur.",
            "usage": f"{PREFIX}qr <metin>",
            "example": f"{PREFIX}qr https://discord.gg/ornek",
            "permissions": "Yok",
        },
        {
            "name": "hesapla",
            "aliases": ["calc", "hesap"],
            "description": "Matematiksel ifade hesaplar.",
            "usage": f"{PREFIX}hesapla <ifade>",
            "example": f"{PREFIX}hesapla (5 + 3) * 2",
            "permissions": "Yok",
            "notes": "Desteklenen: +, -, *, /, %, parantez.",
        },
        {
            "name": "afk",
            "aliases": [],
            "description": "AFK moduna geçer.",
            "usage": f"{PREFIX}afk [sebep]",
            "example": f"{PREFIX}afk yemekteyim",
            "permissions": "Yok",
        },
        {
            "name": "davet",
            "aliases": ["invite", "davetlink"],
            "description": "Botun davet linkini paylaşır.",
            "usage": f"{PREFIX}davet",
            "example": f"{PREFIX}davet",
            "permissions": "Yok",
        },
        {
            "name": "arkaplansil",
            "aliases": ["removebg", "bgkaldir"],
            "description": "Resmin arka planını kaldırır.",
            "usage": f"{PREFIX}arkaplansil (görsel ekle)",
            "example": f"{PREFIX}arkaplansil",
            "permissions": "Yok",
            "notes": "Komutla birlikte görsel eklemen gerekir.",
        },
        {
            "name": "havadurumu",
            "aliases": ["weather", "hava"],
            "description": "Şehir için hava durumu gösterir.",
            "usage": f"{PREFIX}havadurumu <şehir>",
            "example": f"{PREFIX}havadurumu İstanbul",
            "permissions": "Yok",
        },
    ],
}


def all_commands() -> list[dict]:
    cmds = []
    for commands in CATEGORIES.values():
        cmds.extend(commands)
    return cmds


def find_command(name: str) -> dict | None:
    name = name.lower().strip()
    for cmd in all_commands():
        if cmd["name"] == name or name in cmd.get("aliases", []):
            return cmd
    return None


def total_command_count() -> int:
    return len(all_commands())
