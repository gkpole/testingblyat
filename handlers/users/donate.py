import random
from datetime import datetime
from hashlib import md5
from json import loads
from urllib.parse import urlencode

import aiohttp
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from config import donates, payok_api_key, payok_api_id, payok_shop_id, payok_secret, freekassa_shop_id, \
    coins_obmen_enabled, payok, freekassa, bot_name
from keyboard.main import donate_kb, link_to_owner, donate_kbi, check_ls_kb, back_donate, oplata_kb, oplata_url_kb, \
    donates_kb
from utils.freekassa import secrets
from utils.main.cash import to_str, get_cash
from utils.main.users import User


async def donate_handler(message: Message):
    text = '''📃 Список привилегий в боте:
➖➖➖➖➖➖➖➖➖➖➖➖
<b>💎 VIP</b> (<code>150 🪙</code>):
<i>Писать @Cut1eb1tch</i>
➖➖➖➖➖➖➖➖➖➖➖➖
<b>🥋 JUNIOR</b> (<code>1000 🪙</code>)::
<i>Писать @Cut1eb1tch</i>    
➖➖➖➖➖➖➖➖➖➖➖➖
<b>❤️‍🔥 ADMIN</b> (<code>5000 🪙</code>):
<i>Писать @Cut1eb1tch</i>    
➖➖➖➖➖➖➖➖➖➖➖➖
<b>👻 Уник</b> (<code>10000 🪙</code>):
<i>Писать @Cut1eb1tch</i>    
➖➖➖➖➖➖➖➖➖➖➖➖
<i>Курс обмена коин->доллар</i>
<code>$100,000</code> = 1🪙
➖➖➖➖➖➖➖➖➖➖➖➖
<b>Для покупки писать вастеру и ждать пока ответят в течении 2 часов от 12:00 — 23:00
<b>Аккаунт создателя @h1neky</b>
<b>Удачной игры!</b>'''

    if message.text.lower().startswith('купить') and len(message.text.split()) > 1:
        return await privilegia_handler(message)

    try:
        await message.bot.send_message(
            chat_id=message.from_user.id,
            text=text,
            reply_markup=donate_kbi,
        disable_web_page_preview=True)
        if message.chat.id != message.from_user.id:
            return await message.reply('✈️ Я отправил вам в лс ДОНАТ-МЕНЮ!')
    except:
        return await message.reply(text='💎 Я не могу отправить вам в лс донат-меню, напишите мне что-то!',
                                   reply_markup=check_ls_kb)


async def zadonatit_handler(message: Message):
    try:
        if isinstance(message, Message):
            message = message
            call = None
        else:
            call = message

        if call:
            return await call.message.edit_text(text='💎 Выберите метод оплаты:', reply_markup=donates_kb,
                                                disable_web_page_preview=True)
        else:
            await message.bot.send_message(
                chat_id=message.from_user.id,
                text='💎 Выберите метод оплаты:', reply_markup=donates_kb,
                disable_web_page_preview=True)
            return await message.reply('✈️ Я отправил вам в лс клавиатуру для доната!')
    except:
        return await message.reply('🍁 Не могу отправить тебе в лс ничего, напиши в лс бота!')


async def other_method_handler(call: CallbackQuery):
    text = '<b>МЕНЮ ДОНАТА</b>\n\n' \
           '• Для покупки писать @vaster_o\n' \
           '<i>Курс 1🪙 = 1RUB</i>\n' \
           'Скидка действительна!\n' \
           '➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n' \
           f'🪙 Также можно обменять игровые деньги на коины <code>Обменять {кол-во} </code>' \
           f' {to_str(1000000000)} = 1🪙' \
           '</i>'
    return await call.message.edit_text(text=text,
                                        reply_markup=back_donate)


class Payok(StatesGroup):
    start = State()


async def payok_handler(call: CallbackQuery):
    if not payok:
        return await call.answer('⛔ Этот метод оплаты отключён!')
    text = '🪙 Напишите кол-во коинов которые вы хотите задонатить'
    await Payok.start.set()
    return await call.message.edit_text(text=text,
                                        reply_markup=back_donate)


