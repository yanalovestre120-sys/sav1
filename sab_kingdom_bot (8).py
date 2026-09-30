import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import json
import os
import re
import asyncio
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

# ============================================================
# SAB KINGDOM — Full Merged Ticket + Moderation Bot
# Theme: vibrant orange / yellow (SAB KINGDOM)
# ============================================================

# ============================================================
# TOKEN — environment variable only (never hardcode a real token)
# Set DISCORD_BOT_TOKEN or TOKEN on your host.
# If a token was ever pasted in chat/code, regenerate it in the
# Discord Developer Portal immediately.
# ============================================================
TOKEN = os.environ.get("DISCORD_BOT_TOKEN") or os.environ.get("TOKEN") or ""
PREFIX = "+"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Full-access owner user IDs — bypass all perm / role checks for commands
OWNER_USER_IDS = [
    1532561566271017009,
]

THEME_COLOR = 0xFF8C00  # vibrant orange
THEME_COLOR_ALT = 0xFFAA00  # golden yellow accent
FOOTER_TEXT = "⚡ SAB KINGDOM • Server Services"
BRAND_NAME = "SAB KINGDOM"

# ============================================================
# ANIMATED / CUSTOM EMOJIS
# Only CUSTOM Discord emojis (uploaded as GIF) can animate.
# How to get one: in Discord type  \:your_emoji_name:  and copy
# the result, e.g.  <a:sparkle:123456789012345678>
# Paste those strings below. Unicode (⚡ 🛡️) cannot animate.
# ============================================================

def pe(s):
    """Return PartialEmoji for custom <:name:id> / <a:name:id>, else unicode str."""
    if not s:
        return None
    s = str(s).strip()
    if s.startswith("<") and ":" in s and s.endswith(">"):
        try:
            return discord.PartialEmoji.from_str(s)
        except Exception:
            return s
    return s

def es(s):
    """Emoji as plain string for embed text (works for custom + unicode)."""
    if not s:
        return ""
    return str(s).strip()

# --- Panel / select emojis (replace values with <a:name:id> to animate) ---
E = {
    # Global / titles
    "bolt": "⚡",
    # Support panel + TicketSelect
    "support": "🛡️",
    "scammer": "🚨",
    "reward": "🎁",
    "ads": "📢",
    "rolls": "💰",
    # Index bases
    "gold": "🟡",
    "diamond": "💠",
    "rainbow": "🌈",
    "galaxy": "🌌",
    "candy": "🍬",
    "lava": "🌋",
    "radioactive": "☢️",
    "yingyang": "☯️",
    "cursed": "☠️",
    "divine": "✨",
    "cyber": "🤖",
    "phantom": "👻",
    "crystal": "💎",
    # Middleman
    "mm_cross": "🟡",
    "mm_og": "🥇",
    "mm_1b": "🥈",
    "mm_500m": "🥉",
    "mm_0_250m": "✅",
    # Staff panel
    "staff_app": "📝",
    "staff_rolls": "🎟️",
    "staff_index": "📦",
    "staff_mm": "🤝",
    # Partnerships
    "partner": "🤝",
    # Ticket buttons
    "claim": "👤",
    "close": "🔒",
    # Reaction roles (keys match labels loosely)
    "rr_important": "🚨",
    "rr_shop": "🛒",
    "rr_poll": "📊",
    "rr_announce": "📢",
    "rr_dead": "💤",
    "rr_trade": "💱",
    "rr_leaks": "🔓",
    "rr_sab": "🧠",
    "rr_invite": "🎟️",
    "rr_giveaway": "🎉",
}

# ==================== CHANNELS ====================
LOG_CHANNEL_ID = 1550996038159179898
WELCOME_CHANNEL_ID = 1551280369771225101
INVITE_TRACKER_ID = 1551720482401689702
BOOST_CHANNEL_ID = 1551280619240034314
LEAVES_CHANNEL_ID = 1551280673619443754

# Panel channels (auto-posted on startup)
PANEL_CHANNEL_SUPPORT = 1550996022979858515   # support / scammer / reward / ads / rolls
PANEL_CHANNEL_INDEX = 1550996020572323931     # index panel
PANEL_CHANNEL_MM = 1550996014419288065        # middleman panel
PANEL_CHANNEL_STAFF = 1550996017720074374     # staff applications panel
PANEL_CHANNEL_REACTION = 1550995981582082220  # reaction roles panel
PANEL_CHANNEL_RULES = 1550999253667815557     # server rules panel
PANEL_CHANNEL_PARTNERSHIPS = 1551270491665338399  # partnerships panel

# SAB Leaks relay — when Sammy posts an announcement, forward here with images/text + ping
SAB_LEAKS_CHANNEL_ID = 1550995978549731418
SAB_LEAKS_ROLE_ID = 1551571055166885948  # Leaks Ping role
# SpyderSammy — bot must share a guild with this user to relay announcements
SAMMY_USER_IDS = [
    "303327056274653197",
]
# Optional filters (empty / None = relay any message from Sammy user IDs above)
SAMMY_ANNOUNCE_CHANNEL_IDS = []  # e.g. [announcement_channel_id]
SAMMY_SOURCE_GUILD_ID = None     # e.g. official Steal a Brainrot guild ID

# Partners role (granted when partnership is accepted)
PARTNERS_ROLE_ID = 1550995876569423955

# ==================== REACTION ROLES ====================
# GIFs chosen to match each role theme (shown when user toggles the role)
REACTION_ROLES = [
    {"id": 1550995943028166747, "label": "Important Ping", "emoji_key": "rr_important"},
    {"id": 1550995945640951831, "label": "Shop Ping", "emoji_key": "rr_shop"},
    {"id": 1550995948589551746, "label": "Poll Ping", "emoji_key": "rr_poll"},
    {"id": 1550995950997348396, "label": "Announcement Ping", "emoji_key": "rr_announce"},
    {"id": 1550995954415444068, "label": "Dead Chat Ping", "emoji_key": "rr_dead"},
    {"id": 1551571055129268244, "label": "Trade Ping", "emoji_key": "rr_trade"},
    {"id": 1551571055166885948, "label": "Leaks Ping", "emoji_key": "rr_leaks"},
    {"id": 1551571546789781594, "label": "SAB", "emoji_key": "rr_sab"},
    {"id": 1551726575160922252, "label": "Invite Reward Ping", "emoji_key": "rr_invite"},
    {"id": 1551726682950344936, "label": "Giveaway Ping", "emoji_key": "rr_giveaway"},
]

# ==================== CATEGORIES ====================
SUPPORT_CATEGORY_ID = 1551278227417202790
SCAMMER_CATEGORY_ID = 1551278311811063908
REWARD_CATEGORY_ID = 1551278391867478027
MM_CATEGORY_ID = 1551278466090139728
INDEX_CATEGORY_ID = 1551278551989489764
RECRUITMENT_CATEGORY_ID = 1551278227417202790
PAY_ROLES_CATEGORY_ID = 1551278772244979763
INDEX_APP_CATEGORY_ID = 1551278848166076508
MM_APP_CATEGORY_ID = 1551278466090139728
PARTNERSHIP_CATEGORY_ID = 1551278227417202790  # partner tickets open here
INVITE_REWARDS_CHANNEL_ID = 1550995989714698451

# ==================== COMMAND PERM ROLES ====================
# Members with these roles can use the corresponding moderation commands.
BAN_PERM_ROLE_ID = 1554600314844483654      # +ban
UNBAN_PERM_ROLE_ID = 1554604264754778203    # +unban
KICK_PERM_ROLE_ID = 1554604201164804186     # +kick
BL_PERM_ROLE_ID = 1554604153819365476       # +bl
UNBL_PERM_ROLE_ID = 1554604296803188796     # +unbl

# High Ranking Staff — auto-granted to Server Manager and above
HIGH_RANKING_STAFF_ROLE_ID = 1553183968927547432
# Role IDs that count as Server Manager and above (levels 5–6)
SM_AND_ABOVE_ROLE_IDS = [
    1550995737398083645,  # Server Manager
    1550995734281588776,  # Supervisor
    1550995730053996718,  # Co Owner
    1550995725746438254,  # Owners
    1550995714828406824,  # Guardian
    1550995712496631818,  # Founder
    1550995708793065563,  # Creator
]

def _has_role_id(member, role_id: int) -> bool:
    if not member or not getattr(member, "roles", None):
        return False
    return any(r.id == role_id for r in member.roles)

def is_owner(member) -> bool:
    """True if member is in OWNER_USER_IDS (full command access)."""
    if not member:
        return False
    try:
        return int(getattr(member, "id", 0)) in OWNER_USER_IDS
    except Exception:
        return False

def can_use_ban(member) -> bool:
    return is_owner(member) or _has_role_id(member, BAN_PERM_ROLE_ID)

def can_use_unban(member) -> bool:
    return is_owner(member) or _has_role_id(member, UNBAN_PERM_ROLE_ID)

def can_use_kick(member) -> bool:
    return is_owner(member) or _has_role_id(member, KICK_PERM_ROLE_ID)

def can_use_bl(member) -> bool:
    return is_owner(member) or _has_role_id(member, BL_PERM_ROLE_ID)

def can_use_unbl(member) -> bool:
    return is_owner(member) or _has_role_id(member, UNBL_PERM_ROLE_ID)

def is_sm_or_above(member) -> bool:
    """True if member has Server Manager or any higher rank (or is owner)."""
    if is_owner(member):
        return True
    if not member or not getattr(member, "roles", None):
        return False
    return any(r.id in SM_AND_ABOVE_ROLE_IDS for r in member.roles)

async def ensure_high_ranking_staff(member):
    """Give High Ranking Staff role if member is SM+ and doesn't already have it."""
    if not member or getattr(member, "bot", False):
        return
    if not is_sm_or_above(member):
        return
    if _has_role_id(member, HIGH_RANKING_STAFF_ROLE_ID):
        return
    guild = member.guild
    if not guild:
        return
    role = guild.get_role(HIGH_RANKING_STAFF_ROLE_ID)
    if not role:
        return
    if role >= guild.me.top_role:
        return
    try:
        await member.add_roles(role, reason="Auto: Server Manager+ → High Ranking Staff")
        print(f"[AUTO-ROLE] Gave High Ranking Staff to {member} ({member.id})")
    except Exception as e:
        print(f"[AUTO-ROLE] Failed for {member.id}: {e}")

# ==================== ROLE HIERARCHY ====================
ROLES = {
    1: {"slots": [{"ids": [1550995784483479606], "names": ["Test Mod", "Test Moderator"]}]},
    2: {"slots": [
        {"ids": [1550995776199589910], "names": ["Moderator"]},
        {"ids": [1550995773481554000], "names": ["Senior Mod", "Senior Moderator"]},
    ]},
    3: {"slots": [
        {"ids": [1550995770931675376], "names": ["Head Staff"]},
        {"ids": [1550995767525769296], "names": ["Head Moderator"]},
    ]},
    4: {"slots": [
        {"ids": [1550995764635902032], "names": ["Admin", "Administrator"]},
        {"ids": [1550995740149555322], "names": ["Vice Manager"]},
        {"ids": [1551702843868577792], "names": ["Head Administrator"]},
    ]},
    5: {"slots": [
        {"ids": [1550995734281588776], "names": ["Supervisor"]},
        {"ids": [1550995730053996718], "names": ["Co Owner", "Co-Owner"]},
        {"ids": [1550995725746438254], "names": ["Owners", "Owner"]},
        {"ids": [1550995737398083645], "names": ["Server Manager"]},
    ]},
    6: {"slots": [
        {"ids": [1550995714828406824], "names": ["Guardian"]},
        {"ids": [1550995712496631818], "names": ["Founder"]},
        {"ids": [1550995708793065563], "names": ["Creator"]},
    ]},
}
ROLE_MANAGE_EXTRA_IDS = [1550995745958658088, 1550995750824050831]

# Extra roles always stripped by +derank (in addition to hierarchy staff ranks)
DERANK_EXTRA_ROLE_IDS = {
    1550995782520414258,  # Staff Team
    1553183968927547432,  # High Ranking Staff
    1550995745958658088,  # Head of Recruitment
    1550995750824050831,  # Recruiter
}

# Commands regular members may use (everyone else is silent for non-staff)
PUBLIC_COMMAND_NAMES = {
    "snipe",
    "mc", "membercount", "members", "membercounts",
    "ping",
    "userinfo",
    "serverinfo",
    "i", "invites",
    "lb", "ilb",
    "avatar", "av", "pfp",
    "role_info", "ri", "roleinfo",
}

TICKET_TEAM_T1 = "1550995871179735192"
TICKET_TEAM = "1550995873880870962"

MM_ROLES = {
    "cross": "1550995798060433599",
    "og": "1550995795216699543",
    "1b": "1550995800186683464",
    "500m": "1550995803277893642",
    "0-250m": "1550995805479895103",
}
MM_DISPLAY = {
    "cross": "Cross Trades", "og": "OG Trades", "1b": "1B+ Trades",
    "500m": "500M Trades", "0-250m": "0-250M Trades",
}
MM_EMOJIS = {"cross": "mm_cross", "og": "mm_og", "1b": "mm_1b", "500m": "mm_500m", "0-250m": "mm_0_250m"}  # keys into E
ALL_MM_ROLES = list(MM_ROLES.values())

INDEX_ROLES = {
    "crystal": "1550995810752143382", "phantom": "1550995823528247391",
    "cyber": "1550995826417991713", "divine": "1550995830092070992",
    "cursed": "1550995832466047008", "radioactive": "1550995835121311796",
    "yingyang": "1550995837549551830", "galaxy": "1550995840372445215",
    "lava": "1550995843191017513", "candy": "1550995845954928701",
    "rainbow": "1550995848626700438", "diamond": "1550995853651738777",
    "gold": "1550995857023963177",
}
INDEX_PRICES = {
    "crystal": "1x Base Drag (or equivalent value ; collat will be needed)",
    "phantom": "9 garam (or equivalent value ; collat will be needed)",
    "cyber": "9 garam (or equivalent value ; collat will be needed)",
    "divine": "Ask staff for current price (or equivalent value ; collat will be needed)",
    "cursed": "7+ garams (or equivalent value ; collat will be needed)",
    "radioactive": "6+ garams (or equivalent value ; collat will be needed)",
    "yingyang": "5+ garams (or equivalent value ; collat will be needed)",
    "galaxy": "3+ garams (or equivalent value ; collat will be needed)",
    "lava": "3+ garams (or equivalent value ; collat will be needed)",
    "candy": "2+ garams (or equivalent value ; collat will be needed)",
    "rainbow": "5 garams (or equivalent value ; collat will be needed)",
    "diamond": "4 garams (or equivalent value ; collat will be needed)",
    "gold": "3 garams (or equivalent value ; collat will be needed)",
}
INDEX_DISPLAY = {
    "crystal": "Crystal Base", "phantom": "Phantom Base", "cyber": "Cyber Base",
    "divine": "Divine Base", "cursed": "Cursed Base", "radioactive": "Radioactive Base",
    "yingyang": "Yin Yang Base", "galaxy": "Galaxy Base", "lava": "Lava Base",
    "candy": "Candy Base", "rainbow": "Rainbow Base", "diamond": "Diamond Base", "gold": "Gold Base",
}
INDEX_EMOJIS = {
    "crystal": "crystal", "phantom": "phantom", "cyber": "cyber", "divine": "divine", "cursed": "cursed",
    "radioactive": "radioactive", "yingyang": "yingyang", "galaxy": "galaxy", "lava": "lava", "candy": "candy",
    "rainbow": "rainbow", "diamond": "diamond", "gold": "gold",
}  # keys into E
ALL_INDEX_ROLES = list(INDEX_ROLES.values())

BOOST_ROLE_ID = 1550995890485985281

STAFF_PANEL_ROLES = [
    "1550995708793065563", "1550995712496631818", "1550995714828406824",
    "1550995725746438254", "1550995730053996718", "1550995734281588776",
    "1550995737398083645", "1550995740149555322", "1550995745958658088", "1550995750824050831",
]
STAFF_CATEGORY_IDS = {
    "recruitment": RECRUITMENT_CATEGORY_ID,
    "payrolls": PAY_ROLES_CATEGORY_ID,
    "indexprovider": INDEX_APP_CATEGORY_ID,
    "mmapplication": MM_APP_CATEGORY_ID,
}

HIGH_STAFF_ROLES = [
    "1550995708793065563", "1550995712496631818", "1550995714828406824",
    "1550995725746438254", "1550995730053996718", "1550995734281588776",
    "1550995737398083645", "1550995740149555322", "1550995764635902032",
    "1551702843868577792",  # Head Administrator
]
ADMIN_AND_ABOVE_ROLES = HIGH_STAFF_ROLES[:]
REWARD_STAFF_ROLES = HIGH_STAFF_ROLES[:]
ADS_STAFF_ROLES = [
    "1550995708793065563", "1550995725746438254", "1550995734281588776",
    "1550995737398083645", "1550995740149555322",
]
ROLLS_STAFF_ROLES = ADS_STAFF_ROLES[:]
ALL_STAFF_ROLES = [
    "1550995708793065563", "1550995712496631818", "1550995714828406824",
    "1550995725746438254", "1550995730053996718", "1550995734281588776",
    "1550995737398083645", "1550995740149555322", "1550995764635902032",
    "1551702843868577792",  # Head Administrator
    "1550995767525769296", "1550995770931675376", "1550995773481554000",
    "1550995776199589910", "1550995784483479606",
    TICKET_TEAM, TICKET_TEAM_T1,
]

# ==================== ANTI-RAID / ANTI-NUKE ====================
# Auto-detects mass ban/kick/channel/role/webhook + *dangerous* bot-add via audit logs.
# Bot needs: View Audit Log, Manage Roles, Moderate Members (timeout), Ban Members (optional).
ANTI_NUKE_ENABLED = True       # Core protection — on by default, more important than before
ANTI_NUKE_WINDOW = 10          # tighter window (seconds)
ANTI_NUKE_BAN_ON_TRIGGER = True
ANTI_NUKE_TIMEOUT_HOURS = 24
ANTI_NUKE_ALERT_EVERYONE_HIGH = True
# STRICT thresholds (more sensitive than the previous version)
ANTI_NUKE_THRESHOLDS = {
    "ban": 2,
    "kick": 2,
    "unban": 3,
    "channel_delete": 2,
    "role_delete": 2,
    "channel_create": 3,
    "role_create": 3,
    "webhook": 1,
    "bot_add": 1,
    "prune": 1,
    "perm_grant": 1,
}
# Any mix of dangerous actions in the window
ANTI_NUKE_COMBINED_THRESHOLD = 3
# Roles immune (guild owner always immune in code)
ANTI_NUKE_IMMUNE_ROLES = [
    "1550995708793065563",  # creator
    "1550995712496631818",  # founder
    "1550995714828406824",  # guardian
    "1550995725746438254",  # owners
    str(HIGH_RANKING_STAFF_ROLE_ID),  # high ranking staff
]

BLACKLISTED_WORDS = [
    "nigger", "nigga", "faggot", "fag", "tranny", "retard", "retarded",
    "nazi", "hitler", "kike", "chink", "spic", "coon", "beaner",
    "femboy", "d*ck", "dick", "cock", "pussy", "whore", "slut", "hoe",
    "porn", "nudes", "onlyfans",
    "kys", "kill yourself", "kill urself", "hang yourself", "go die",
    "neck yourself", "end yourself",
]
SCAM_WORDS = [
    "free nitro", "discord.gift", "steamcommunity.com/gift",
    "free nitro giveaway", "nitro gift", "claim nitro",
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None, case_insensitive=True)

# ==================== DATA ====================
os.makedirs("data", exist_ok=True)
SANCTIONS_FILE = "data/sanctions.json"
BLACKLIST_FILE = "data/blacklist.json"
SNIPE_FILE = "data/snipe.json"
ROLE_PERMS_FILE = "data/role_perms.json"
TEMPROLES_FILE = "data/temproles.json"
COMMAND_PERMS_FILE = "data/command_perms.json"
LINKED_ALTS_FILE = "data/linked_alts.json"
CONFIG_FILE = "config.json"

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

