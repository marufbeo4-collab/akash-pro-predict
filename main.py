import asyncio
import logging
import os
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from threading import Thread
from typing import Dict, List, Optional, Tuple

import requests
from flask import Flask

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# =========================
# CONFIG (ONLY TOKEN YOU SET)
# =========================
BOT_TOKEN = "8534138943:AAHvIRzDybgZz8Vu2AA935BSvDzsXT4TDR0"

BRAND_NAME = "𝐋𝐄𝐀𝐃𝐄𝐑 𝐀𝐊𝐀𝐒𝐇 𝐕𝐈𝐏™"
CHANNEL_LINK = "https://t.me/N_JCOMMUNITY"
REG_LINK = "https://tkclub2.com/#/register?invitationCode=54348203116"
OWNER_USERNAME = "@LEADER_AKASH69"

TARGETS = {"MAIN_GROUP": -1003651634734}

# =========================
# MARUF-STYLE 1M API (POST)
# =========================
API_URL = "https://api880.inpay88.net/api/webapi/GetNoaverageEmerdList"
FETCH_TIMEOUT = 6.0
FETCH_RETRY_SLEEP = 0.7

BD_TZ = timezone(timedelta(hours=6))

# Password source A1 (PUBLIC VIEW required)
PASSWORD_SHEET_ID = "1_x1JOZp3HOTf9x02qKB0Tm4wD6Ype9MgguH-ATD0QCk"
PASSWORD_SHEET_GID = "0"
PASSWORD_FALLBACK = "2222"

MAX_RECOVERY_STEPS = 8
ENGINE_TICK = 0.8  # loop smooth