async def payok_check(call: CallbackQuery):
    order_id = int(call.data.split('_')[1])
    api = payok_api_key
    url = 'https://payok.io/api/transaction'
    async with aiohttp.ClientSession() as session:
        data = {
            'API_ID': payok_api_id,
            'API_KEY': api,
            'shop': payok_shop_id,
            'payment': order_id,
        }
        response = await session.post(url=url, data=data)
        json = loads(await response.text())
        if json["status"] != 'success' or int(json['1']['transaction_status']) != 1:
            return await call.answer('🧙 Счёт не оплачен!', show_alert=True)
        else:
            user = User(user=call.from_user)
            x = int(json['1']['amount'])
            user.edit('coins', user.coins + x)
            return await call.message.edit_text(text=f'✅ На баланс зачислено +{x} COINS!')


async def payok_step1(message: Message, state):
    await state.finish()
    if not message.text.isdigit() or int(message.text) <= 0:
        return await message.reply('❌ Неверная сумма!')
    summ = int(message.text.split()[0])

    payment = int("".join(random.choice('0123456789') for _ in range(random.randint(4, 16))))
    desc = f'Пополнение_{summ}RUB'
    data = {'amount': str(summ),
            'payment': str(payment),
            'shop': f'{payok_shop_id}',
            'currency': 'RUB',
            'desc': desc,
            'secret': f'{payok_secret}'
            }
    sign = md5('|'.join(data.values()).encode()).hexdigest()

    data.update({'sign': sign})
    del data['secret']

    url = 'https://payok.io/pay?' + urlencode(data)
    text = f'💎 Ваш счёт на <b>{summ}RUB</b> сгенерирован!\n' \
           f'Перейдите по <a href="{url}">ссылке</a> чтобы оплатить.\n\n' \
           f'Возникли проблемы? Пишите основателю'
    return await message.reply(text=text,
                               reply_markup=oplata_kb(payment, url))


class Freekassa(StatesGroup):
    start = State()


async def freekassa_handler(call: CallbackQuery):
    if not freekassa:
        return await call.answer('⛔ Этот метод оплаты отключён!')
    text = '🪙 Напишите кол-во коинов которые вы хотите задонатить'
    await Freekassa.start.set()
    return await call.message.edit_text(text=text,
                                        reply_markup=back_donate)


async def freekassa_step1(message: Message, state):
    await state.finish()
    if not message.text.isdigit() or int(message.text) <= 0:
        return await message.reply('❌ Неверная сумма!')
    summ = int(message.text.split()[0])
    data = {
        "m": freekassa_shop_id,
        "oa": summ,
        "currency": "RUB",
        "o": f'{message.from_user.id}',
        'lang': 'ru'
    }
    sign = md5(':'.join([f"{freekassa_shop_id}", str(summ), secrets[0], "RUB", data['o']]).encode()).hexdigest()

    data.update({'s': sign})

    url = 'https://pay.freekassa.ru/?' + urlencode(data)
    text = f'💎 Ваш счёт на <b>{summ}RUB</b> сгенерирован!\n' \
           f'Перейдите по <a href="{url}">ссылке</a> чтобы оплатить.\n\n' \
           f'Возникли проблемы? Пишите основателю'
    return await message.reply(text=text,
                               reply_markup=oplata_url_kb(url))


