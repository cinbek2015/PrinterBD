from datetime import datetime
from flask import Flask, render_template, url_for, request, flash, session, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from os import urandom
import csv

# render_template() передача переменных в html файла
# url_for() получение url адреса
# request работа с данными форм POST или GET
# flash() мгновенные сообщения пользователям
# session для отслеживания сессии пользователя
# redirect() перадресация на сессию пользователя
# abort() ошибки

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///printer.db'
# при переносе на севрер надо не забыть заменить IP адрес на localhost
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:12345@192.168.1.46:5432/PrinterBD"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

key = urandom(20).hex()
app.config['SECRET_KEY'] = key


class MOL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(50), nullable=True, unique=True)
    department = db.Column(db.String(100), default="AO SevCavNIPIgaz")

    def __repr__(self):
        return f"<MOL {self.id}>"

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    inv = db.Column(db.String(50))
    sn = db.Column(db.String(100), unique=True)
    kab = db.Column(db.Integer, nullable=True)
    data_vvoda = db.Column(db.Date(),  default=datetime.utcnow)
    #создаем переменную для соединения двух таблиц
    mol = db.relationship('MOL', backref='Device')

    molid = db.Column(db.Integer, db.ForeignKey('MOL.id'))

    def __repr__(self):
        return f"<Device {self.id}>"


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    deviceid = db.Column(db.Integer, db.ForeignKey('device.id'))
    type_work = db.Column(db.String(300), nullable=True)
    note = db.Column(db.String(300))
    #создаем перменную для соединения двух таблиц
    device = db.relationship('Device', backref='Job')

    def __repr__(self):
        return f"<Job {self.id}>"

menu = [{"name": "Главная", "url": "index"},
        {"name": "Поиск", "url": "find-device"},
        {"name": "Устройства", "url": "add-device"},
        {"name": "МОЛ", "url": "add-mol"},
        {"name": "Карточки", "url": "add-job"},
        {"name": "О сайте", "url": "about"}]

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", menu=menu)

@app.route('/find-device', methods=["POST", "GET"])
def find_device():
    name_device = []
    if request.method == "POST":
        try:
            if request.form['name_device']:#если заполнено поле имя устройства
                if request.form['sn']:#если заполнен серийный номер
                    name_device = Device.query.filter(
                        Device.name==request.form['name_device']or Device.sn==request.form['sn']).all()
                else:#заполнен только имя устройства
                    name_device = Device.query.filter(
                        Device.name == request.form['name_device']).all()
            elif request.form['sn']:#заполнен только серийный номер
                name_device = Device.query.filter(Device.sn == request.form['sn']).all()
            else:#ничего не заполнено
                print("request.form['sn']=",request.form['sn'],"request.form['name_device']=",request.form['name_device'])
        except:
            print("Ошибка базы данных")
    text_card =[]
    for i in name_device:
        temp = str(i.name) + ";" + str(i.inv) + ";" + str(i.sn) + ";" + str(i.kab) + ";" + str(i.mol.fio) + ";"
        text_card.append(temp)
    return render_template("find-device.html", title="Поиск устройств", menu=menu, list_name=name_device, text=text_card)

@app.route('/save_file/<text>/', methods=["POST", "GET"])
def save_file(text):
    print(text)
    with open("printer.csv", 'w', encoding='cp1251') as output:
        print("Имя устройства",";","Инвентарный номер",";","Серийный номер",";","Кабинет",";","МОЛ",";", file=output)
        text = text[1:-1].split(',')
        text = [x.replace("'", "") for x in text]
        for n in range(len(text)):
            print(text[n], file=output)
        flash('Данные успешно экспортированы', category='success')

    return render_template("find-device.html", title="Поиск устройств", menu=menu)

@app.route('/add-job', methods=["POST", "GET"])
def add_job():
    info_device = []
    info_inv = []
    if request.method == "POST":
        try:
            if request.form['name_select']:
                info_inv = Device.query.filter_by(name=request.form['name_select']).order_by(Device.inv).all()
            else:
                print("не выбрано устройство на странице add-job")
            device_id = Device.query.filter_by(sn=request.form['name_select']).first()
            if request.form['date']:
                d = Job(date=request.form['date'], deviceid=device_id.id, type_work=request.form['type_work'],
                        note=request.form['note'])
            else:
                d = Job(deviceid=device_id.id, type_work=request.form['type_work'],note=request.form['note'])

            db.session.add(d)  # данные храняться еще в сессии (памяти устройства)
            db.session.commit()  # Добавляем запись в базу данных
            flash('Данные успешно занесены в базу данных', category='success')
        except:
            db.session.rollback()
            flash('Ошибка добавления в БД', category='error')
    try:  # получаем данные из БД для МОЛ
        info_sn = Device.query.order_by(Device.sn).all()
        info_inv = Device.query.order_by(Device.inv).all()
    except:
        print("Ошибка базы данных")
    return render_template("add-job.html", title="Добавление произведенной работы в базу данных", menu=menu, list_sn=info_sn,
                           list_inv=info_inv)


