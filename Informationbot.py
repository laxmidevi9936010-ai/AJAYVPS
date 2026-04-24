import telebot
import threading
from PIL import Image
import requests
from io import BytesIO
import time
import json 

# ================= CONFIG =================
TOKEN = "8361883535:AAFtLauspq0GXd0TMS2PvpKcW9OnCv-rvb4"
bot = telebot.TeleBot(TOKEN)

# ========= API LINKS =========
INFO_API = "https://info-api-xi-tawny.vercel.app/get?uid={uid}"
BANNER_API = "https://ffavtarbanner.vercel.app/avatar-banner?uid={uid}&region=ind"
OUTFIT_API = "https://outfit-api-by-ajay-one.vercel.app/outfit?uid={uid}&key=AJAY"

def banner_to_sticker(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content)).convert("RGBA")

    # resize for sticker
    img.thumbnail((512, 512))

    output = BytesIO()
    output.name = "sticker.webp"
    img.save(output, "WEBP")

    output.seek(0)
    return output
    
# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    text = """
<b>🤖 FREE FIRE PLAYER INFO BOT 🤖
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ BOT FEATURES ⚡

PLAYER INFO
View level, likes, rank, account info, activity and more
PLAYER SYSTEM
Get complete player information using UID with fast response and accurate data processing
REAL TIME DATA
All data is fetched live from API ensuring up to date and reliable information
MULTIPLE API INTEGRATION
Uses multiple APIs simultaneously for faster performance and better results
FAST API DATA
Optimized system with parallel requests for instant output
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆘 MAIN COMMANDS 🆘

/get &lt;uid&gt; - Full player info with all personal details  
/bancheck &lt;uid&gt; - Account status  
/banner &lt;uid&gt; - give banner image
/outfit &lt;region&gt; &lt;uid&gt; - give Outfit image
/region &lt;uid&gt; - Region information  
/token &lt;uid&gt; &lt;password&gt; - Generate login JWT token  
/wishlist &lt;uid&gt; - Get wishlist data in JSON   
/level &lt;uid&gt; - Get level data with EXP and next level progress  
/events &lt;region&gt; - Give events images 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type /help to get all commands
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💫 PLAYER INFO DATA

Get full player data  
Player guild information  
Ban check status  
Get wishlist items  
Update guest account bio  
Region information  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌏 GLOBAL REGION SUPPORT  
IND, BD, US, VN, SG  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 BOT POWERED BY AGAJAYOFFICIAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>"""
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# ================= HELP =================
@bot.message_handler(commands=['help'])
def help(message):
    text = """
<b>📖 FREE FIRE PLAYER INFO BOT HELP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆘 COMMAND GUIDE 🆘

/get &lt;uid&gt;
Get complete player information including level, rank, likes and account data
/bancheck &lt;uid&gt;
Check if the account is banned or safe
/region &lt;uid&gt;
Detect the player region using UID
/token &lt;uid&gt; &lt;password&gt;
Generate JWT login token for account access
/wishlist &lt;uid&gt;
Get player wishlist items directly from API
/banner &lt;uid&gt; - give banner image
/outfit &lt;region&gt; &lt;uid&gt; - give Outfit image
/level &lt;uid&gt;
Get player level details including EXP and level progress
/events &lt;region&gt; - Give events images 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DATA PROVIDED BY BOT

ACCOUNT INFORMATION
Player name, UID, level, likes, region and signature
ACCOUNT ACTIVITY
Rank details, fire pass status and last login
GUILD INFORMATION
Guild name, guild ID, guild level and leader details
PET DETAILS
Pet name, type, level and experience
IMAGE DATA
Banner image and outfit image sent directly from API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 BOT POWERED BY AGAJAYOFFICIAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
"""
    bot.send_message(message.chat.id, text, parse_mode="HTML")
    

# ========= FORMAT FUNCTION =========
def format_info(data):
    return f"""<b>ACCOUNT INFORMATION:
