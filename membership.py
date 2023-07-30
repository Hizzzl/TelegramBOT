from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import sqlite3

# Replace with your API token
API_TOKEN = '6652643521:AAHDgfx_MVs8UDsbZULuVeWTCH8al2yF0Jc'

# Initialize the bot
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def check_channel_membership(user_id, channel_id):
    try:
        # Get the ChatMember object for the specified user and channel
        chat_member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)

        # Check the status of the channel member
        if chat_member.status in [types.ChatMemberStatus.MEMBER, types.ChatMemberStatus.ADMINISTRATOR,
                                  types.ChatMemberStatus.CREATOR]:
            return True
        else:
            return False
    except Exception as e:
        print("Error checking channel membership:", e)
        return False


async def check(user_id):

    channel_id = -1001983444165  # Замените на chat_id вашего канала

    # Проверяем присоединение пользователя к каналу
    is_member = await check_channel_membership(user_id, channel_id)
    return is_member