@app.route('/device/<id>/', methods=["POST", "GET"])#выводим карточку устройства
def device(id):
    if request.method == "GET":
        info_card = Job.query.filter_by(deviceid=id).all()
        name_device = Device.query.filter_by(id=id).first()
        return render_template("device.html", title="Карточка устройства", menu=menu, card=info_card, name=name_device)

@app.route('/add-device', methods=["POST", "GET"])#добавление устроство в БД
def add_device():
    info_mol = []
    if request.method == "POST":
        # проверяем, что бы серийный номер был уникальным
        info_sn = []
        try:
            info_sn = Device.query.all()  # получаем все устройства из БД
        except:
            print("Ошибка базы данных")
        for dv in info_sn:
            if request.form['sn'] == dv.sn:
                flash('Устройство с этим серийным номером уже имеется в БД', category='error')
                break
        try:#выбор МОЛ на страничке
            mol_id = MOL.query.filter_by(fio=request.form['comp_select']).first()
            print("mol_id=", mol_id)
            d = Device(name=request.form['name'], inv=request.form['inv'], sn=request.form['sn'],
                       kab=request.form['kab'], data_vvoda=request.form['data_vvoda'],  molid=mol_id.id)
            print(d.name, d.inv, d.sn, d.kab, d.data_vvoda, d.molid)
            db.session.add(d)  # данные храняться еще в сессии (памяти устройства)
            print(3)
            db.session.commit()  # Добавляем запись в базу данных
            flash('Данные успешно занесены в базу данных', category='success')
        except:
            db.session.rollback()
            flash('Ошибка добавления в БД', category='error')

    try:#получаем данные из БД для МОЛ отсортировав по фамилии
        info_mol = MOL.query.order_by(MOL.fio).all()
    except:
        print("Ошибка получения данных их базы данных для MOL")
    return render_template("add-device.html", title="Добавление устройств в базу данных", menu=menu, list=info_mol)

@app.route('/add-mol', methods=["POST", "GET"])#добавление МОЛ в БД
def add_mol():
    if request.method == "POST":
        if len(request.form['fio']) == 0 or len(request.form['department']) == 0:
            flash('Заполните все данные', category='error')
        else:
            #проверяем, что бы новый МОЛ был уникальным
            info_mol = []
            try:
                info_mol = MOL.query.all() #получаем все МОЛ из БД
            except:
                print("Ошибка базы данных")
            for user in info_mol:
                if request.form['fio'] == user.fio:
                    flash('Данное ФИО уже имеется в БД', category='error')
                    break
            try:
                m = MOL(fio=request.form['fio'], department=request.form['department'])
                db.session.add(m)  # данные храняться еще в сессии (памяти устройства)
                db.session.commit()#Добавляем запись в базу данных
                flash('Данные успешно занесены в базу данных', category='success')
            except:
                db.session.rollback()
                print("Ошибка добавления в БД")

    return render_template("add-mol.html", title="Добавление МОЛ в базу данных", menu=menu)

@app.route('/about')
def about():  # О сайте
    return render_template("about.html", menu=menu)

# приятный сюрприз для администратора
@app.route('/cisco')
def cisco():  # Управление cisco
    return render_template("cisco.html", menu=menu)

@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu), 404


# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if 'userLogged' in session:
#         return redirect(url_for('profile', username=session['userLogged']))
#     elif request.method == 'POST' and request.form['username'] == "cinbek" and request.form['psw'] == "123":
#         session['userLogged'] = request.form['username']
#         return redirect(url_for('profile', username=session['userLogged']))
#     return render_template('login.html', title="Авторизация", menu=menu)
#
#
# @app.route('/profile/<username>')
# def profile(username):
#     if 'userLogged' not in session or session['userLogged'] != username:
#         abort(401)
#
#     return f"Пользователь: {username}"

# проверка работы без сервера
# with app.test_request_context():
#     print(url_for("index"))
#     print( url_for("about"))
#     print( url_for("profile", username="KovalchukAV"))

if __name__ == '__main__':
    app.run(port=80, debug=True)


