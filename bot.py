import telebot
import requests
import time
import sqlite3
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8340071997:AAH3nG5GmoQ2Es73EkoVGFQnH-01Qjx96A4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

OWNER_ID = 7953454559  # yahan apna Telegram user ID daal

LIKE_API = "https://new-like-api-by-ajay-2.vercel.app/"
VISIT_API = "https://visit-api-by-ajay-free.vercel.app/"
SPAM_API = "YOUR_SPAM_API"

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    last_like TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cooldown (
    user_id INTEGER,
    command TEXT,
    time INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS uid_cooldown (
    uid TEXT,
    time INTEGER
)
""")

conn.commit()

def can_like(user_id):
    now = datetime.now()

    reset_time = now.replace(hour=4, minute=0, second=0, microsecond=0)
    if now.hour < 4:
        reset_time -= timedelta(days=1)

    cursor.execute("SELECT last_like FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()

    if data:
        last_like = datetime.fromisoformat(data[0])
        if last_like > reset_time:
            return False

    cursor.execute("REPLACE INTO users (user_id, last_like) VALUES (?,?)",
                   (user_id, now.isoformat()))
    conn.commit()
    return True
    
def check_cooldown(user_id, command, seconds=30):
    now = int(time.time())

    cursor.execute("SELECT time FROM cooldown WHERE user_id=? AND command=?",
                   (user_id, command))
    data = cursor.fetchone()

    if data:
        if now - data[0] < seconds:
            return False

    cursor.execute("REPLACE INTO cooldown (user_id, command, time) VALUES (?,?,?)",
                   (user_id, command, now))
    conn.commit()
    return True

def check_uid(uid, seconds=30):
    now = int(time.time()

)
    cursor.execute("SELECT time FROM uid_cooldown WHERE uid=?", (uid,))
    data = cursor.fetchone()

    if data:
        if now - data[0] < seconds:
            return False

    cursor.execute("REPLACE INTO uid_cooldown (uid, time) VALUES (?,?)",
                   (uid, now))
    conn.commit()
    return True 
    
def start_message():
    text = """<b>Welcome to the Garena Free Fire Bot! 👋

Available Commands: 📋
/like {region} {uid} - Send likes to player (1 use per day, resets at 4 AM IST)
/visit {region} {uid} - Get player information
/spam {uid} - Send friend requests
/help - Show this help message

Note: Commands have limits ⏳
• /like: 1 time per day (resets at 4 AM IST)
• /visit & /spam: 30 seconds cooldown</b>"""

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("OWNER", url="https://t.me/agajayofficial"),
        InlineKeyboardButton("CHANNEL", url="https://t.me/AjayFFCommunity")
    )
    return text, markup


@bot.message_handler(commands=['start'])
def start(msg):
    text, markup = start_message()
    bot.reply_to(msg, text, reply_markup=markup)

def help_message():
    text = """<b>Help Information ❓

/like command: 💖
• Sends likes to player profile
• Usage: /like [region] [UID]
• Example: /like 14169575811
• Daily Limit: 1 use per day (resets at 4 AM IST)
• Note: Only IND server UIDs are supported

/visit command: 🔍
• Fetches detailed player information
• Usage: /visit [region] [UID]
• Example: /visit ind 14169575811
• UID Cooldown: 30 seconds (prevents multiple users from checking same UID)

/spam command: 📨
• Sends multiple friend requests
• Usage: /spam [UID]
• Example: /spam 14169575811

Limits: ⏰
• /like: 1 time per day (resets at 4 AM IST)
• /visit & /spam: 30 seconds cooldown per user
• /visit: 30 second UID cooldown

Tips: 💡
• You can use UID or Nickname for /visit and /spam
• /like only works with numeric UID and IND server
• Make sure the player exists in Garena database</b>"""

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("OWNER", url="https://t.me/agajayofficial"),
        InlineKeyboardButton("CHANNEL", url="https://t.me/AjayFFCommunity")
    )
    return text, markup
    
@bot.message_handler(commands=['help'])
def help_cmd(msg):
    text, markup = help_message()
    bot.reply_to(msg, text, reply_markup=markup)
    
@bot.message_handler(commands=['like'])
def like(msg):
    user_id = msg.from_user.id

    try:
        _, region, uid = msg.text.split()

        # OWNER BYPASS
        if user_id != OWNER_ID:
            if not can_like(user_id):
                bot.reply_to(msg, "<b>Daily limit used! Try after 4 AM IST ⏳</b>")
                return

        m = bot.reply_to(msg, "<b>⏳Sending Likes...</b>")

        try:
            res = requests.get(f"{LIKE_API}/like?uid={uid}&server_name={region}", timeout=10)
            r = res.json()
        except:
            bot.edit_message_text("<b>API Error ❌<b>", msg.chat.id, m.message_id)
            return

        nickname = r.get("PlayerNickname", "-")
        before = int(r.get("LikesbeforeCommand", 0))
        after = int(r.get("LikesafterCommand", 0))
        added = int(r.get("LikesGivenByAPI", 0))
        level = r.get("Level", "0")        

        if added > 0:
            text = f"""<b>Likes Sent Successfully ✅
Player Nickname: {nickname}
Player Uid: {uid}
Player Region: {region}
Player Level: {level}
Before Likes: {before}
After Likes: {after}
Likes Given By Bot: {added}</b>"""

        elif added == 0:
            text = f"""<b> Failed to send Likes ❌
Player Nickname:: {nickname}
Player Uid:: {uid}
Player Region:: {region}
Message:: Likes_already_send</b>"""

        else:
            text = f"""<b>Failed to Send Likes</b> ❌
Player Uid: {uid}
Player Region: {region}
Api Reason: Failed to retrieve initial player info.
Owner Message: Wait some time I set new token ✅<b>"""

        bot.edit_message_text(text, msg.chat.id, m.message_id)

    except:
        bot.reply_to(msg, "<b>Usage: /like ind 123456</b>")
        
@bot.message_handler(commands=['visit'])
def visit(msg):
    user_id = msg.from_user.id

    try:
        _, region, uid = msg.text.split()

        # OWNER BYPASS
        if user_id != OWNER_ID:
            if not check_cooldown(user_id, "visit"):
                bot.reply_to(msg, "<b>Cooldown 30 sec ⏳</b>")
                return

            if not check_uid(uid):
                bot.reply_to(msg, "<b>This UID is busy, try later ⏳</b>")
                return

        m = bot.reply_to(msg, "<b>⏳ Sending Visit...</b>")

        try:
            res = requests.get(f"{VISIT_API}/{region}/{uid}", timeout=100)
            r = res.json()
        except:
            bot.edit_message_text("<b>API Error ❌</b>", msg.chat.id, m.message_id)
            return

        text = f"""<b>┌ Player Visit Information ✅
├─ Nickname: {r.get("nickname","-")}
├─ UID: {uid}
├─ Region: {region.upper()}
├─ Level: {r.get("level","-")}
├─ Likes: {r.get("likes","-")}
├─ Success: {r.get("success","-")}
├─ Failed: {r.get("fail","-")}
└─ Time Taken: {r.get("time","-")} Some seconds</b>"""

        bot.edit_message_text(text, msg.chat.id, m.message_id)

    except:
        bot.reply_to(msg, "<b>Usage: /visit ind 123456</b>")
        
@bot.message_handler(commands=['spam'])
def spam(msg):
    user_id = msg.from_user.id

    try:
        _, uid = msg.text.split()

        if not check_cooldown(user_id, "spam"):
            bot.reply_to(msg, "<b>Cooldown 30 sec ⏳</b>")
            return

        m = bot.reply_to(msg, "<b>⏳Sending spam...</b>")

        r = requests.get(f"{SPAM_API}?uid={uid}").json()

        text = f"""<b>┌ Friend Request Spam Successful! ✅
├─ Nickname: {r.get("nickname","-")}
├─ UID: {uid}
├─ Region: {r.get("region","IND")}
├─ Level: {r.get("level","-")}
├─ Likes: {r.get("likes","-")}
└─ Message: {r.get("message","Successfully sent Friend Requests")}</b>"""

        bot.edit_message_text(text, msg.chat.id, m.message_id)

    except:
        bot.reply_to(msg, "<b>Spam command in maintenance mode try few days leter 💖</b>")
        
print("Bot Running...")
bot.infinity_polling()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
