
levels = {
    0: {
        'name': 'РодДом 🤰',
        'doxod': 0
    },
    1: {
        'name': 'Ясельная група 👶',
        'doxod': 0
    },
    2: {
        'name': 'Средняя група 👦',
        'doxod': 0
    },
    3: {
        'name': 'Старшая група 📕',
        'doxod': 0
    },
    4: {
        'name': 'Школьник 🎒',
        'doxod': 0
    },
    5: {
        'name': '2️⃣ Класс',
        'doxod': 0
    },
    6: {
        'name': '5️⃣ Класс',
        'doxod': 0
    },
    7: {
        'name': '9️⃣ Класс',
        'doxod': 100
    },
    8: {
        'name': '11 Класс 👦',
        'doxod': 1000
    },
    9: {
        'name': '🏢 1-Курс',
        'doxod': 1000
    },
    10: {
        'name': '🏢 2-Курс',
        'doxod': 3000
    },
    11: {
        'name': '🏢 3-Курс',
        'doxod': 5000
    },
    12: {
        'name': '❤️‍🩹 Жизнь',
        'doxod': 0
    }
}


jobs = {
    1: {
        'name': '🕵️‍♂️ Детектив',
        'doxod': 25000,
        'level': 20
    },
    2: {
        'name': '🧙‍♂️ Экстрасекс',
        'doxod': 20000,
        'level': 17
    },
    3: {
        'name': '🧑‍⚖️ Судья',
        'doxod': 15000,
        'level': 15
    },
    4: {
        'name': '👮 СБУшник',
        'doxod': 14500,
        'level': 14
    },
    5: {
        'name': '🧑‍🏫 Учитель',
        'doxod': 13500,
        'level': 13
    }
}


class Job:
    def __init__(self, index: int):
        self.json = jobs[index]

        self.name: str = self.json['name']
        self.index = index
        self.doxod: int = self.json['doxod']