┌ ACCOUNT BASIC INFORMATION
├─ Prime Level: {data.get('AccountInfo', {}).get('AccountType', 'Not Found')}
├─ Name: {data.get('AccountInfo', {}).get('AccountName', 'Not Found')}
├─ UID: {data.get('uid', {}).get('AccountName', 'Not Found')}
├─ Level: {data.get('AccountInfo', {}).get('AccountLevel', 'Not Found')} (Exp: {data.get('AccountInfo', {}).get('AccountEXP', 'Not Found')})
├─ Region: {data.get('AccountInfo', {}).get('AccountRegion', 'Not Found')}
├─ Likes: {data.get('AccountInfo', {}).get('AccountLikes', 'Not Found')}
├─ Honor Score: {data.get('creditScoreInfo', {}).get('creditScore', 'Not Found')}
├─ Celebrity Status: {data.get('AccountInfo', {}).get('AccountBPID', 'Not Found')}
├─ Title Name: {data.get('AccountInfo', {}).get('Title', 'Not Found')}
└─ Signature: {data.get('socialinfo', {}).get('signature', 'Not Found')}

ACCOUNT ACTIVITY:
┌ ACCOUNT ACTIVITY
├─ Most Recent OB: {data.get('AccountInfo', {}).get('ReleaseVersion', 'Not Found')}
├─ Fire Pass: {data.get('AccountInfo', {}).get('AccountSeasonId', 'Not Found')}
├─ Current Bp Badges: {data.get('AccountInfo', {}).get('AccountBPBadges', 'Not Found')}
├─ Br Rank: {data.get('AccountInfo', {}).get('BrRank', 'Not Found')} ({data.get('AccountInfo', {}).get('BrRankPoint', 'Not Found')})
├─ Cs Rank: {data.get('AccountInfo', {}).get('CsRank', 'Not Found')} ({data.get('AccountInfo', {}).get('CsRankPoint', 'Not Found')} Star)
├─ Gender: {data.get('socialinfo', {}).get('gender', 'Not Found')}
├─ Show Rank: {data.get('AccountInfo', {}).get('ShowRank', 'Not Found')}
├─ Show Br Rank: {data.get('AccountInfo', {}).get('ShowBrRank', 'Not Found')}
├─ Show Cs Rank: {data.get('AccountInfo', {}).get('ShowCsRank', 'Not Found')}
├─ Created At: {data.get('AccountInfo', {}).get('AccountCreateTime', 'Not Found')}
└─ Last Login: {data.get('AccountInfo', {}).get('AccountLastLogin', 'Not Found')}

ACCOUNT OVERVIEW:
┌ ACCOUNT OVERVIEW
├─ Avatar ID: {data.get('AccountInfo', {}).get('AccountAvatarId', 'Not Found')}
├─ Banner ID: {data.get('AccountInfo', {}).get('AccountBannerId', 'Not Found')}
├─ Mode Prefer: {data.get('socialinfo', {}).get('rankShow', 'Not Found')}
├─ Equipped Skills: {data.get('AccountProfileInfo', {}).get('EquippedSkills', 'Not Found')}
├─ Language: {data.get('socialinfo', {}).get('language', 'Not Found')}
└─ Outfits: {data.get('AccountProfileInfo', {}).get('EquippedOutfit', 'Not Found')}

PET DETAILS:
┌ PET DETAILS
├─ Equipped?: {data.get('petInfo', {}).get('isSelected', 'Not Found')}
├─ Pet Name: {data.get('petInfo', {}).get('name', 'Not Found')}
├─ Pet Type: {data.get('petInfo', {}).get('id', 'Not Found')}
├─ Pet Exp: {data.get('petInfo', {}).get('exp', 'Not Found')}
└─ Pet Level: {data.get('petInfo', {}).get('level', 'Not Found')}

