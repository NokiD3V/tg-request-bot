from aiogram import Bot, Dispatcher, executor, types
import redis, json, logging, random
from aiogram.utils.markdown import hlink


# Config data
API_TOKEN = 'TOKEN OF BOT'
CHAT_ID = "YOUR CHAT ID"


# bot's logging 
logging.basicConfig(level=logging.INFO)


# aiogram create bot
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# Redis connect
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
Redis = redis.Redis(connection_pool=pool)

DEFAULT_TIME = 3600 # Time for redis


# Handler of regestration code
@dp.message_handler()
async def echo(message: types.Message):
    redis_user = Redis.get('request_' + str(message.from_user.id))

    if redis_user:
        redis_user = json.loads(redis_user)
        command_args = message.text.split(" ")
        if command_args[0] == "/code":

            if len(command_args) < 2: 
                await message.answer('Введите /code [Код]')
                return False
            if command_args[1] == redis_user["request_code"]:
                lnk = hlink("Перейти в канал", "https://t.me/+smrJTZTmUQsxY2Yy")
                await message.answer("Вы прошли регистрацию! Нажмите " + lnk, parse_mode='HTML')
                
                ch = await bot.get_chat(CHAT_ID)
                print(ch.id)
                

                await dp.bot.approve_chat_join_request(chat_id=redis_user["chat_id"], user_id=str(message.from_user.id))
                Redis.delete('request_' + str(message.from_user.id))
            else:
                await message.answer("Неверный код!")
        else:
            await message.answer('Введите /code [Код]')


# Invite handler
@dp.chat_join_request_handler()
async def invite(update: types.ChatJoinRequest):
    code = random.randint(1000, 9999)
    data = {"request_code":str(code), "chat_id": update.chat.id}
    Redis.set("request_" + str(update.user_chat_id), json.dumps(data), DEFAULT_TIME)
    await bot.send_message(update.user_chat_id, "Для того, чтобы вступить в канал, введите команду /code и следующее значение:\n\n <b>{}</b>\n\nПосле введения кода вашу заявку на добавление в канал одобрит бот.".format(str(code)), parse_mode="HTML")


# Main start process
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)