sanctions_data = load_json(SANCTIONS_FILE, {})
blacklist = load_json(BLACKLIST_FILE, [])
snipe_data = load_json(SNIPE_FILE, {})
clearing_channels = set()
role_perms = load_json(ROLE_PERMS_FILE, {})
temproles_data = load_json(TEMPROLES_FILE, [])
_temprole_tasks = {}
command_overrides = load_json(COMMAND_PERMS_FILE, {})
linked_alts = load_json(LINKED_ALTS_FILE, {})
config = load_json(CONFIG_FILE, {"ticketCounter": 0})

# Invite tracking cache: {guild_id: {code: uses}}
_invite_cache = {}
# New accounts younger than this (hours) get flagged in welcome log
NEW_ACCOUNT_HOURS = 48

# Anti-nuke action tracker: {guild_id: {user_id: {action: [timestamps...]}}}
_antinuke_actions = {}
_antinuke_punished = set()  # user ids currently being punished (avoid loops)

def save_config():
    save_json(CONFIG_FILE, config)

BAN_FILE = "data/banned_ips.txt"
def load_banned_ips():
    if not os.path.exists(BAN_FILE):
        return set()
    with open(BAN_FILE, "r") as f:
        return {line.strip() for line in f if line.strip()}
def save_banned_ips(ips):
    with open(BAN_FILE, "w") as f:
        for ip in sorted(ips):
            f.write(ip + "\n")
BANNED_IPS = load_banned_ips()

def ban_ip(ip: str) -> str:
    ip = ip.strip()
    if not re.match(r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$", ip):
        return f"Invalid IP: {ip}"
    if ip in BANNED_IPS:
        return f"{ip} is already banned"
    BANNED_IPS.add(ip)
    save_banned_ips(BANNED_IPS)
    return f"Banned {ip} (total: {len(BANNED_IPS)})"

def unban_ip(ip: str) -> str:
    ip = ip.strip()
    if ip not in BANNED_IPS:
        return f"{ip} was not banned"
    BANNED_IPS.discard(ip)
    save_banned_ips(BANNED_IPS)
    return f"Unbanned IP {ip}"

DEFAULT_COMMAND_PERMS = {
    "warn": 1, "tempmute": 1, "unmute": 1, "mutelist": 1, "sanctions": 1, "perms": 1, "poll": 1,
    "del": 2, "rolemembers": 2, "clearwarns": 3,
    "derank": 4, "addrole": 4, "delrole": 4, "clear": 4, "lock": 4, "unlock": 4, "slowmode": 4, "nick": 4,
    "banlist": 5, "baninfo": 5, "blist": 5, "linkalt": 5, "say": 5, "softban": 5,
    "create": 6, "temprole": 6, "syncroles": 6, "modstats": 6, "changeperm": 6, "roleall": 6, "role": 6,
    "lockdown": 6, "unlockdown": 6,
    "ban": 99, "unban": 99, "kick": 99, "bl": 99, "unbl": 99,
}

def save_sanctions(): save_json(SANCTIONS_FILE, sanctions_data)
def save_blacklist(): save_json(BLACKLIST_FILE, blacklist)
def save_snipe(): save_json(SNIPE_FILE, snipe_data)
def save_role_perms(): save_json(ROLE_PERMS_FILE, role_perms)
def save_temproles(): save_json(TEMPROLES_FILE, temproles_data)
def save_command_perms(): save_json(COMMAND_PERMS_FILE, command_overrides)
def save_linked_alts(): save_json(LINKED_ALTS_FILE, linked_alts)

def get_cmd_perm(name: str) -> int:
    key = name.lower().strip()
    if key in command_overrides:
        val = command_overrides[key]
        if val is None or str(val).lower() == "none":
            return 99
        try:
            return int(val)
        except Exception:
            return DEFAULT_COMMAND_PERMS.get(key, 5)
    return DEFAULT_COMMAND_PERMS.get(key, 5)

# ==================== PERM HELPERS ====================
def _match_role_exact(guild, name):
    name = name.strip()
    if not name:
        return None
    role = discord.utils.find(lambda r, n=name: r.name == n, guild.roles)
    if role:
        return role
    role = discord.utils.find(lambda r, n=name: r.name.lower() == n.lower(), guild.roles)
    if role:
        return role
    return None

def resolve_role_ids(guild, force=False):
    gid = str(guild.id)
    mapping = {}
    used_ids = set()
    for level in sorted(ROLES.keys(), reverse=True):
        entry = ROLES[level]
        found = []
        for slot in entry.get("slots", []):
            picked = None
            for rid in slot.get("ids", []):
                if rid in used_ids:
                    continue
                role = guild.get_role(rid)
                if role is not None:
                    picked = rid
                    break
            if picked is None:
                for name in slot.get("names", []):
                    role = _match_role_exact(guild, name)
                    if role and role.id not in used_ids:
                        picked = role.id
                        break
            if picked is not None:
                found.append(picked)
                used_ids.add(picked)
        mapping[level] = found
    role_perms[gid] = {str(k): v for k, v in mapping.items()}
    save_role_perms()
    return mapping

def get_perm_level(member):
    if is_owner(member):
        return 6  # full access
    if not member or not getattr(member, "guild", None):
        return 0
    cache = resolve_role_ids(member.guild)
    member_ids = {r.id for r in member.roles}
    highest = 0
    for level, role_ids in cache.items():
        if member_ids & set(role_ids):
            highest = max(highest, level)
    return highest

def has_perm(member, level):
    if is_owner(member):
        return True
    return get_perm_level(member) >= level

def can_moderate(moderator, target):
    if moderator is None or target is None or moderator.id == target.id:
        return False
    if is_owner(moderator) or moderator.id == moderator.guild.owner_id:
        return True
    if is_owner(target) or target.id == target.guild.owner_id:
        return False
    mod_level = get_perm_level(moderator)
    target_level = get_perm_level(target)
    if target_level == 0:
        return mod_level >= 1
    return mod_level > target_level

def has_role_manage_extra(member):
    if is_owner(member):
        return True
    if not member or not getattr(member, "roles", None):
        return False
    return any(r.id in ROLE_MANAGE_EXTRA_IDS for r in member.roles)

def has_staff_permission(member):
    if is_owner(member):
        return True
    try:
        all_roles = ALL_STAFF_ROLES + ALL_INDEX_ROLES + ALL_MM_ROLES + [str(x) for x in ROLE_MANAGE_EXTRA_IDS]
        return any(str(role.id) in all_roles for role in member.roles)
    except Exception:
        return False

def has_high_staff_permission(member):
    if is_owner(member):
        return True
    try:
        return any(str(role.id) in HIGH_STAFF_ROLES for role in member.roles)
    except Exception:
        return False

def member_has_any_role(member, role_ids):
    try:
        return any(str(role.id) in [str(r) for r in role_ids] for role in member.roles)
    except Exception:
        return False

# ==================== TICKET HELPERS ====================
def get_ticket_kind(channel):
    if not channel or not channel.category_id:
        return "unknown"
    cat = channel.category_id
    if cat == INDEX_CATEGORY_ID: return "index"
    if cat == MM_CATEGORY_ID: return "mm"
    if cat == SCAMMER_CATEGORY_ID: return "scammer"
    if cat == REWARD_CATEGORY_ID: return "reward"
    if cat == SUPPORT_CATEGORY_ID: return "support"
    if cat in STAFF_CATEGORY_IDS.values(): return "staff"
    return "unknown"

def can_add_or_remove(member, channel):
    if is_owner(member):
        return True
    kind = get_ticket_kind(channel)
    if kind == "index":
        return False
    if kind == "mm":
        return member_has_any_role(member, ALL_MM_ROLES) or member_has_any_role(member, HIGH_STAFF_ROLES)
    if kind in ("support", "scammer"):
        return (member_has_any_role(member, [TICKET_TEAM, TICKET_TEAM_T1])
                or member_has_any_role(member, ADMIN_AND_ABOVE_ROLES))
    return member_has_any_role(member, ADMIN_AND_ABOVE_ROLES)

def is_ticket_opener(channel, user):
    if not channel.topic or not str(channel.topic).startswith("ticket-"):
        return False
    return str(user.id) == str(channel.topic).replace("ticket-", "")

def clean_channel_name(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9\-]', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return name[:90] if name else "ticket"

def get_staff_mentions(ticket_type="support"):
    """Who gets pinged when a ticket opens."""
    # Creator, Server Manager, Supervisor, Ticket Team
    CREATOR = "1550995708793065563"
    SERVER_MANAGER = "1550995737398083645"
    SUPERVISOR = "1550995734281588776"
    core = [CREATOR, SERVER_MANAGER, SUPERVISOR, TICKET_TEAM]
    if ticket_type in ("support", "scammer", "reward"):
        return " ".join(f"<@&{r}>" for r in dict.fromkeys(core))
    if ticket_type in ("ads", "rolls"):
        roles = [CREATOR, "1550995725746438254", SUPERVISOR]  # creator, owners, supervisor
        return " ".join(f"<@&{r}>" for r in dict.fromkeys(roles))
    return ""

async def resolve_member(ctx, user_input):
    if ctx.message.mentions:
        return ctx.message.mentions[0]
    user_input = user_input.strip()
    if user_input.isdigit():
        member = ctx.guild.get_member(int(user_input))
        if member:
            return member
        try:
            return await bot.fetch_user(int(user_input))
        except Exception:
            pass
    lower = user_input.lower()
    for m in ctx.guild.members:
        if m.name.lower() == lower or m.display_name.lower() == lower:
            return m
    return None

# ==================== TICKET UI ====================
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Contact Staff", description="Need help? Open a support ticket.", value="support", emoji=pe(E["support"])),
            discord.SelectOption(label="Scammer Report", description="Report a scammer with evidence.", value="scammer", emoji=pe(E["scammer"])),
            discord.SelectOption(label="Claim Reward", description="Won a giveaway? Claim here.", value="reward", emoji=pe(E["reward"])),
            discord.SelectOption(label="Promote / Ads", description="Advertise your server or content.", value="ads", emoji=pe(E["ads"])),
            discord.SelectOption(label="Pay for Rolls", description="Purchase secure rolls.", value="rolls", emoji=pe(E["rolls"])),
        ]
        super().__init__(placeholder=f'{es(E["bolt"])} Select a service…', min_values=1, max_values=1, options=options, custom_id="ticket_select")

    async def callback(self, interaction):
        await interaction.response.defer(ephemeral=True)
        await create_ticket(interaction, self.values[0])

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class IndexSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Gold Base", description=INDEX_PRICES["gold"], value="gold", emoji=pe(E["gold"])),
            discord.SelectOption(label="Diamond Base", description=INDEX_PRICES["diamond"], value="diamond", emoji=pe(E["diamond"])),
            discord.SelectOption(label="Rainbow Base", description=INDEX_PRICES["rainbow"], value="rainbow", emoji=pe(E["rainbow"])),
            discord.SelectOption(label="Galaxy Base", description=INDEX_PRICES["galaxy"], value="galaxy", emoji=pe(E["galaxy"])),
            discord.SelectOption(label="Candy Base", description=INDEX_PRICES["candy"], value="candy", emoji=pe(E["candy"])),
            discord.SelectOption(label="Lava Base", description=INDEX_PRICES["lava"], value="lava", emoji=pe(E["lava"])),
            discord.SelectOption(label="Radioactive Base", description=INDEX_PRICES["radioactive"], value="radioactive", emoji=pe(E["radioactive"])),
            discord.SelectOption(label="Yin Yang Base", description=INDEX_PRICES["yingyang"], value="yingyang", emoji=pe(E["yingyang"])),
            discord.SelectOption(label="Cursed Base", description=INDEX_PRICES["cursed"], value="cursed", emoji=pe(E["cursed"])),
            discord.SelectOption(label="Divine Base", description=INDEX_PRICES["divine"], value="divine", emoji=pe(E["divine"])),
            discord.SelectOption(label="Cyber Base", description=INDEX_PRICES["cyber"], value="cyber", emoji=pe(E["cyber"])),
            discord.SelectOption(label="Phantom Base", description=INDEX_PRICES["phantom"], value="phantom", emoji=pe(E["phantom"])),
            discord.SelectOption(label="Crystal Base", description=INDEX_PRICES["crystal"], value="crystal", emoji=pe(E["crystal"])),
        ]
        super().__init__(placeholder="⚡ Select a base to index…", min_values=1, max_values=1, options=options, custom_id="index_select")

    async def callback(self, interaction):
        await interaction.response.defer(ephemeral=True)
        await create_index_ticket(interaction, self.values[0])

class IndexView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(IndexSelect())

class MiddlemanModal(discord.ui.Modal, title="MiddleMan Request"):
    def __init__(self, trade_type):
        super().__init__()
        self.trade_type = trade_type
        self.trade_with = discord.ui.TextInput(label="Who is the trade with?", placeholder="Ex: @user", required=True, max_length=100)
        self.trade_details = discord.ui.TextInput(label="What is the trade?", placeholder="Ex: Dragon for garamas", required=True, max_length=200)
        self.tip = discord.ui.TextInput(label="What is the tip?", placeholder="Please tip 10% or ticket may be closed.", required=True, max_length=100)
        self.add_item(self.trade_with)
        self.add_item(self.trade_details)
        self.add_item(self.tip)

    async def on_submit(self, interaction):
        await interaction.response.defer(ephemeral=True)
        await create_middleman_ticket(interaction, self.trade_type, self.trade_with.value, self.trade_details.value, self.tip.value)

class MiddlemanSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Cross Trades", description="Cross trade middleman", value="cross", emoji=pe(E["mm_cross"])),
            discord.SelectOption(label="OG Trades", description="OG trade middleman", value="og", emoji=pe(E["mm_og"])),
            discord.SelectOption(label="1B+ Trades", description="1B+ value middleman", value="1b", emoji=pe(E["mm_1b"])),
            discord.SelectOption(label="500M Trades", description="500M middleman", value="500m", emoji=pe(E["mm_500m"])),
            discord.SelectOption(label="0-250M Trades", description="0 to 250M middleman", value="0-250m", emoji=pe(E["mm_0_250m"])),
        ]
        super().__init__(placeholder=f'{es(E["bolt"])} Select a trade service…', min_values=1, max_values=1, options=options, custom_id="middleman_select")

    async def callback(self, interaction):
        await interaction.response.send_modal(MiddlemanModal(self.values[0]))

class MiddlemanView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MiddlemanSelect())

class StaffPanelSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Staff Application", description="Apply for a staff position", value="recruitment", emoji=pe(E["staff_app"])),
            discord.SelectOption(label="Pay for Rolls", description="Purchase secure staff rolls", value="payrolls", emoji=pe(E["staff_rolls"])),
            discord.SelectOption(label="Index Provider", description="Apply to become an index provider", value="indexprovider", emoji=pe(E["staff_index"])),
            discord.SelectOption(label="Middleman Application", description="Apply to become a middleman", value="mmapplication", emoji=pe(E["staff_mm"])),
        ]
        super().__init__(placeholder=f'{es(E["bolt"])} Choose a staff option…', min_values=1, max_values=1, options=options, custom_id="staff_panel_select")

    async def callback(self, interaction):
        await interaction.response.defer(ephemeral=True)
        await create_staff_ticket(interaction, self.values[0])

class StaffPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(StaffPanelSelect())


class PartnershipButton(Button):
    def __init__(self):
        super().__init__(
            label="Apply for Partnership",
            emoji=pe(E["partner"]),
            style=discord.ButtonStyle.primary,
            custom_id="partnership_apply",
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await create_partnership_ticket(interaction)


class PartnershipView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PartnershipButton())


class ReactionRoleButton(Button):
    def __init__(self, role_id: int, label: str, emoji):
        super().__init__(
            label=label,
            emoji=pe(emoji) if isinstance(emoji, str) else emoji,
            style=discord.ButtonStyle.secondary,
            custom_id=f"rr_{role_id}",
        )
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id) if interaction.guild else None
        if role is None:
            return await interaction.response.send_message("Role not found on this server.", ephemeral=True)
        member = interaction.user
        try:
            if role in member.roles:
                await member.remove_roles(role, reason="Reaction role toggle")
                text = f"✅ Removed **{role.name}**"
            else:
                await member.add_roles(role, reason="Reaction role toggle")
                text = f"✅ Added **{role.name}**"
            await interaction.response.send_message(text, ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to manage that role.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed: {e}", ephemeral=True)

class ReactionRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for r in REACTION_ROLES:
            emoji_val = E.get(r.get("emoji_key", ""), r.get("emoji", "🔔"))
            self.add_item(ReactionRoleButton(r["id"], r["label"], emoji_val))

class TicketButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary, emoji="👤", custom_id="ticket_claim")
    async def claim_button(self, interaction, button):
        if is_ticket_opener(interaction.channel, interaction.user):
            return await interaction.response.send_message("You cannot claim your own ticket.", ephemeral=True)
        if not has_staff_permission(interaction.user):
            return await interaction.response.send_message("Only staff can claim tickets.", ephemeral=True)
        embed = interaction.message.embeds[0]
        for field in embed.fields:
            if field.name.lower() == "claimed by":
                return await interaction.response.send_message("This ticket is already claimed.", ephemeral=True)
        embed.add_field(name="Claimed by", value=interaction.user.mention, inline=True)
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message(f"Ticket claimed by {interaction.user.mention}")

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_close")
    async def close_button(self, interaction, button):
        if not (is_ticket_opener(interaction.channel, interaction.user) or has_staff_permission(interaction.user)):
            return await interaction.response.send_message("Only staff or the ticket owner can close tickets.", ephemeral=True)
        await interaction.response.defer()
        deleted = await close_ticket(interaction.channel, interaction.user)
        if not deleted:
            try:
                await interaction.followup.send("❌ Could not delete channel. Bot needs Manage Channels.", ephemeral=True)
            except Exception:
                pass

# ==================== CREATE TICKETS ====================
async def create_ticket(interaction, ticket_type):
    guild = interaction.guild
    member = interaction.user
    for channel in guild.text_channels:
        if channel.topic == f"ticket-{member.id}":
            return await interaction.followup.send(f"You already have an open ticket: {channel.mention}", ephemeral=True)

    config["ticketCounter"] = config.get("ticketCounter", 0) + 1
    save_config()
    channel_name = clean_channel_name(member.name)

    if ticket_type == "support":
        category_id = SUPPORT_CATEGORY_ID
    elif ticket_type == "scammer":
        category_id = SCAMMER_CATEGORY_ID
    elif ticket_type == "reward":
        category_id = REWARD_CATEGORY_ID
    else:
        category_id = SUPPORT_CATEGORY_ID

    if ticket_type in ("support", "scammer"):
        allowed_roles = [TICKET_TEAM, TICKET_TEAM_T1] + HIGH_STAFF_ROLES
    elif ticket_type == "reward":
        allowed_roles = REWARD_STAFF_ROLES
    elif ticket_type == "ads":
        allowed_roles = ADS_STAFF_ROLES
    else:
        allowed_roles = ROLLS_STAFF_ROLES

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, manage_messages=True),
    }
    for rid in allowed_roles:
        role = guild.get_role(int(rid))
        if role:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True, manage_messages=True)

    category = guild.get_channel(category_id)
    channel = await guild.create_text_channel(name=channel_name, category=category, topic=f"ticket-{member.id}", overwrites=overwrites)

    if ticket_type == "support":
        embed = discord.Embed(title=f"⚡ Ticket opened by {member.name}", description="Thank you for contacting **SAB KINGDOM** support.\nPlease describe your issue and wait for a response.", color=THEME_COLOR)
    elif ticket_type == "scammer":
        embed = discord.Embed(title=f"⚡ Scammer Report — {member.name}", description="**SCAMMER REPORT SERVICE**\n\nPlease follow the format:\n\n`DISCORDIDOFSCAMMER - ID`\n`DISCORDIDOFVICTIM - ID`\n`ROBLOXUSEROFSCAMMER - USER`\n`ROBLOXUSEROFVICTIM - USER`\n\n**Deal:** (ex: Robux for Brainrots)\n**Evidences:** Screens / Records only", color=THEME_COLOR)
    elif ticket_type == "reward":
        embed = discord.Embed(title=f"⚡ Reward Claim — {member.name}", description="**REWARD CLAIMING SERVICE**\n\n`DISCORDIDOFWINNER - ID`\n`ROBLOXUSEROFWINNER - USER`\n\n**Prize:**\n**Evidences:**", color=THEME_COLOR)
    elif ticket_type == "ads":
        embed = discord.Embed(title=f"⚡ Promote Your Server — {member.name}", description="**📢 Promote Your Server!**\n\n**Package 1:** 2 Days | 1 Ping\n**Package 2:** 3 Days | 2 Pings\n**Package 3:** 7 Days | 4 Pings\n**Package 4:** 12 Days | 6 Pings\n\nTell us which package you want.", color=THEME_COLOR)
    else:
        embed = discord.Embed(title=f"⚡ Pay for Rolls — {member.name}", description="**💰 Pay for Rolls**\n\nTell us how many rolls and what you are offering.", color=THEME_COLOR)

    embed.set_footer(text=FOOTER_TEXT)
    await channel.send(content=get_staff_mentions(ticket_type), embed=embed, view=TicketButtons())
    await interaction.followup.send(f"Ticket created: {channel.mention}", ephemeral=True)