GUILD INFORMATION:
┌ GUILD INFORMATION
├─ Guild Name: {data.get('GuildInfo', {}).get('GuildName', 'Not Found')}
├─ Guild ID: {data.get('GuildInfo', {}).get('GuildID', 'Not Found')}
├─ Guild Level: {data.get('GuildInfo', {}).get('GuildLevel', 'Not Found')}
├─ Live Members: {data.get('GuildInfo', {}).get('GuildMember', 'Not Found')}
└─ Leader Information:
    ├─ Leader Name: {data.get('captainBasicInfo', {}).get('nickname', 'Not Found')}
    ├─ Leader UID: {data.get('captainBasicInfo', {}).get('accountId', 'Not Found')}
    ├─ Leader Level: {data.get('captainBasicInfo', {}).get('level', 'Not Found')} (Exp: {data.get('captainBasicInfo', {}).get('exp', 'Not Found')})
    ├─ Leader Region: {data.get('captainBasicInfo', {}).get('region', 'Not Found')}
    ├─ Leader Fire Pass: {data.get('captainBasicInfo', {}).get('seasonId', 'Not Found')}
    ├─ Leader Created At: {data.get('captainBasicInfo', {}).get('createAt', 'Not Found')}
    ├─ Leader Last Login: {data.get('captainBasicInfo', {}).get('lastLoginAt', 'Not Found')}
    ├─ Leader Most Recent OB: {data.get('captainBasicInfo', {}).get('releaseVersion', 'Not Found')}
    ├─ Leader Title Name: {data.get('captainBasicInfo', {}).get('title', 'Not Found')}
    ├─ Leader Current Bp Badges: {data.get('captainBasicInfo', {}).get('badgeId', 'Not Found')}
    ├─ Leader Br Rank: {data.get('captainBasicInfo', {}).get('rank', 'Not Found')}
    └─ Leader Cs Rank: {data.get('captainBasicInfo', {}).get('csRank', 'Not Found')}

