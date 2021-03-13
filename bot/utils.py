import json
import locale
from datetime import datetime, timedelta

import requests


def get_menu_msg(place, date, meal) -> str:
    r = requests.get(f"http://api:9543/{place}/{date}/{meal}")
    data = json.loads(r.text)
    rv = ""

    if not data['empty']:
        menu = data['menu']

        if menu['first']:
            rv += "🍝 *Primo:*\n"
            for dish in menu['first']:
                rv += f" • {dish}\n"

        if menu['second']:
            rv += "\n🍖 *Secondo:*\n"
            for dish in menu['second']:
                rv += f" • {dish}\n"

        if menu['side']:
            rv += "\n🍟 *Contorno:*\n"
            for dish in menu['side']:
                rv += f" • {dish}\n"

        if menu['fruit']:
            rv += "\n🍨 *Frutta/Dolci:*\n"
            for dish in menu['fruit']:
                rv += f" • {dish}\n"

        rv += "\n⚠️ _Il menù potrebbe subire delle variazioni_ ⚠️"

    return rv


def prepare_week_keyboard() -> list:
    keyboard = []
    row = []
    counter = 0

    # Make sure the locale is set to italian
    locale.setlocale(locale.LC_TIME, "it_IT.UTF-8")

    now = datetime.now()
    keyboard.append([f"Oggi [{now.strftime('%d/%m')}]"])

    for day in range(1, 8):
        date = now + timedelta(day)
        row.append(date.strftime("%A [%d/%m]"))
        counter += 1

        # Put 3 days in each row
        if counter > 3:
            keyboard.append(row)
            row = []
            counter = 0
    keyboard.append(row)

    return keyboard
