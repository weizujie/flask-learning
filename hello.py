from flask import Flask, request, make_response, redirect, render_template, url_for
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField # 导入需要使用的，WTFroms支持的HTML标准字段
from wtforms.validators import Required # 验证函数，确保字段不为空
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return '<h1>Hello, world!</h1>' \
           '<h2>Your browser is %s</h2>' % user_agent
    # return url_for('index', _external=True) 返回绝对地址:http://127.0.0.1:5000/
    # 如果不加_external=Ture 则返回 /
    # 一般返回相对地址就足够了，如果要生成浏览器之外使用的链接，则必须使用绝对地址

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, %s' % name

@app.route('/bad')
def bad_request():
    return 'Bad Request', 302

@app.route('/response')
def response():
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    return response

@app.route('/redirect')
def redirect_text():
    return redirect('http://127.0.0.1:5000/')

@app.route('/template')
def template_index():
    return render_template('index.html')

@app.route('/template/user/<name>')
def template_user(name=None):
    return render_template('user_1.html', name=name)

@app.route('/template/bootstrap/<name>')
def bootstap_use(name):
    return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/urlfor')
def urlfor_use():
    return url_for('index', name='panghu', page=2, _external=True)
    # 返回http://127.0.0.1:5000/?name=panghu&page=2

@app.route('/datetime')
def use_datetime():
    return render_template('datetime.html', current_time=datetime.utcnow())

class NameForm(Form):
    name = StringField('what is your name?', validators=[Required()]) # 用户可以输入内容的文本框，值被name变量接收
    submit = SubmitField('Submit') # 提交按钮

@app.route('/wtf', methods=['GET', 'POST']) # 告诉Flask做URL映射中把这个视图函数注册为GET和POST请求的处理程序
def wtf():
    name = None
    form = NameForm()
    if form.validate_on_submit(): # 如果输入的数据验证通过，validate_on_submit()方法返回True
        name = form.name.data # 赋值给局部变量
        form.name.data = ' ' # 将表单字段清空
    return render_template('wtf.html', form=form, name=name) # 渲染模板，带有变量name的值


if __name__ == '__main__':
    manager.run()
