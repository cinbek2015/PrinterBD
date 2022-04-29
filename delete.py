import PySimpleGUI as sg

sg.theme('Dark Blue 3')

layout = [
    [sg.Text('Введите данные', font='Default 14')],
    [sg.Text('Объект (адрес, ЖК, и.т.д.)', size=(26, 1)), sg.InputText(size=(15, 1))],
    [sg.Text('Стоимость аренды', size=(26, 1)), sg.InputText(size=(10, 1))],
    [sg.Text('Коммуналка', size=(26, 1)), sg.InputText(size=(10, 1))],
    [sg.Text('Оплата помощи', size=(26, 1)), sg.InputText(size=(10, 1))],
    [sg.Text('Стоимость доп.оснащения', size=(26, 1)), sg.InputText(size=(10, 1))],
    [sg.Text('Интернет, ТВ, Расходники и.т.д ', size=(26, 1)), sg.InputText(size=(10, 1))],
    [sg.Text('Количество дней', size=(26, 1)), sg.InputText(size=(10, 1))],
    [sg.Text('Желаемый доход в месяц', size=(26, 1)), sg.InputText(size=(10, 1))],
    [sg.Text('Процент площадки бронирования', size=(26, 1)), sg.InputText(size=(10, 1))],
    [sg.Submit('Calc', size=(10, 9)), sg.Cancel('Exit', size=(10, 9))]
]

window = sg.Window('Arenda Calc', layout, size=(380, 310))
event, values = window.read()
window.close()
base_ar = int(values[1])
komm = int(values[2])
servise = int(values[3])
dop = int(values[4])
mult = int(values[5])
day = int(values[6])
dohod = int(values[7])
bron_procent = int(values[8])
dop_clear = dop/12 # считаем стоимость доп оснащения на 12 месяцев
all_credit = base_ar+komm+servise+dop_clear+mult # Считаем общие вложения - расходы
min_point = all_credit/day # Считаем точку безубыточности, от кол-во дней
min_point_dohod = dohod/day+min_point # Считаем минимальную арендную ставку с учетом желаемого дохода
procent = min_point_dohod+bron_procent # Добовляем % площадки бронирования

object_dic = {'Объект': values[0], 'Минимальная стоимость аренды в сутки': int(min_point),
              'Минимальная стоимость аренды с учетом желаемого дохода': int(procent)}
with open('arenda.csv', 'a+', encoding="utf8") as out:
    print('\n', file=out)
    for key,val in object_dic.items():
        out.write('{}:{}\t'.format(key,val))

sg.popup(#values[0], 'Минимальная стоимость аренды в сутки', int(min_point),
object_dic)#'Минимальная стоимость аренды с учетом желаемого дохода', int(procent))