PUBLIC CRAFTLAND MAPS:
┌ PUBLIC CRAFTLAND MAPS
Not Available</b>"""

# ========= COMMAND =========
@bot.message_handler(commands=['get'])
def get_info(message):
    
    parts = message.text.split()

    if len(parts) < 2:
        bot.reply_to(message, "<b>❌ Use: /get UID</b>", parse_mode="HTML")
        return

    uid = parts[1]

    # 👉 Processing message
    processing = bot.reply_to(message, f"<b>⏳ Fetching {uid} details please wait...</b>", parse_mode="HTML")

    # ===== INFO =====
    try:
        res = requests.get(INFO_API.format(uid=uid)).json()
        text = format_info(res)

        try:
            bot.delete_message(message.chat.id, processing.message_id)
        except:
            pass

        bot.reply_to(message, text, parse_mode="HTML")
    except Exception as e:
        try:
            bot.delete_message(message.chat.id, processing.message_id)
        except:
            pass

        bot.send_message(message.chat.id, f"❌ Info Error: {e}")
        return

    # ===== BANNER AS STICKER =====
    try:
        banner_url = BANNER_API.format(uid=uid)
        sticker = banner_to_sticker(banner_url)
        bot.send_sticker(message.chat.id, sticker)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Banner Sticker Error: {e}")

    # ===== OUTFIT =====
    try:
        outfit_url = OUTFIT_API.format(uid=uid)
        bot.send_photo(message.chat.id, outfit_url)
    except:
        bot.send_message(message.chat.id, "❌ Outfit Error")
       
# ================= WISHLIST =================
@bot.message_handler(commands=['wishlist'])
def wishlist(message):
    try:
        parts = message.text.split()

        # ✅ UID check
        if len(parts) < 2:
            bot.reply_to(
                message,
                "<b>Usage: /wishlist UID</b>\nExample: /wishlist 2471015544",
                parse_mode="HTML"
            )
            return

        uid = parts[1]

        # 🔥 Processing message
        msg = bot.reply_to(
            message,
            "<b>⏳ Fetching wishlist.</b>",
            parse_mode="HTML"
        )

        # 🔄 Dot animation
        try:
            time.sleep(0.5)
            bot.edit_message_text("<b>⏳ Fetching wishlist..</b>", message.chat.id, msg.message_id, parse_mode="HTML")
            time.sleep(0.5)
            bot.edit_message_text("<b>⏳ Fetching wishlist...</b>", message.chat.id, msg.message_id, parse_mode="HTML")
        except:
            pass

        # 👉 YOUR API
        url = f"http://203.57.85.58:2035/wishlist?uid={uid}&key=@yashapis"

        res = requests.get(url, timeout=150)

        if res.status_code != 200:
            bot.edit_message_text(
                "❌ Wishlist not found",
                message.chat.id,
                msg.message_id
            )
            return

        data = res.json()

        # 👉 Pretty JSON
        json_text = json.dumps(data, indent=2)

        # 👉 Delete processing msg
        try:
            bot.delete_message(message.chat.id, msg.message_id)
        except:
            pass

        # 👉 Telegram limit fix (split)
        for i in range(0, len(json_text), 4000):
            bot.send_message(
                message.chat.id,
                f"<pre>{json_text[i:i+4000]}</pre>",
                parse_mode="HTML"
            )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")
        
# ================= Region =================
@bot.message_handler(commands=['region'])
def region(message):
    try:
        parts = message.text.split()

        # ✅ UID check
        if len(parts) < 2:
            bot.reply_to(
                message,
                "<b>Usage: /region UID</b>",
                parse_mode="HTML"
            )
            return

        uid = parts[1]

        # 🔥 Processing message
        msg = bot.reply_to(
            message,
            "<b>⏳ Checking region.</b>",
            parse_mode="HTML"
        )

        # 🔄 Dot animation
        try:
            time.sleep(0.5)
            bot.edit_message_text("<b>⏳ Checking region..</b>", message.chat.id, msg.message_id, parse_mode="HTML")
            time.sleep(0.5)
            bot.edit_message_text("<b>⏳ Checking region...</b>", message.chat.id, msg.message_id, parse_mode="HTML")
        except:
            pass

        # 👉 API
        url = f"https://region-check-api-by-ajay-k3ax.vercel.app/region?uid={uid}"
        res = requests.get(url, timeout=20)

        if res.status_code != 200:
            bot.edit_message_text(
                "❌ Region not found",
                message.chat.id,
                msg.message_id
            )
            return

        data = res.json()

        # 👉 Extract safely
        region_code = data.get("region_code", "N/A")
        region_name = data.get("region_name", data.get("region", "N/A"))
        server = data.get("nickname", "N/A")
        ping = data.get("region", "N/A")
        player_base = data.get("player_base", "N/A")

        # 🔥 FINAL DESIGN (exact style)
        text = f"""
<b>REGION INFORMATION
┌ DETAILS
├─ UID: {uid}
├─ Nickname: {server}
├─ Region: {ping}
└─ PLAYER DATA FETCH SUCCESSFULLY ✅</b>
"""

        # 👉 Show result
        bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=msg.message_id,
            parse_mode="HTML"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")
        
# ================= LEVEL =================
@bot.message_handler(commands=['level'])
def level(message):
    try:
        parts = message.text.split()

        # ✅ UID check
        if len(parts) < 2:
            bot.reply_to(
                message,
                "<b>Usage: /level UID</b>\nExample: /level 2471015544",
                parse_mode="HTML"
            )
            return

        uid = parts[1]

        # 🔥 Processing message
        msg = bot.reply_to(
            message,
            "<b>⏳ Fetching level.</b>",
            parse_mode="HTML"
        )

        # 🔄 Dot animation
        try:
            time.sleep(0.5)
            bot.edit_message_text("<b>⏳ Fetching level..</b>", message.chat.id, msg.message_id, parse_mode="HTML")

            time.sleep(0.5)
            bot.edit_message_text("<b>⏳ Fetching level...</b>", message.chat.id, msg.message_id, parse_mode="HTML")
        except:
            pass

        # 👉 YOUR API
        url = f"https://level-info-api-by-ajay.vercel.app/level/{uid}"
        res = requests.get(url, timeout=100)

        if res.status_code != 200:
            bot.edit_message_text(
                "❌ Level data not found",
                message.chat.id,
                msg.message_id
            )
            return

        data = res.json()
        p = data.get("data", data)  # fallback support

        nickname = p.get("nickname", "N/A")
        level_data = p.get("current_level", p.get("level", "N/A"))
        exp = p.get("current_exp", p.get("exp", "N/A"))
        next_exp = p.get("exp_for_next_level", "N/A")
        exp_for_100_level = p.get("exp_needed_for_100", "N/A")

        # 🔥 Final message
        text = f"""
