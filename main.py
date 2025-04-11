import telebot
import schedule
import time
import threading
import json
from datetime import datetime, date
import os

# === CONFIGURATION ===
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# === CHARGEMENT DU PROGRAMME ===
with open("programme_skinwise.json", "r", encoding="utf-8") as f:
    programme = json.load(f)

# === CHARGEMENT DES UTILISATEURS ===
try:
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

def save_users():
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# === COMMANDES ===
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {
            "start_date": str(date.today()),
            "paused": False
        }
        save_users()
        bot.send_message(message.chat.id, """👋 *Bienvenue sur SkinWise* 🌿

Tu viens d’activer ton programme de 30 jours...

🕒 *Le Jour 1 commence dès aujourd’hui.*  
Tu vas changer doucement, mais profondément.  
*Félicitations. Tu fais partie de ceux qui OSENT.*""", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Tu es déjà inscrit. Le programme continue.")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, """🔹 *Quel gel nettoyant choisir ?*
...

Tape `/reset` pour recommencer, ou `/pause` pour mettre en pause.""", parse_mode="Markdown")

@bot.message_handler(commands=['pause'])
def pause(message):
    user_id = str(message.chat.id)
    if user_id in users:
        users[user_id]["paused"] = True
        save_users()
        bot.send_message(message.chat.id, "⏸️ Programme mis en pause. Envoie /resume pour continuer.")
    else:
        bot.send_message(message.chat.id, "Tu n'es pas encore inscrit. Envoie /start pour commencer.")

@bot.message_handler(commands=['resume'])
def resume(message):
    user_id = str(message.chat.id)
    if user_id in users:
        users[user_id]["paused"] = False
        save_users()
        bot.send_message(message.chat.id, "▶️ Programme relancé.")
    else:
        bot.send_message(message.chat.id, "Tu n'es pas encore inscrit. Envoie /start pour commencer.")

@bot.message_handler(commands=['reset'])
def reset(message):
    user_id = str(message.chat.id)
    if user_id in users:
        users[user_id]["start_date"] = str(date.today())
        users[user_id]["paused"] = False
        save_users()
        bot.send_message(message.chat.id, "🔄 Programme redémarré.")
    else:
        bot.send_message(message.chat.id, "Tu n'es pas encore inscrit. Envoie /start pour commencer.")

# === ENVOI QUOTIDIEN ===
def envoyer_messages(moment):
    today = date.today()
    for user_id, data in users.items():
        if data.get("paused"):
            continue
        start = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        jour = (today - start).days + 1
        if str(jour) in programme:
            msg_data = programme[str(jour)].get(moment)
            if msg_data:
                texte = f"🌞 *{msg_data['titre']}*\n\n" + "\n".join([f"• {action}" for action in msg_data["actions"]])
                bot.send_message(int(user_id), texte, parse_mode='Markdown')

schedule.every().day.at("12:30").do(envoyer_messages, moment="midi")
schedule.every().day.at("21:20").do(envoyer_messages, moment="soir")

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_schedule).start()

bot.polling()