async def create_index_ticket(interaction, base_key):
    guild = interaction.guild
    member = interaction.user
    for channel in guild.text_channels:
        if channel.topic == f"ticket-{member.id}":
            return await interaction.followup.send(f"You already have an open ticket: {channel.mention}", ephemeral=True)
    if base_key not in INDEX_ROLES:
        return await interaction.followup.send("Invalid base.", ephemeral=True)

    config["ticketCounter"] = config.get("ticketCounter", 0) + 1
    save_config()
    display_name = INDEX_DISPLAY.get(base_key, base_key.title())
    price = INDEX_PRICES.get(base_key, "Ask staff")
    role_id = INDEX_ROLES[base_key]
    emoji = es(E.get(INDEX_EMOJIS.get(base_key, ""), "📦"))
    channel_name = clean_channel_name(display_name)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, manage_messages=True),
    }
    role = guild.get_role(int(role_id))
    if role:
        overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True, manage_messages=True)

    category = guild.get_channel(INDEX_CATEGORY_ID)
    if category is None or not isinstance(category, discord.CategoryChannel):
        return await interaction.followup.send(
            f"❌ Index category not found (ID: `{INDEX_CATEGORY_ID}`). Check the category ID and bot permissions.",
            ephemeral=True
        )

    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        topic=f"ticket-{member.id}",
        overwrites=overwrites
    )

    embed = discord.Embed(
        title=f"{emoji} Index Request: {display_name}",
        description=f"**Ticket opened by {member.mention}**\n\n**Base:** {display_name}\n**Price:** {price}\n\n**Index Base Rules**\n1. PLEASE HAVE AN EMPTY BASE\n2. IF YOU FAIL TO RETURN A BRAINROT THE INDEX WILL BE CANCELED\n3. HIGH VALUE BRAINROTS WILL BE GIVEN ONE AT A TIME\n\nWe only take Garam's+.",
        color=THEME_COLOR
    )
    embed.set_footer(text=FOOTER_TEXT)
    # Ping the specific index role for this base
    await channel.send(content=f"<@&{role_id}>", embed=embed, view=TicketButtons())
    await interaction.followup.send(f"Index ticket created: {channel.mention}", ephemeral=True)

async def create_middleman_ticket(interaction, trade_type, trade_with, trade_details, tip):
    guild = interaction.guild
    member = interaction.user
    for channel in guild.text_channels:
        if channel.topic == f"ticket-{member.id}":
            return await interaction.followup.send(f"You already have an open ticket: {channel.mention}", ephemeral=True)
    if trade_type not in MM_ROLES:
        return await interaction.followup.send("Invalid trade type.", ephemeral=True)

    config["ticketCounter"] = config.get("ticketCounter", 0) + 1
    save_config()
    display_name = MM_DISPLAY.get(trade_type, trade_type)
    role_id = MM_ROLES[trade_type]
    emoji = es(E.get(MM_EMOJIS.get(trade_type, ""), E.get("partner", "🤝")))
    channel_name = clean_channel_name(display_name)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, manage_messages=True),
    }
    role = guild.get_role(int(role_id))
    if role:
        overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True, manage_messages=True)

    category = guild.get_channel(MM_CATEGORY_ID)
    if category is None or not isinstance(category, discord.CategoryChannel):
        return await interaction.followup.send(
            f"❌ Middleman category not found (ID: `{MM_CATEGORY_ID}`). Check the category ID and bot permissions.",
            ephemeral=True
        )

    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        topic=f"ticket-{member.id}",
        overwrites=overwrites
    )

    embed = discord.Embed(
        title=f"{emoji} MiddleMan Request: {display_name}",
        description=f"**Ticket opened by {member.mention}**\n\n**Service:** {display_name}\n**Trade with:** {trade_with}\n**Trade:** {trade_details}\n**Tip:** {tip}\n\nA middleman will assist you shortly.",
        color=THEME_COLOR
    )
    embed.set_footer(text=FOOTER_TEXT)
    # Ping the specific middleman role for this trade type
    await channel.send(content=f"<@&{role_id}>", embed=embed, view=TicketButtons())
    await interaction.followup.send(f"MiddleMan ticket created: {channel.mention}", ephemeral=True)

async def create_staff_ticket(interaction, ticket_type):
    guild = interaction.guild
    member = interaction.user
    for channel in guild.text_channels:
        if channel.topic == f"ticket-{member.id}":
            return await interaction.followup.send(f"You already have an open ticket: {channel.mention}", ephemeral=True)

    category_id = STAFF_CATEGORY_IDS.get(ticket_type)
    if not category_id:
        return await interaction.followup.send("Staff category not set.", ephemeral=True)

    config["ticketCounter"] = config.get("ticketCounter", 0) + 1
    save_config()
    channel_name = clean_channel_name(member.name)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, manage_messages=True),
    }
    for rid in STAFF_PANEL_ROLES:
        role = guild.get_role(int(rid))
        if role:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True, manage_messages=True)

    category = guild.get_channel(category_id)
    channel = await guild.create_text_channel(name=channel_name, category=category, topic=f"ticket-{member.id}", overwrites=overwrites)

    recruitment_ping = "<@&1550995750824050831> <@&1550995745958658088>"
    high_staff_ping = "<@&1550995708793065563> <@&1550995712496631818> <@&1550995725746438254> <@&1550995730053996718>"
    ping = recruitment_ping if ticket_type == "recruitment" else high_staff_ping

    if ticket_type == "recruitment":
        embed = discord.Embed(title="📝 Staff Application", description=f"Welcome {member.mention}! Thanks for applying to **SAB KINGDOM**.\n\n**Application Form**\n```\n1. Discord Username:\n2. Age:\n3. Fluent in English?\n4. Days active per week:\n5. Hours online per day:\n6. How would you handle a toxic member?\n7. Previous staff experience?\n8. Why do you want to join staff?\n9. Anything else?\n```\nCopy, fill, and send.", color=THEME_COLOR)
        embed.set_footer(text="Staff Recruitment • SAB KINGDOM")
    elif ticket_type == "payrolls":
        embed = discord.Embed(title="🎟️ Pay for Rolls", description=f"Ticket opened by {member.mention}\n\n**Staff Pay Rates**\n```\nTest Mod — 2 Garams\nModerator — 3 Garams\nSenior Mod — 4 Garams\nHead Staff — 5 Garams\nAdmin — 7 Garams / 1 Colored Garam\n```\nTell us which role and what you offer.", color=THEME_COLOR)
        embed.set_footer(text="Pay for Rolls • SAB KINGDOM")
    elif ticket_type == "indexprovider":
        embed = discord.Embed(title="📦 Index Provider Application", description=f"Welcome {member.mention}!\n\n**Payment & Collat:** 1+ Drag\n\nTell us why you want to be an index provider, how active you are, and any experience.", color=THEME_COLOR)
        embed.set_footer(text="Index Provider • SAB KINGDOM")
    else:
        embed = discord.Embed(title="🤝 Middleman Application", description=f"Welcome {member.mention}!\n\n**Payment & Collat:** 1+ Drag\n\nTell us why you want to middleman, how often you can be online, and past experience.", color=THEME_COLOR)
        embed.set_footer(text="Middleman Application • SAB KINGDOM")

    await channel.send(content=ping, embed=embed, view=TicketButtons())
    await interaction.followup.send(f"Ticket created: {channel.mention}", ephemeral=True)


async def create_partnership_ticket(interaction):
    guild = interaction.guild
    member = interaction.user
    try:
        for channel in guild.text_channels:
            if channel.topic == f"ticket-{member.id}":
                return await interaction.followup.send(f"You already have an open ticket: {channel.mention}", ephemeral=True)

        config["ticketCounter"] = config.get("ticketCounter", 0) + 1
        save_config()
        channel_name = clean_channel_name(f"partner-{member.name}")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, manage_messages=True),
        }
        staff_role_ids = list(dict.fromkeys(HIGH_STAFF_ROLES + ADS_STAFF_ROLES + [TICKET_TEAM, TICKET_TEAM_T1]))
        for rid in staff_role_ids:
            role = guild.get_role(int(rid))
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=True, attach_files=True,
                    read_message_history=True, manage_messages=True,
                )

        category = guild.get_channel(PARTNERSHIP_CATEGORY_ID)
        if category is None:
            try:
                category = await bot.fetch_channel(PARTNERSHIP_CATEGORY_ID)
            except Exception:
                category = None
        if category is None or not isinstance(category, discord.CategoryChannel):
            return await interaction.followup.send(
                f"❌ Partnership category not found (ID: `{PARTNERSHIP_CATEGORY_ID}`). "
                "Check the category ID and that the bot can see it.",
                ephemeral=True,
            )

        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            topic=f"ticket-{member.id}",
            overwrites=overwrites,
        )

        ping = get_staff_mentions("ads")
        embed = discord.Embed(
            title="🤝 Partnership Application — SAB KINGDOM",
            description=(
                f"Welcome {member.mention}!\n\n"
                "You're applying to become an official **Partner** of this server.\n"
                f"If accepted you receive the <@&{PARTNERS_ROLE_ID}> role and can chat in partner channels.\n\n"
                "**Fill this form and send it here:**\n"
                "```\n"
                "1. Your Discord server / brand name:\n"
                "2. Permanent invite link:\n"
                "3. Member count:\n"
                "4. What do you offer us? (ads, events, collabs, etc.)\n"
                "5. What do you want from us?\n"
                "6. Any previous partnerships?\n"
                "7. Extra notes:\n"
                "```\n"
                "Staff will review your application. Stay patient.\n"
                f"*Staff: use `+partner accept {member.mention}` when accepted.*"
            ),
            color=THEME_COLOR,
        )
        embed.set_footer(text="Partnerships • SAB KINGDOM")
        await channel.send(content=ping or None, embed=embed, view=TicketButtons())
        await interaction.followup.send(f"Partnership ticket created: {channel.mention}", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send(
            "❌ Bot is missing **Manage Channels** (or similar) permission to open partnership tickets.",
            ephemeral=True,
        )
    except Exception as e:
        print(f"create_partnership_ticket error: {e}")
        try:
            await interaction.followup.send(f"❌ Failed to open partnership ticket: {e}", ephemeral=True)
        except Exception:
            pass


async def close_ticket(channel, closer):
    channel_name = channel.name
    channel_id = channel.id
    guild = channel.guild
    try:
        await channel.edit(topic="closed", reason="Ticket closing")
    except Exception:
        pass
    try:
        messages = [msg async for msg in channel.history(limit=50, oldest_first=True)]
        transcript = "---- TICKET LOGS ----\n\n"
        for msg in messages:
            time = msg.created_at.strftime("%d/%m/%Y %H:%M")
            transcript += f"{time} - {msg.author}: {msg.content}\n"
        log_path = f"log_{channel_id}.txt"
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            try:
                await log_channel.send(content=f"Ticket closed by {closer.mention}\nChannel: `{channel_name}`", file=discord.File(log_path, filename="log.txt"))
            except Exception:
                pass
        if os.path.exists(log_path):
            os.remove(log_path)
    except Exception as e:
        print(f"Transcript error: {e}")

    for _ in range(5):
        try:
            ch = guild.get_channel(channel_id)
            if ch is None:
                return True
            await ch.delete(reason=f"Ticket closed by {closer}")
            return True
        except discord.NotFound:
            return True
        except discord.Forbidden:
            return False
        except Exception:
            await asyncio.sleep(0.8)
    return False

# ==================== MOD HELPERS ====================
def _blacklist_pattern(word):
    parts = [re.escape(p) for p in word.split() if p] or [re.escape(word)]
    body = r"\s+".join(parts)
    return re.compile(rf"(?<![A-Za-z0-9_]){body}(?![A-Za-z0-9_])", re.IGNORECASE)

def _find_blacklisted(text):
    if not text:
        return []
    hits = []
    for word in sorted(BLACKLISTED_WORDS, key=len, reverse=True):
        if not word:
            continue
        for m in _blacklist_pattern(word).finditer(text):
            hits.append((m.group(0), word))
    return hits

def censor_blacklisted(text):
    if not text:
        return text
    out = text
    for word in sorted(BLACKLISTED_WORDS, key=len, reverse=True):
        if not word:
            continue
        out = _blacklist_pattern(word).sub(lambda m: "•" * len(m.group(0)), out)
    return out

def parse_duration(text):
    match = re.match(r"^(\d+)([smhd])$", text.lower())
    if not match:
        return None
    num, unit = int(match.group(1)), match.group(2)
    if unit == "s": return timedelta(seconds=num)
    if unit == "m": return timedelta(minutes=num)
    if unit == "h": return timedelta(hours=num)
    if unit == "d": return timedelta(days=num)
    return None

def _sort_sanctions_newest_first(lst):
    def _key(s):
        ts = s.get("timestamp")
        if ts:
            try:
                return datetime.fromisoformat(ts)
            except Exception:
                pass
        return datetime.min.replace(tzinfo=timezone.utc)
    return sorted(lst, key=_key, reverse=True)

def add_sanction(user_id, reason, mod_id):
    uid = str(user_id)
    if uid not in sanctions_data:
        sanctions_data[uid] = []
    now = datetime.now(timezone.utc)
    entry = {"id": len(sanctions_data[uid]) + 1, "reason": reason, "date": now.strftime("%d/%m/%Y %H:%M"), "timestamp": now.isoformat(), "moderator": str(mod_id)}
    sanctions_data[uid].append(entry)
    save_sanctions()
    return entry

async def get_target(ctx, arg=None):
    if ctx.message.mentions:
        return ctx.message.mentions[0]
    if ctx.message.reference:
        ref = ctx.message.reference
        if ref.resolved and hasattr(ref.resolved, "author"):
            return ref.resolved.author
        if ref.message_id:
            try:
                msg = await ctx.channel.fetch_message(ref.message_id)
                return msg.author
            except Exception:
                pass
    if arg:
        arg = arg.strip()
        if arg.isdigit():
            try:
                return await bot.fetch_user(int(arg))
            except Exception:
                pass
        if ctx.guild:
            lower = arg.lower()
            for m in ctx.guild.members:
                if m.name.lower() == lower or (m.display_name and m.display_name.lower() == lower):
                    return m
    return None

async def get_member(guild, user):
    if user is None or guild is None:
        return None
    uid = getattr(user, "id", user)
    try:
        uid = int(uid)
    except Exception:
        return None
    member = guild.get_member(uid)
    if member:
        return member
    try:
        return await guild.fetch_member(uid)
    except Exception:
        return None

def find_role(guild, query):
    """Find role by ID, exact name, partial name, or common short forms."""
    if not query or not guild:
        return None
    query = query.strip()
    # Strip role mention
    if query.startswith("<@&") and query.endswith(">"):
        query = query[3:-1]
    if query.isdigit():
        role = guild.get_role(int(query))
        if role:
            return role
    q = query.lower()
    # 1) Exact name
    role = discord.utils.find(lambda r: r.name.lower() == q, guild.roles)
    if role:
        return role
    # 2) Exact after stripping brackets/prefixes like "[ H ] • "
    def clean(n):
        n = n.lower()
        if "•" in n:
            n = n.split("•")[-1].strip()
        n = n.replace("[", " ").replace("]", " ")
        return " ".join(n.split())
    role = discord.utils.find(lambda r: clean(r.name) == q, guild.roles)
    if role:
        return role
    # 3) Substring match (prefer shortest role name = best match)
    matches = [r for r in guild.roles if q in r.name.lower() or q in clean(r.name)]
    if matches:
        matches.sort(key=lambda r: len(r.name))
        return matches[0]
    # 4) All words present (order independent) e.g. "head recruitment" -> "Head of Recruitment"
    words = [w for w in q.replace("-", " ").split() if w and w not in ("of", "the", "and")]
    if words:
        candidates = []
        for r in guild.roles:
            rn = clean(r.name)
            if all(w in rn for w in words):
                candidates.append(r)
        if candidates:
            candidates.sort(key=lambda r: len(r.name))
            return candidates[0]
    return None

CMD_FAIL_MSG = "I'm sorry this command you tried to use is not going to work with your perm or u just did the command wrong — SAB KINGDOM"

async def cmd_fail(ctx):
    # Never reply to non-staff (members get silence on staff cmds)
    try:
        if not has_staff_permission(ctx.author):
            return
        await ctx.send(CMD_FAIL_MSG)
    except Exception:
        pass

async def cmd_usage(ctx, text):
    # Never reply to non-staff
    try:
        if not has_staff_permission(ctx.author):
            return
        await ctx.send(f"Usage: {text}")
    except Exception:
        pass

async def empty_result(ctx, text):
    try:
        emb = discord.Embed(description=text, color=THEME_COLOR, timestamp=datetime.now(timezone.utc))
        emb.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=emb)
    except Exception:
        pass

async def send_log(embed):
    ch = bot.get_channel(LOG_CHANNEL_ID)
    if ch is None:
        try:
            ch = await bot.fetch_channel(LOG_CHANNEL_ID)
        except Exception:
            return
    try:
        await ch.send(embed=embed)
    except Exception:
        pass

def _temprole_key(gid, uid, rid):
    return f"{gid}:{uid}:{rid}"

async def _remove_temprole(gid, uid, rid):
    key = _temprole_key(gid, uid, rid)
    _temprole_tasks.pop(key, None)
    global temproles_data
    temproles_data = [e for e in temproles_data if not (e.get("guild_id") == gid and e.get("user_id") == uid and e.get("role_id") == rid)]
    save_temproles()
    guild = bot.get_guild(gid)
    if not guild:
        return
    member = guild.get_member(uid)
    if not member:
        try:
            member = await guild.fetch_member(uid)
        except Exception:
            return
    role = guild.get_role(rid)
    if not role or role not in member.roles:
        return
    try:
        await member.remove_roles(role, reason="Temporary role expired")
    except Exception:
        pass

def schedule_temprole(gid, uid, rid, ends_at):
    key = _temprole_key(gid, uid, rid)
    old = _temprole_tasks.pop(key, None)
    if old and not old.done():
        old.cancel()
    now = datetime.now(timezone.utc)
    if ends_at.tzinfo is None:
        ends_at = ends_at.replace(tzinfo=timezone.utc)
    delay = max(0, (ends_at - now).total_seconds())
    async def _runner():
        try:
            await asyncio.sleep(delay)
            await _remove_temprole(gid, uid, rid)
        except asyncio.CancelledError:
            return
    _temprole_tasks[key] = asyncio.create_task(_runner())
    global temproles_data
    temproles_data = [e for e in temproles_data if not (e.get("guild_id") == gid and e.get("user_id") == uid and e.get("role_id") == rid)]
    temproles_data.append({"guild_id": gid, "user_id": uid, "role_id": rid, "ends_at": ends_at.isoformat()})
    save_temproles()

