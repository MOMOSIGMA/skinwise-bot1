import telebot
import schedule
import time
import threading
import json
from datetime import datetime, date
from flask import Flask

# === CONFIGURATION ===
TOKEN = "7952444866:AAFw6-jYo1deEkLHJPYnoCM3j3kzh3p0Afo"
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

# === COMMANDE /start ===
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {
            "start_date": str(date.today()),
            "paused": False
        }
        save_users()
        bot.send_message(message.chat.id, "Bienvenue sur SkinWise 🌿 ! Tu es inscrit au programme. Jour 1 commence aujourd’hui.")
    else:
        bot.send_message(message.chat.id, "Tu es déjà inscrit. Le programme continue.")

# === ENVOI AUTOMATIQUE ===
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

# === PLANIFICATION DES HEURES ===
schedule.every().day.at("12:30").do(envoyer_messages, moment="midi")
schedule.every().day.at("21:20").do(envoyer_messages, moment="soir")

# === TÂCHE DE PLANIFICATION EN BOUCLE ===
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_schedule).start()

# === SERVEUR FLASK POUR REPLIT ===
app = Flask(__name__)

@app.route('/')
def home():
    return "SkinWise Bot actif."

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()
# === COMMANDE /pause ===
@bot.message_handler(commands=['pause'])
def pause(message):
    user_id = str(message.chat.id)
    if user_id in users:
        users[user_id]["paused"] = True
        save_users()
        bot.send_message(message.chat.id, "⏸️ Programme mis en pause. Envoie /resume pour continuer.")
    else:
        bot.send_message(message.chat.id, "Tu n'es pas encore inscrit. Envoie /start pour commencer.")

# === COMMANDE /resume ===
@bot.message_handler(commands=['resume'])
def resume(message):
    user_id = str(message.chat.id)
    if user_id in users:
        users[user_id]["paused"] = False
        save_users()
        bot.send_message(message.chat.id, "▶️ Programme relancé. Tu recevras les messages aux heures prévues.")
    else:
        bot.send_message(message.chat.id, "Tu n'es pas encore inscrit. Envoie /start pour commencer.")

# === COMMANDE /reset ===
@bot.message_handler(commands=['reset'])
def reset(message):
    user_id = str(message.chat.id)
    if user_id in users:
        users[user_id]["start_date"] = str(date.today())
        users[user_id]["paused"] = False
        save_users()
        bot.send_message(message.chat.id, "🔄 Programme redémarré. Aujourd’hui est le nouveau Jour 1.")
    else:
        bot.send_message(message.chat.id, "Tu n'es pas encore inscrit. Envoie /start pour commencer.")

# === LANCEMENT DU BOT ===
bot.polling()
