import discord

from utils.embeds import base_embed
from utils.help_data import CATEGORIES, PREFIX, find_command, total_command_count

CATEGORY_ICONS = {
    "Moderasyon": "🛡️",
    "Yönetim": "⚙️",
    "Araçlar": "🔑",
}


def _replace_prefix(text: str, prefix: str) -> str:
    return text.replace(PREFIX, prefix) if prefix != PREFIX else text


def build_help_menu(prefix: str = PREFIX) -> discord.Embed:
    total = total_command_count()
    embed = base_embed(
        "🌈 Rainbow 5.0 Komut Listesi",
        f"**Prefix:** `{prefix}`\n"
        f"**Toplam Komut:** {total}\n\n"
        f"`{prefix}yardım <komut>` ile detaylı bilgi alabilirsin.",
    )

    for category, commands in CATEGORIES.items():
        icon = CATEGORY_ICONS.get(category, "📋")
        lines = [f"`{c['name']}` – {c['description']}" for c in commands]
        embed.add_field(
            name=f"{icon} {category}",
            value="\n".join(lines),
            inline=False,
        )

    return embed


def build_command_help(cmd: dict, prefix: str = PREFIX) -> discord.Embed:
    embed = base_embed(
        f"Komut: {cmd['name']}",
        cmd["description"],
    )
    embed.add_field(
        name="Kullanım",
        value=f"`{_replace_prefix(cmd['usage'], prefix)}`",
        inline=False,
    )
    embed.add_field(
        name="Örnek",
        value=f"`{_replace_prefix(cmd['example'], prefix)}`",
        inline=False,
    )
    embed.add_field(name="Gerekli İzin", value=cmd["permissions"], inline=True)

    if cmd.get("aliases"):
        embed.add_field(
            name="Alternatifler",
            value=", ".join(f"`{a}`" for a in cmd["aliases"]),
            inline=True,
        )

    if cmd.get("notes"):
        embed.add_field(name="Not", value=cmd["notes"], inline=False)

    return embed


def get_help_response(query: str | None, prefix: str = PREFIX) -> discord.Embed:
    if not query:
        return build_help_menu(prefix)

    cmd = find_command(query)
    if not cmd:
        return base_embed(
            "Komut Bulunamadı",
            f"`{query}` adında bir komut yok.\n"
            f"Tüm komutlar için `{prefix}yardım` yaz.",
        )

    return build_command_help(cmd, prefix)