<b>LEVEL INFORMATION
┌ DETAILS
├─ UID: {uid}
├─ Nickname: {nickname}
├─ Current Level: {level_data}
├─ Current EXP: {exp}
├─ EXP NEEDED FOR 100 LEVEL: {exp_for_100_level}
└─ Next Level EXP: {next_exp}

STATUS: LEVEL DATA FETCHED ✅</b>
"""

        # 👉 Show result
        bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=msg.message_id,
            parse_mode="HTML"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")
        
# ================= BAN =================
@bot.message_handler(commands=['bancheck'])
def bancheck(message):
    try:
        parts = message.text.split()

        # ✅ UID check
        if len(parts) < 2:
            bot.reply_to(
                message,
                "<b>Usage: /bancheck UID</b>\nExample: /bancheck 2471015544",
                parse_mode="HTML"
            )
            return

        uid = parts[1]

        # 🔥 Processing message
        msg = bot.reply_to(
            message,
            "<b>⏳Checking ban check...</b>",
            parse_mode="HTML"
        )

        # 👉 Simple loading effect (optional)
        try:
            time.sleep(0.5)
            bot.edit_message_text("<b>⏳Checking ban check.</b>", message.chat.id, msg.message_id, parse_mode="HTML")

            time.sleep(0.5)
            bot.edit_message_text("<b>⏳Checking ban check..</b>", message.chat.id, msg.message_id, parse_mode="HTML")

            time.sleep(0.5)
            bot.edit_message_text("<b>⏳Checking ban check...</b>", message.chat.id, msg.message_id, parse_mode="HTML")
        except:
            pass

        # 👉 API call
        url = f"https://free-fire-official-bancheck-api-by.vercel.app/bancheck?uid={uid}"
        response = requests.get(url)

        if response.status_code != 200:
            bot.edit_message_text("❌ API Error", message.chat.id, msg.message_id)
            return

        data = response.json()

        # 🔥 Result text
        text = f"""
<b>BAN CHECK RESULT
┌ PLAYER INFO
├─ Name: {data.get('nickname', 'Not Found')}
├─ UID: {uid}
├─ Region: {data.get('region', 'Not Found')}
└─ Status: {data.get('ban_status', 'Not Found')}

┌ BAN DETAILS
└─ Ban Period: {data.get('ban_period', 'Not Found')}</b>
"""

        # 👉 Delete processing msg (safe)
        try:
            bot.delete_message(message.chat.id, msg.message_id)
        except:
            pass

        # 👉 Final result reply
        bot.reply_to(
            message,
            text,
            parse_mode="HTML"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")
        
# ================= TOKEN =================
@bot.message_handler(commands=['token'])
def token(message):
    try:
        parts = message.text.split()

        # ✅ UID + Password check
        if len(parts) < 2:
            bot.reply_to(
                message,
                "<b>Usage: /token UID PASSWORD</b>\nExample: /token 123456789 abcd1234 ",
                parse_mode="HTML"
            )
            return

        uid = parts[1]
        password = parts[2]

        # 🔥 Processing message
        msg = bot.reply_to(message, "<b>Generate JWT token...</b>", parse_mode="HTML")

        # 👉 API URL
        api_url = f"http://203.57.85.58:2035/token?uid={uid}&password={password}&key=@yashapis"

        # 👉 Request (sync)
        response = requests.get(api_url, timeout=105)

        if response.status_code != 200:
            bot.edit_message_text(
                "<b>ERROR: API FAILED</b>",
                message.chat.id,
                msg.message_id,
                parse_mode="HTML"
            )
            return

        data = response.json()

        # 👉 Delete processing msg (safe)
        try:
            bot.delete_message(message.chat.id, msg.message_id)
        except:
            pass

        # 🔥 Extract data
        decoded = data.get("decoded", {})
        expiry = decoded.get("expiry_info", {})

        token_value = data.get("jwt_token", "N/A")

        # 🔥 split long token
        def split_text(text, size=60):
            return "\n".join([text[i:i+size] for i in range(0, len(text), size)])

        token_value = split_text(token_value)

        # 🔥 Final message
        text = f"""
