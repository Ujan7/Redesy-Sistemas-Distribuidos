import requests
from datetime import date


def get_url(year):
    return f"https://nolaborables.com.ar/api/v2/feriados/{year}"


months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
days = ['Lunes', 'Martes', 'Miércoles',
        'Jueves', 'Viernes', 'Sábado', 'Domingo']


def day_of_week(day, month, year):
    return days[date(year, month, day).weekday()]


class NextHoliday:
    def __init__(self):
        self.loading = True
        self.year = date.today().year
        self.holiday = None

    def set_next(self, holidays):
        now = date.today()
        today = {
            'day': now.day,
            'month': now.month
        }

        holiday = next(
            (h for h in holidays if h['mes'] == today['month']
             and h['dia'] > today['day'] or h['mes'] > today['month']),
            holidays[0]
        )

        self.loading = False
        self.holiday = holiday

    def fetch_holidays(self):
        response = requests.get(get_url(self.year))
        data = response.json()
        self.set_next(data)

    def fetch_holidays_by_type(self, type):
        holidays = requests.get(get_url(self.year))
        holidays = holidays.json()
        self.holiday = []
        for holiday in holidays:
            if holiday['tipo'] == type:
                self.holiday.append(holiday)
        self.loading = False

    def render(self):
        if self.loading:
            print("Buscando...")
        else:
            print("Próximo feriado")
            print(self.holiday['motivo'])
            print("Fecha:")
            print(day_of_week(self.holiday['dia'],
                  self.holiday['mes'], self.year))
            print(self.holiday['dia'])
            print(months[self.holiday['mes'] - 1])
            print("Tipo:")
            print(self.holiday['tipo'])

    def render_by_type(self):
        if self.loading:
            print("Buscando...")
        else:
            print("\nFeriados por tipo\n")
            for holiday in self.holiday:
                print(f"********* {holiday['motivo']} *********")
                print(
                    f"Fecha: {day_of_week(holiday['dia'], holiday['mes'], self.year)} {holiday['dia']} de {months[holiday['mes'] - 1]}")
                print(f"Tipo: {holiday['tipo']}")
                print()


if __name__ == "__main__":
    next_holiday = NextHoliday()
    next_holiday.fetch_holidays()
    next_holiday.render()

    next_holiday_by_type = NextHoliday()
    next_holiday_by_type.fetch_holidays_by_type('inamovible')
    next_holiday_by_type.render_by_type()