async def restore_temproles():
    now = datetime.now(timezone.utc)
    for entry in list(temproles_data):
        try:
            gid, uid, rid = int(entry["guild_id"]), int(entry["user_id"]), int(entry["role_id"])
            ends = datetime.fromisoformat(entry["ends_at"])
            if ends.tzinfo is None:
                ends = ends.replace(tzinfo=timezone.utc)
            if ends <= now:
                await _remove_temprole(gid, uid, rid)
            else:
                schedule_temprole(gid, uid, rid, ends)
        except Exception as e:
            print(f"temprole restore error: {e}")

async def filter_bad_content(message):
    if not message.guild or message.author.bot:
        return False
    content = message.content or ""
    if not content:
        return False
    content_lower = content.lower()
    member = message.guild.get_member(message.author.id)
    # Immune: Perm 5+
    if member and has_perm(member, 5):
        return False
    async def _warn(text):
        try:
            m = await message.channel.send(text)
            await m.delete(delay=2)
        except Exception:
            pass
    for word in SCAM_WORDS:
        if word in content_lower:
            try:
                await message.delete()
            except Exception:
                pass
            add_sanction(message.author.id, "link", bot.user.id if bot.user else 0)
            await _warn(f"{message.author.mention} this a some bad things you got going")
            return True
    hits = _find_blacklisted(content)
    if hits:
        try:
            await message.delete()
        except Exception:
            pass
        add_sanction(message.author.id, "bad word", bot.user.id if bot.user else 0)
        await _warn(f"{message.author.mention} you cant say this word its blacklisted")
        return True
    return False

# ==================== AUTO PANEL POSTER ====================
async def _clear_bot_messages(channel, limit=15):
    """Remove previous panel messages from this bot so panels reset cleanly."""
    try:
        def is_me(m):
            return m.author.id == bot.user.id
        await channel.purge(limit=limit, check=is_me)
    except Exception as e:
        print(f"Could not clear old panels in {getattr(channel, 'id', '?')}: {e}")


async def _find_panel_message(channel, title_contains: str = None):
    """Find an existing bot panel message to edit in place."""
    try:
        async for msg in channel.history(limit=30):
            if msg.author.id != bot.user.id:
                continue
            if title_contains and msg.embeds:
                for emb in msg.embeds:
                    if emb.title and title_contains.lower() in emb.title.lower():
                        return msg
            if msg.components:
                return msg
            if msg.embeds:
                return msg
    except Exception as e:
        print(f"find panel failed in {getattr(channel, 'id', '?')}: {e}")
    return None


async def _upsert_panel(channel, embed, view=None, title_key: str = None):
    """Edit existing panel message in place, or send if missing. No banner images."""
    existing = await _find_panel_message(channel, title_key)
    if existing:
        kwargs = {"embed": embed, "attachments": []}
        if view is not None:
            kwargs["view"] = view
        await existing.edit(**kwargs)
        return "edited"
    kwargs = {"embed": embed}
    if view is not None:
        kwargs["view"] = view
    await channel.send(**kwargs)
    return "posted"


