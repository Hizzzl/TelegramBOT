import random

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import sqlite3
import membership
import stripe

# Replace with your API token
API_TOKEN = '6652643521:AAHDgfx_MVs8UDsbZULuVeWTCH8al2yF0Jc'
stripe.api_key = "284685063:TEST:NDU2YmIzMzAxYjgz"

# Initialize the bot
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Initialize database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):

    is_member = await membership.check((message.chat.id))
    if is_member:
        await sendStartMessages(message.chat.id)
        return

    if 'ref' in message.text:

        ref_code = message.text.split(' ')[1]
        balance = 0

        for i in cursor.execute("SELECT * FROM users WHERE ref=?", (ref_code,)):
            balance = i[1]

        cursor.execute("UPDATE users SET balance = ? WHERE ref = ?", (balance + 0.5, ref_code))
        conn.commit()


    keyboard = types.InlineKeyboardMarkup(row_width=2)

    channel_url = "https://t.me/facedeepapp"  # Change on your channel link
    channel_button = types.InlineKeyboardButton("Subscribe now", url=channel_url)

    button2 = types.InlineKeyboardButton("I subscribed! ✅", callback_data="show_table")

    keyboard.add(channel_button, button2)

    await bot.send_message(message.from_user.id, "To continue you need to subscribe our channel using 'subscribe now' and click 'I subscribed'!", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'show_table')
async def process_show_table(callback_query: types.CallbackQuery):
    is_member = await membership.check(callback_query.message.chat.id)

    if is_member:
        await sendStartMessages(callback_query.message.chat.id)
    else:
        await bot.answer_callback_query(callback_query.id, "You are not subscribed")


async def sendStartMessages(chat_id):
    # add user to database and give 2 free coins
    cursor.execute("SELECT * FROM users WHERE id=?", (chat_id,))
    user = cursor.fetchone()

    if user is None:

        rnd = "abcdefghijklmnpqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        ref = 'ref'
        for i in range(10):
            ref = ref + random.choice(rnd)

        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (chat_id, 2, ref))
        conn.commit()

    await bot.send_message(chat_id, """Welcome to Facedeep 🤩 The new cutting-edge Ai technology to swap faces, if it's your first time enjoy free 2 generations.  to gain more coins you can /deposit or you can earn more free coins simply just by /invite.
Payments are secure by stripe/crypto.""")


    gif_file_id = 'demo.gif'
    with open(gif_file_id, 'rb') as gif_file:
        await bot.send_animation(chat_id=chat_id, animation=gif_file)

    await bot.send_message(chat_id, "Please send the base photo 🖼️ (Remember, this is the face you want to use)")

@dp.message_handler(commands=['balance'])
async def sendUserBalance(message: types.Message):
    if await membership.check(message.from_user.id):
        # get balance from database
        user_id = message.from_user.id
        balance = 0
        for i in cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)):
            balance = i[1]

        await bot.send_message(user_id, "Your current balance - " + str(balance) + " coins💰")


@dp.message_handler(commands=['add'])
async def addUserBalance(message: types.Message):
    if await membership.check(message.from_user.id):
        # get balance from database
        user_id = message.from_user.id
        balance = 0

        for i in cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)):
            balance = i[1]

        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (balance + 1, user_id))
        conn.commit()


@dp.message_handler(commands=['invite'])
async def inviteInfo(message: types.Message):
    custom_link = 'https://t.me/facedeepbot?start='
    ref = ''
    user_id = message.chat.id
    for i in cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)):
        ref = i[2]
    custom_link = custom_link + ref

    await bot.send_message(message.chat.id, """For every referral, you will get 0.5$ in coins balance.
Tips: 
-Share in telegram groups comments
-add a referral link to your profile
-Share generated video on (Reddit, telegram, and Discord) with a referral link""")
    await bot.send_message(message.chat.id, "This is you referral link - " + custom_link)


@dp.message_handler(commands=['faq'])
async def faqInfo(message: types.Message):
    await bot.send_message(message.chat.id, """For best results for your video/photo use this: tips:
✅ Photos with only one face looking at the camera
✅ Photos with good lighting
✅ High-quality photos
❌ Avoid full-body photos
❌ Avoid sunglasses or glasses
❌ Avoid faces covered by hair or caps
❌ Avoid multiple faces in the same photo For best results for your video
""")
    await bot.send_message(message.chat.id, """Your account is billed based on the media type (photo or video)
🎥 For videos, your account will be billed based on the processing time in minutes. Most of the time, 1 minute of video duration equals 1 minute of processing time.
If the processing time is less than a minute, you will NOT be billed for the full minute.
    
""")

@dp.message_handler(commands=['deposit'])
async def sendUserBalance(message: types.Message):
    # Create InlineKeyboardMarkup with 1 button
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Stripe", callback_data='methodStripe')
    keyboard.add(button)

    # Send message with button
    await bot.send_message(message.chat.id, "Choose a payment method", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'methodStripe')
async def stripePriceList(callback_query: types.CallbackQuery):

    # Create InlineKeyboardMarkup with 5 buttons
    keyboard = types.InlineKeyboardMarkup(row_width=2)


    button1 = types.InlineKeyboardButton("3$", callback_data='3')
    button2 = types.InlineKeyboardButton("5$", callback_data='5')
    button3 = types.InlineKeyboardButton("10$", callback_data='10')
    button4 = types.InlineKeyboardButton("25$", callback_data='25')
    button5 = types.InlineKeyboardButton("50$", callback_data='50')

    keyboard.add(button1, button2, button3, button4, button5)

    # Send message with buttons
    await bot.send_message(callback_query.from_user.id, "Choose the amount of replenishment", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == '3')
async def stripePriceList(callback_query: types.CallbackQuery):
    print(3)

@dp.callback_query_handler(lambda c: c.data == '5')
async def stripePriceList(callback_query: types.CallbackQuery):
    print(5)

@dp.callback_query_handler(lambda c: c.data == '10')
async def stripePriceList(callback_query: types.CallbackQuery):
    print(10)

@dp.callback_query_handler(lambda c: c.data == '25')
async def stripePriceList(callback_query: types.CallbackQuery):
    print(25)

@dp.callback_query_handler(lambda c: c.data == '50')
async def stripePriceList(callback_query: types.CallbackQuery):
    print(50)


if __name__ == '__main__':

    executor.start_polling(dp)