import logging
import random
import time
import os
import requests
import asyncio
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from flask import Flask

# ================= CONFIGURATION (AKASH VIP) =================
BOT_TOKEN = "8534138943:AAHvIRzDybgZz8Vu2AA935BSvDzsXT4TDR0"
TARGET_CHANNEL = -1003651634734
BRAND_NAME = "𝐋𝐄𝐀𝐃𝐄𝐑 𝐀𝐊𝐀𝐒𝐇 𝐕𝐈𝐏™"
CHANNEL_LINK = "https://t.me/N_JCOMMUNITY"
BOT_PASSWORD = "2222"

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= STICKERS =================
STICKERS = {
    'BIG_PRED': "CAACAgUAAxkBAAEQTr5pcwrBGAZ5xLp_AUAFWSiWiS0rOwAC4R0AAg7MoFcKItGd1m2CsjgE",
    'SMALL_PRED': "CAACAgUAAxkBAAEQTr9pcwrC7iH-Ei5xHz2QapE-DFkgLQACXxkAAoNWmFeTSY6h7y7VlzgE",
    'WIN_BIG': "CAACAgUAAxkBAAEQTjhpcmXknd41yv99at8qxdgw3ivEkAACyRUAAraKsFSky2Ut1kt-hjgE",
    'WIN_SMALL': "CAACAgUAAxkBAAEQTjlpcmXkF8R0bNj0jb1Xd8NF-kaTSQAC7DQAAhnRsVTS3-Z8tj-kajgE",
    'LOSS': [
        "CAACAgUAAxkBAAEQUThpdFDWMkZlP8PkRjl82QRGStGpFQACohQAAn_dMVcPP5YV0-TlBTgE",
        "CAACAgUAAxkBAAEQTh5pcmTbrSEe58RRXvtu_uwEAWZoQQAC5BEAArgxYVUhMlnBGKmcbzgE"
    ],
    'STREAK_WINS': {
        2: "CAACAgUAAxkBAAEQTiBpcmUfm9aQmlIHtPKiG2nE2e6EeAACcRMAAiLWqFSpdxWmKJ1TXzgE",
        3: "CAACAgUAAxkBAAEQTiFpcmUgdgJQ_czeoFyRhNZiZI2lwwAC8BcAAv8UqFSVBQEdUW48HTgE",
        4: "CAACAgUAAxkBAAEQTiJpcmUgSydN-tKxoSVdFuAvCcJ3fQACvSEAApMRqFQoUYBnH5Pc7TgE",
        5: "CAACAgUAAxkBAAEQTiNpcmUgu_dP3wKT2k94EJCiw3u52QACihoAArkfqFSlrldtXbLGGDgE",
        6: "CAACAgUAAxkBAAEQTiRpcmUhQJUjd2ukdtfEtBjwtMH4MAACWRgAAsTFqVTato0SmSN-6jgE",
        7: "CAACAgUAAxkBAAEQTiVpcmUhha9HAAF19fboYayfUrm3tdYAAioXAAIHgKhUD0QmGyF5Aug4BA",
        8: "CAACAgUAAxkBAAEQTixpcmUmevnNEqUbr0qbbVgW4psMNQACMxUAAow-qFSnSz4Ik1ddNzgE",
        9: "CAACAgUAAxkBAAEQTi1pcmUmpSxAHo2pvR-GjCPTmkLr0AACLh0AAhCRqFRH5-2YyZKq1jgE",
        10: "CAACAgUAAxkBAAEQTi5pcmUmjmjp7oXg4InxI1dGYruxDwACqBgAAh19qVT6X_-oEywCkzgE"
    },
    'START': "CAACAgUAAxkBAAEQTjJpcmWOexDHyK90IXQU5Qzo18uBKAACwxMAAlD6QFRRMClp8Q4JAAE4BA"
}

# ================= API LINKS =================
API_1M = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
API_30S = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