async def post_panels():
    """Upsert all service panels — edit in place when possible, never wipe other messages."""
    # Support
    try:
        ch = bot.get_channel(PANEL_CHANNEL_SUPPORT) or await bot.fetch_channel(PANEL_CHANNEL_SUPPORT)
        embed = discord.Embed(
            title=f'{es(E["bolt"])}  Server Services',
            description=(
                "Need help? Open a **private ticket** with the menu below.\n"
                "A staff member will assist you shortly."
            ),
            color=THEME_COLOR,
        )
        embed.add_field(name=f'{es(E["support"])} Contact Staff', value="General support & questions", inline=True)
        embed.add_field(name=f'{es(E["scammer"])} Scammer Report', value="Report with evidence", inline=True)
        embed.add_field(name=f'{es(E["reward"])} Claim Reward', value="Claim giveaway prizes", inline=True)
        embed.add_field(name=f'{es(E["ads"])} Promote / Ads', value="Paid server promotions", inline=True)
        embed.add_field(name=f'{es(E["rolls"])} Pay for Rolls', value="Purchase secure rolls", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.set_footer(text=FOOTER_TEXT)
        action = await _upsert_panel(ch, embed, TicketView(), "Server Services")
        print(f"Support panel {action} in {PANEL_CHANNEL_SUPPORT}")
    except Exception as e:
        print(f"Failed to post support panel: {e}")

    # Index
    try:
        ch = bot.get_channel(PANEL_CHANNEL_INDEX) or await bot.fetch_channel(PANEL_CHANNEL_INDEX)
        embed = discord.Embed(
            title=f'{es(E["bolt"])}  Index Department',
            description=(
                "Select a **base** below to open an index ticket.\n"
                "Staff will handle your request in a private channel."
            ),
            color=THEME_COLOR,
        )
        embed.add_field(
            name="Available Bases",
            value=(
                f"{es(E['gold'])} Gold  ·  {es(E['diamond'])} Diamond  ·  {es(E['rainbow'])} Rainbow  ·  {es(E['galaxy'])} Galaxy\n"
                f"{es(E['candy'])} Candy  ·  {es(E['lava'])} Lava  ·  {es(E['radioactive'])} Radioactive  ·  {es(E['yingyang'])} Yin Yang\n"
                f"{es(E['cursed'])} Cursed  ·  {es(E['divine'])} Divine  ·  {es(E['cyber'])} Cyber  ·  {es(E['phantom'])} Phantom  ·  {es(E['crystal'])} Crystal"
            ),
            inline=False,
        )
        embed.add_field(
            name="Rules",
            value=(
                "1️⃣ Empty base required\n"
                "2️⃣ Fail to return a brainrot → index canceled\n"
                "3️⃣ High-value items one at a time\n"
                "4️⃣ We only take **Garam's+** — no lowballs"
            ),
            inline=False,
        )
        embed.set_footer(text=FOOTER_TEXT)
        action = await _upsert_panel(ch, embed, IndexView(), "Index")
        print(f"Index panel {action} in {PANEL_CHANNEL_INDEX}")
    except Exception as e:
        print(f"Failed to post index panel: {e}")

    # Middleman
    try:
        ch = bot.get_channel(PANEL_CHANNEL_MM) or await bot.fetch_channel(PANEL_CHANNEL_MM)
        embed = discord.Embed(
            title=f'{es(E["bolt"])}  Middleman',
            description=(
                "Safe trades only. Pick your service below and a middleman will assist.\n"
                "*Tip your MM. Stay secure.*"
            ),
            color=THEME_COLOR,
        )
        embed.add_field(name="🟡 Cross Trades", value="Cross-trade middleman", inline=True)
        embed.add_field(name="🥇 OG Trades", value="OG trade middleman", inline=True)
        embed.add_field(name="🥈 1B+ Trades", value="High value 1B+", inline=True)
        embed.add_field(name="🥉 500M Trades", value="Mid value 500M", inline=True)
        embed.add_field(name="✅ 0–250M Trades", value="Lower value trades", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.set_footer(text=FOOTER_TEXT)
        action = await _upsert_panel(ch, embed, MiddlemanView(), "Middleman")
        print(f"Middleman panel {action} in {PANEL_CHANNEL_MM}")
    except Exception as e:
        print(f"Failed to post middleman panel: {e}")

    # Staff
    try:
        ch = bot.get_channel(PANEL_CHANNEL_STAFF) or await bot.fetch_channel(PANEL_CHANNEL_STAFF)
        embed = discord.Embed(
            title=f'{es(E["bolt"])}  Staff & Team',
            description=(
                "Interested in joining the team? Open a private ticket below.\n"
                "Every application is reviewed carefully."
            ),
            color=THEME_COLOR,
        )
        embed.add_field(name="📝 Staff Application", value="Apply for a staff position", inline=True)
        embed.add_field(name="🎟️ Pay for Rolls", value="Purchase staff rolls", inline=True)
        embed.add_field(name="📦 Index Provider", value="Become an index provider", inline=True)
        embed.add_field(name="🤝 Middleman App", value="Become a middleman", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.set_footer(text=FOOTER_TEXT)
        action = await _upsert_panel(ch, embed, StaffPanelView(), "Staff")
        print(f"Staff panel {action} in {PANEL_CHANNEL_STAFF}")
    except Exception as e:
        print(f"Failed to post staff panel: {e}")

    # Reaction roles — edit in place
    try:
        ch = bot.get_channel(PANEL_CHANNEL_REACTION) or await bot.fetch_channel(PANEL_CHANNEL_REACTION)
        embed = discord.Embed(
            title=f'{es(E["bolt"])}  Reaction Roles',
            description=(
                "Click the buttons below to **toggle** notification roles.\n"
                "Only get pinged for what you care about."
            ),
            color=THEME_COLOR,
        )
        embed.add_field(
            name="Ping Roles",
            value=(
                "🚨 Important  ·  🛒 Shop  ·  📊 Poll  ·  📢 Announcement\n"
                "💤 Dead Chat  ·  💱 Trade  ·  🔓 Leaks  ·  🧠 SAB\n"
                "🎟️ Invite Reward  ·  🎉 Giveaway"
            ),
            inline=False,
        )
        embed.set_footer(text=FOOTER_TEXT)
        action = await _upsert_panel(ch, embed, ReactionRoleView(), "Reaction Roles")
        print(f"Reaction roles panel {action} in {PANEL_CHANNEL_REACTION}")
    except Exception as e:
        print(f"Failed to post reaction roles panel: {e}")

    # Server rules
    try:
        ch = bot.get_channel(PANEL_CHANNEL_RULES) or await bot.fetch_channel(PANEL_CHANNEL_RULES)
        embed = discord.Embed(
            title=f'{es(E["bolt"])}  Server Rules',
            description=(
                "Failure to follow these rules or Discord TOS will result in moderation.\n"
                "Use common sense."
            ),
            color=THEME_COLOR,
        )
        embed.add_field(name="🤝 1. Respect", value="Treat everyone with kindness.", inline=False)
        embed.add_field(name="🚫 2. No Spam", value="No spam, wall text, excessive caps, or mass pings.", inline=False)
        embed.add_field(name="🔒 3. Protect Info", value="Don't share personal info (names, emails, IPs, addresses, etc.).", inline=False)
        embed.add_field(name="📢 4. No Advertising", value="DM ads and server ads are not allowed.", inline=False)
        embed.add_field(name="🔞 5. No NSFW", value="No NSFW content, links, or 18+ servers.", inline=False)
        embed.add_field(name="❗ 6. 13+ Only", value="You must be 13+ (Discord TOS).", inline=False)
        embed.add_field(name="❌ 7–8. No Hate", value="No racism or homophobia.", inline=False)
        embed.add_field(name="🤬 9. No Swearing", value="Cussing prohibited (incl. VC). *Damn* & *Hell* only exceptions.", inline=False)
        embed.add_field(name="🏛️ 10. No Politics", value="Avoid politics and similar topics.", inline=False)
        embed.add_field(name="🚨 11. No Scamming", value="Do not scam.", inline=False)
        embed.add_field(name="⚠️ 12. No Links", value="Links are auto-deleted and result in a warn.", inline=False)
        embed.set_footer(text=FOOTER_TEXT)
        action = await _upsert_panel(ch, embed, None, "Server Rules")
        print(f"Rules panel {action} in {PANEL_CHANNEL_RULES}")
    except Exception as e:
        print(f"Failed to post rules panel: {e}")

    # Partnerships
    try:
        ch = bot.get_channel(PANEL_CHANNEL_PARTNERSHIPS) or await bot.fetch_channel(PANEL_CHANNEL_PARTNERSHIPS)
        embed = discord.Embed(
            title=f'{es(E["bolt"])}  Partnerships',
            description=(
                "Partner with **SAB KINGDOM**.\n"
                "We work with servers and brands that want real collabs — not spam."
            ),
            color=THEME_COLOR,
        )
        embed.add_field(
            name="How to apply",
            value=(
                "1️⃣ Click **Apply for Partnership** below\n"
                "2️⃣ Fill the form in your private ticket\n"
                "3️⃣ Wait for staff review"
            ),
            inline=False,
        )
        embed.add_field(
            name="Benefits",
            value=(
                f"• Official <@&{PARTNERS_ROLE_ID}> role\n"
                "• Access to partner chat\n"
                "• Cross-promotion opportunities\n"
                "• Priority for joint events / giveaways\n"
                "• Direct line to our team"
            ),
            inline=False,
        )
        embed.add_field(
            name="What we look for",
            value=(
                "• Active community (not dead / not a scam server)\n"
                "• Fair offers both ways\n"
                "• Follows Discord TOS & our rules"
            ),
            inline=False,
        )
        embed.set_footer(text=FOOTER_TEXT)
        action = await _upsert_panel(ch, embed, PartnershipView(), "Partner")
        print(f"Partnerships panel {action} in {PANEL_CHANNEL_PARTNERSHIPS}")
    except Exception as e:
        print(f"Failed to post partnerships panel: {e}")


# ==================== ANTI-NUKE HELPERS ====================
def _antinuke_is_immune(member) -> bool:
    if not member:
        return True
    if getattr(member, "bot", False):
        return True
    if is_owner(member):
        return True
    if member.guild and member.id == member.guild.owner_id:
        return True
    try:
        if any(str(r.id) in ANTI_NUKE_IMMUNE_ROLES for r in member.roles):
            return True
    except Exception:
        pass
    return False


# Keywords often used by nuke / raid bots (name or display name)
_NUKE_BOT_NAME_KEYWORDS = (
    "nuke", "nuker", "raid", "raider", "wizz", "wizzard", "destroy", "crash",
    "massban", "masskick", "anti-raid", "antiraid", "server-killer", "serverkiller",
)


def _is_dangerous_bot(member) -> bool:
    """
    True if this bot looks like a nuke/raid tool (dangerous perms and/or nuke-style name).
    Normal utility bots (music, tickets, etc.) with limited perms return False.
    """
    if not member or not getattr(member, "bot", False):
        return False
    try:
        perms = member.guild_permissions
        dangerous_perms = (
            perms.administrator
            or perms.ban_members
            or perms.kick_members
            or perms.manage_guild
            or perms.manage_roles
            or perms.manage_channels
            or perms.manage_webhooks
            or perms.mention_everyone
        )
        if dangerous_perms:
            return True
    except Exception:
        pass
    name_blob = f"{getattr(member, 'name', '')} {getattr(member, 'display_name', '')} {getattr(member, 'global_name', '') or ''}".lower()
    if any(k in name_blob for k in _NUKE_BOT_NAME_KEYWORDS):
        return True
    return False


def _antinuke_record(guild_id: int, user_id: int, action: str) -> tuple:
    """Record action. Returns (action_count, combined_dangerous_count)."""
    now = datetime.now(timezone.utc).timestamp()
    g = _antinuke_actions.setdefault(guild_id, {})
    u = g.setdefault(user_id, {})
    times = u.setdefault(action, [])
    cutoff = now - ANTI_NUKE_WINDOW
    times[:] = [t for t in times if t >= cutoff]
    times.append(now)
    # combined: all tracked action timestamps for this user
    combined = 0
    for act, lst in u.items():
        lst[:] = [x for x in lst if x >= cutoff]
        combined += len(lst)
    return len(times), combined


async def _antinuke_recent_executor(guild: discord.Guild, action: discord.AuditLogAction, target_id: int = None, max_age: float = 8.0):
    """
    Find who performed an audit action very recently.
    Returns (executor User, entry) or (None, None).
    """
    try:
        await asyncio.sleep(0.8)  # give Discord time to write the audit log
        now = datetime.now(timezone.utc)
        async for entry in guild.audit_logs(limit=6, action=action):
            if entry.created_at is None:
                continue
            age = (now - entry.created_at.replace(tzinfo=timezone.utc)).total_seconds()
            if age > max_age:
                continue
            if target_id is not None:
                tid = getattr(entry.target, "id", None)
                if tid is None and entry.target is not None:
                    try:
                        tid = int(entry.target)
                    except Exception:
                        tid = None
                if tid != target_id:
                    continue
            if entry.user is None:
                continue
            return entry.user, entry
    except discord.Forbidden:
        print("[ANTI-NUKE] Missing View Audit Log permission — cannot auto-detect.")
    except Exception as e:
        print(f"[ANTI-NUKE] audit fetch error ({action}): {e}")
    return None, None


async def _antinuke_punish(guild: discord.Guild, member: discord.Member, action: str, count: int, combined: int = 0):
    """Timeout, strip roles, optionally ban, and alert staff."""
    if not ANTI_NUKE_ENABLED or not member or not guild:
        return
    key = f"{guild.id}:{member.id}"
    if key in _antinuke_punished:
        return
    _antinuke_punished.add(key)
    responses = []
    try:
        # 1) Timeout
        try:
            until = datetime.now(timezone.utc) + timedelta(hours=ANTI_NUKE_TIMEOUT_HOURS)
            await member.timeout(until, reason=f"Anti-nuke: mass {action} ({count})")
            responses.append(f"{ANTI_NUKE_TIMEOUT_HOURS}h timeout")
        except Exception as e:
            responses.append(f"timeout failed ({e})")

        # 2) Strip all removable roles
        removable = [
            r for r in member.roles
            if r != guild.default_role and not r.managed and r < guild.me.top_role
        ]
        if removable:
            try:
                await member.remove_roles(*removable, reason=f"Anti-nuke: mass {action}")
                responses.append(f"stripped {len(removable)} roles")
            except Exception:
                ok = 0
                for r in removable:
                    try:
                        await member.remove_roles(r, reason=f"Anti-nuke: mass {action}")
                        ok += 1
                    except Exception:
                        pass
                responses.append(f"stripped {ok}/{len(removable)} roles")

        # 3) Ban attacker (optional but recommended)
        if ANTI_NUKE_BAN_ON_TRIGGER:
            try:
                await guild.ban(
                    member,
                    reason=f"Anti-nuke auto-ban: mass {action} ({count} in {ANTI_NUKE_WINDOW}s)",
                    delete_message_days=0,
                )
                responses.append("banned")
            except Exception as e:
                responses.append(f"ban failed ({e})")

        emb = discord.Embed(
            title="🚨🚨 ANTI-NUKE TRIGGERED — CRITICAL",
            description=(
                f"**Server protection fired.**\n\n"
                f"**User:** {member.mention} (`{member.id}`)\n"
                f"**Detected:** mass `{action}`\n"
                f"**Count:** `{count}` in `{ANTI_NUKE_WINDOW}s`\n"
                f"**Combined actions:** `{combined}`\n"
                f"**Auto response:** {', '.join(responses)}\n\n"
                f"⚠️ **Review this account immediately.**"
            ),
            color=0xFF0000,
            timestamp=datetime.now(timezone.utc),
        )
        emb.set_footer(text=f"{FOOTER_TEXT} • Anti-Nuke System")
        ping_roles = " ".join(f"<@&{r}>" for r in ANTI_NUKE_IMMUNE_ROLES[:4])
        content = f"🚨 **ANTI-NUKE** {ping_roles}".strip()
        ch = bot.get_channel(LOG_CHANNEL_ID)
        if ch:
            try:
                await ch.send(content=content, embed=emb)
            except Exception:
                pass
        print(f"[ANTI-NUKE] CRITICAL — Punished {member} ({member.id}) for {action} x{count} combined={combined} → {responses}")
    finally:
        await asyncio.sleep(8)
        _antinuke_punished.discard(key)


async def _antinuke_check(guild: discord.Guild, user: discord.abc.User, action: str):
    """Record + punish if threshold or combined score exceeded."""
    if not ANTI_NUKE_ENABLED or not guild or not user:
        return
    if getattr(user, "bot", False) and user.id == getattr(bot.user, "id", None):
        return
    threshold = ANTI_NUKE_THRESHOLDS.get(action)
    if not threshold and action not in ANTI_NUKE_THRESHOLDS:
        return
    member = guild.get_member(user.id)
    if member is None:
        try:
            member = await guild.fetch_member(user.id)
        except Exception:
            return
    if _antinuke_is_immune(member):
        return
    count, combined = _antinuke_record(guild.id, user.id, action)
    triggered = False
    reason = action
    if threshold and count >= threshold:
        triggered = True
    elif combined >= ANTI_NUKE_COMBINED_THRESHOLD:
        triggered = True
        reason = f"{action}+combined"
    if triggered:
        await _antinuke_punish(guild, member, reason, count, combined)


async def _antinuke_from_event(guild, audit_action, target_id, track_as: str):
    """Shared path: resolve executor from audit log then check thresholds."""
    if not ANTI_NUKE_ENABLED or not guild:
        return
    user, _ = await _antinuke_recent_executor(guild, audit_action, target_id=target_id)
    if user:
        await _antinuke_check(guild, user, track_as)


# ==================== INVITE + UTILITY HELPERS ====================
async def refresh_invite_cache(guild):
    """Cache current invite uses for tracking who invited whom."""
    try:
        invites = await guild.invites()
        _invite_cache[guild.id] = {inv.code: inv.uses or 0 for inv in invites}
    except Exception:
        _invite_cache.setdefault(guild.id, {})

async def find_used_invite(guild):
    """Compare invite uses to find which invite was used on join."""
    old = _invite_cache.get(guild.id, {})
    try:
        invites = await guild.invites()
    except Exception:
        return None, None
    used = None
    inviter = None
    new_map = {}
    for inv in invites:
        new_map[inv.code] = inv.uses or 0
        before = old.get(inv.code, 0)
        if (inv.uses or 0) > before:
            used = inv
            inviter = inv.inviter
    _invite_cache[guild.id] = new_map
    return used, inviter


# ==================== EVENTS ====================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("SAB KINGDOM bot is ready!")
    print("=" * 50)
    print(f"ANTI-NUKE: {'ENABLED' if ANTI_NUKE_ENABLED else 'DISABLED'} | window={ANTI_NUKE_WINDOW}s | ban={ANTI_NUKE_BAN_ON_TRIGGER}")
    print(f"ANTI-NUKE thresholds: {ANTI_NUKE_THRESHOLDS}")
    print(f"ANTI-NUKE combined limit: {ANTI_NUKE_COMBINED_THRESHOLD}")
    print("=" * 50)
    # DND status + Streaming "SAB KINGDOM tickets"
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Streaming(name="SAB KINGDOM tickets", url="https://www.twitch.tv/discord"),
    )
    for guild in bot.guilds:
        try:
            resolve_role_ids(guild)
        except Exception as e:
            print(f"Role resolve failed: {e}")
        # Keep the bot's real username — Discord nicknames cannot have a real glow effect
        try:
            if guild.me and guild.me.nick is not None:
                await guild.me.edit(nick=None)
        except Exception as e:
            print(f"Nickname clear failed in {guild.id}: {e}")
    try:
        await restore_temproles()
    except Exception as e:
        print(f"Temp role restore failed: {e}")

    # Auto-grant High Ranking Staff to Server Manager+
    for guild in bot.guilds:
        try:
            for member in guild.members:
                if not member.bot:
                    await ensure_high_ranking_staff(member)
        except Exception as e:
            print(f"High Ranking Staff sync failed for {guild.id}: {e}")

    bot.add_view(TicketView())
    bot.add_view(TicketButtons())
    bot.add_view(IndexView())
    bot.add_view(MiddlemanView())
    bot.add_view(StaffPanelView())
    bot.add_view(ReactionRoleView())
    bot.add_view(PartnershipView())

    # Auto-post all panels
    await post_panels()
    # Cache invites for tracker
    for guild in bot.guilds:
        try:
            await refresh_invite_cache(guild)
        except Exception as e:
            print(f"Invite cache failed for {guild.id}: {e}")

    # Announce anti-nuke status (priority system)
    try:
        ch = bot.get_channel(LOG_CHANNEL_ID)
        if ch and ANTI_NUKE_ENABLED:
            emb = discord.Embed(
                title="🛡️ Anti-Nuke Online — SAB KINGDOM",
                description=(
                    "**Server protection is active and monitoring.**\n\n"
                    f"**Window:** `{ANTI_NUKE_WINDOW}s`\n"
                    f"**Ban on trigger:** `{ANTI_NUKE_BAN_ON_TRIGGER}`\n"
                    f"**Combined limit:** `{ANTI_NUKE_COMBINED_THRESHOLD}`\n\n"
                    "Auto-detects mass bans, kicks, channel/role wipes, "
                    "dangerous perms, webhooks, **nuke/dangerous bot adds**, and prunes.\n"
                    "Normal utility bots are ignored."
                ),
                color=0xFF0000,
            )
            emb.set_footer(text=f"{FOOTER_TEXT} • Anti-Nuke System")
            await ch.send(embed=emb)
    except Exception as e:
        print(f"Anti-nuke startup log failed: {e}")

@bot.event
async def on_member_ban(guild, user):
    try:
        await _antinuke_from_event(guild, discord.AuditLogAction.ban, user.id, "ban")
    except Exception as e:
        print(f"anti-nuke ban track error: {e}")


@bot.event
async def on_member_unban(guild, user):
    try:
        await _antinuke_from_event(guild, discord.AuditLogAction.unban, user.id, "unban")
    except Exception as e:
        print(f"anti-nuke unban track error: {e}")


@bot.event
async def on_guild_channel_delete(channel):
    try:
        await _antinuke_from_event(channel.guild, discord.AuditLogAction.channel_delete, channel.id, "channel_delete")
    except Exception as e:
        print(f"anti-nuke channel_delete error: {e}")


@bot.event
async def on_guild_channel_create(channel):
    try:
        await _antinuke_from_event(channel.guild, discord.AuditLogAction.channel_create, channel.id, "channel_create")
    except Exception as e:
        print(f"anti-nuke channel_create error: {e}")


@bot.event
async def on_guild_role_delete(role):
    try:
        await _antinuke_from_event(role.guild, discord.AuditLogAction.role_delete, role.id, "role_delete")
    except Exception as e:
        print(f"anti-nuke role_delete error: {e}")


@bot.event
async def on_guild_role_create(role):
    try:
        await _antinuke_from_event(role.guild, discord.AuditLogAction.role_create, role.id, "role_create")
    except Exception as e:
        print(f"anti-nuke role_create error: {e}")


@bot.event
async def on_guild_role_update(before, after):
    """Auto-detect dangerous permission grants on roles."""
    try:
        if not ANTI_NUKE_ENABLED:
            return
        bp, ap = before.permissions, after.permissions
        gained = (
            (not bp.administrator and ap.administrator)
            or (not bp.ban_members and ap.ban_members)
            or (not bp.manage_guild and ap.manage_guild)
            or (not bp.manage_roles and ap.manage_roles)
            or (not bp.manage_channels and ap.manage_channels)
        )
        if not gained:
            return
        user, _ = await _antinuke_recent_executor(
            after.guild, discord.AuditLogAction.role_update, target_id=after.id
        )
        if user:
            await _antinuke_check(after.guild, user, "perm_grant")
    except Exception as e:
        print(f"anti-nuke role_update error: {e}")


@bot.event
async def on_webhooks_update(channel):
    try:
        user, _ = await _antinuke_recent_executor(
            channel.guild, discord.AuditLogAction.webhook_create, target_id=None
        )
        if user:
            await _antinuke_check(channel.guild, user, "webhook")
    except Exception as e:
        print(f"anti-nuke webhook error: {e}")



async def relay_sammy_announcement(message: discord.Message):
    """Forward Sammy's announcement (text + images) to SAB leaks channel and ping Leaks role."""
    if not SAMMY_USER_IDS:
        return
    if str(message.author.id) not in [str(x) for x in SAMMY_USER_IDS]:
        return
    if SAMMY_SOURCE_GUILD_ID is not None and message.guild and message.guild.id != SAMMY_SOURCE_GUILD_ID:
        return
    if SAMMY_ANNOUNCE_CHANNEL_IDS and message.channel.id not in SAMMY_ANNOUNCE_CHANNEL_IDS:
        return
    # Don't re-relay from the leaks channel itself
    if message.channel.id == SAB_LEAKS_CHANNEL_ID:
        return

    target = bot.get_channel(SAB_LEAKS_CHANNEL_ID)
    if target is None:
        try:
            target = await bot.fetch_channel(SAB_LEAKS_CHANNEL_ID)
        except Exception as e:
            print(f"SAB leaks channel fetch failed: {e}")
            return

    text = (message.content or "").strip()
    files = []
    image_urls = []
    for att in message.attachments:
        try:
            data = await att.read()
            files.append(discord.File(__import__("io").BytesIO(data), filename=att.filename))
        except Exception:
            if att.url:
                image_urls.append(att.url)
    # Also pick image embeds from the original message
    for emb in message.embeds:
        if emb.image and emb.image.url:
            image_urls.append(emb.image.url)
        if emb.thumbnail and emb.thumbnail.url:
            image_urls.append(emb.thumbnail.url)

    ping = f"<@&{SAB_LEAKS_ROLE_ID}>"
    header = discord.Embed(
        title="🔓 SAB Leaks — Sammy Announcement",
        description=text or "*No text — see attachments/images below.*",
        color=THEME_COLOR,
        timestamp=datetime.now(timezone.utc),
    )
    header.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
    header.add_field(name="Source", value=f"[Jump to message]({message.jump_url})", inline=False)
    header.set_footer(text=FOOTER_TEXT)
    if image_urls and not files:
        header.set_image(url=image_urls[0])

    try:
        await target.send(content=ping, embed=header, files=files[:10] if files else None)
        # Extra images beyond the first if we only had URLs
        for url in image_urls[1:5]:
            emb = discord.Embed(color=THEME_COLOR)
            emb.set_image(url=url)
            emb.set_footer(text=FOOTER_TEXT)
            await target.send(embed=emb)
        print(f"[SAB LEAKS] Relayed Sammy message from {message.author} ({message.id})")
    except Exception as e:
        print(f"SAB leaks relay failed: {e}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # Relay Sammy announcements to SAB leaks (runs even across guilds the bot is in)
    try:
        await relay_sammy_announcement(message)
    except Exception as e:
        print(f"sammy relay error: {e}")
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        # Do not reply with prefix when the message is a reply to the bot (or any reply)
        is_reply = message.reference is not None
        content = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        if len(content) < 3 and not is_reply:
            await message.channel.send(f"My prefix on this server is: `{PREFIX}`")
            return
    if await filter_bad_content(message):
        return
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild or message.channel.id in clearing_channels:
        return
    content = message.content or "*no text*"
    snipe_data[str(message.channel.id)] = {
        "content": content,
        "author": str(message.author),
        "author_id": message.author.id,
        "time": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    save_snipe()

@bot.event
async def on_member_join(member):
    # Anti-nuke: only punish when a *dangerous / nuke* bot is added.
    # Normal utility bots (music, tickets, etc.) are ignored.
    try:
        if member.bot and ANTI_NUKE_ENABLED:
            # Brief delay so Discord applies the integration role / perms
            await asyncio.sleep(1.2)
            # Refresh member so guild_permissions are up to date
            try:
                member = member.guild.get_member(member.id) or await member.guild.fetch_member(member.id)
            except Exception:
                pass
            if member and _is_dangerous_bot(member):
                user, _ = await _antinuke_recent_executor(
                    member.guild, discord.AuditLogAction.bot_add, target_id=member.id
                )
                if user:
                    await _antinuke_check(member.guild, user, "bot_add")
                # Also remove the nuke bot itself so it cannot act
                try:
                    await member.ban(reason="Anti-nuke: dangerous/nuke bot auto-removed")
                    print(f"[ANTI-NUKE] Banned dangerous bot {member} ({member.id})")
                except Exception as be:
                    try:
                        await member.kick(reason="Anti-nuke: dangerous/nuke bot auto-removed")
                        print(f"[ANTI-NUKE] Kicked dangerous bot {member} ({member.id})")
                    except Exception as ke:
                        print(f"[ANTI-NUKE] Could not remove dangerous bot: ban={be} kick={ke}")
            else:
                # Normal bot — do not punish the adder
                print(f"[ANTI-NUKE] Normal bot joined (ignored): {member} ({getattr(member, 'id', '?')})")
    except Exception as e:
        print(f"anti-nuke bot_add error: {e}")
    # Don't run welcome / invite tracker for bots
    if getattr(member, "bot", False):
        return
    if str(member.id) in blacklist:
        try:
            await member.ban(reason="Blacklisted (auto on join)")
        except Exception:
            pass
        return
    # Auto High Ranking Staff if they already have SM+
    try:
        await ensure_high_ranking_staff(member)
    except Exception as e:
        print(f"High Ranking Staff on join error: {e}")
    # Invite tracking
    used_invite, inviter = None, None
    try:
        used_invite, inviter = await find_used_invite(member.guild)
    except Exception as e:
        print(f"Invite track error: {e}")

    account_age = datetime.now(timezone.utc) - member.created_at
    is_new_account = account_age < timedelta(hours=NEW_ACCOUNT_HOURS)

    try:
        ch = bot.get_channel(WELCOME_CHANNEL_ID) or await bot.fetch_channel(WELCOME_CHANNEL_ID)
        desc = f"👏 Welcome {member.mention} to **{BRAND_NAME}**!\n*Stay dark.*"
        if is_new_account:
            desc += f"\n\n⚠️ **New account** — created {discord.utils.format_dt(member.created_at, 'R')}"
        emb = discord.Embed(
            title="⚡ New Member Joined!",
            description=desc,
            color=THEME_COLOR,
            timestamp=datetime.now(timezone.utc)
        )
        emb.add_field(name="Account Created", value=discord.utils.format_dt(member.created_at, "R"), inline=True)
        emb.add_field(name="Member #", value=f"`{member.guild.member_count}`", inline=True)
        if inviter:
            emb.add_field(name="Invited by", value=f"{inviter.mention}", inline=True)
        if used_invite:
            emb.add_field(name="Invite", value=f"`{used_invite.code}` ({used_invite.uses or 0} uses)", inline=True)
        emb.set_thumbnail(url=member.display_avatar.url)
        emb.set_footer(text=FOOTER_TEXT)
        await ch.send(embed=emb)
    except Exception as e:
        print(f"Welcome failed: {e}")

    # Log invite to tracker channel
    if inviter or used_invite:
        try:
            tch = bot.get_channel(INVITE_TRACKER_ID) or await bot.fetch_channel(INVITE_TRACKER_ID)
            inv_emb = discord.Embed(
                title="⚡ Invite Tracker",
                description=(
                    f"**Member:** {member.mention} (`{member.id}`)\n"
                    f"**Inviter:** {inviter.mention if inviter else 'Unknown'}\n"
                    f"**Code:** `{used_invite.code if used_invite else '?'}`\n"
                    f"**Uses:** `{used_invite.uses if used_invite else '?'}`"
                ),
                color=THEME_COLOR,
                timestamp=datetime.now(timezone.utc),
            )
            if is_new_account:
                inv_emb.add_field(name="⚠️ Flag", value="Account younger than 48h", inline=False)
            inv_emb.set_footer(text=FOOTER_TEXT)
            await tch.send(embed=inv_emb)
        except Exception as e:
            print(f"Invite tracker failed: {e}")

@bot.event
async def on_member_remove(member):
    # Anti-nuke: auto-detect kicks via audit log
    try:
        user, _ = await _antinuke_recent_executor(
            member.guild, discord.AuditLogAction.kick, target_id=member.id, max_age=10.0
        )
        if user:
            await _antinuke_check(member.guild, user, "kick")
        # Member prune (mass kick)
        user2, entry2 = await _antinuke_recent_executor(
            member.guild, discord.AuditLogAction.member_prune, target_id=None, max_age=10.0
        )
        if user2:
            await _antinuke_check(member.guild, user2, "prune")
    except Exception as e:
        print(f"anti-nuke kick track error: {e}")
    # Leave log
    try:
        ch = bot.get_channel(LEAVES_CHANNEL_ID) or await bot.fetch_channel(LEAVES_CHANNEL_ID)
        emb = discord.Embed(
            title="⚡ Member Left",
            description=f"👋 **{member}** has left **{BRAND_NAME}**.",
            color=THEME_COLOR,
            timestamp=datetime.now(timezone.utc)
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        emb.set_footer(text=FOOTER_TEXT)
        await ch.send(embed=emb)
    except Exception as e:
        print(f"Leave failed: {e}")

@bot.event
async def on_member_update(before, after):
    # Auto-grant High Ranking Staff when someone gets Server Manager+
    try:
        if before.roles != after.roles:
            await ensure_high_ranking_staff(after)
    except Exception as e:
        print(f"High Ranking Staff update error: {e}")
    try:
        if before.premium_since is None and after.premium_since is not None:
            role = after.guild.get_role(BOOST_ROLE_ID)
            if role and role not in after.roles:
                try:
                    await after.add_roles(role, reason="Server boost — VIP")
                except Exception:
                    pass
            emb = discord.Embed(title=f"⚡ Thank you for boosting! — {BRAND_NAME}", description=f"{after.mention} boosted the server and received 💎 **VIP**!", color=THEME_COLOR, timestamp=datetime.now(timezone.utc))
            emb.set_thumbnail(url=after.display_avatar.url)
            emb.set_footer(text=FOOTER_TEXT)
            ch = bot.get_channel(BOOST_CHANNEL_ID) or await bot.fetch_channel(BOOST_CHANNEL_ID)
            await ch.send(content=after.mention, embed=emb)
    except Exception as e:
        print(f"Boost error: {e}")

@bot.event
async def on_command_error(ctx, error):
    # Silent ignore: unknown cmds, missing Discord perms, or non-staff blocked by global check
    if isinstance(error, (commands.CommandNotFound, commands.MissingPermissions, commands.CheckFailure)):
        return
    if isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument, commands.UserInputError)):
        # Only reply with usage/fail if the invoker is staff (members stay silent)
        if has_staff_permission(ctx.author):
            await cmd_fail(ctx)
        return

# Members may only use PUBLIC_COMMAND_NAMES; everyone else needs staff permission.
# Non-staff hitting other commands get a silent CheckFailure (no reply).
@bot.check
async def _require_staff_or_public(ctx):
    if ctx.command is None:
        return True
    # Root command name (handles groups like "role all")
    root = (ctx.command.root_parent or ctx.command).name.lower()
    aliases = set()
    cmd = ctx.command.root_parent or ctx.command
    if getattr(cmd, "aliases", None):
        aliases = {a.lower() for a in cmd.aliases}
    if root in PUBLIC_COMMAND_NAMES or any(a in PUBLIC_COMMAND_NAMES for a in aliases):
        return True
    if has_staff_permission(ctx.author):
        return True
    # Ticket opener may close their own ticket (no staff role required)
    if root == "close" and is_ticket_opener(getattr(ctx, "channel", None), ctx.author):
        return True
    raise commands.CheckFailure("Members may only use public commands")

# ==================== COMMANDS ====================
@bot.command()
async def ping(ctx):
    emb = discord.Embed(title=f"⚡ Pong — {BRAND_NAME}", description=f"Latency: **`{round(bot.latency*1000)}ms`**", color=THEME_COLOR)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def help(ctx):
    # Staff-only (enforced by global check + explicit guard)
    if not has_staff_permission(ctx.author):
        return
    emb = discord.Embed(
        title=f"⚡ {BRAND_NAME} Help",
        description=(
            f"**Prefix:** `{PREFIX}`\n"
            "Higher perm can use lower perm commands.\n"
            "**Public (everyone):** `+snipe` `+mc` `+ping` `+userinfo` `+serverinfo` `+i` `+lb` `+avatar` `+roleinfo`\n"
            "**All other commands require staff.**\n\n"
            "**Perm 1**\n"
            "`+warn` `+tempmute` `+unmute` `+mutelist` `+sanctions` `+perms` `+poll`\n\n"
            "**Perm 2**\n"
            "`+del sanction`\n\n"
            "**Perm 3**\n"
            "`+clearwarns`\n\n"
            "**Perm 4**\n"
            "`+clear` `+lock` `+unlock` `+derank` `+addrole` `+delrole` `+slowmode` `+nick`\n\n"
            "**Perm 5**\n"
            "`+banlist` `+baninfo` `+blist` `+linkalt` `+softban` `+say`\n\n"
            "**Perm 6**\n"
            "`+temprole` `+modstats` `+syncroles` `+create` `+changeperm` `+role all` `+lockdown`\n\n"
            "**🛡️ Anti-Nuke (critical — Perm 6)**\n"
            "`+antinuke status`  `+antinuke on`  `+antinuke off`\n"
            "Auto-protects against mass ban/kick/channel/role wipes.\n\n"
            "**Ban / Kick / Blacklist (role-gated)**\n"
            "`+ban` `+unban` `+kick` `+bl` `+unbl`\n"
            "Requires the matching command-perm role.\n\n"
            "**Tickets (staff)**\n"
            "`+claim` `+close` `+rename` `+add` `+remove` `+commands`\n\n"
            "**Staff only**\n"
            "`+help`"
        ),
        color=THEME_COLOR
    )
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)


@bot.command(name="antinuke")
async def antinuke_cmd(ctx, mode: str = None):
    """+antinuke [on|off|status] — toggle or view anti-nuke (Perm 6).
    Auto-detects mass ban/kick/channel/role/webhook/bot-add/perm grants via audit logs.
    """
    global ANTI_NUKE_ENABLED
    if not has_perm(ctx.author, 6):
        return await cmd_fail(ctx)
    if mode is None or mode.lower() in ("status", "info"):
        me = ctx.guild.me
        perms = me.guild_permissions if me else None
        lines = [
            f"**Enabled:** `{ANTI_NUKE_ENABLED}`",
            f"**Window:** `{ANTI_NUKE_WINDOW}s`",
            f"**Ban on trigger:** `{ANTI_NUKE_BAN_ON_TRIGGER}`",
            f"**Combined threshold:** `{ANTI_NUKE_COMBINED_THRESHOLD}`",
            "",
            "**Auto-detects:**",
            "• Mass bans / kicks / unbans",
            "• Channel create / delete spam",
            "• Role create / delete spam",
            "• Dangerous permission grants",
            "• Webhook spam / **dangerous (nuke) bot adds** / prune",
            "• Normal utility bots are **not** treated as threats",
            "",
            "**Thresholds:**",
        ]
        for k, v in ANTI_NUKE_THRESHOLDS.items():
            lines.append(f"• `{k}` → **{v}** in {ANTI_NUKE_WINDOW}s")
        if perms is not None:
            lines.append("")
            lines.append("**Bot permissions:**")
            lines.append(f"• View Audit Log: `{'✅' if perms.view_audit_log else '❌ NEEDED'}`")
            lines.append(f"• Manage Roles: `{'✅' if perms.manage_roles else '❌ NEEDED'}`")
            lines.append(f"• Moderate Members: `{'✅' if perms.moderate_members else '❌ (timeout)'}`")
            lines.append(f"• Ban Members: `{'✅' if perms.ban_members else '❌ (auto-ban)'}`")
        emb = discord.Embed(title=f"🛡️ Anti-Nuke Protection — {BRAND_NAME}", description="\n".join(lines), color=THEME_COLOR)
        emb.set_footer(text=FOOTER_TEXT)
        return await ctx.send(embed=emb)
    m = mode.lower()
    if m in ("on", "enable", "true", "1"):
        ANTI_NUKE_ENABLED = True
        return await ctx.send(embed=discord.Embed(
            description="✅ Anti-nuke **enabled** — auto-detecting dangerous actions.",
            color=THEME_COLOR,
        ))
    if m in ("off", "disable", "false", "0"):
        ANTI_NUKE_ENABLED = False
        return await ctx.send(embed=discord.Embed(
            description="⚠️ Anti-nuke **disabled**.",
            color=0xFFAA00,
        ))
    return await cmd_usage(ctx, "`+antinuke [on|off|status]`")


@bot.command(name="partner")
async def partner_cmd(ctx, action: str = None, *, target: str = None):
    """+partner accept @user | +partner remove @user — grant/remove Partners role (high staff)."""
    if not has_high_staff_permission(ctx.author):
        return await cmd_fail(ctx)
    if not action or action.lower() not in ("accept", "add", "remove", "revoke", "deny"):
        return await cmd_usage(ctx, "`+partner accept @user`  or  `+partner remove @user`")

    user = None
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
    elif ctx.message.reference:
        user = await get_target(ctx, None)
    elif target:
        # strip leftover action words if user typed "+partner accept @user"
        cleaned = target.strip()
        for word in ("accept", "add", "remove", "revoke", "deny"):
            if cleaned.lower().startswith(word + " "):
                cleaned = cleaned[len(word):].strip()
        user = await get_target(ctx, cleaned)

    if not user:
        return await cmd_usage(ctx, "`+partner accept @user`  or  `+partner remove @user`")

    member = await get_member(ctx.guild, user)
    if not member:
        return await ctx.send("Could not find that member on this server.")

    role = ctx.guild.get_role(PARTNERS_ROLE_ID)
    if not role:
        return await ctx.send(
            f"❌ Partners role not found (ID `{PARTNERS_ROLE_ID}`). "
            "Create the role or fix the ID in the bot config."
        )

    if role >= ctx.guild.me.top_role:
        return await ctx.send("❌ My role must be **above** the Partners role so I can assign it.")

    act = action.lower()
    try:
        if act in ("accept", "add"):
            if role in member.roles:
                return await ctx.send(f"{member.mention} already has {role.mention}.")
            await member.add_roles(role, reason=f"Partnership accepted by {ctx.author}")
            emb = discord.Embed(
                title=f"⚡ Partner Accepted — {BRAND_NAME}",
                description=(
                    f"{member.mention} is now a **Partner**.\n"
                    f"**Role:** {role.mention}\n"
                    "They can now type in partner channels."
                ),
                color=THEME_COLOR,
            )
            emb.set_footer(text=FOOTER_TEXT)
            await ctx.send(embed=emb)
        else:
            if role not in member.roles:
                return await ctx.send(f"{member.mention} does not have {role.mention}.")
            await member.remove_roles(role, reason=f"Partnership removed by {ctx.author}")
            emb = discord.Embed(
                title=f"⚡ Partner Removed — {BRAND_NAME}",
                description=f"Removed {role.mention} from {member.mention}.",
                color=THEME_COLOR,
            )
            emb.set_footer(text=FOOTER_TEXT)
            await ctx.send(embed=emb)
    except discord.Forbidden:
        await ctx.send("❌ Missing permission to manage the Partners role (bot role hierarchy / Manage Roles).")
    except Exception as e:
        await ctx.send(f"Failed: {e}")


@bot.command(name="setsammy")
async def setsammy_cmd(ctx, action: str = None, user_id: str = None):
    """+setsammy add|remove|list [user_id] — configure Sammy user IDs for SAB leaks relay (Perm 6)."""
    global SAMMY_USER_IDS
    if not has_perm(ctx.author, 6):
        return await cmd_fail(ctx)
    if action is None or action.lower() in ("list", "status"):
        ids = SAMMY_USER_IDS or ["*(none set — relay disabled)*"]
        emb = discord.Embed(
            title=f"⚡ Sammy Relay — {BRAND_NAME}",
            description=(
                f"**Leaks channel:** <#{SAB_LEAKS_CHANNEL_ID}>\n"
                f"**Ping role:** <@&{SAB_LEAKS_ROLE_ID}>\n"
                f"**Tracked IDs:**\n" + "\n".join(f"• `{i}`" for i in ids)
            ),
            color=THEME_COLOR,
        )
        emb.set_footer(text=FOOTER_TEXT)
        return await ctx.send(embed=emb, allowed_mentions=discord.AllowedMentions.none())
    a = action.lower()
    if a in ("add", "set") and user_id:
        uid = user_id.strip().replace("<@", "").replace("!", "").replace(">", "")
        if not uid.isdigit():
            return await cmd_usage(ctx, "`+setsammy add <user_id>`")
        if uid not in SAMMY_USER_IDS:
            SAMMY_USER_IDS.append(uid)
        return await ctx.send(embed=discord.Embed(description=f"✅ Sammy ID `{uid}` added. Relay active when bot sees their messages.", color=THEME_COLOR))
    if a in ("remove", "del", "rm") and user_id:
        uid = user_id.strip().replace("<@", "").replace("!", "").replace(">", "")
        if uid in SAMMY_USER_IDS:
            SAMMY_USER_IDS.remove(uid)
            return await ctx.send(embed=discord.Embed(description=f"✅ Removed `{uid}` from Sammy list.", color=THEME_COLOR))
        return await ctx.send("That ID was not in the list.")
    return await cmd_usage(ctx, "`+setsammy [list|add <id>|remove <id>]`")


@bot.command()
async def perms(ctx):
    cache = resolve_role_ids(ctx.guild)
    emb = discord.Embed(title=f"⚡ {BRAND_NAME} Permissions", color=THEME_COLOR)
    for level in sorted(ROLES.keys()):
        mentions = [ctx.guild.get_role(rid).mention for rid in cache.get(level, []) if ctx.guild.get_role(rid)]
        emb.add_field(name=f"▸ Perm {level}", value="\n".join(mentions) or "*None*", inline=False)

    # Command-perm roles (ban / unban / kick / bl / unbl)
    role_lines = []
    for label, rid in (
        ("+ban", BAN_PERM_ROLE_ID),
        ("+unban", UNBAN_PERM_ROLE_ID),
        ("+kick", KICK_PERM_ROLE_ID),
        ("+bl", BL_PERM_ROLE_ID),
        ("+unbl", UNBL_PERM_ROLE_ID),
    ):
        role = ctx.guild.get_role(rid)
        mention = role.mention if role else f"`{rid}` (role missing)"
        role_lines.append(f"**{label}** → {mention}")
    emb.add_field(
        name="⚡ Command Perm Roles",
        value="\n".join(role_lines),
        inline=False,
    )
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb, allowed_mentions=discord.AllowedMentions.none())

@bot.command()
async def snipe(ctx):
    data = snipe_data.get(str(ctx.channel.id))
    if not data:
        return await empty_result(ctx, "Nothing to snipe.")
    emb = discord.Embed(title=f"⚡ Snipe — {BRAND_NAME}", description=censor_blacklisted(data.get("content") or ""), color=THEME_COLOR)
    emb.add_field(name="Author", value=data["author"], inline=True)
    emb.add_field(name="Deleted", value=data.get("time", "?"), inline=True)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)


