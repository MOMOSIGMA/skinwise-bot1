import telebot
import schedule
import time
import threading
import json
from datetime import datetime, date
import os
from flask import Flask
from threading import Thread

# === CONFIGURATION ===
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# === FLASK POUR RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Le bot SkinWise est en ligne ✅"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_flask).start()

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
        message_bienvenue = """👋 *Bienvenue sur SkinWise* 🌿

Tu viens d’activer ton programme de 30 jours pour une peau plus saine, un mental plus fort, et des habitudes puissantes.

🧠 *Chaque jour, tu recevras :*
• 1 message le midi ✅  
• 1 message le soir 🌙  
• Avec des routines simples à faire chez toi (hydratation, nutrition, soin, mental…)

🎯 *Objectif* : Rééduquer ta peau naturellement, sans produits agressifs.  
Mais aussi t’apprendre la discipline, l’amour de soi et la régularité.

---

📦 *Avant de commencer, voici ce que je te recommande d’avoir :*

✅ Un gel nettoyant doux (ou savon neutre)  
✅ Une huile naturelle adaptée (jojoba, nigelle, carotte, ou karité)  
✅ De l’eau en quantité  
✅ Un miroir, un carnet ou ton téléphone pour noter  
✅ Ta volonté. Même petite, elle suffit.

---

📌 Tu veux un conseil ou tu ne sais pas quel produit choisir ?  
Tape simplement `/help`

🕒 *Le Jour 1 commence dès aujourd’hui.*  
Tu vas changer doucement, mais profondément.  
*Félicitations. Tu fais partie de ceux qui OSENT.*"""
        bot.send_message(message.chat.id, message_bienvenue, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Tu es déjà inscrit. Le programme continue.")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, """🔹 *Quel gel nettoyant choisir ?*
Utilise un savon doux ou un gel sans parfum ni alcool (sulfuré, neem ou charbon si possible).

🔹 *Quelle huile naturelle utiliser ?*
• Peau grasse : jojoba ou nigelle  
• Peau sèche : karité ou avocat  
• Peau mixte : carotte ou noisette

🔹 *Puis-je faire le programme sans produits ?*
Oui. Bois de l’eau, note tes progrès, applique les routines. Les produits sont un plus.

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
        bot.send_message(message.chat.id, "▶️ Programme relancé. Tu recevras les messages aux heures prévues.")
    else:
        bot.send_message(message.chat.id, "Tu n'es pas encore inscrit. Envoie /start pour commencer.")

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

# === LANCEMENT DU BOT ===
bot.polling()