async def privilegia_handler(message: Message):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[2:]
    arg = arg[0].lower()
    if 'vip' in arg or 'вип' in arg:
        priva = 1
    elif 'prem' in arg or 'прем' in arg:
        priva = 2
    elif 'адм' in arg or 'adm' in arg:
        priva = 3
    elif 'уник' in arg or 'unik' in arg:
        priva = 5
    else:
        return await message.reply('❌ Такой привилегии не существует!')

    item = donates[priva]
    user = User(user=message.from_user)
    donate = user.donate
    if user.coins < item["price"]:
        return await message.reply(f'🪙 Недостаточно коинов, нужно: <code>{item["price"]}</code>',
                                   reply_markup=donate_kb if message.chat.id != message.from_user.id else donate_kbi)
    elif donate and donate.id >= priva:
        return await message.reply('➖ У вас и так такая привилегия или выше!')

    user.editmany(donate_source=f'{priva},{datetime.now().strftime("%d-%m-%Y %H:%M")}',
                  coins=user.coins - item['price'])

    await message.reply(f'✅ Вы успешно приобрели привилегию <b>{item["name"]}</b> за {item["price"]}🪙')

    if priva > 2:
        pass


async def cobmen_handler(message: Message):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[2:]
    if len(arg) == 0:
        return await message.reply('❌ Введите: <code>Кобменять {кол-во коинов}</code>')
    try:
        summ = abs(get_cash(arg[0]))
        if summ == 0:
            raise Exception('123')
    except:
        return await message.reply('❌ Введите: <code>Кобменять {кол-во коинов}</code>')

    user = User(user=message.from_user)
    if user.coins < summ:
        return await message.reply(f'🪙 Недостаточно коинов на балансе, нужно <code>{summ}</code> а у вас '
                                   f'<code>{user.coins}</code>',
                                   reply_markup=donate_kb if message.chat.id != message.from_user.id else donate_kbi)

    user.editmany(coins=user.coins - summ,
                  balance=user.balance + summ * 100000)

    return await message.reply(f'✅ Вы успешно обменяли {summ} коинов на {to_str(summ * 100000)}')


async def obmen_handler(message: Message):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[2:]
    if len(arg) == 0:
        return await message.reply('❌ Введите: <code>Обменять {кол-во $}</code>')

    user = User(user=message.from_user)

    try:
        summ = abs(get_cash(arg[0] if arg[0].lower() not in ['всё', 'все'] else str(user.balance)))
        if summ == 0:
            raise Exception('123')
    except:
        return await message.reply('❌ Введите: <code>Обменять {кол-во $}</code>')

    if user.balance < summ:
        return await message.reply(f'💲 Недостаточно $ на руках, нужно {to_str(summ)} а у вас '
                                   f'<code>{user.balance}</code>')

    coins = summ // 1000000000
    if coins <= 0:
        return await message.reply('💲 Этой суммы не хватит даже на 1 коин!')

    if not coins_obmen_enabled:
        return await message.reply('👻 Функция отключена разработчиком.')

    price = coins * 1000000000

    user.editmany(coins=user.coins + coins,
                  balance=user.balance - price)

    return await message.reply(f'✅ Вы успешно обменяли {to_str(price)} на {coins} 🪙')


async def percent_buy_handler(message: Message):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[2:]
    user = User(user=message.from_user)

    if len(arg) == 0:
        x = f'+{user.donate.percent}' if user.donate else ""
        return await message.reply(f'😐 Ваш процент: {user.percent}{x}%/10\n'
                                   'Введите: <code>Процент {кол-во}</code> чтобы купить')
    try:
        summ = abs(get_cash(arg[0]))
        if summ == 0:
            raise Exception('123')
    except:
        return await message.reply('❌ Введите: <code>Процент {кол-во}</code>')

    price = summ * 200

    if price > user.coins:
        return await message.reply(f'🪙 Недостаточно коинов на балансе, нужно <code>{price}</code> а у вас '
                                   f'<code>{user.coins}</code>',
                                   reply_markup=donate_kb if message.chat.id != message.from_user.id else donate_kbi)

    if (summ + user.percent) > 10:
        return await message.reply(f'🪙 Будет превышен лимит донат-процента, у вас: '
                                   f'<code>{user.percent}</code>/10',
                                   reply_markup=donate_kb if message.chat.id != message.from_user.id else donate_kbi)

    user.editmany(coins=user.coins - price,
                  percent=user.percent + summ)

    return await message.reply(f'✅ Вы успешно купили +{summ}% к депозитной ставке за {price}🪙')
