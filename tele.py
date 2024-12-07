import os
import django

# Укажите путь к файлу настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops_telegram.settings')

# Инициализация Django (до любых импортов Django моделей или других компонентов)
django.setup()

# Импорты после настройки Django
import telebot
from products.models import Product
from products.models import UserTelegram

# Телеграм-бот
bot = telebot.TeleBot("8001604543:AAFXvYwt1klDtEhuy51Bi1OWXjBEhZl1cEg")

# Словарь для хранения статусов пользователей (логин/пароль)
user_sessions = {}

def check_authorization(user_id):
    """Проверка, авторизован ли пользователь"""
    return user_sessions.get(user_id) is not None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if check_authorization(message.chat.id):
        bot.reply_to(message, "Welcome back! You are already logged in.")
    else:
        bot.reply_to(message, "Please, login: 'login your_login your_password'\nIf you are not registered, register: 'register your_login your_password'")

@bot.message_handler(func=lambda message: message.text.lower().startswith('register'))
def register(message):
    if check_authorization(message.chat.id):
        bot.reply_to(message, "You are already logged in!")
        return
    
    try:
        _, username, password = message.text.split()
    except ValueError:
        bot.reply_to(message, "Invalid registration format. Use: register <your_login> <your_password>")
        return

    # Создание нового пользователя
    if UserTelegram.objects.filter(username=username).exists():
        bot.reply_to(message, "User with this login already exists.")
        return

    user = UserTelegram.objects.create_user(username=username, password=password)
    user_sessions[message.chat.id] = user  # Сохраняем авторизацию для текущего пользователя

    bot.reply_to(message, f"Registration successful! Welcome, {username}.")

@bot.message_handler(func=lambda message: message.text.lower().startswith('login'))
def login(message):
    if check_authorization(message.chat.id):
        bot.reply_to(message, "You are already logged in!")
        return

    try:
        _, username, password = message.text.split()
    except ValueError:
        bot.reply_to(message, "Invalid login format. Use: login <your_login> <your_password>")
        return

    # Проверка логина и пароля
    try:
        user = UserTelegram.objects.get(username=username)
        if user.check_password(password):
            user_sessions[message.chat.id] = user  # Сохраняем авторизацию
            bot.reply_to(message, f"Welcome, {username}! You are logged in.")
        else:
            bot.reply_to(message, "Incorrect password. Please try again.")
    except UserTelegram.DoesNotExist:
        bot.reply_to(message, "User not found. Please check your login and try again.")

@bot.message_handler(func=lambda message: message.text.lower().startswith('buy'))
def buy(message):
    if not check_authorization(message.chat.id):
        bot.reply_to(message, "Please, login first!")
        return

    # Получаем название товара
    product_name = message.text[len('buy '):].strip()

    try:
        product = Product.objects.get(name=product_name)
        bot.reply_to(message, f"Successful purchase of {product.name} for {product.price} tgs.")
    except Product.DoesNotExist:
        bot.reply_to(message, "Product not found. Please check the name and try again.")

@bot.message_handler(func=lambda message: True)
def unknown_message(message):
    if not check_authorization(message.chat.id):
        bot.reply_to(message, "Please, login: 'login your_login your_password'\nIf you are not registered, register: 'register your_login your_password'")
    else:
        bot.reply_to(message, "Sorry, I can't handle that request right now.")
        

#@bot.message_handler (func=lambda message: True)
#def all_msgs (message: telebot.types.Message):
#	custom_user_id = message.from_user.id
#	user_telegram = UserTelegram.objects.filter(chat_id=custom_user_id).first()
#	if not user_telegram:
#		user_telegram = UserTelegram.objects.create(
#			chat_id=custom_user_id, first_name=message.from_user.first_name,
#			Language_code=message.from_user.language_code
#		)
#	if not user_telegram.user:
#		bot.send_message(custom_user_id, "Please, login: 'login your_login your_password'")
#		return

bot.infinity_polling()