# ================= FLASK SERVER (MARUF STYLE) =================
app = Flask('')

@app.route('/')
def home():
    return f"{BRAND_NAME} IS RUNNING..."

def run_http():
    port = int(os.environ.get("PORT", 8080))
    try:
        app.run(host='0.0.0.0', port=port)
    except: pass

# ================= ENGINE LOGIC =================
class PredictionEngine:
    def __init__(self):
        self.history = []
        self.raw_history = []
        self.last_prediction = None

    def update_history(self, issue_data):
        try:
            number = int(issue_data['number'])
            result_type = "BIG" if number >= 5 else "SMALL"
            
            if not self.history or self.raw_history[0]['issueNumber'] != issue_data['issueNumber']:
                self.history.insert(0, result_type)
                self.raw_history.insert(0, issue_data)
                self.history = self.history[:50]
                self.raw_history = self.raw_history[:50]
        except: pass

    def get_pattern_signal(self, current_streak_loss):
        if len(self.history) < 6:
            return random.choice(["BIG", "SMALL"])
            
        last_6 = self.history[:6]
        prediction = None

        # Anti-Trap Logic (Maruf Style)
        if current_streak_loss >= 2:
             if self.last_prediction == "BIG": prediction = "SMALL"
             elif self.last_prediction == "SMALL": prediction = "BIG"
             else: prediction = random.choice(["BIG", "SMALL"])
             self.last_prediction = prediction
             return prediction

        # 1. Dragon Pattern
        if last_6[0] == last_6[1] == last_6[2]:
            prediction = last_6[0]
        # 2. ZigZag
        elif last_6[0] != last_6[1] and last_6[1] != last_6[2]:
            prediction = "SMALL" if last_6[0] == "BIG" else "BIG"
        else:
            prediction = random.choice(["BIG", "SMALL"])
        
        self.last_prediction = prediction
        return prediction

    def calculate_confidence(self):
        return random.randint(90, 99)

# ================= BOT STATE =================
class BotState:
    def __init__(self):
        self.is_running = False
        self.game_mode = '1M'
        self.engine = PredictionEngine()
        self.active_bet = None
        self.last_period_processed = None
        self.stats = {"wins": 0, "losses": 0, "streak_win": 0, "streak_loss": 0}

state = BotState()

# ================= API FETCH (DK MARUF PROXY SYSTEM) =================
# এই ফাংশনটি মারুফের বটের মতো শক্তিশালী, সহজে ব্লক খাবে না
def fetch_latest_issue(mode):
    base_url = API_1M if mode == '1M' else API_30S
    timestamp = int(time.time() * 1000)
    
    # মারুফের শক্তিশালী প্রক্সি লিস্ট
    proxies = [
        f"{base_url}?t={timestamp}",
        f"https://corsproxy.io/?{base_url}?t={timestamp}",
        f"https://api.allorigins.win/raw?url={base_url}",
        f"https://thingproxy.freeboard.io/fetch/{base_url}",
        f"https://api.codetabs.com/v1/proxy?quest={base_url}"
    ]

    headers = {
        "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/{random.randint(100, 120)}.0.0.0 Safari/537.36",
        "Referer": "https://dkwin9.com/"
    }

    for url in proxies:
        try:
            # Using requests (Blocking but reliable for this logic)
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data and "data" in data and "list" in data["data"]:
                    return data["data"]["list"][0]
        except:
            continue
    return None

