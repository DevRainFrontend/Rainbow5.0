import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _path(name: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / name


def _load(name: str) -> dict:
    path = _path(name)
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(name: str, data: dict) -> None:
    path = _path(name)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def guild_key(guild_id: int) -> str:
    return str(guild_id)


# --- Karaliste ---

def get_blacklist(guild_id: int) -> list[int]:
    data = _load("blacklist.json")
    return [int(uid) for uid in data.get(guild_key(guild_id), [])]


def add_blacklist(guild_id: int, user_id: int) -> None:
    data = _load("blacklist.json")
    key = guild_key(guild_id)
    users = data.setdefault(key, [])
    if user_id not in users:
        users.append(user_id)
    _save("blacklist.json", data)


def remove_blacklist(guild_id: int, user_id: int) -> bool:
    data = _load("blacklist.json")
    key = guild_key(guild_id)
    users = data.get(key, [])
    if user_id not in users:
        return False
    users.remove(user_id)
    data[key] = users
    _save("blacklist.json", data)
    return True


def is_blacklisted(guild_id: int, user_id: int) -> bool:
    return user_id in get_blacklist(guild_id)


# --- Uyarılar ---

def get_warnings(guild_id: int) -> dict[str, list[dict]]:
    data = _load("warnings.json")
    return data.get(guild_key(guild_id), {})


def get_user_warnings(guild_id: int, user_id: int) -> list[dict]:
    return get_warnings(guild_id).get(str(user_id), [])


def add_warning(guild_id: int, user_id: int, moderator_id: int, reason: str) -> int:
    data = _load("warnings.json")
    key = guild_key(guild_id)
    guild_data = data.setdefault(key, {})
    user_key = str(user_id)
    warnings = guild_data.setdefault(user_key, [])
    warnings.append({
        "moderator_id": moderator_id,
        "reason": reason,
        "count": len(warnings) + 1,
    })
    _save("warnings.json", data)
    return len(warnings)


def reset_warnings(guild_id: int, user_id: int) -> int:
    data = _load("warnings.json")
    key = guild_key(guild_id)
    guild_data = data.get(key, {})
    user_key = str(user_id)
    count = len(guild_data.get(user_key, []))
    if user_key in guild_data:
        del guild_data[user_key]
    data[key] = guild_data
    _save("warnings.json", data)
    return count


def reset_all_warnings(guild_id: int) -> None:
    data = _load("warnings.json")
    data[guild_key(guild_id)] = {}
    _save("warnings.json", data)


# --- Uyarı rolleri ---

def get_warning_roles(guild_id: int) -> dict[str, int]:
    data = _load("warning_roles.json")
    return {k: int(v) for k, v in data.get(guild_key(guild_id), {}).items()}


def set_warning_role(guild_id: int, level: int, role_id: int) -> None:
    data = _load("warning_roles.json")
    key = guild_key(guild_id)
    guild_data = data.setdefault(key, {})
    guild_data[str(level)] = role_id
    _save("warning_roles.json", data)


# --- Prefix ---

DEFAULT_PREFIX = "r!"


def get_prefix(guild_id: int | None) -> str:
    if guild_id is None:
        return DEFAULT_PREFIX
    data = _load("prefixes.json")
    return data.get(guild_key(guild_id), DEFAULT_PREFIX)


def set_prefix(guild_id: int, prefix: str) -> None:
    data = _load("prefixes.json")
    data[guild_key(guild_id)] = prefix
    _save("prefixes.json", data)


# --- AFK ---

def set_afk(user_id: int, reason: str, original_nick: str | None = None) -> None:
    data = _load("afk.json")
    data[str(user_id)] = {
        "reason": reason,
        "original_nick": original_nick,
    }
    _save("afk.json", data)


def get_afk(user_id: int) -> dict | None:
    data = _load("afk.json")
    return data.get(str(user_id))


def clear_afk(user_id: int) -> None:
    data = _load("afk.json")
    if str(user_id) in data:
        del data[str(user_id)]
        _save("afk.json", data)