# =========================
# STICKERS
# =========================
STICKERS = {
    "PRED_1M_BIG": "CAACAgUAAxkBAAEQTr5pcwrBGAZ5xLp_AUAFWSiWiS0rOwAC4R0AAg7MoFcKItGd1m2CsjgE",
    "PRED_1M_SMALL": "CAACAgUAAxkBAAEQTr9pcwrC7iH-Ei5xHz2QapE-DFkgLQACXxkAAoNWmFeTSY6h7y7VlzgE",
    "START_1M": "CAACAgUAAxkBAAEQUrRpdYvESSIrn4-Lm936I6F8_BaN-wACChYAAuBHOVc6YQfcV-EKqjgE",
    "START_END_ALWAYS": "CAACAgUAAxkBAAEQTjRpcmWdzXBzA7e9KNz8QgTI6NXlxgACuRcAAh2x-FaJNjq4QG_DujgE",
    "WIN_BIG": "CAACAgUAAxkBAAEQTjhpcmXknd41yv99at8qxdgw3ivEkAACyRUAAraKsFSky2Ut1kt-hjgE",
    "WIN_SMALL": "CAACAgUAAxkBAAEQTjlpcmXkF8R0bNj0jb1Xd8NF-kaTSQAC7DQAAhnRsVTS3-Z8tj-kajgE",
    "WIN_ALWAYS": "CAACAgUAAxkBAAEQUTZpdFC4094KaOEdiE3njwhAGVCuBAAC4hoAAt0EqVQXmdKVLGbGmzgE",
    "WIN_ANY": "CAACAgUAAxkBAAEQTydpcz9Kv1L2PJyNlbkcZpcztKKxfQACDRsAAoq1mFcAAYLsJ33TdUA4BA",
    "LOSS": "CAACAgUAAxkBAAEQTytpcz9VQoHyZ5ClbKSqKCJbpqX6yQACahYAAl1wAAFUL9xOdyh8UL84BA",
    "WIN_POOL": [
        "CAACAgUAAxkBAAEQTzNpcz9ns8rx_5xmxk4HHQOJY2uUQQAC3RoAAuCpcFbMKj0VkxPOdTgE",
        "CAACAgUAAxkBAAEQTzRpcz9ni_I4CjwFZ3iSt4xiXxFgkwACkxgAAnQKcVYHd8IiRqfBXTgE",
        "CAACAgUAAxkBAAEQTx9pcz8GryuxGBMFtzRNRbiCTg9M8wAC5xYAAkN_QFWgd5zOh81JGDgE",
        "CAACAgUAAxkBAAEQT_tpc4E3AxHmgW9VWKrzWjxlrvzSowACghkAAlbXcFWxdto6TqiBrzgE",
        "CAACAgUAAxkBAAEQT_9pc4FHKn0W6ZfWOSaN6FUPzfmbnQACXR0AAqMbMFc-_4DHWbq7sjgE",
        "CAACAgUAAxkBAAEQUAFpc4FIokHE09p165cCsWiUYV648wACuhQAAo3aMVeAsNW9VRuVvzgE",
        "CAACAgUAAxkBAAEQUANpc4FJNTnfuBiLe-dVtoNCf3CQlAAC9xcAArE-MFfS5HNyds2tWTgE",
        "CAACAgUAAxkBAAEQUAVpc4FKhJ_stZ3VRRzWUuJGaWbrAgACOhYAAst6OVehdeQEGZlXiDgE",
        "CAACAgUAAxkBAAEQUAtpc4HcYxkscyRY2rhAAcmqMR29eAACOBYAAh7fwVU5Xy399k3oFDgE",
        "CAACAgUAAxkBAAEQUCdpc4IuoaqPZ-5vn2RTlJZ_kbeXHQACXRUAAgln-FQ8iTzzJg_GLzgE",
    ],
    "SUPER_WIN": {
        2: "CAACAgUAAxkBAAEQTiBpcmUfm9aQmlIHtPKiG2nE2e6EeAACcRMAAiLWqFSpdxWmKJ1TXzgE",
        3: "CAACAgUAAxkBAAEQTiFpcmUgdgJQ_czeoFyRhNZiZI2lwwAC8BcAAv8UqFSVBQEdUW48HTgE",
        4: "CAACAgUAAxkBAAEQTiJpcmUgSydN-tKxoSVdFuAvCcJ3fQACvSEAApMRqFQoUYBnH5Pc7TgE",
        5: "CAACAgUAAxkBAAEQTiNpcmUgu_dP3wKT2k94EJCiw3u52QACihoAArkfqFSlrldtXbLGGDgE",
        6: "CAACAgUAAxkBAAEQTiRpcmUhQJUjd2ukdtfEtBjwtMH4MAACWRgAAsTFqVTato0SmSN-6jgE",
        7: "CAACAgUAAxkBAAEQTiVpcmUhha9HAAF19fboYayfUrm3tdYAAioXAAIHgKhUD0QmGyF5Aug4BA",
        8: "CAACAgUAAxkBAAEQTixpcmUmevnNEqUbr0qbbVgW4psMNQACMxUAAow-qFSnSz4Ik1ddNzgE",
        9: "CAACAgUAAxkBAAEQTi1pcmUmpSxAHo2pvR-GjCPTmkLr0AACLh0AAhCRqFRH5-2YyZKq1jgE",
        10: "CAACAgUAAxkBAAEQTi5pcmUmjmjp7oXg4InxI1dGYruxDwACqBgAAh19qVT6X_-oEywCkzgE",
    },
    "COLOR_RED": "CAACAgUAAxkBAAEQUClpc4JDd9n_ZQ45hPk-a3tEjFXnugACbhgAAqItoVd2zRs4VkXOHDgE",
    "COLOR_GREEN": "CAACAgUAAxkBAAEQUCppc4JDHWjTzBCFIOx2Hcjtz9UnnAACzRwAAnR3oVejA9DVGekyYTgE",
}

# =========================
# FLASK KEEP ALIVE
# =========================
app = Flask("")

@app.route("/")
def home():
    return "ALIVE"

def run_http():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    Thread(target=run_http, daemon=True).start()