@bot.command(name="i", aliases=["invites"])
async def invites_cmd(ctx, *, target: str = None):
    """+i [@user|user_id] — show how many invites a user has (sum of their invite uses)."""
    user = None
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
    elif ctx.message.reference:
        user = await get_target(ctx, None)
    elif target:
        user = await get_target(ctx, target)
    user = user or ctx.author

    try:
        invites = await ctx.guild.invites()
    except discord.Forbidden:
        return await ctx.send("❌ I need the **Manage Server** permission to view invites.")
    except Exception as e:
        return await ctx.send(f"Failed to fetch invites: {e}")

    total_uses = 0
    invite_count = 0
    lines = []
    for inv in invites:
        if inv.inviter and inv.inviter.id == user.id:
            uses = inv.uses or 0
            total_uses += uses
            invite_count += 1
            max_uses = inv.max_uses if inv.max_uses else "∞"
            lines.append(f"`{inv.code}` — **{uses}** uses (max {max_uses})")

    emb = discord.Embed(
        title=f"⚡ Invites — {BRAND_NAME}",
        description=(
            f"**User:** {user.mention} (`{user.id}`)\n"
            f"**Total invites used:** `{total_uses}`\n"
            f"**Active invite links:** `{invite_count}`"
        ),
        color=THEME_COLOR,
        timestamp=datetime.now(timezone.utc),
    )
    emb.set_thumbnail(url=user.display_avatar.url)
    if lines:
        emb.add_field(
            name="Links",
            value="\n".join(lines[:15]) + ("\n…" if len(lines) > 15 else ""),
            inline=False,
        )
    else:
        emb.add_field(name="Links", value="*No active invite links created by this user.*", inline=False)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)


@bot.command(name="lb", aliases=["ilb"])
async def invite_leaderboard(ctx):
    """+lb — invite leaderboard (top inviters)."""
    try:
        invites = await ctx.guild.invites()
    except discord.Forbidden:
        return await ctx.send("❌ I need the **Manage Server** permission to view invites.")
    except Exception as e:
        return await ctx.send(f"Failed to fetch invites: {e}")

    totals = {}  # user_id -> {"user": User, "uses": int}
    for inv in invites:
        if not inv.inviter:
            continue
        uid = inv.inviter.id
        if uid not in totals:
            totals[uid] = {"user": inv.inviter, "uses": 0}
        totals[uid]["uses"] += inv.uses or 0

    ranked = sorted(totals.values(), key=lambda x: x["uses"], reverse=True)
    ranked = [r for r in ranked if r["uses"] > 0][:15]

    if not ranked:
        return await empty_result(ctx, "No invites recorded yet.")

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    lines = []
    for i, row in enumerate(ranked, 1):
        medal = medals.get(i, f"**{i}.**")
        u = row["user"]
        lines.append(f"{medal} {u.mention} — **{row['uses']}** invite{'s' if row['uses'] != 1 else ''}")

    emb = discord.Embed(
        title=f"⚡ Invite Leaderboard — {BRAND_NAME}",
        description="\n".join(lines),
        color=THEME_COLOR,
        timestamp=datetime.now(timezone.utc),
    )
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)


@bot.command(aliases=["warns"])
async def sanctions(ctx, *, target: str = None):
    user = None
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
    elif ctx.message.reference:
        user = await get_target(ctx, None)
    elif target:
        user = await get_target(ctx, target)
    user = user or ctx.author
    uid = str(user.id)
    lst = sanctions_data.get(uid, [])
    if not lst:
        emb = discord.Embed(description="No sanctions received", color=THEME_COLOR)
        emb.set_author(name=str(user), icon_url=user.display_avatar.url)
        emb.set_footer(text=FOOTER_TEXT)
        return await ctx.send(embed=emb)
    ordered = _sort_sanctions_newest_first(lst)
    lines = [f"**{i}.** `{s.get('date','?')}`\n↳ {s.get('reason','No reason')}" for i, s in enumerate(ordered, 1)]
    emb = discord.Embed(title=f"⚡ Sanctions — {BRAND_NAME}", description="\n\n".join(lines)[:4000], color=THEME_COLOR)
    emb.set_author(name=str(user), icon_url=user.display_avatar.url)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def warn(ctx, *, args=None):
    if not has_perm(ctx.author, get_cmd_perm("warn")):
        return await cmd_fail(ctx)
    user = None
    reason = "No reason provided"
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
        if args:
            reason = args
            for m in ctx.message.mentions:
                reason = reason.replace(f"<@{m.id}>", "").replace(f"<@!{m.id}>", "")
            reason = reason.strip() or "No reason provided"
    elif ctx.message.reference:
        user = await get_target(ctx, None)
        if args:
            reason = args.strip() or "No reason provided"
    elif args:
        parts = args.split(None, 1)
        user = await get_target(ctx, parts[0])
        if user and len(parts) > 1:
            reason = parts[1]
    if not user:
        return await cmd_usage(ctx, "`+warn <@member> [reason]`")
    target_member = await get_member(ctx.guild, user)
    if target_member and not can_moderate(ctx.author, target_member):
        return await ctx.send("You can't warn someone with equal or higher rank.")
    add_sanction(user.id, reason, ctx.author.id)
    emb = discord.Embed(title=f"⚡ Warn — {BRAND_NAME}", description=f"{user.mention} was warned\n**Reason:** {reason}", color=THEME_COLOR)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def tempmute(ctx, *, args=None):
    if not has_perm(ctx.author, get_cmd_perm("tempmute")):
        return await cmd_fail(ctx)
    user = None
    rest = args or ""
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
        for m in ctx.message.mentions:
            rest = rest.replace(f"<@{m.id}>", "").replace(f"<@!{m.id}>", "")
    elif ctx.message.reference:
        user = await get_target(ctx, None)
    tokens = rest.strip().split()
    if user is None and tokens and tokens[0].isdigit():
        user = await get_target(ctx, tokens[0])
        tokens = tokens[1:]
    duration = None
    reason = "No reason"
    for i, tok in enumerate(tokens):
        if parse_duration(tok):
            duration = tok
            reason = " ".join(tokens[i+1:]).strip() or "No reason"
            break
    if not user or not duration:
        return await cmd_usage(ctx, "`+tempmute <@member> <duration> [reason]`")
    delta = parse_duration(duration)
    member = await get_member(ctx.guild, user)
    if not member or not can_moderate(ctx.author, member):
        return await ctx.send("Cannot mute this user.")
    try:
        await member.timeout(datetime.now(timezone.utc) + delta, reason=reason)
        add_sanction(member.id, f"tempmute {duration} - {reason}", ctx.author.id)
        emb = discord.Embed(title=f"⚡ Temp Mute — {BRAND_NAME}", description=f"{member.mention} muted for **{duration}**\n**Reason:** {reason}", color=THEME_COLOR)
        emb.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=emb)
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command()
async def unmute(ctx, *, target: str = None):
    if not has_perm(ctx.author, get_cmd_perm("unmute")):
        return await cmd_fail(ctx)
    user = None
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
    elif ctx.message.reference:
        user = await get_target(ctx, None)
    elif target:
        user = await get_target(ctx, target)
    if not user:
        return await cmd_usage(ctx, "`+unmute <@member>`")
    member = await get_member(ctx.guild, user)
    if not member:
        return await cmd_usage(ctx, "`+unmute <@member>`")
    try:
        await member.timeout(None, reason=f"Unmuted by {ctx.author}")
        emb = discord.Embed(title=f"⚡ Unmute — {BRAND_NAME}", description=f"{member.mention} has been unmuted.", color=THEME_COLOR)
        emb.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=emb)
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command()
async def clear(ctx, *, args: str = None):
    """+clear [amount] [@member] — silent delete, no bot reply.
    Examples:
      +clear
      +clear 20
      +clear @user
      +clear 50 @user
    """
    if not has_perm(ctx.author, get_cmd_perm("clear")):
        return await cmd_fail(ctx)

    amount = 10
    target_user = None

    if ctx.message.mentions:
        target_user = ctx.message.mentions[0]

    if args:
        tokens = args.split()
        for tok in tokens:
            if tok.isdigit():
                amount = int(tok)
                break
        if target_user is None:
            for tok in tokens:
                if not tok.isdigit() and not tok.startswith("<@"):
                    target_user = await get_target(ctx, tok)
                    if target_user:
                        break
    # Reply-to also targets that user
    if target_user is None and ctx.message.reference:
        target_user = await get_target(ctx, None)

    if amount < 1 or amount > 100:
        try:
            await ctx.message.delete()
        except Exception:
            pass
        return

    clearing_channels.add(ctx.channel.id)
    try:
        # Delete the command message first
        try:
            await ctx.message.delete()
        except Exception:
            pass

        def check(m):
            if target_user:
                return m.author.id == target_user.id
            return True

        # Purge up to `amount` matching messages (command already deleted)
        await ctx.channel.purge(limit=amount, check=check)
        # No bot response — stays silent
    except Exception:
        pass
    finally:
        clearing_channels.discard(ctx.channel.id)


