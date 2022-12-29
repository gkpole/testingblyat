from aiogram.types import Message

from config import bot_name
from utils.items.items import items
from utils.main.cash import to_str
from utils.main.users import User
from keyboard.main import check_ls_kb

items_to_sell = items.copy()
del items_to_sell[-1]
del items_to_sell[2]
del items_to_sell[3]
del items_to_sell[4]


async def users_shop_handler(message: Message):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[2:]
    if len(arg) > 1 and arg[0].lower() == 'купить':
        try:
            item_id = int(arg[1])
        except:
            return await message.reply('🚫 Используйте: <code>Шоп купить {номер} *{кол-во}</code>')

        try:
            item = items_to_sell[item_id]
        except:
            return await message.reply('🚫 Неверный номер предмета!')

        try:
            count = abs(int(arg[2]))
            if count == 0:
                count = 1
        except:
            count = 1

        price = (item['sell_price'] * 1.5) * count
        user = User(user=message.from_user)
        if user.balance < price:
            return await message.reply(f'💲 Недостаточно средств на руках, нужно: {to_str(price)}')
        user.edit('balance', user.balance - price)
        user.items = list(user.items)
        user.set_item(item_id=item_id, x=count)
        return await message.reply(f'💲 Вы купили {item["name"]} (x{count}) за {to_str(price)}')
    else:
        text = '🏪 Игровой магазин:\n\n'
        for index, item in items_to_sell.items():
            price = item['sell_price'] * 1.5
            text += f'{index}. <b>{item["name"]}{item["emoji"]}</b> - {to_str(price)}\n'

        text += '\n\nВведите: <code>Шоп купить {номер} *{кол-во}</code> чтобы приобрести предмет'

        try:
            await message.bot.send_message(chat_id=message.chat.id,
                                            text=text)
        except:
            return await message.reply('🚫 Не удалось отправить сообщение вам в личку!\n'
                                       'Зайдите в бота и напишите ему что-то!',
                                       reply_markup=check_ls_kb)
