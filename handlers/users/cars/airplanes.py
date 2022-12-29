from aiogram.types import Message

from config import bot_name
from keyboard.generate import buy_airplane_kb, show_balance_kb, show_inv_kb, show_airplane_kb, airplane_kb, \
    ride_airplane_kb
from utils.logs import writelog
from utils.main.airplanes import airplanes, Airplane
from utils.main.cash import to_str, get_cash
from utils.main.db import sql


async def airplanes_list_handler(message: Message):
    text = 'Название - цена - сток - налог\n'
    asd = sql.execute(f'SELECT sell_count FROM users WHERE id = {message.from_user.id}', False, True)[0][0]
    if asd is None:
        asd = 0
    xa = asd = float(f'0.{asd}')
    for index, i in airplanes.items():
        price = i["price"] - int(i["price"] * xa)
        text += f'<code>{index}</code>. {i["name"]} - {to_str(price)} - {i["fuel"]}' \
                f' - {to_str(i["nalog"])}\n'
    return await message.reply(
        f'<i>(Ваша скидка: x{asd})</i>\n\n'
        + text + '\n\nИспользуйте: <code>Самолёт купить {номер}</code> чтобы купить!',
        reply_markup=buy_airplane_kb)


async def airplanes_handler(message: Message):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[2:]
    try:
        airplane = Airplane(user_id=message.from_user.id)
    except:
        airplane = None
        if len(arg) < 1 or arg[0].lower() != 'купить' or not arg[1].isdigit():
            return await airplanes_list_handler(message)
    if len(arg) == 0:
        return await message.reply(text=airplane.text, reply_markup=airplane_kb)
    elif arg[0].lower() in ['список', 'лист']:
        return await airplanes_list_handler(message)

    elif arg[0].lower() == 'продать':
        doxod = airplane.sell()
        sql.execute(f'UPDATE users SET bank = bank + {doxod} WHERE id = {message.from_user.id}')
        await message.reply(f'✅ Вы продали самолёт и с учётом налогов, и дохода вы получили: {to_str(doxod)}',
                            reply_markup=show_balance_kb)
        await writelog(message.from_user.id, f'Самолёт продажа')
        return
    elif arg[0].lower() == 'купить':
        if airplane:
            return await message.reply('❗ У вас уже есть самолёт, можно иметь только 1.',
                                       reply_markup=show_airplane_kb)
        try:
            i = airplanes[int(arg[1])]
        except:
            return await message.reply('❌ Ошибка. Неверный номер самолёты!')
        xa = sql.execute(f'SELECT sell_count, balance FROM users WHERE id = {message.from_user.id}', False, True)[0]
        balance = xa[1]
        xa = xa[0]
        if xa is None:
            xa = 0
        xa = float(f'0.{xa}')
        price = i["price"] - int(i["price"] * xa)

        if balance < price:
            return await message.reply(
                f'💲 На руках недостаточно денег для покупки, нужно: {to_str(price)}')
        Airplane.create(user_id=message.from_user.id, airplane_index=int(arg[1]))
        sql.execute(f'UPDATE users SET balance = balance - {price}, sell_count = 0 WHERE id ='
                    f' {message.from_user.id}', True)
        await message.reply(f'✅ Вы успешно приобрели самолёт <b>{i["name"]}</b> за'
                            f' {to_str(price)}', reply_markup=show_airplane_kb)
        await writelog(message.from_user.id, f'Самолёт покупка')
        return
    elif arg[0].lower() in ['снять', 'доход']:
        xd = airplane.cash
        if len(arg) > 1:
            try:
                xd = get_cash(arg[1])
            except:
                pass
        if airplane.cash < xd or airplane.cash < 0:
            return await message.reply('💲 Недостаточно денег на счету самолёты!')
        elif xd <= 0:
            return await message.reply('❌ Нельзя так!')
        sql.executescript(f'''UPDATE users SET bank = bank + {xd} WHERE id = {message.from_user.id};
                              UPDATE airplanes SET cash = cash - {xd} WHERE id = {airplane.id};''',
                          True)

        await message.reply(f'✅ Вы успешно сняли {to_str(xd)} с прибыли самолёта!', reply_markup=show_balance_kb)
        await writelog(message.from_user.id, f'Снятие с прибыли самолёта.')
        return
    elif arg[0].lower() in ['ехать', 'зарабатывать', 'заработать', 'работать',
                            'работа', 'лететь', 'летать']:
        if airplane.fuel <= 0:
            return await message.reply('✈️ Самолёт больше не может летать! Его состояние: 0%\n'
                                       'Вам нужно <b>Болтик 🔩</b> (x10) чтобы восстановить 1%\n\nВведите <code>'
                                       ' Самолёт починить</code> чтобы починить самолёт', reply_markup=show_airplane_kb)
        elif airplane.energy <= 0:
            return await message.reply('⚡ У самолёты разрядился аккумулятор, подождите немного чтобы он зарядился!')

        doxod = airplane.ride()
        await message.reply(f'✈️️ Вы проехали {doxod[0]} км. и заработали {to_str(doxod[1])}'
                            f' на счёт самолёты! (-1⚡) (-1⛽)\n'
                            f'⚡ Текущая энергия: {airplane.energy}\n'
                            f'⛽ Текущее состояние самолёты: {airplane.fuel}%', reply_markup=ride_airplane_kb)
        await writelog(message.from_user.id, f'Самолёт лететь')
        return

    elif arg[0].lower() in ['починить', 'чинить', 'починка']:
        items = sql.execute(f'SELECT items FROM users WHERE id = {message.from_user.id}', False, True)[0][0]
        if '22:' not in items:
            return await message.reply('❌ У вас нет <b>Болтик 🔩</b> (x10) в инвентаре!',
                                       reply_markup=show_inv_kb)
        count = int(items.split('22:')[1].split(',')[0])
        if count < 10:
            return await message.reply(f'❌ Не хватает {10 - count} <b>Болтиков 🔩</b> для починки!',
                                       reply_markup=show_inv_kb)
        user_items = [[int(x.split(':')[0]), int(x.split(':')[1])] for x in items.split(',') if x]
        for index, i in enumerate(user_items):
            if i[0] == 22:
                break
        user_items[index] = [22, i[1] - 10]
        if (i[1] - 10) <= 0:
            user_items.remove(user_items[index])
        str_items = ','.join(f'{x[0]}:{x[1]}' for x in user_items if x)
        sql.executescript(f'UPDATE users SET items = "{str_items}" WHERE id = {message.from_user.id};\n'
                          f'UPDATE airplanes SET fuel = fuel + 1 WHERE id = {airplane.id};')
        await message.reply('✅ Самолёт восстановлен на +1%')
        await writelog(message.from_user.id, f'Самолёт восстановление')
        return

    elif arg[0].lower() in ['оплата', 'оплатить', 'налог', 'налоги']:
        xd = airplane.nalog
        if len(arg) > 1:
            try:
                xd = get_cash(arg[1])
            except:
                pass
        if airplane.nalog < 1:
            return await message.reply('💲 Налог на самолёт и так оплачен!')
        elif airplane.nalog < xd:
            xd = airplane.nalog
        elif xd <= 0:
            return await message.reply('❌ Нельзя так!')
        if sql.execute(f'SELECT bank FROM users WHERE id = {message.from_user.id}', False, True)[0][0] < xd:
            return await message.reply(f'💲 Недостаточно денег в банке для оплаты налога, нужно: {to_str(xd)}!',
                                       reply_markup=show_balance_kb)

        sql.executescript(f'''UPDATE users SET bank = bank - {xd} WHERE id = {message.from_user.id};
                              UPDATE airplanes SET nalog = {airplane.nalog - xd} WHERE id = {airplane.id};''',
                          True)

        await message.reply('✅ Налог на самолёт успешно оплачен!')
        await writelog(message.from_user.id, f'Самолёт налог оплата')
        return
    else:
        return await message.reply('❌ Ошибка. Используйте: <code>Самолёт [снять|оплатить|ехать] *{сумма}</code>')
