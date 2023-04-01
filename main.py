from flask import Flask, render_template, request, redirect
from PIL import Image as PilIMG, ImageDraw, ImageFont
from fpdf import FPDF  # fpdf2
from io import BytesIO
import base64
import os
from flask_sqlalchemy import SQLAlchemy
import csv


# проверка на ввод нулевого значения, если пусто, то возвращает None
def null_check(x):
    if x == "":
        return None
    else:
        return x


# запрос к базе для описания текста в PDF
def db_request(area, number):
    result = Article.query.filter(Article.area == area, Article.number == number).first()
    return result


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ds-matrix.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# оформление базы данных
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(100), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(300), nullable=False)
    intro = db.Column(db.Text, nullable=False)
    inbound = db.Column(db.Text)
    outbound = db.Column(db.Text)


def __repr__(self):
    return '<Article %r>' % self.id


# преход со страницы database на страницу со списком записей в конкреной базе
@app.route('/database/<string:area>')
def post_area(area):
    articles = Article.query.filter(Article.area == area).order_by(Article.number)
    return render_template('db_area_list.html', articles=articles)


# обработчик удаления записи
@app.route('/database/<int:id>/del')
def post_del(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/database')
    except:
        return "При удалении статьи произошла ошибка"


# обработчик редактирования записи
@app.route('/database/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    article = Article.query.get_or_404(id)
    if request.method == 'POST':
        article.number = null_check(request.form['number'])
        article.title = null_check(request.form['title'])
        article.intro = null_check(request.form['intro'])
        article.inbound = request.form['inbound']
        article.outbound = request.form['outbound']
        try:
            db.session.commit()
            return redirect('/database')
        except:
            return "При обновлении статьи произошла ошибка"
    else:
        return render_template('db_update.html', article=article)


@app.route('/about')
def about():
    return render_template('about.html')


# админка
# @app.route('/db-edit', methods=['POST', 'GET'])
# def dbedit():
#     if request.method == 'POST':
#         area = null_check(request.form['area'])
#         number = null_check(request.form['number'])
#         title = null_check(request.form['title'])
#         intro = null_check(request.form['intro'])
#         inbound = request.form['inbound']
#         outbound = request.form['outbound']
#         article = Article(area=area, number=number, title=title, intro=intro, inbound=inbound, outbound=outbound)
#
#         try:
#             db.session.add(article)
#             db.session.commit()
#             return redirect('/db-edit')
#         except:
#             return "При добавлении статьи произошла ошибка"
#     else:
#         return render_template('db-edit.html')


# @app.route('/db-all')
# def db_all():
#     articles = Article.query.order_by(Article.id.desc()).all()
#     return render_template('db_area_list_full.html', articles=articles)

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        global wid_output  # to pass it to another route
        wid_output = request.form['birthday']
        return redirect('/result')
    else:
        try:
            wid_output = None
            os.remove("static/destiny_matrix.pdf")
        except:
            pass
        return render_template('home.html')


@app.route('/database')
def database():
    return render_template('database.html')


@app.route('/result')
def result():
    try:
    # input data calculation
        a = int(wid_output.split("-")[2])  # input day
        b = int(wid_output.split("-")[1])  # input month
        c = int(wid_output.split("-")[0])  # year

        # if x > 22 then split and sum digits eg. 27 -> 2 + 7 = 9
        def n_rule(x):
            if x > 22:
                while x > 22:  # check whether input digit satisfy the rule until it meet the rule
                    x = sum([int(a) for a in str(x)])  # split and sum input integers
                else:
                    return x
            else:
                return x

        # matrix information
        a = n_rule(a)
        b = n_rule(b)
        c = n_rule(c)
        d = n_rule(a + b + c)
        i = n_rule(a + b + c + d)
        e = n_rule(a + b)
        f = n_rule(b + c)
        h = n_rule(c + d)
        g = n_rule(d + a)
        j = n_rule(a + i)
        k = n_rule(b + i)
        n = n_rule(d + i)
        m = n_rule(n + d)
        r = n_rule(i + c)
        p = n_rule(n + r)
        q = n_rule(p + r)
        o = n_rule(n + p)

        # additional information
        x3 = n_rule(n_rule(a + c) + n_rule(b + d))  # личное предназначение
        y3 = n_rule(n_rule(e + h) + n_rule(g + f))  # социальное
        z3 = n_rule(x3 + y3)  # духовное

        # Create Image
        with PilIMG.open("static/matrix_image.png") as im:
            draw = ImageDraw.Draw(im)

            class artboard():
                def white_big(self, string):
                    draw.text(self, str(string), anchor="mm", font=ImageFont.truetype("static/times.ttf", 22),
                              fill=(255, 255, 255))

                def white_small(self, string):
                    draw.text(self, str(string), anchor="mm", font=ImageFont.truetype("static/times.ttf", 20),
                              fill=(255, 255, 255))

                def black_big(self, string):
                    draw.text(self, str(string), anchor="mm", font=ImageFont.truetype("static/times.ttf", 22),
                              fill=(20, 20, 20))

                def black_small(self, string):
                    draw.text(self, str(string), anchor="mm", font=ImageFont.truetype("static/times.ttf", 20),
                              fill=(20, 20, 20))

            artboard.white_big((21, 275), a)
            artboard.white_big((275, 21), b)
            artboard.white_big((529, 275), c)
            artboard.white_big((275, 529), d)

            artboard.white_small((95, 275), j)
            artboard.white_small((275, 95), k)
            artboard.white_small((455, 275), r)
            artboard.white_small((275, 455), n)

            artboard.black_big((95, 95), e)
            artboard.black_big((455, 95), f)
            artboard.black_big((95, 455), g)
            artboard.black_big((455, 455), h)
            artboard.black_big((275, 275), i)

            artboard.black_small((275, 492), m)
            artboard.black_small((320, 410), o)
            artboard.black_small((365, 365), p)
            artboard.black_small((410, 320), q)

            artboard.black_big((112, 658), n_rule(b + d))
            artboard.black_big((112, 708), n_rule(a + c))
            artboard.black_big((226, 683), x3)
            artboard.black_big((324, 657), n_rule(g + f))
            artboard.black_big((325, 707), n_rule(e + h))
            artboard.black_big((437, 683), y3)
            artboard.black_big((410, 765), z3)

            byte_io = BytesIO()

            im.save(byte_io, 'PNG')
            encoded_img_data = base64.b64encode(byte_io.getvalue())
        #
        # # Create PDF
        #
        # Блок создания PDF

        class PDF(FPDF):
            def area_title(self, area_text_title):
                self.set_font('font_bd', '', 15)
                self.set_text_color(20, 20, 20)
                self.set_fill_color(200, 220, 255)
                self.cell(0, 20, area_text_title, align="C", border=True, fill=True)
                self.ln()

            def area_text(self, area_text_text):
                self.ln()
                self.set_font('font', '', 15)
                self.set_text_color(20, 20, 20)
                self.multi_cell(0, 20, area_text_text, align="L")

            def area_intro_text(self, area_intro_text):
                self.ln()
                self.set_font('font_bd', '', 15)
                self.set_text_color(20, 20, 20)
                self.multi_cell(0, 20, area_intro_text, align="L")

            def print_chapter(self, area_text_title, area_intro_text, area_text_text):
                self.add_page()
                self.area_title(area_text_title)
                self.area_intro_text(area_intro_text)
                self.area_text(area_text_text)

        pdf = PDF('P', 'pt', 'A4')  # 595, 841
        pdf.add_font('font', '', 'static/times.ttf')
        pdf.add_font('font_bd', '', 'static/timesbd.ttf')

        pdf.add_page()
        pdf.image("static/pdf_layout.svg", x=0, y=0, w=595)

        # Title
        pdf.set_font('font_bd', '', 52)
        pdf.set_text_color(64, 64, 64)
        pdf.text(94, 745, "Матрица Судьбы")

        # Text
        pdf.set_font('font', '', 18)
        pdf.set_text_color(35, 31, 32)
        pdf.text(178, 688, "Духовное предназначение")
        pdf.text(183, 547, "Личное")
        pdf.text(153, 569, "предназначение")
        pdf.text(331, 547, "Социальное")
        pdf.text(319, 569, "предназначение")

        # Numbers

        pdf.set_font('font', '', 18)  # White Big
        pdf.set_text_color(255, 255, 255)
        # a
        pdf.set_xy(99, 301)
        pdf.cell(1, 0, f"{a}", align="C")
        # b
        pdf.set_xy(297, 102)
        pdf.cell(1, 0, f"{b}", align="C")
        # c
        pdf.set_xy(496, 301)
        pdf.cell(1, 0, f"{c}", align="C")
        # d
        pdf.set_xy(297, 499)
        pdf.cell(1, 0, f"{d}", align="C")

        pdf.set_font('font', '', 18)  # Back Big
        pdf.set_text_color(31, 31, 31)
        # e
        pdf.set_xy(157, 160)
        pdf.cell(1, 0, f"{e}", align="C")
        # f
        pdf.set_xy(438, 160)
        pdf.cell(1, 0, f"{f}", align="C")
        # g
        pdf.set_xy(157, 441)
        pdf.cell(1, 0, f"{g}", align="C")
        # h
        pdf.set_xy(438, 441)
        pdf.cell(1, 0, f"{h}", align="C")
        # i
        pdf.set_xy(297, 301)
        pdf.cell(1, 0, f"{i}", align="C")

        pdf.set_font('font', '', 15)  # Black Small
        pdf.set_text_color(31, 31, 31)
        # m
        pdf.set_xy(297, 470)
        pdf.cell(1, 0, f"{m}", align="C")
        # o
        pdf.set_xy(332, 406)
        pdf.cell(1, 0, f"{o}", align="C")
        # p
        pdf.set_xy(367, 371)
        pdf.cell(1, 0, f"{p}", align="C")
        # q
        pdf.set_xy(402, 335)
        pdf.cell(1, 0, f"{q}", align="C")
        # n_rule(b + d)
        pdf.set_xy(170, 600)
        pdf.cell(1, 0, f"{n_rule(b + d)}", align="C")
        # n_rule(a + c)
        pdf.set_xy(170, 640)
        pdf.cell(1, 0, f"{n_rule(a + c)}", align="C")
        # x3
        pdf.set_xy(258, 620)
        pdf.cell(1, 0, f"{x3}", align="C")
        # n_rule(e + h)
        pdf.set_xy(336, 600)
        pdf.cell(1, 0, f"{n_rule(e + h)}", align="C")
        # n_rule(g + f)
        pdf.set_xy(336, 640)
        pdf.cell(1, 0, f"{n_rule(g + f)}", align="C")
        # y3
        pdf.set_xy(425, 620)
        pdf.cell(1, 0, f"{y3}", align="C")
        # z3
        pdf.set_xy(403, 684)
        pdf.cell(1, 0, f"{z3}", align="C")

        pdf.set_font('font', '', 15)  # White Small
        pdf.set_text_color(255, 255, 255)
        # n
        pdf.set_xy(297, 441)
        pdf.cell(1, 0, f"{n}", align="C")
        # j
        pdf.set_xy(157, 301)
        pdf.cell(1, 0, f"{j}", align="C")
        # k
        pdf.set_xy(297, 160)
        pdf.cell(1, 0, f"{k}", align="C")
        # r
        pdf.set_xy(438, 301)
        pdf.cell(1, 0, f"{r}", align="C")

        # текстовое описание r q p
        pdf.print_chapter("Линия денежнего канала",
                          f"Показывает, через какие сферы и таланты приходят деньги, что блокирует их приход",
                          f"Вход в денежный канал: {db_request('finance', r).number}\n{db_request('finance', r).title}\
                          \n\n{db_request('finance', r).inbound} \n\n{db_request('finance', r).intro}\
                          \n\nЦентр денежного канала: {db_request('finance', q).number}\n{db_request('finance', q).title}\
                          \n\n{db_request('finance', q).inbound} \n\n{db_request('finance', q).intro}\
                          \n\nВыход из денежного канала: {db_request('finance', p).number}\n{db_request('finance', p).title}\
                          \n\n{db_request('finance', p).outbound} \n\n{db_request('finance', p).intro}")

        pdf.output('static/destiny_matrix.pdf')

        return render_template('result.html', wid_output=z3, img_data=encoded_img_data.decode('utf-8'))
    except:
        return redirect('/')


# сохранить базу в csv
@app.route('/csv', methods=['GET', 'POST'])
def exportcsv():
    with open('static/dump.csv', 'w', newline='',  encoding='utf-8') as f:
        out = csv.writer(f, delimiter=";")  # lineterminator="\r"
        out.writerow(['id', 'area', 'number', 'title', 'intro', 'inbound', 'outbound'])

        for item in Article.query.all():
            out.writerow([item.id, item.area, item.number, item.title, item.intro, item.inbound, item.outbound])
    return redirect('static/dump.csv')


if __name__ == '__main__':
    app.run(debug=True)
