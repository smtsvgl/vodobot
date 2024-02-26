import subprocess
import sys
import requests
import random
import base64
import json
import telebot

# Telegram bot token
TOKEN = "6396522183:AAEnn5XSKtNlBf1c45Zr1vAbAWgANTkRjek"

# Telebot instance
bot = telebot.TeleBot(TOKEN)

# Generate random IP address
def generate_random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

# Handle /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Merhaba! Lütfen Vodafone telefon numaranızı girin:")
    bot.register_next_step_handler(message, ask_phone)

# Ask for phone number
def ask_phone(message):
    global telno
    telno = message.text
    bot.reply_to(message, "Şimdi Vodafone şifrenizi girin:")
    bot.register_next_step_handler(message, ask_password)

# Ask for password
def ask_password(message):
    global parola
    parola = message.text
    headers = {
        "User-Agent": "VodafoneMCare/2308211432 CFNetwork/1325.0.1 Darwin/21.1.0",
        "Content-Length": "83",
        "Connection": "keep-alive",
        "Accept-Language": "tr_TR",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "m.vodafone.com.tr",
        "Cache-Control": "no-cache",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Forwarded-For": generate_random_ip()
    }

    url = "https://m.vodafone.com.tr/maltgtwaycbu/api/"
    data = {
        "context": "e30=",
        "username": telno,
        "method": "twoFactorAuthentication",
        "password": parola
    }

    response = requests.post(url, headers=headers, data=data)
    proid = response.json().get('process_id')

    if proid is None:
        bot.reply_to(message, "Şifre veya numara yanlış.")
    else:
        bot.reply_to(message, "Şifre doğrulama başarılı. Şimdi SMS ile gelen kodu girin:")
        bot.register_next_step_handler(message, ask_verification_code)

# Ask for verification code
def ask_verification_code(message):
    global kod
    kod = message.text
    veri = {
        "langId": "tr_TR",
        "clientVersion": "17.2.5",
        "reportAdvId": "0AD98FF8-C8AB-465C-9235-DDE102D738B3",
        "pbmRight": "1",
        "rememberMe": "true",
        "sid": proid,
        "otpCode": kod,
        "platformName": "iPhone"
    }

    base64_veri = base64.b64encode(json.dumps(veri).encode('utf-8'))

    data2 = {
        "context": base64_veri,
        "grant_type": "urn:vodafone:params:oauth:grant-type:two-factor",
        "code": kod,
        "method": "tokenUsing2FA",
        "process_id": proid,
        "scope": "ALL"
    }

    response2 = requests.post(url, headers=headers, data=data2)
    sonuc2 = response2.json()

    o_head = {
        "Accept": "application/json",
        "Language": "tr",
        "ApplicationType": "1",
        "ClientKey": "AC491770-B16A-4273-9CE7-CA790F63365E",
        "sid": proid,
        "Content-Type": "application/json",
        "Content-Length": "54",
        "Host": "m.vodafone.com.tr",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/4.10.0",
        "X-Forwarded-For": generate_random_ip()
    }

    o_data = {"campaignID": 6873, "latitude": "0.0", "longitude": "0.0"}
    cark_data = {
        "clientKey": "AC491770-B16A-4273-9CE7-CA790F63365E",
        "clientVersion": "16.8.3",
        "language": "tr",
        "operatingSystem": "android"
    }
    o_url = f"https://m.vodafone.com.tr/marketplace?method=participateCampaignBE&sid={proid}"
    cark_url = f"https://m.vodafone.com.tr/squat/getSquatMarketingProduct?sid={proid}"

    al_url = f"https://m.vodafone.com.tr/squat/updateSquatMarketingProduct?sid={proid}"

    cark = requests.post(cark_url, headers=o_head, json=cark_data)
    try:
        c1 = cark.json()["data"]["name"]
        c2 = cark.json()["data"]["code"]
        c3 = cark.json()["data"]["interactionID"]
        c4 = cark.json()["data"]["identifier"]
        al_data = {
            "clientKey": "AC491770-B16A-4273-9CE7-CA790F63365E",
            "clientVersion": "16.8.3",
            "code": "",
            "identifier": c4,
            "interactionId": c3,
            "language": "tr",
            "operatingSystem": "android"
        }
        al_url = f"https://m.vodafone.com.tr/squat/updateSquatMarketingProduct?sid={proid}"
        al = requests.post(al_url, headers=o_head, json=al_data).json()
        result_message = f"[✓] {c1}\n"
        if c2:
            result_message += f"[•] İndirim Kodu: {c2}"
        else:
            result_message += "[!] İndirim Kodu Bulunamadı."
        bot.reply_to(message, result_message)
    except:
        bot.reply_to(message, "[#] Çarkta bir hata oluştu.")

# Handle unknown commands
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.reply_to(message, "Anlaşılamadı. Lütfen /start komutu ile başlayın.")

# Start the bot
bot.polling()