# =========================
# PASSWORD
# =========================
def fetch_password_a1() -> str:
    try:
        url = (
            f"https://docs.google.com/spreadsheets/d/{PASSWORD_SHEET_ID}/export"
            f"?format=csv&gid={PASSWORD_SHEET_GID}&range=A1"
        )
        r = requests.get(url, timeout=8, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return PASSWORD_FALLBACK
        val = r.text.strip().strip('"').strip()
        return val if val else PASSWORD_FALLBACK
    except Exception:
        return PASSWORD_FALLBACK

async def get_live_password() -> str:
    return await asyncio.to_thread(fetch_password_a1)

# =========================
# PREDICTION ENGINE (ZIGZAG PRIORITY)
# =========================
class PredictionEngine:
    def __init__(self):
        self.history: List[str] = []
        self.raw_history: List[dict] = []
        self.last_prediction: Optional[str] = None

    def update_history(self, issue_data: dict):
        try:
            number = int(issue_data["number"])
            result_type = "BIG" if number >= 5 else "SMALL"
        except Exception:
            return

        if (not self.raw_history) or (self.raw_history[0].get("issueNumber") != issue_data.get("issueNumber")):
            self.history.insert(0, result_type)
            self.raw_history.insert(0, issue_data)
            self.history = self.history[:120]
            self.raw_history = self.raw_history[:120]

    def calc_confidence(self, streak_loss):
        base = random.randint(95, 99)
        return max(60, base - (streak_loss * 5))

    def get_pattern_signal(self, current_streak_loss):
        # ইতিহাস খুব ছোট হলে ডিফল্ট
        if len(self.history) < 3:
            return self.history[0] if self.history else random.choice(["BIG", "SMALL"])

        last = self.history[0]
        prev1 = self.history[1]
        prev2 = self.history[2]

        # =========================================================
        # 🔥 PRIORITY 1: ZIGZAG MODE (B-S-B or S-B-S)
        # =========================================================
        # যদি লাস্ট ৩টা জিগজ্যাগ হয়, তবে লস থাকলেও এটা ফলো করবে।
        if last != prev1 and prev1 != prev2:
            # ZigZag Mode: উল্টা ধরো
            return "SMALL" if last == "BIG" else "BIG"

        # =========================================================
        # 🔥 PRIORITY 2: DOUBLE MODE (B-B or S-S)
        # =========================================================
        # যদি লাস্ট ২টা সেম হয়, তবে সেম ধরবে।
        if last == prev1:
            return last

        # =========================================================
        # 🐢 PRIORITY 3: DEFAULT / LOSS RECOVERY
        # =========================================================
        # যদি কোনো স্ট্রং প্যাটার্ন না থাকে (বা প্যাটার্ন ভেঙে যায়), 
        # তখন আমরা সেফ মোড (Trend Follow/Copy Paste) এ থাকব।
        return last

# =========================
# BOT STATE
# =========================
def now_bd_str() -> str:
    return datetime.now(BD_TZ).strftime("%I:%M:%S %p")

@dataclass
class ActiveBet:
    predicted_issue: str
    pick: str
    random_color: Optional[str] = None
    checking_msg_ids: Dict[int, int] = field(default_factory=dict)

@dataclass
class BotState:
    running: bool = False
    session_id: int = 0

    engine: PredictionEngine = field(default_factory=PredictionEngine)
    active: Optional[ActiveBet] = None

    last_result_issue: Optional[str] = None
    last_signal_issue: Optional[str] = None

    wins: int = 0
    losses: int = 0
    streak_win: int = 0
    streak_loss: int = 0
    max_win_streak: int = 0
    max_loss_streak: int = 0

    unlocked: bool = False
    expected_password: str = PASSWORD_FALLBACK

    selected_targets: List[int] = field(default_factory=lambda: [TARGETS["MAIN_GROUP"]])

    color_mode: bool = False

    graceful_stop_requested: bool = False
    stop_event: asyncio.Event = field(default_factory=asyncio.Event)

state = BotState()

# =========================
# FETCH API
# =========================
def _fetch_latest_issue_sync() -> Optional[dict]:
    payload = {
        "pageSize": 10,
        "pageNo": 1,
        "typeId": 1,
        "language": 0,
        "random": "4ec1d2c67364426aa056214302636756",
        "signature": "D39F9069695C55720235791E0D10D695",
        "timestamp": int(time.time()),
    }
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Mobile Safari/537.36",
        "Origin": "https://dkwin9.com",
        "Referer": "https://dkwin9.com/",
    }
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=FETCH_TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            if data and "data" in data and "list" in data["data"] and data["data"]["list"]:
                return data["data"]["list"][0]
    except Exception:
        pass
    return None

async def fetch_latest_issue() -> Optional[dict]:
    return await asyncio.to_thread(_fetch_latest_issue_sync)

# =========================
# MESSAGES
# =========================
def pick_badge(pick: str) -> str:
    return "🟢 <b>BIG</b>" if pick == "BIG" else "🔴 <b>SMALL</b>"

def marketing_block() -> str:
    return (
        "📌 <b>NOTICE:</b> এই লিংকে <b>Account Open</b> করে <b>Deposit</b> করুন —\n"
        "💎 তারপর <b>VIP</b> তে আরও Strong System নিন 👇\n"
        f"🔗 <b><a href='{REG_LINK}'>REGISTRATION LINK</a></b>"
    )