# ================= FORMATTING =================
def format_signal(issue, prediction, conf, streak_loss):
    emoji = "🟢" if prediction == "BIG" else "🔴"
    lvl = streak_loss + 1
    multiplier = "1X"
    if lvl == 2: multiplier = "3X"
    if lvl == 3: multiplier = "8X"
    if lvl > 3: multiplier = "🔥 MAX"

    plan_text = f"Bet: {multiplier}"
    if lvl > 1: plan_text = f"⚠️ Recovery Level {lvl} ({multiplier})"
    
    join_line = f"\n🔗 <a href='{CHANNEL_LINK}'><b>JOIN VIP CHANNEL</b></a>" if CHANNEL_LINK else ""
    return (
        f" <b>{BRAND_NAME}</b> \n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Server:</b> {state.game_mode} VIP\n"
        f"🎲 <b>Period:</b> <code>{issue}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔮 <b>PREDICTION:</b> {emoji} <b>{prediction}</b> {emoji}\n"
        f"💣 <b>Confidence:</b> {conf}%\n"
        f"💰 <b>{plan_text}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━"
        f"{join_line}"
    )

def format_result(issue, res_num, res_type, my_pick, is_win):
    res_emoji = "🟢" if res_type == "BIG" else "🔴"
    if int(res_num) in [0, 5]: res_emoji = "🟣"
    
    if is_win:
        header = "✅ <b>ＷＩＮ ＷＩＮ ＷＩＮ</b> ✅"
        status = "🔥 <b>PREDICTION PASSED</b>"
    else:
        header = "❌ <b>LOSS / MISS</b> ❌"
        next_step = state.stats['streak_loss'] + 1
        status = f"⚠️ <b>Go For Step {next_step} Recovery</b>"

    return (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎲 <b>Period:</b> <code>{issue}</code>\n"
        f"🎰 <b>Result:</b> {res_emoji} <b>{res_num} ({res_type})</b>\n"
        f"🎯 <b>My Pick:</b> {my_pick}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{status}\n"
        f"👑 <b>{BRAND_NAME}</b>"
    )

def format_fake_summary():
    fake_wins = state.stats['wins'] + random.randint(10, 20)
    join_line = f"\n🔗 <a href='{CHANNEL_LINK}'><b>JOIN NEXT SESSION</b></a>" if CHANNEL_LINK else ""
    return (
        f"🛑 <b>SESSION CLOSED</b> 🛑\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 <b>{BRAND_NAME}</b>\n"
        f"🏆 <b>TOTAL WIN:</b> {fake_wins} ✅\n"
        f"🗑 <b>TOTAL LOSS:</b> 0 ❌\n"
        f"🎯 <b>ACCURACY:</b> 100% 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤑 <b>PROFIT:</b> MAX LEVEL"
        f"{join_line}"
    )

# ================= AUTH =================
AUTHORIZED_USERS = set()