@bot.command()
async def lock(ctx):
    if not has_perm(ctx.author, get_cmd_perm("lock")):
        return await cmd_fail(ctx)
    try:
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(embed=discord.Embed(description=f"{ctx.channel.mention} locked.", color=THEME_COLOR))
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command()
async def unlock(ctx):
    if not has_perm(ctx.author, get_cmd_perm("unlock")):
        return await cmd_fail(ctx)
    try:
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(embed=discord.Embed(description=f"{ctx.channel.mention} unlocked.", color=THEME_COLOR))
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command()
async def addrole(ctx, *, args=None):
    """+addrole [user] <role>
    Examples:
      +addrole head of recruitment     (adds to yourself)
      +addrole @user Moderator
      +addrole Moderator
    """
    if not has_perm(ctx.author, get_cmd_perm("addrole")) and not has_role_manage_extra(ctx.author):
        return await cmd_fail(ctx)
    if not args:
        return await cmd_usage(ctx, "`+addrole [@member] <role>`")

    user = None
    role_name = None

    if ctx.message.mentions:
        user = ctx.message.mentions[0]
        role_name = args
        for m in ctx.message.mentions:
            role_name = role_name.replace(f"<@{m.id}>", "").replace(f"<@!{m.id}>", "")
        role_name = role_name.strip()
    elif ctx.message.reference:
        user = await get_target(ctx, None)
        role_name = args.strip()
    else:
        # Try first token as user ID, otherwise whole string is role (self)
        parts = args.split(None, 1)
        if parts[0].isdigit() and len(parts[0]) >= 15 and ctx.guild.get_member(int(parts[0])):
            user = await get_target(ctx, parts[0])
            role_name = parts[1] if len(parts) > 1 else None
        else:
            user = ctx.author
            role_name = args.strip()

    if not user or not role_name:
        return await cmd_usage(ctx, "`+addrole [@member] <role>`")

    member = await get_member(ctx.guild, user)
    if not member:
        return await ctx.send("Could not find that member.")

    role = find_role(ctx.guild, role_name)
    if not role:
        return await ctx.send(f"Could not find a role matching **{role_name}**.")

    # Hierarchy checks
    if role >= ctx.author.top_role:
        return await ctx.send("You can't assign a role equal or higher than your top role.")
    if role >= ctx.guild.me.top_role:
        return await ctx.send("My role must be above that role to assign it.")

    if role in member.roles:
        return await ctx.send(f"{member.mention} already has {role.mention}.")

    try:
        await member.add_roles(role, reason=f"addrole by {ctx.author}")
        await ctx.send(f"1 role was added to 1 member")
    except discord.Forbidden:
        await ctx.send("I don't have permission to add that role.")
    except Exception as e:
        await ctx.send(f"Failed: {e}")


@bot.command()
async def delrole(ctx, *, args=None):
    """+delrole [user] <role>
    Examples:
      +delrole head of recruitment
      +delrole @user Moderator
    """
    if not has_perm(ctx.author, get_cmd_perm("delrole")) and not has_role_manage_extra(ctx.author):
        return await cmd_fail(ctx)
    if not args:
        return await cmd_usage(ctx, "`+delrole [@member] <role>`")

    user = None
    role_name = None

    if ctx.message.mentions:
        user = ctx.message.mentions[0]
        role_name = args
        for m in ctx.message.mentions:
            role_name = role_name.replace(f"<@{m.id}>", "").replace(f"<@!{m.id}>", "")
        role_name = role_name.strip()
    elif ctx.message.reference:
        user = await get_target(ctx, None)
        role_name = args.strip()
    else:
        parts = args.split(None, 1)
        if parts[0].isdigit() and len(parts[0]) >= 15 and ctx.guild.get_member(int(parts[0])):
            user = await get_target(ctx, parts[0])
            role_name = parts[1] if len(parts) > 1 else None
        else:
            user = ctx.author
            role_name = args.strip()

    if not user or not role_name:
        return await cmd_usage(ctx, "`+delrole [@member] <role>`")

    member = await get_member(ctx.guild, user)
    if not member:
        return await ctx.send("Could not find that member.")

    role = find_role(ctx.guild, role_name)
    if not role:
        return await ctx.send(f"Could not find a role matching **{role_name}**.")

    if role >= ctx.author.top_role:
        return await ctx.send("You can't manage a role equal or higher than your top role.")
    if role >= ctx.guild.me.top_role:
        return await ctx.send("My role must be above that role to remove it.")

    if role not in member.roles:
        return await ctx.send(f"{member.mention} does not have {role.mention}.")

    try:
        await member.remove_roles(role, reason=f"delrole by {ctx.author}")
        await ctx.send("1 role was successfully removed from 1 member")
    except discord.Forbidden:
        await ctx.send("I don't have permission to remove that role.")
    except Exception as e:
        await ctx.send(f"Failed: {e}")


@bot.command()
async def derank(ctx, *, target: str = None):
    if not has_perm(ctx.author, get_cmd_perm("derank")):
        return await cmd_fail(ctx)
    user = None
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
    elif ctx.message.reference:
        user = await get_target(ctx, None)
    elif target:
        user = await get_target(ctx, target)
    if not user:
        return await cmd_usage(ctx, "`+derank <@member>`")
    member = await get_member(ctx.guild, user)
    if not member or not can_moderate(ctx.author, member):
        return await ctx.send("Cannot derank this user.")
    try:
        cache = resolve_role_ids(ctx.guild)
        staff_ids = set()
        for rids in cache.values():
            staff_ids.update(rids)
        # Always strip staff team / HRS / recruitment roles when deranking
        staff_ids.update(DERANK_EXTRA_ROLE_IDS)
        roles = [
            r for r in member.roles
            if r.id in staff_ids and r != ctx.guild.default_role and not r.managed
        ]
        if not roles:
            return await ctx.send("No staff roles to remove.")
        await member.remove_roles(*roles, reason=f"Derank by {ctx.author}")
        await ctx.send(f"{member.mention} was deranked successfully")
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command()
async def userinfo(ctx, *, target: str = None):
    user = None
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
    elif ctx.message.reference:
        user = await get_target(ctx, None)
    elif target:
        user = await get_target(ctx, target)
    user = user or ctx.author
    member = ctx.guild.get_member(user.id)
    emb = discord.Embed(title=f"⚡ User Info — {BRAND_NAME}", color=THEME_COLOR)
    emb.set_author(name=str(user), icon_url=user.display_avatar.url)
    emb.set_thumbnail(url=user.display_avatar.url)
    emb.add_field(name="ID", value=f"`{user.id}`", inline=True)
    emb.add_field(name="Created", value=discord.utils.format_dt(user.created_at, "R"), inline=True)
    if member and member.joined_at:
        emb.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, "R"), inline=True)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def serverinfo(ctx):
    g = ctx.guild
    emb = discord.Embed(title=f"⚡ {g.name}", description=f"**{BRAND_NAME}**", color=THEME_COLOR)
    if g.icon:
        emb.set_thumbnail(url=g.icon.url)
    emb.add_field(name="Members", value=f"`{g.member_count}`", inline=True)
    emb.add_field(name="Boosts", value=f"`{g.premium_subscription_count or 0}`", inline=True)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

# Extra moderation commands

@bot.command()
async def clearwarns(ctx, *, target: str = None):
    if not has_perm(ctx.author, get_cmd_perm("clearwarns")):
        return await cmd_fail(ctx)
    user = None
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
    elif ctx.message.reference:
        user = await get_target(ctx, None)
    elif target:
        user = await get_target(ctx, target)
    if not user:
        return await cmd_usage(ctx, "`+clearwarns <@member>`")
    target_member = await get_member(ctx.guild, user)
    if target_member and not can_moderate(ctx.author, target_member):
        return await ctx.send("You can't clear warns of someone with equal or higher rank.")
    uid = str(user.id)
    count = len(sanctions_data.get(uid, []))
    sanctions_data[uid] = []
    save_sanctions()
    emb = discord.Embed(title=f"⚡ Clear Warns — {BRAND_NAME}", description=f"Cleared **{count}** sanction(s) from {user.mention}", color=THEME_COLOR)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command(name="del")
async def del_sanction(ctx, action: str = None, *, rest: str = None):
    if action != "sanction":
        return
    if not has_perm(ctx.author, get_cmd_perm("del")):
        return await cmd_fail(ctx)
    user = None
    number = None
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
    if rest:
        tokens = rest.split()
        for tok in tokens:
            if tok.isdigit() and user is None and len(tok) >= 15:
                user = await get_target(ctx, tok)
            elif tok.isdigit():
                number = tok
    if user is None and ctx.message.reference:
        user = await get_target(ctx, None)
    if not user or not number:
        return await cmd_usage(ctx, "`+del sanction <@member> <number>`")
    uid = str(user.id)
    lst = sanctions_data.get(uid, [])
    if not lst:
        return await cmd_fail(ctx)
    ordered = _sort_sanctions_newest_first(lst)
    num = int(number)
    if num < 1 or num > len(ordered):
        return await cmd_usage(ctx, "`+del sanction <@member> <number>`")
    deleted = ordered[num - 1]
    sanctions_data[uid] = [s for s in lst if s is not deleted]
    save_sanctions()
    emb = discord.Embed(title=f"⚡ Del Sanction — {BRAND_NAME}", description=f"Deleted: **{deleted.get('date','?')}**: {deleted.get('reason','')}", color=THEME_COLOR)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def mutelist(ctx):
    if not has_perm(ctx.author, get_cmd_perm("mutelist")):
        return await cmd_fail(ctx)
    muted = [m for m in ctx.guild.members if m.timed_out_until and m.timed_out_until > datetime.now(timezone.utc)]
    if not muted:
        return await empty_result(ctx, "No one is currently muted.")
    lines = [f"{m.mention} — until {discord.utils.format_dt(m.timed_out_until, 'R')}" for m in muted[:25]]
    emb = discord.Embed(title=f"⚡ Mute List — {BRAND_NAME}", description="\n".join(lines), color=THEME_COLOR)
    emb.set_footer(text=f"{FOOTER_TEXT}  •  {len(muted)} muted")
    await ctx.send(embed=emb)

@bot.command()
async def banlist(ctx):
    if not has_perm(ctx.author, get_cmd_perm("banlist")):
        return await cmd_fail(ctx)
    try:
        bans = [entry async for entry in ctx.guild.bans(limit=50)]
    except Exception as e:
        return await ctx.send(f"Failed: {e}")
    if not bans:
        return await empty_result(ctx, "There are no banned users.")
    lines = []
    for entry in bans[:40]:
        reason = entry.reason or "No reason"
        if len(reason) > 60:
            reason = reason[:57] + "..."
        lines.append(f"**{entry.user}** (`{entry.user.id}`)\n↳ {reason}")
    emb = discord.Embed(title=f"⚡ Ban List — {BRAND_NAME}", description="\n\n".join(lines), color=THEME_COLOR)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def baninfo(ctx, *, target: str = None):
    if not has_perm(ctx.author, get_cmd_perm("baninfo")):
        return await cmd_fail(ctx)
    user = None
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
    elif target:
        user = await get_target(ctx, target)
    if not user:
        return await cmd_usage(ctx, "`+baninfo <@member|id>`")
    try:
        ban_entry = await ctx.guild.fetch_ban(user)
    except discord.NotFound:
        return await ctx.send(f"**{user}** is not banned.")
    except Exception as e:
        return await ctx.send(f"Failed: {e}")
    emb = discord.Embed(title=f"⚡ Ban Info — {BRAND_NAME}", color=THEME_COLOR)
    emb.set_author(name=str(user), icon_url=user.display_avatar.url)
    emb.add_field(name="User", value=f"{user} (`{user.id}`)", inline=False)
    emb.add_field(name="Reason", value=ban_entry.reason or "No reason", inline=False)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def modstats(ctx):
    if not has_perm(ctx.author, get_cmd_perm("modstats")):
        return await cmd_fail(ctx)
    counts = {}
    for uid, entries in sanctions_data.items():
        for s in entries:
            mid = str(s.get("moderator", "0"))
            if mid and mid != "0":
                counts[mid] = counts.get(mid, 0) + 1
    if not counts:
        return await ctx.send("No moderation actions recorded yet.")
    sorted_mods = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:25]
    lines = [f"**{i}.** <@{mid}> — `{cnt}` actions" for i, (mid, cnt) in enumerate(sorted_mods, 1)]
    emb = discord.Embed(title=f"⚡ Moderator Statistics — {BRAND_NAME}", description="\n".join(lines), color=THEME_COLOR)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def syncroles(ctx):
    if not has_perm(ctx.author, get_cmd_perm("syncroles")):
        return await cmd_fail(ctx)
    cache = resolve_role_ids(ctx.guild, force=True)
    lines = []
    for level in sorted(cache.keys()):
        roles = [ctx.guild.get_role(rid).mention for rid in cache[level] if ctx.guild.get_role(rid)]
        lines.append(f"**▸ Perm {level}:** {' '.join(roles) if roles else '*none*'}")
    emb = discord.Embed(title=f"⚡ Roles Synced — {BRAND_NAME}", description="\n".join(lines) or "No roles matched.", color=THEME_COLOR)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def temprole(ctx, *, args: str = None):
    if not has_perm(ctx.author, get_cmd_perm("temprole")):
        return await cmd_fail(ctx)
    if not args:
        return await cmd_usage(ctx, "`+temprole <@member> <duration> <role>` (e.g. 1h)")
    user = None
    rest = args
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
        for m in ctx.message.mentions:
            rest = rest.replace(f"<@{m.id}>", "").replace(f"<@!{m.id}>", "")
    tokens = rest.strip().split()
    if user is None and tokens and tokens[0].isdigit() and len(tokens[0]) >= 15:
        user = await get_target(ctx, tokens[0])
        tokens = tokens[1:]
    duration = None
    duration_idx = None
    for i, tok in enumerate(tokens):
        if parse_duration(tok):
            duration = tok
            duration_idx = i
            break
    if duration is None or user is None:
        return await cmd_usage(ctx, "`+temprole <@member> <duration> <role>`")
    role_name = " ".join(tokens[:duration_idx] + tokens[duration_idx+1:]).strip()
    if not role_name:
        return await cmd_usage(ctx, "`+temprole <@member> <duration> <role>`")
    delta = parse_duration(duration)
    member = await get_member(ctx.guild, user)
    role = find_role(ctx.guild, role_name)
    if not member or not role or not delta:
        return await cmd_usage(ctx, "`+temprole <@member> <duration> <role>`")
    if role >= ctx.author.top_role:
        return await cmd_fail(ctx)
    try:
        if role not in member.roles:
            await member.add_roles(role, reason=f"Temp role {duration} by {ctx.author}")
        ends_at = datetime.now(timezone.utc) + delta
        schedule_temprole(ctx.guild.id, member.id, role.id, ends_at)
        emb = discord.Embed(title=f"⚡ Temp Role — {BRAND_NAME}", description=f"Gave **{role.name}** to {member.mention} for **{duration}**\nRemoves {discord.utils.format_dt(ends_at, 'R')}", color=THEME_COLOR)
        emb.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=emb)
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command()
async def create(ctx, emoji: str = None, *, name: str = None):
    if not has_perm(ctx.author, get_cmd_perm("create")):
        return await cmd_fail(ctx)
    if emoji and not name:
        name = emoji
        emoji = None
    if not name:
        return await cmd_usage(ctx, "`+create [emoji] <name>`")
    role_name = f"{emoji} {name}".strip() if emoji else name.strip()
    existing = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), ctx.guild.roles)
    if existing:
        return await ctx.send(f"A role named **{role_name}** already exists.")
    try:
        new_role = await ctx.guild.create_role(name=role_name, reason=f"Created by {ctx.author}")
        await ctx.send(f"Successfully created role **{new_role.name}**")
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command()
async def linkalt(ctx, *, args: str = None):
    if not has_perm(ctx.author, get_cmd_perm("linkalt")):
        return await cmd_fail(ctx)
    if not args:
        return await ctx.send("Usage: `+linkalt <main> <alt>`")
    main_user = alt_user = None
    mentions = list(ctx.message.mentions)
    if len(mentions) >= 2:
        main_user, alt_user = mentions[0], mentions[1]
    else:
        parts = args.split(None, 1)
        if len(parts) >= 2:
            main_user = await get_target(ctx, parts[0])
            alt_user = await get_target(ctx, parts[1])
    if not main_user or not alt_user or main_user.id == alt_user.id:
        return await cmd_fail(ctx)
    main_id, alt_id = str(main_user.id), str(alt_user.id)
    if alt_id not in blacklist:
        blacklist.append(alt_id)
        save_blacklist()
    if main_id not in linked_alts:
        linked_alts[main_id] = []
    if alt_id not in linked_alts[main_id]:
        linked_alts[main_id].append(alt_id)
        save_linked_alts()
    try:
        await ctx.guild.ban(alt_user, reason=f"Linked alt of {main_id}")
    except Exception:
        pass
    if main_id not in blacklist:
        blacklist.append(main_id)
        save_blacklist()
    emb = discord.Embed(title=f"⚡ Link Alt — {BRAND_NAME}", description=f"Linked **{alt_user}** as alt of **{main_user}** and blacklisted.", color=THEME_COLOR)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def changeperm(ctx, command: str = None, level: str = None):
    if not has_perm(ctx.author, get_cmd_perm("changeperm")):
        return await cmd_fail(ctx)
    if not command or level is None:
        return await ctx.send("Usage: `+changeperm <command> <level|none>`")
    cmd = command.lower().strip()
    if level.lower() in ("none", "off", "disable"):
        command_overrides[cmd] = "none"
        save_command_perms()
        return await ctx.send(f"Permission for `{cmd}` set to **none**.")
    try:
        lvl = int(level)
        if lvl < 0 or lvl > 6:
            return await ctx.send("Level must be 0-6 or `none`.")
    except ValueError:
        return await ctx.send("Level must be 0-6 or `none`.")
    command_overrides[cmd] = lvl
    save_command_perms()
    await ctx.send(f"Permission for `{cmd}` set to **Perm {lvl}**.")