def format_signal(issue: str, pick: str, conf: int, rand_col: Optional[str]) -> str:
    entry = f"🎯 <b>Entry:</b> {pick_badge(pick)}"
    
    # Random Color Display
    if state.color_mode and rand_col:
        c_txt = "🟩 <b>GREEN</b>" if rand_col == "GREEN" else "🟥 <b>RED</b>"
        entry += f"  |  {c_txt}"

    return (
        f"⚡ <b>{BRAND_NAME}</b> ⚡\n"
        f"🧾 <b>Period:</b> <code>{issue}</code>\n"
        f"{entry}\n"
        f"✨ <b>Confidence:</b> 🔥 <b>{conf}%</b>\n"
        f"🧠 <b>Recovery:</b> <b>{state.streak_loss}/{MAX_RECOVERY_STEPS}</b>\n"
        f"🕒 <b>{now_bd_str()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{marketing_block()}\n"
        f"👤 <b>Owner:</b> {OWNER_USERNAME}"
    )

def format_checking(wait_issue: str) -> str:
    return (
        "🛰 <b>RESULT CHECKING...</b>\n"
        f"🧾 <b>Waiting:</b> <code>{wait_issue}</code>\n"
        f"🕒 <b>{now_bd_str()}</b>"
    )

def format_result(issue: str, res_num: str, res_type: str, pick: str, is_win: bool) -> str:
    head = "✅ <b>WIN CONFIRMED</b>" if is_win else "❌ <b>LOSS CONFIRMED</b>"
    res_emoji = "🟢" if res_type == "BIG" else "🔴"
    return (
        f"{head}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🧾 <b>Period:</b> <code>{issue}</code>\n"
        f"🎰 <b>Result:</b> {res_emoji} <b>{res_num} ({res_type})</b>\n"
        f"🎯 <b>Your Pick:</b> {pick_badge(pick)}\n"
        f"🧠 <b>Recovery:</b> <b>{state.streak_loss}/{MAX_RECOVERY_STEPS}</b>\n"
        f"📊 <b>W:</b> <b>{state.wins}</b> | <b>L:</b> <b>{state.losses}</b>\n"
        f"🕒 <b>{now_bd_str()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{marketing_block()}"
    )

def format_summary() -> str:
    total = state.wins + state.losses
    wr = (state.wins / total * 100) if total else 0.0
    return (
        "🛑 <b>SESSION SUMMARY</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Total:</b> <b>{total}</b>\n"
        f"✅ <b>Win:</b> <b>{state.wins}</b>\n"
        f"❌ <b>Loss:</b> <b>{state.losses}</b>\n"
        f"🎯 <b>Win Rate:</b> <b>{wr:.1f}%</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 <b>Max Win Streak:</b> <b>{state.max_win_streak}</b>\n"
        f"🧨 <b>Max Loss Streak:</b> <b>{state.max_loss_streak}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📣 <b>Channel:</b> <b><a href='{CHANNEL_LINK}'>JOIN NOW</a></b>\n"
        f"🕒 <b>Closed:</b> <b>{now_bd_str()}</b>"
    )

# =========================
# PANEL
# =========================
def _chat_name(chat_id: int) -> str:
    if chat_id == TARGETS["MAIN_GROUP"]:
        return "MAIN GROUP"
    return str(chat_id)

def panel_text() -> str:
    running = "🟢 RUNNING" if state.running else "🔴 STOPPED"
    total = state.wins + state.losses
    wr = (state.wins / total * 100) if total else 0.0

    color = "🎨 <b>COLOR:</b> <b>ON</b>" if state.color_mode else "🎨 <b>COLOR:</b> <b>OFF</b>"
    
    grace = "🧠 <b>STOP AFTER WIN:</b> ✅" if state.graceful_stop_requested else "🧠 <b>STOP AFTER WIN:</b> ❌"

    return (
        "🔐 <b>CONTROL PANEL</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 <b>Status:</b> {running}\n"
        f"{color}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 <b>Live Stats</b>\n"
        f"✅ Win: <b>{state.wins}</b>\n"
        f"❌ Loss: <b>{state.losses}</b>\n"
        f"🎯 WinRate: <b>{wr:.1f}%</b>\n"
        f"🔥 WinStreak: <b>{state.streak_win}</b> | 🧊 LossStreak: <b>{state.streak_loss}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{grace}\n"
        "👇 <i>Select then Start</i>"
    )

