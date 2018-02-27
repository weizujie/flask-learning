"""
唯一 URL / 重定向行为:
Flask 的 URL 规则基于 Werkzeug 的路由模块。这个模块背后的思想是基于 Apache 以及更早的 HTTP 服务器主张的先例，保证优雅且唯一的 URL。
就是访问一个结尾不带斜线的URL会被flask重定向到带斜线的规范URL去；
优点：有助于避免搜索引擎索引同一个页面两次。
所以...能带斜线就尽量带

jinja2中的条件语句：{%if xxxx%}...{% else%}...{% endif %}
如果计算结果为Ture则渲染if和else之间的值，如果计算结果为false，则渲染else和endif之间的值(狗书P36)
"""

from flask import Flask, request, make_response, redirect, render_template, url_for, session, flash, current_app
from flask.ext.script import Manager, Shell
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField # 导入需要使用的，WTFroms支持的HTML标准字段
from wtforms.validators import Required # 验证函数，确保字段不为空
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.mail import Mail, Message
# from flask_mail import Mail, Message
from threading import Thread
import os

basedir = os.path.abspath(os.path.dirname(__file__)) # 获取当前路径，用于后面指定数据库文件路径
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string' # 设置秘钥，防止表单受到CSRF攻击
# 程序使用数据库的URL必须保存到Flask配置对象的SQLALCHEMY_DATABASE_URI键
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite') # 配置数据库URL到SQLALCHEMY_DATABASE_URI键中
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True # 配置SQLALCHEMY_COMMIT_ON_TEARDWON键，每次请求结束之后都会自动提交数据库中的变动
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # 狗书里没写，这个要自己加...
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)     #初始化应用程序和数据库
manager.add_command('db', MigrateCommand)     #将MigrateCommand类附加到Flask-Script的manager对象上

app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '13737294987@163.com'  # os.environ.get(xx)
app.config['MAIL_PASSWORD'] = 'asdasdasd0'  # 这里使用的是163的授权码 不是登录实际密码
# 这里的MAIL_USERNAME 为你的gmail邮箱
# 这里的MAIL_PASSWORD 为你的gmail密码，这是你的实际密码，
# 就是你登录gmail邮箱时用的密码，这和国内邮箱是有区别的
app.config['MAIL_DEBUG'] = True
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '163.com'
app.config['FLASKY_MAIL_SENDER'] = '13737294987@163.com'
app.config['FLASKY_ADMIN'] = '13737294987@163.com'

mail = Mail(app)

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

@app.route('/bad/')
def bad_request():
    return 'Bad Request', 302

@app.route('/response/')
def response():
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    return response

@app.route('/redirect/')
def redirect_text():
    return redirect('http://127.0.0.1:5000/')

@app.route('/template')
def template_index():
    return render_template('index.html')

@app.route('/template/user/')
def template_user():
    name = None
    return render_template('user_1.html', name=name)

@app.route('/template/bootstrap/<name>')
def bootstap_use(name):
    return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/urlfor/')
def urlfor_use():
    return url_for('index', name='panghu', page=2, _external=True)
    # 返回http://127.0.0.1:5000/?name=panghu&page=2

@app.route('/datetime/')
def use_datetime():
    return render_template('datetime.html', current_time=datetime.utcnow())

class FlaskForm(FlaskForm):
    name = StringField('what is your name?', validators=[Required()]) # 用户可以输入内容的文本框，值被name变量接收
    submit = SubmitField('Submit') # 提交按钮


@app.route('/wtf/', methods=['GET', 'POST']) # 告诉Flask做URL映射中把这个视图函数注册为GET和POST请求的处理程序
def wtf():
    name = None
    form = FlaskForm()
    if form.validate_on_submit(): # 如果输入的数据验证通过，validate_on_submit()方法返回True
        name = form.name.data # 赋值给局部变量
        form.name.data = ' ' # 将表单字段清空
    return render_template('wtf.html', form=form, name=name) # 渲染模板，带有变量name的值


"""
输入name之后再刷新网页，浏览器会重新发送之前已经发送过的最后一个请求，我们最后一次发送的请求是包含表单数据的POST请求，所以刷新页面之后
会继续提交表单。程序可以把数据存储在用户会话中，在请求之间‘记住’数据。
我们使用redirect重定向到wtf1这个页面，所以就不会有那个莫名其妙的警告了
"""
# 在上面一个版本中，局部变量name用户存储用户在表单输入的名字。这个变量现在保存在用户会话中，即session['name']
@app.route('/wtf1/', methods=['GET', 'POST'])
def wtf1():
    form = FlaskForm()
    if form.validate_on_submit():           # 如果表单中有数据则传到session['name']里保存
        session['name'] = form.name.data
        # print(session['name'])
        return redirect(url_for('wtf1'))  # 保存到session['name']后重定向
    return render_template('wtf.html', form=form, name=session.get('name'))
    # session.get('name')直接从会话中读取到键的异常情况，因为对于不存在的键，get()会返回默认值None

# 使用flash，当用户提交了错误的登录表单后，提示消息
# 还要在模板里渲染 base.html 下面
@app.route('/flash/', methods=['GET','POST'])
def test_flash():
    form = FlaskForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Look like you have change your name!')
        else:
            flash('Welcome %s' % session['name'])
        session['name'] = form.name.data
        return redirect(url_for('test_flash'))
    return render_template('wtf.html', form=form, name=session.get('name'))

# 定义Role和User模型
class Role(db.Model):
    __tablename__ = 'roles'  # 定义数据库中使用的表名
    id = db.Column(db.Integer, primary_key=True)  # 模型属性，被定义为db.Column类的实例
    name = db.Column(db.String(64), unique=True)  # 模型属性，uinque=True表示这一列不允许出现重复的值

    def __repr__(self):  # 定义__repr__()方法，返回一个具有可读性的字符串表示的模型，可在调试和测试时使用
        return '<Role %r>' % self.name

    #  表示两个模型间的关系，backref定义反向关系, 添加lazy='dynamic'参数从而禁止自动执行查询
    users = db.relationship('User', backref='role', lazy='dynamic')  #



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)  # index=True表示为这列创建索引，提升查询效率

    def __repr__(self):
        return '<User %r>' % self.username

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 定义外键，说明该列的值是roles表中行的id值

# 在视图函数中操作数据库
@app.route('/sujuku/', methods=['GET', 'POST'])
def sujuku():
    form = FlaskForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('sujuku'))
    return render_template('sujuku.html', form=form, name=session.get('name'), known=session.get('known', False))

# 回调函数
def make_shell_context():
    return dict(app=app)
manager.add_command("shell", Shell(make_context=make_shell_context))


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])

    msg.body=render_template(template+'.txt',**kwargs)
    msg.html=render_template(template+'.html',**kwargs)

    mail.send(msg)
    # 发送邮件
    #thr = Thread(target=send_async_email,args=[app,msg])
    #thr.start()
    #return thr


@app.route('/sendemail/', methods=['POST', 'GET'])
def sendemail():
    form = FlaskForm()
    if form.validate_on_submit():
        user = form.name.data
        session['known'] = True
        if app.config['FLASKY_ADMIN']:
            send_email([app.config['FLASKY_ADMIN'], '13737294987@163.com'], 'New User',
                       'mail/new_user', user=user)
        session['name'] = form.name.data
        return redirect(url_for('sendemail'))
    return render_template('sujuku.html', form=form, name=session.get('name'),
                           known=session.get('known', False))

if __name__ == '__main__':
    manager.run()