@bot.command(name="commands")
async def commands_command(ctx):
    if not has_staff_permission(ctx.author):
        return await cmd_fail(ctx)
    emb = discord.Embed(title=f"⚡ Ticket Commands — {BRAND_NAME}", color=THEME_COLOR)
    emb.add_field(name="Ticket tools", value="`+claim` `+close` `+rename <name>` `+add <user>` `+remove <user>`", inline=False)
    emb.add_field(name="Note", value="Panels auto-post on bot startup.", inline=False)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def ban(ctx, *, args=None):
    if not can_use_ban(ctx.author):
        return await cmd_fail(ctx)
    user = None
    reason = "No reason"
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
        if args:
            reason = args
            for m in ctx.message.mentions:
                reason = reason.replace(f"<@{m.id}>", "").replace(f"<@!{m.id}>", "")
            reason = reason.strip() or "No reason"
    elif ctx.message.reference:
        user = await get_target(ctx, None)
        if args:
            reason = args.strip() or "No reason"
    elif args:
        parts = args.split(None, 1)
        user = await get_target(ctx, parts[0])
        if user and len(parts) > 1:
            reason = parts[1]
    if not user:
        return await cmd_usage(ctx, "`+ban <@member> [reason]`")
    try:
        await ctx.guild.ban(user, reason=reason)
    except Exception:
        pass
    emb = discord.Embed(title=f"⚡ Ban — {BRAND_NAME}", description=f"{user.mention} banned.\n**Reason:** {reason}", color=THEME_COLOR)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def unban(ctx, user_id=None):
    if not can_use_unban(ctx.author):
        return await cmd_fail(ctx)
    if not user_id:
        return await cmd_fail(ctx)
    uid = user_id.strip().replace("<@", "").replace("!", "").replace(">", "")
    if not uid.isdigit():
        return await cmd_fail(ctx)
    try:
        user = await bot.fetch_user(int(uid))
        await ctx.guild.unban(user)
        emb = discord.Embed(title=f"⚡ Unban — {BRAND_NAME}", description=f"{user} unbanned.", color=THEME_COLOR)
        emb.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=emb)
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command()
async def kick(ctx, *, args=None):
    if not can_use_kick(ctx.author):
        return await cmd_fail(ctx)
    user = None
    reason = "No reason"
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
        if args:
            reason = args
            for m in ctx.message.mentions:
                reason = reason.replace(f"<@{m.id}>", "").replace(f"<@!{m.id}>", "")
            reason = reason.strip() or "No reason"
    elif ctx.message.reference:
        user = await get_target(ctx, None)
        if args:
            reason = args.strip() or "No reason"
    elif args:
        parts = args.split(None, 1)
        user = await get_target(ctx, parts[0])
        if user and len(parts) > 1:
            reason = parts[1]
    if not user:
        return await cmd_usage(ctx, "`+kick <@member> [reason]`")
    member = await get_member(ctx.guild, user)
    if not member:
        return await cmd_fail(ctx)
    try:
        await member.kick(reason=reason)
        emb = discord.Embed(title=f"⚡ Kick — {BRAND_NAME}", description=f"{user.mention} kicked.\n**Reason:** {reason}", color=THEME_COLOR)
        emb.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=emb)
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command()
async def bl(ctx, *, args=None):
    if not can_use_bl(ctx.author):
        return await cmd_fail(ctx)
    user = None
    reason = "No reason"
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
        if args:
            reason = args
            for m in ctx.message.mentions:
                reason = reason.replace(f"<@{m.id}>", "").replace(f"<@!{m.id}>", "")
            reason = reason.strip() or "No reason"
    elif ctx.message.reference:
        user = await get_target(ctx, None)
        if args:
            reason = args.strip() or "No reason"
    elif args:
        parts = args.split(None, 1)
        user = await get_target(ctx, parts[0])
        if user and len(parts) > 1:
            reason = parts[1]
    if not user:
        return await cmd_usage(ctx, "`+bl <@member> [reason]`")
    uid = str(user.id)
    if uid not in blacklist:
        blacklist.append(uid)
        save_blacklist()
    try:
        await ctx.guild.ban(user, reason=f"Blacklisted: {reason}")
    except Exception:
        pass
    emb = discord.Embed(title=f"⚡ Blacklist — {BRAND_NAME}", description=f"{user.mention} banned and blacklisted.\nreason: {reason}", color=THEME_COLOR)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def unbl(ctx, user_id=None):
    if not can_use_unbl(ctx.author):
        return await cmd_fail(ctx)
    if not user_id:
        return await cmd_fail(ctx)
    uid = user_id.strip().replace("<@", "").replace("!", "").replace(">", "")
    if not uid.isdigit():
        return await cmd_fail(ctx)
    if uid in blacklist:
        blacklist.remove(uid)
        save_blacklist()
    try:
        user = await bot.fetch_user(int(uid))
        await ctx.guild.unban(user)
    except Exception:
        pass
    emb = discord.Embed(title=f"⚡ Unblacklist — {BRAND_NAME}", description=f"`{uid}` removed from blacklist and unbanned.", color=THEME_COLOR)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)

@bot.command()
async def blist(ctx):
    if not has_perm(ctx.author, get_cmd_perm("blist")):
        return await cmd_fail(ctx)
    if not blacklist:
        return await empty_result(ctx, "No blacklisted users.")
    lines = []
    for uid in blacklist[:40]:
        try:
            user = await bot.fetch_user(int(uid))
            lines.append(f"**{user}** (`{uid}`)")
        except Exception:
            lines.append(f"Unknown (`{uid}`)")
    emb = discord.Embed(title=f"⚡ Blacklist — {BRAND_NAME}", description="\n".join(lines), color=THEME_COLOR)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)


# ==================== EXTRA UTILITY COMMANDS ====================

@bot.command(aliases=["av", "pfp"])
async def avatar(ctx, *, target: str = None):
    """Show a user's avatar."""
    user = None
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
    elif ctx.message.reference:
        user = await get_target(ctx, None)
    elif target:
        user = await get_target(ctx, target)
    user = user or ctx.author
    emb = discord.Embed(title=f"⚡ Avatar — {user}", color=THEME_COLOR)
    emb.set_image(url=user.display_avatar.url)
    emb.add_field(name="Link", value=f"[Open]({user.display_avatar.url})", inline=False)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)


@bot.command(aliases=["ri", "roleinfo"])
async def role_info(ctx, *, role_input: str = None):
    """Show info about a role."""
    role = None
    if ctx.message.role_mentions:
        role = ctx.message.role_mentions[0]
    elif role_input:
        role = find_role(ctx.guild, role_input)
    if not role:
        return await cmd_usage(ctx, "`+roleinfo <@role|name|id>`")
    members = len(role.members)
    emb = discord.Embed(title=f"⚡ Role Info — {role.name}", color=role.color.value or THEME_COLOR)
    emb.add_field(name="ID", value=f"`{role.id}`", inline=True)
    emb.add_field(name="Members", value=f"`{members}`", inline=True)
    emb.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
    emb.add_field(name="Hoisted", value="Yes" if role.hoist else "No", inline=True)
    emb.add_field(name="Position", value=f"`{role.position}`", inline=True)
    emb.add_field(name="Color", value=f"`{str(role.color)}`", inline=True)
    emb.add_field(name="Created", value=discord.utils.format_dt(role.created_at, "R"), inline=False)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb, allowed_mentions=discord.AllowedMentions.none())


@bot.command(name="mc", aliases=["membercount", "members", "membercounts"])
async def membercount(ctx):
    """Show server member counts."""
    g = ctx.guild
    bots = sum(1 for m in g.members if m.bot)
    humans = g.member_count - bots if g.member_count else len([m for m in g.members if not m.bot])
    online = sum(1 for m in g.members if m.status != discord.Status.offline and not m.bot)
    emb = discord.Embed(title=f"⚡ Member Count — {g.name}", color=THEME_COLOR)
    emb.add_field(name="Total", value=f"`{g.member_count}`", inline=True)
    emb.add_field(name="Humans", value=f"`{humans}`", inline=True)
    emb.add_field(name="Bots", value=f"`{bots}`", inline=True)
    emb.add_field(name="Online (approx)", value=f"`{online}`", inline=True)
    emb.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=emb)


@bot.command()
async def poll(ctx, *, args: str = None):
    """+poll Question | Option1 | Option2 | ... (up to 10 options). Perm 1."""
    if not has_perm(ctx.author, get_cmd_perm("poll")):
        return await cmd_fail(ctx)
    if not args or "|" not in args:
        return await cmd_usage(ctx, "`+poll Question | Option1 | Option2 | ...`")
    parts = [p.strip() for p in args.split("|") if p.strip()]
    if len(parts) < 3:
        return await ctx.send("Need a question and at least **2** options, separated by `|`.")
    question, options = parts[0], parts[1:11]
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lines = [f"**{question}**", ""]
    for i, opt in enumerate(options):
        lines.append(f"{emojis[i]} {opt}")
    emb = discord.Embed(title=f"⚡ Poll — {BRAND_NAME}", description="\n".join(lines), color=THEME_COLOR)
    emb.set_footer(text=f"{FOOTER_TEXT} • by {ctx.author}")
    msg = await ctx.send(embed=emb)
    for i in range(len(options)):
        try:
            await msg.add_reaction(emojis[i])
        except Exception:
            pass


@bot.command()
async def slowmode(ctx, seconds: str = None):
    """+slowmode <seconds|off> — set channel slowmode. Perm 4."""
    if not has_perm(ctx.author, get_cmd_perm("slowmode")):
        return await cmd_fail(ctx)
    if seconds is None:
        return await cmd_usage(ctx, "`+slowmode <seconds|off>` (0–21600)")
    if seconds.lower() in ("off", "0", "disable", "none"):
        delay = 0
    elif seconds.isdigit():
        delay = int(seconds)
    else:
        return await cmd_usage(ctx, "`+slowmode <seconds|off>` (0–21600)")
    if delay < 0 or delay > 21600:
        return await ctx.send("Slowmode must be between **0** and **21600** seconds.")
    try:
        await ctx.channel.edit(slowmode_delay=delay)
        if delay == 0:
            await ctx.send(embed=discord.Embed(description=f"⚡ Slowmode **disabled** in {ctx.channel.mention}.", color=THEME_COLOR))
        else:
            await ctx.send(embed=discord.Embed(description=f"⚡ Slowmode set to **{delay}s** in {ctx.channel.mention}.", color=THEME_COLOR))
    except Exception as e:
        await ctx.send(f"Failed: {e}")


@bot.command(aliases=["setnick", "nickname"])
async def nick(ctx, *, args: str = None):
    """+nick [@member] <new nick|reset> — change nickname. Perm 4."""
    if not has_perm(ctx.author, get_cmd_perm("nick")):
        return await cmd_fail(ctx)
    if not args:
        return await cmd_usage(ctx, "`+nick [@member] <new nick|reset>`")
    user = None
    nick_name = args
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
        for m in ctx.message.mentions:
            nick_name = nick_name.replace(f"<@{m.id}>", "").replace(f"<@!{m.id}>", "")
        nick_name = nick_name.strip()
    else:
        user = ctx.author
    if not nick_name:
        return await cmd_usage(ctx, "`+nick [@member] <new nick|reset>`")
    member = await get_member(ctx.guild, user)
    if not member:
        return await ctx.send("Could not find that member.")
    if not can_moderate(ctx.author, member) and member.id != ctx.author.id:
        return await ctx.send("You can't change this member's nickname.")
    new_nick = None if nick_name.lower() in ("reset", "clear", "none", "remove") else nick_name[:32]
    try:
        await member.edit(nick=new_nick, reason=f"nick by {ctx.author}")
        shown = new_nick or member.name
        await ctx.send(embed=discord.Embed(description=f"⚡ Nickname for {member.mention} set to **{shown}**.", color=THEME_COLOR))
    except Exception as e:
        await ctx.send(f"Failed: {e}")


@bot.command()
async def softban(ctx, *, args: str = None):
    """+softban <@member> [reason] — ban then unban to delete recent messages. Perm 5."""
    if not has_perm(ctx.author, get_cmd_perm("softban")):
        return await cmd_fail(ctx)
    user = None
    reason = "No reason"
    if ctx.message.mentions:
        user = ctx.message.mentions[0]
        if args:
            reason = args
            for m in ctx.message.mentions:
                reason = reason.replace(f"<@{m.id}>", "").replace(f"<@!{m.id}>", "")
            reason = reason.strip() or "No reason"
    elif ctx.message.reference:
        user = await get_target(ctx, None)
        if args:
            reason = args.strip() or "No reason"
    elif args:
        parts = args.split(None, 1)
        user = await get_target(ctx, parts[0])
        if user and len(parts) > 1:
            reason = parts[1]
    if not user:
        return await cmd_usage(ctx, "`+softban <@member> [reason]`")
    member = await get_member(ctx.guild, user)
    if member and not can_moderate(ctx.author, member):
        return await ctx.send("You can't softban someone with equal or higher rank.")
    try:
        await ctx.guild.ban(user, reason=f"Softban: {reason}", delete_message_days=1)
        await ctx.guild.unban(user, reason=f"Softban unban: {reason}")
        add_sanction(user.id, f"softban - {reason}", ctx.author.id)
        emb = discord.Embed(
            title=f"⚡ Softban — {BRAND_NAME}",
            description=f"{user.mention} softbanned (messages purged).\n**Reason:** {reason}",
            color=THEME_COLOR,
        )
        emb.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=emb)
        await send_log(emb)
    except Exception as e:
        await ctx.send(f"Failed: {e}")


@bot.command()
async def say(ctx, *, message: str = None):
    """+say <message> — make the bot send a message (deletes your command). Perm 5."""
    if not has_perm(ctx.author, get_cmd_perm("say")):
        return await cmd_fail(ctx)
    if not message:
        return await cmd_usage(ctx, "`+say <message>`")
    try:
        await ctx.message.delete()
    except Exception:
        pass
    # Prevent @everyone / role mass-ping abuse
    allowed = discord.AllowedMentions(everyone=False, roles=False, users=True)
    if has_perm(ctx.author, 6):
        allowed = discord.AllowedMentions.all()
    await ctx.send(message[:2000], allowed_mentions=allowed)


@bot.command()
async def lockdown(ctx):
    """+lockdown — lock all text channels (deny @everyone send). Perm 6."""
    if not has_perm(ctx.author, get_cmd_perm("lockdown")):
        return await cmd_fail(ctx)
    locked = 0
    failed = 0
    status = await ctx.send(embed=discord.Embed(description="⚡ Locking channels…", color=THEME_COLOR))
    for channel in ctx.guild.text_channels:
        try:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            if overwrite.send_messages is False:
                continue
            overwrite.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"Lockdown by {ctx.author}")
            locked += 1
        except Exception:
            failed += 1
    emb = discord.Embed(
        title=f"⚡ Lockdown — {BRAND_NAME}",
        description=f"Locked **{locked}** channels.\nFailed: `{failed}`",
        color=THEME_COLOR,
    )
    emb.set_footer(text=FOOTER_TEXT)
    try:
        await status.edit(embed=emb)
    except Exception:
        await ctx.send(embed=emb)


@bot.command()
async def unlockdown(ctx):
    """+unlockdown — unlock all text channels. Perm 6."""
    if not has_perm(ctx.author, get_cmd_perm("unlockdown")):
        return await cmd_fail(ctx)
    unlocked = 0
    failed = 0
    status = await ctx.send(embed=discord.Embed(description="⚡ Unlocking channels…", color=THEME_COLOR))
    for channel in ctx.guild.text_channels:
        try:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            if overwrite.send_messages is not False:
                continue
            overwrite.send_messages = None
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"Unlockdown by {ctx.author}")
            unlocked += 1
        except Exception:
            failed += 1
    emb = discord.Embed(
        title=f"⚡ Unlockdown — {BRAND_NAME}",
        description=f"Unlocked **{unlocked}** channels.\nFailed: `{failed}`",
        color=THEME_COLOR,
    )
    emb.set_footer(text=FOOTER_TEXT)
    try:
        await status.edit(embed=emb)
    except Exception:
        await ctx.send(embed=emb)


@bot.group(name="role", invoke_without_command=True)
async def role_group(ctx):
    """+role all <@role> — give a role to every member (Perm 6)."""
    if not has_perm(ctx.author, get_cmd_perm("role")):
        return await cmd_fail(ctx)
    return await cmd_usage(ctx, "`+role all <@role|role name|role id>`")


@role_group.command(name="all")
async def role_all(ctx, *, role_input: str = None):
    """Give the specified role to every member in the server. Perm 6 only."""
    if not has_perm(ctx.author, get_cmd_perm("roleall")):
        return await cmd_fail(ctx)
    if not role_input and not ctx.message.role_mentions:
        return await cmd_usage(ctx, "`+role all <@role|role name|role id>`")

    role = None
    if ctx.message.role_mentions:
        role = ctx.message.role_mentions[0]
    else:
        role = find_role(ctx.guild, role_input)

    if not role:
        return await ctx.send(f"Could not find a role matching **{role_input}**.")

    if role >= ctx.guild.me.top_role:
        return await ctx.send("My role must be above that role to assign it.")
    if role >= ctx.author.top_role:
        return await ctx.send("You can't assign a role equal or higher than your top role.")
    if role.managed:
        return await ctx.send("That role is managed by an integration and can't be assigned this way.")

    members = [m for m in ctx.guild.members if not m.bot and role not in m.roles]
    total = len(members)
    if total == 0:
        emb = discord.Embed(
            title=f"⚡ Role All — {BRAND_NAME}",
            description=f"Everyone who can receive {role.mention} already has it.",
            color=THEME_COLOR,
        )
        emb.set_footer(text=FOOTER_TEXT)
        return await ctx.send(embed=emb)

    status = await ctx.send(
        embed=discord.Embed(
            description=f"Giving {role.mention} to **{total}** members… this may take a bit.",
            color=THEME_COLOR,
        )
    )

    success = 0
    failed = 0
    for i, member in enumerate(members, 1):
        try:
            await member.add_roles(role, reason=f"role all by {ctx.author}")
            success += 1
        except Exception:
            failed += 1
        if i % 10 == 0:
            await asyncio.sleep(1.0)

    emb = discord.Embed(
        title=f"⚡ Role All — {BRAND_NAME}",
        description=(
            f"**Role:** {role.mention}\n"
            f"**Given to:** `{success}` members\n"
            f"**Failed:** `{failed}`"
        ),
        color=THEME_COLOR,
    )
    emb.set_footer(text=FOOTER_TEXT)
    try:
        await status.edit(embed=emb)
    except Exception:
        await ctx.send(embed=emb)


@bot.command(name="roleall")
async def roleall_alias(ctx, *, role_input: str = None):
    """Alias for +role all."""
    await role_all(ctx, role_input=role_input)


# Ticket commands
@bot.command(name="claim")
async def claim_command(ctx):
    if is_ticket_opener(ctx.channel, ctx.author) or not has_staff_permission(ctx.author):
        return await ctx.reply("❌ Cannot claim.", mention_author=False)
    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ Ticket channels only.")
    try:
        async for msg in ctx.channel.history(limit=20):
            if msg.author.id == bot.user.id and msg.embeds:
                embed = msg.embeds[0]
                for field in embed.fields:
                    if field.name.lower() == "claimed by":
                        return await ctx.reply("❌ Already claimed.")
                embed.add_field(name="Claimed by", value=ctx.author.mention, inline=True)
                await msg.edit(embed=embed)
                await ctx.reply(f"✅ Claimed by {ctx.author.mention}")
                return
        await ctx.reply("❌ Could not find ticket message.")
    except Exception as e:
        await ctx.reply(f"❌ {e}")

@bot.command(name="close")
async def close_command(ctx):
    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ Ticket channels only.")
    if not (is_ticket_opener(ctx.channel, ctx.author) or has_staff_permission(ctx.author)):
        return await ctx.reply("❌ No permission.", mention_author=False)
    await close_ticket(ctx.channel, ctx.author)

@bot.command(name="rename")
async def rename_command(ctx, *, new_name=None):
    if not has_staff_permission(ctx.author):
        return await ctx.reply("❌ No permission.", mention_author=False)
    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ Ticket channels only.")
    if not new_name or len(new_name.strip()) < 2:
        return await ctx.reply("❌ Provide a name.")
    try:
        await ctx.channel.edit(name=new_name.lower().replace(" ", "-")[:100])
        await ctx.reply("✅ Renamed.")
    except Exception as e:
        await ctx.reply(f"❌ {e}")

@bot.command(name="add")
async def add_command(ctx, *, user_input=None):
    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ Ticket channels only.")
    if not can_add_or_remove(ctx.author, ctx.channel):
        return await ctx.reply("❌ No permission.", mention_author=False)
    if not user_input:
        return await ctx.reply("❌ Provide a user.")
    target = await resolve_member(ctx, user_input)
    if not target:
        return await ctx.reply("❌ User not found.")
    try:
        await ctx.channel.set_permissions(target, view_channel=True, send_messages=True, attach_files=True, read_message_history=True)
        await ctx.reply(f"✅ Added {target.mention}")
    except Exception as e:
        await ctx.reply(f"❌ {e}")

@bot.command(name="remove")
async def remove_command(ctx, *, user_input=None):
    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ Ticket channels only.")
    if not can_add_or_remove(ctx.author, ctx.channel):
        return await ctx.reply("❌ No permission.", mention_author=False)
    if not user_input:
        return await ctx.reply("❌ Provide a user.")
    target = await resolve_member(ctx, user_input)
    if not target:
        return await ctx.reply("❌ User not found.")
    if ctx.channel.topic.startswith("ticket-") and str(target.id) == ctx.channel.topic.replace("ticket-", ""):
        return await ctx.reply("❌ Cannot remove the ticket opener.")
    try:
        await ctx.channel.set_permissions(target, overwrite=None)
        await ctx.reply(f"✅ Removed {target.mention}")
    except Exception as e:
        await ctx.reply(f"❌ {e}")

# Keep-alive
class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"SAB KINGDOM Bot is online")
    def log_message(self, format, *args):
        return

def start_keep_alive():
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(("0.0.0.0", port), _HealthHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        print(f"Keep-alive on port {port}")
    except Exception as e:
        print(f"Keep-alive failed: {e}")

if __name__ == "__main__":
    start_keep_alive()
    if not TOKEN:
        print("ERROR: Set DISCORD_BOT_TOKEN environment variable.")
    else:
        bot.run(TOKEN)