def selector_markup() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🎨 Random Color", callback_data="TOGGLE_COLOR")],
        [InlineKeyboardButton("⚡ Start 1 MIN", callback_data="START:1M")],
        [InlineKeyboardButton("🧠 Stop After Win", callback_data="STOP:GRACEFUL"),
         InlineKeyboardButton("🛑 Stop Now", callback_data="STOP:FORCE")],
        [InlineKeyboardButton("🔄 Refresh Panel", callback_data="REFRESH_PANEL")]
    ]
    return InlineKeyboardMarkup(rows)

# =========================
# HELPERS
# =========================
async def safe_delete(bot, chat_id: int, msg_id: int):
    try:
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except Exception:
        pass

async def broadcast_sticker(bot, sticker_id: str):
    for cid in state.selected_targets:
        try:
            await bot.send_sticker(cid, sticker_id)
        except Exception:
            pass

async def broadcast_message(bot, text: str) -> Dict[int, int]:
    out = {}
    for cid in state.selected_targets:
        try:
            m = await bot.send_message(cid, text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            out[cid] = m.message_id
        except Exception:
            pass
    return out

# =========================
# SESSION CONTROL
# =========================
def reset_stats():
    state.wins = 0
    state.losses = 0
    state.streak_win = 0
    state.streak_loss = 0
    state.max_win_streak = 0
    state.max_loss_streak = 0

async def stop_session(bot, reason: str = "manual"):
    state.session_id += 1
    state.running = False
    state.stop_event.set()

    if state.active:
        for cid, mid in (state.active.checking_msg_ids or {}).items():
            await safe_delete(bot, cid, mid)

    await broadcast_sticker(bot, STICKERS["START_END_ALWAYS"])

    for cid in state.selected_targets:
        try:
            await bot.send_message(cid, format_summary(), parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        except Exception:
            pass

    state.active = None
    state.graceful_stop_requested = False

async def start_session(bot):
    state.session_id += 1
    state.running = True
    state.stop_event.clear()
    state.graceful_stop_requested = False

    state.engine = PredictionEngine()
    state.active = None
    state.last_result_issue = None
    state.last_signal_issue = None

    reset_stats()

    await broadcast_sticker(bot, STICKERS["START_1M"])
    await broadcast_sticker(bot, STICKERS["START_END_ALWAYS"])

# =========================
# ENGINE LOOP
# =========================
async def engine_loop(app: Application, my_session: int):
    bot = app.bot

    while state.running and state.session_id == my_session:
        if state.stop_event.is_set():
            break

        latest = await fetch_latest_issue()
        if not latest:
            await asyncio.sleep(FETCH_RETRY_SLEEP)
            continue

        issue = str(latest.get("issueNumber"))
        num = str(latest.get("number"))
        res_type = "BIG" if int(num) >= 5 else "SMALL"
        next_issue = str(int(issue) + 1)

        state.engine.update_history(latest)

        resolved_this_tick = False

        # ========== RESULT ==========
        if state.active and state.active.predicted_issue == issue:
            if state.last_result_issue == issue:
                await asyncio.sleep(0.2)
                continue

            pick = state.active.pick
            is_win = (pick == res_type)

            if is_win:
                state.wins += 1
                state.streak_win += 1
                state.streak_loss = 0
                state.max_win_streak = max(state.max_win_streak, state.streak_win)

                await broadcast_sticker(bot, STICKERS["WIN_ALWAYS"])
                if state.streak_win in STICKERS["SUPER_WIN"]:
                    await broadcast_sticker(bot, STICKERS["SUPER_WIN"][state.streak_win])
                else:
                    await broadcast_sticker(bot, random.choice(STICKERS["WIN_POOL"]))
                
                await broadcast_sticker(bot, STICKERS["WIN_BIG"] if res_type == "BIG" else STICKERS["WIN_SMALL"])
                await broadcast_sticker(bot, STICKERS["WIN_ANY"])
            else:
                state.losses += 1
                state.streak_loss += 1
                state.streak_win = 0
                state.max_loss_streak = max(state.max_loss_streak, state.streak_loss)
                await broadcast_sticker(bot, STICKERS["LOSS"])

            await broadcast_message(bot, format_result(issue, num, res_type, pick, is_win))

            for cid, mid in (state.active.checking_msg_ids or {}).items():
                await safe_delete(bot, cid, mid)

            state.last_result_issue = issue
            state.active = None
            resolved_this_tick = True

            if state.graceful_stop_requested and is_win:
                await stop_session(bot, reason="graceful_done")
                break

        # ========== SIGNAL ==========
        if (not state.active) and (not resolved_this_tick) and (state.last_signal_issue != next_issue):
            if state.streak_loss >= MAX_RECOVERY_STEPS:
                await broadcast_message(
                    bot,
                    "🧊 <b>SAFETY STOP</b>\n━━━━━━━━━━━━━━━━━━━━\n"
                    "Recovery limit এ চলে গেছে — সেফটির জন্য Session বন্ধ করা হলো ✅"
                )
                await stop_session(bot, reason="max_steps")
                break

            pred = state.engine.get_pattern_signal(state.streak_loss)
            conf = state.engine.calc_confidence(state.streak_loss)

            rand_color = None
            if state.color_mode:
                rand_color = random.choice(["GREEN", "RED"])

            s_stk = STICKERS["PRED_1M_BIG"] if pred == "BIG" else STICKERS["PRED_1M_SMALL"]
            await broadcast_sticker(bot, s_stk)

            if state.color_mode and rand_color:
                await broadcast_sticker(bot, STICKERS["COLOR_GREEN"] if rand_color == "GREEN" else STICKERS["COLOR_RED"])

            await broadcast_message(bot, format_signal(next_issue, pred, conf, rand_color))

            checking_ids = {}
            for cid in state.selected_targets:
                try:
                    m = await bot.send_message(cid, format_checking(next_issue), parse_mode=ParseMode.HTML)
                    checking_ids[cid] = m.message_id
                except Exception:
                    pass

            state.active = ActiveBet(predicted_issue=next_issue, pick=pred, random_color=rand_color, checking_msg_ids=checking_ids)
            state.last_signal_issue = next_issue

        await asyncio.sleep(ENGINE_TICK)

# =========================
# COMMANDS & CALLBACKS
# =========================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.expected_password = await get_live_password()
    state.unlocked = False
    await update.message.reply_text(
        "🔒 <b>SYSTEM LOCKED</b>\n━━━━━━━━━━━━━━━━━━━━\n✅ Password দিন:",
        parse_mode=ParseMode.HTML
    )

async def cmd_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not state.unlocked:
        state.expected_password = await get_live_password()
        await update.message.reply_text("🔒 <b>LOCKED</b>\nPassword দিন:", parse_mode=ParseMode.HTML)
        return
    await update.message.reply_text(
        panel_text(),
        parse_mode=ParseMode.HTML,
        reply_markup=selector_markup(),
        disable_web_page_preview=True
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "").strip()

    if not state.unlocked:
        state.expected_password = await get_live_password()
        if txt == state.expected_password:
            state.unlocked = True
            await update.message.reply_text("✅ <b>UNLOCKED</b>", parse_mode=ParseMode.HTML)
            await update.message.reply_text(panel_text(), parse_mode=ParseMode.HTML, reply_markup=selector_markup())
        else:
            await update.message.reply_text("❌ <b>WRONG PASSWORD</b>", parse_mode=ParseMode.HTML)
        return

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data or ""

    if not state.unlocked:
        await q.edit_message_text("🔒 <b>LOCKED</b>\n/start দিন।", parse_mode=ParseMode.HTML)
        return

    if data == "REFRESH_PANEL":
        await q.edit_message_text(panel_text(), parse_mode=ParseMode.HTML, reply_markup=selector_markup())
        return

    if data == "TOGGLE_COLOR":
        state.color_mode = not state.color_mode
        await q.edit_message_text(panel_text(), parse_mode=ParseMode.HTML, reply_markup=selector_markup())
        return

    if data == "START:1M":
        if state.running:
            await stop_session(context.bot, reason="restart_manual")
        await start_session(context.bot)
        context.application.create_task(engine_loop(context.application, state.session_id))
        await q.edit_message_text(panel_text(), parse_mode=ParseMode.HTML, reply_markup=selector_markup())
        return

    if data == "STOP:FORCE":
        if state.running:
            await stop_session(context.bot, reason="force")
        await q.edit_message_text(panel_text(), parse_mode=ParseMode.HTML, reply_markup=selector_markup())
        return

    if data == "STOP:GRACEFUL":
        if state.running:
            state.graceful_stop_requested = True
            if state.streak_loss == 0 and state.active is None:
                await stop_session(context.bot, reason="graceful_now")
        await q.edit_message_text(panel_text(), parse_mode=ParseMode.HTML, reply_markup=selector_markup())
        return

# =========================
# MAIN
# =========================
def main():
    logging.basicConfig(level=logging.WARNING)
    keep_alive()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("panel", cmd_panel))
    application.add_handler(CallbackQueryHandler(on_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    application.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