<b>TOKEN INFORMATION

┌ ACCOUNT DETAILS
├─ Account ID: <code>{data.get('account_id', 'Not Found')}</code>
├─ Nickname: {data.get('nickname', 'Not Found')}
├─ Region: {data.get('region', 'Not Found')}
├─ Platform: {data.get('client_type', 'Not Found')}
├─ Client Version: {data.get('client_version', 'Not Found')}
├─ OB Version: {data.get('release_version', 'Not Found')}
├─ Emulator: {data.get('is_emulator', 'Not Found')}

┌ EXPIRY INFO
├─ Expired: {expiry.get('is_expired', 'Not Found')}
├─ Time (IST): {expiry.get('ist', 'Not Found')}
├─ Remaining: {expiry.get('remaining_human', 'Not Found')}
└─ Seconds: {expiry.get('remaining_seconds', 'Not Found')}

┌ REGION INFO
├─ IP Region: {data.get('country_code', 'Not Found')}
├─ Lock Region: {data.get('region', 'Not Found')}
└─ External UID: {data.get('external_uid', 'Not Found')}

┌ TOKEN
<code>{data.get('token', 'Not Found')}</code></b>
"""
        # 👉 Final send
        bot.send_message(message.chat.id, text, parse_mode="HTML")

    except requests.exceptions.Timeout:
        bot.send_message(message.chat.id, "<b>API Timeout ❌ Try again later</b>", parse_mode="HTML")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")
        
@bot.message_handler(commands=['banner'])
def banner(message):
    try:
        parts = message.text.split()

        # ✅ Check args
        if len(parts) < 3:
            bot.reply_to(
                message,
                "<b>Usage: /banner &lt;region&gt; &lt;uid&gt;\nExample: /banner ind 2471015544</b>",
                parse_mode="HTML"
            )
            return

        region = parts[1].lower()
        uid = parts[2]

        # 🔥 Processing message
        msg = bot.reply_to(
            message,
            "<b>⏳ Fetching banner.</b>",
            parse_mode="HTML"
        )

        # 🔄 Dot animation
        try:
            for i in range(3):
                time.sleep(0.5)
                bot.edit_message_text(
                    f"<b>⏳ Fetching banner{'.' * (i+1)}</b>",
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    parse_mode="HTML"
                )
        except:
            pass

        # 👉 Your API
        url = f"https://ffavtarbanner.vercel.app/avatar-banner?uid={uid}&region={region}"

        res = requests.get(url, timeout=105)

        if res.status_code != 200:
            bot.edit_message_text(
                "<b>❌ Banner not found</b>",
                msg.chat.id,
                msg.message_id,
                parse_mode="HTML"
            )
            return

        # 🖼 Convert → sticker (WEBP)
        img = Image.open(BytesIO(res.content)).convert("RGBA")

        # ✅ Resize for sticker
        img.thumbnail((512, 512))

        webp_io = BytesIO()
        webp_io.name = "banner.webp"
        img.save(webp_io, "WEBP")
        webp_io.seek(0)

        # ✅ Send sticker
        bot.send_sticker(message.chat.id, webp_io)

        # 🗑 Delete loading msg
        try:
            bot.delete_message(msg.chat.id, msg.message_id)
        except:
            pass

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")
        
@bot.message_handler(commands=['outfit'])
def outfit(message):
    try:
        parts = message.text.split()

        # ✅ Check args
        if len(parts) < 2:
            bot.reply_to(
                message,
                "<b>Usage: /outfit &lt;uid&gt;\nExample: /outfit 2471015544</b>",
                parse_mode="HTML"
            )
            return

        uid = parts[1]

        # 🔥 Processing message
        msg = bot.reply_to(
            message,
            "<b>⏳ Fetching outfit.</b>",
            parse_mode="HTML"
        )

        # 🔄 Dot animation
        try:
            for i in range(3):
                time.sleep(0.5)
                bot.edit_message_text(
                    f"<b>⏳ Fetching outfit{'.' * (i+1)}</b>",
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    parse_mode="HTML"
                )
        except:
            pass

        # 👉 API URL
        url = f"https://outfit-api-by-ajay-one.vercel.app/outfit?uid={uid}&key=AJAY"

        # 🌐 Request
        res = requests.get(url, timeout=100)

        if res.status_code != 200:
            bot.edit_message_text(
                "<b>❌ Outfit not found</b>",
                msg.chat.id,
                msg.message_id,
                parse_mode="HTML"
            )
            return

        # ✅ Send image
        bot.send_photo(
            message.chat.id,
            res.content
        )

        # 🗑 Delete processing message
        try:
            bot.delete_message(msg.chat.id, msg.message_id)
        except:
            pass

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")    
                
@bot.message_handler(commands=['events'])
def events(message):
    try:
        parts = message.text.split()

        # ✅ Region check
        if len(parts) < 2:
            bot.reply_to(
                message,
                "<b>Usage: /events &lt;region&gt;</b>\n<b>Example:</b> /events ind",
                parse_mode="HTML"
            )
            return

        region = parts[1].lower()

        # 🔥 Processing message
        msg = bot.reply_to(
            message,
            "<b>⏳ Fetching events.</b>",
            parse_mode="HTML"
        )

        # 🔄 Smooth Dot Animation
        try:
            for i in range(3):
                time.sleep(0.5)
                bot.edit_message_text(
                    f"<b>⏳ Fetching events{'.' * (i+1)}</b>",
                    message.chat.id,
                    msg.message_id,
                    parse_mode="HTML"
                )
        except:
            pass

        # 👉 API CALL
        url = f"http://203.57.85.58:2035/events?region={region}&key=@yashapis"
        res = requests.get(url, timeout=15)

        if res.status_code != 200:
            bot.edit_message_text(
                "<b>❌ Events not found</b>",
                message.chat.id,
                msg.message_id,
                parse_mode="HTML"
            )
            return

        data = res.json()

        # ✅ CORRECT PATH
        items = data.get("events", {}).get("items", [])

        if not items:
            bot.edit_message_text(
                "<b>❌ No events available</b>",
                message.chat.id,
                msg.message_id,
                parse_mode="HTML"
            )
            return

        # 👉 delete processing msg
        try:
            bot.delete_message(message.chat.id, msg.message_id)
        except:
            pass

        # 🔥 SEND ONLY BANNERS
        for item in items:
            banner = item.get("Banner")

            if banner:
                try:
                    bot.send_photo(message.chat.id, banner)
                    time.sleep(0.5)
                except:
                    pass

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"<b>❌ Error:</b> {e}",
            parse_mode="HTML"
        )
        
@bot.message_handler(func=lambda message: message.text.startswith('/'))
def unknown_command(message):
    bot.reply_to(
        message,
        "<b>❌ UNKNOWN COMMAND</b>",
        parse_mode="HTML"
    )        
                
#MAIN       
print("💕Bot Running...")
bot.infinity_polling()