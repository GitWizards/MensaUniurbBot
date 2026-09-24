import locale
from datetime import datetime, timedelta

import requests


def get_menu_msg(place, date, meal) -> str:
    try:
        r = requests.get(f"http://api:9543/{place}/{date}/{meal}", timeout=10)
        data = r.json()
    except requests.exceptions.RequestException:
        return "ERROR"

    rv = ""

    if data["error"]:
        rv = "ERROR"
    elif data["empty"]:
        rv = "NO_DATA"
    else:
        menu = data["menu"]

        if menu["first"]:
            rv += "🍝 *Primo:*\n"
            for dish in menu["first"]:
                rv += f" • {dish}\n"

        if menu["second"]:
            rv += "\n🍽️ *Secondo:*\n"
            for dish in menu["second"]:
                rv += f" • {dish}\n"

        if menu["side"]:
            rv += "\n🥗 *Contorno:*\n"
            for dish in menu["side"]:
                rv += f" • {dish}\n"

        if menu["cheese"]:
            rv += "\n🧀 *Salumi/Formaggi:*\n"
            for dish in menu["cheese"]:
                rv += f" • {dish}\n"

        if menu["fruit"]:
            rv += "\n🍎 *Frutta/Dolci:*\n"
            for dish in menu["fruit"]:
                rv += f" • {dish}\n"


        rv += "\n⚠️ _Il menù potrebbe subire delle variazioni_ ⚠️"

    return rv


def get_monthly_stats() -> str:
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%-m")
    day = now.strftime("%-d")

    # Requests statistics from the API
    try:
        r = requests.get("http://api:9543/stats/", timeout=10)
        data = r.json()
    except requests.exceptions.RequestException:
        return "Errore nel recupero delle statistiche."

    rv = (
        f"Richieste totali: {data['total']}\n"
        f"Richieste {month.zfill(2)}/{year}: {data['requests'][year][month]['total']}\n"
        f"Richieste oggi: {data['requests'][year][month][day]}"
    )
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