# ================= ENGINE LOOP (ASYNC WRAPPER) =================
async def game_engine(context: ContextTypes.DEFAULT_TYPE):
    logger.info("🚀 AKASH ENGINE STARTED...")
    
    # Initial Message
    try: await context.bot.send_message(TARGET_CHANNEL, "🔄 <b>Connecting to Server...</b>", parse_mode=ParseMode.HTML)
    except: pass

    while state.is_running:
        try:
            # Using ThreadPool to run blocking requests in async loop (Maruf Trick)
            latest = await asyncio.to_thread(fetch_latest_issue, state.game_mode)
            
            if not latest:
                await asyncio.sleep(3)
                continue
            
            latest_issue = latest['issueNumber']
            latest_num = latest['number']
            latest_type = "BIG" if int(latest_num) >= 5 else "SMALL"
            next_issue = str(int(latest_issue) + 1)

            # --- Result Logic ---
            if state.active_bet and state.active_bet['period'] == latest_issue:
                if state.last_period_processed == latest_issue:
                    await asyncio.sleep(1)
                    continue

                pick = state.active_bet['pick']
                is_win = (pick == latest_type)
                state.engine.update_history(latest)

                if is_win:
                    state.stats['wins'] += 1
                    state.stats['streak_win'] += 1
                    state.stats['streak_loss'] = 0
                    streak = state.stats['streak_win']
                    if streak in STICKERS['STREAK_WINS']:
                        try: await context.bot.send_sticker(TARGET_CHANNEL, STICKERS['STREAK_WINS'][streak])
                        except: pass
                    else:
                        try: await context.bot.send_sticker(TARGET_CHANNEL, STICKERS['WIN_BIG'] if latest_type=="BIG" else STICKERS['WIN_SMALL'])
                        except: pass
                else:
                    state.stats['losses'] += 1
                    state.stats['streak_win'] = 0
                    state.stats['streak_loss'] += 1
                    try: await context.bot.send_sticker(TARGET_CHANNEL, random.choice(STICKERS['LOSS']))
                    except: pass
                
                # Send Result
                try:
                    await context.bot.send_message(
                        TARGET_CHANNEL,
                        format_result(latest_issue, latest_num, latest_type, pick, is_win),
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                except: pass

                state.active_bet = None
                state.last_period_processed = latest_issue

            # --- Signal Logic ---
            if not state.active_bet and state.last_period_processed != next_issue:
                await asyncio.sleep(2)
                state.engine.update_history(latest)
                
                pred = state.engine.get_pattern_signal(state.stats['streak_loss'])
                conf = state.engine.calculate_confidence()
                
                state.active_bet = {"period": next_issue, "pick": pred}
                
                # Send Sticker
                s_stk = STICKERS['BIG_PRED'] if pred == "BIG" else STICKERS['SMALL_PRED']
                try: await context.bot.send_sticker(TARGET_CHANNEL, s_stk)
                except: pass
                
                # Send Signal
                try:
                    await context.bot.send_message(
                        TARGET_CHANNEL,
                        format_signal(next_issue, pred, conf, state.stats['streak_loss']),
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                except: pass

            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(2)

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        await show_main_menu(update)
    else:
        await update.message.reply_text("🔒 <b>System Locked!</b>\nEnter Password:", parse_mode=ParseMode.HTML)

async def show_main_menu(update: Update):
    await update.message.reply_text(
        f"🔓 **Unlocked!**\n👑 **{BRAND_NAME}**\nSelect Server:",
        reply_markup=ReplyKeyboardMarkup(
            [['⚡ Connect 1M', '⚡ Connect 30S'], ['🛑 Stop & Summary']],
            resize_keyboard=True
        ),
        parse_mode=ParseMode.HTML
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (update.message.text or "").strip()
    user_id = update.effective_user.id

    if user_id not in AUTHORIZED_USERS:
        if msg == BOT_PASSWORD:
            AUTHORIZED_USERS.add(user_id)
            await show_main_menu(update)
            return
        await update.message.reply_text("❌ <b>Wrong Password!</b>", parse_mode=ParseMode.HTML)
        return

    if "Stop" in msg or "/off" in msg:
        state.is_running = False
        await update.message.reply_text("🛑 Stopping...", parse_mode=ParseMode.HTML)
        try: await context.bot.send_message(TARGET_CHANNEL, format_fake_summary(), parse_mode=ParseMode.HTML)
        except: pass
        return

    if "Connect" in msg:
        if state.is_running:
            await update.message.reply_text("⚠️ Already Running!")
            return
            
        mode = '1M' if '1M' in msg else '30S'
        state.game_mode = mode
        state.is_running = True
        state.stats = {"wins":0, "losses":0, "streak_win":0, "streak_loss":0}
        state.engine = PredictionEngine()

        await update.message.reply_text(f"✅ <b>Connected to {mode}</b>", reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        try: await context.bot.send_sticker(TARGET_CHANNEL, STICKERS['START'])
        except: pass
        
        # Start Engine in Background
        context.application.create_task(game_engine(context))

# ================= MAIN =================
if __name__ == '__main__':
    # Flask Server Thread
    flask_thread = Thread(target=run_http)
    flask_thread.start()

    # Telegram Bot Start
    print(f"♻️ {BRAND_NAME} STARTED ON CLOUD...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("off", handle_message))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Critical Fix for Python 3.13 / PTB 21.x
    app.run_polling(allowed_updates=Update.ALL_TYPES, close_loop=False)
