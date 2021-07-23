from flask import Flask, render_template, request, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask.helpers import flash
from flask_login import login_user, login_required, logout_user, current_user
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_manager
from sqlalchemy.sql import func
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' #caminho e nome do db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "mgsbmylgmomlmtysyesagthwtshggabhatl"
db = SQLAlchemy(app) # inicializa db com as configurações p/ o app

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return Usuarios.query.get(int(id))


#tabelas do db
class Usuarios(db.Model, UserMixin):
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(25), nullable=False)
    adress = db.Column("adress", db.String(25), nullable=False)
    cnpj = db.Column("cnpj", db.Integer, nullable=False)
    phone = db.Column("phone", db.Integer, nullable=False)
    email = db.Column("email", db.String(25), nullable=False)
    user = db.Column ("user", db.String(25), nullable=False)
    password = db.Column("password", db.String(300), nullable=False)
    categoria = db.Column("categoria", db.String(2), nullable=False)
    item = db.relationship('Pedidos')
    

    def __init__(self, name, adress, cnpj, phone, email, user, password, categoria):
        self.name = name
        self.adress = adress
        self.cnpj = cnpj
        self.phone = phone
        self.email = email
        self.user = user
        self.password = password
        self.categoria = categoria

class Pedidos(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    item = db.Column("item", db.String(100), nullable=False)
    quantidade = db.Column("quantidade", db.Integer, nullable=False)
    doado = db.Column("doado", db.Integer, default=0)
    faltando = db.Column("faltando", db.Integer)
    unidade = db.Column("unidade", db.String(100), nullable=False)
    data = db.Column(db.DateTime(timezone=True), default=func.now())
    instituicao = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    


    def __repr__(self):
        return '<Pedido %r>' % self.id

        


#class Instituicoes(db.Model, UserMixin):
#    _id = db.Column("id", db.Integer, primary_key=True)
#    name = db.Column("name", db.String(25), unique=True, nullable=False)
#    adress = db.Column("adress", db.String(25), nullable=False)
#    cnpj = db.Column("cnpj", db.Integer, unique=True, nullable=False)
#    phone = db.Column("phone", db.Integer, unique=True, nullable=False)
#    email = db.Column("email", db.String(25), unique=True, nullable=False)
#    password = db.Column("password", db.String(300), nullable=False)

#    def __init__(self, name, adress, cnpj, phone, email, password):
#        self.name = name
#        self.adress = adress
#        self.cnpj= cnpj
#        self.phone = phone
#        self.email = email
#        self.password = password

#homepage
@app.route("/", methods=["GET"])
def home():
    if request.method == "GET":
        return render_template("home.html") #html da página inicial

#página de boas vindas aos novos doadores
@app.route("/novo_doador", methods=["GET"])
@login_required
def novo_doador():
    if request.method == "GET":
        return render_template("novo_doador.html")

#página de boas vindas às novas instituições
@app.route("/nova_instituicao", methods=["GET"])
@login_required
def nova_instituicao():
    if request.method == "GET":
        return render_template("nova_instituicao.html")

#login
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        usuario = Usuarios.query.filter_by(email=email).first()
        if usuario:
            if check_password_hash(usuario.password, password):
                flash('Login efetuado com sucesso', category='success')
                # Mantém usuário logado até que algo interfira
                login_user(usuario, remember=True)
                if usuario.categoria == 'D':
                    return redirect('/home_doador')
                else:
                    return redirect('/home_instituicao')
            else:
                flash('Senha incorreta. Por favor, tente novamente.', category='error')
        # Caso não haja um email, retorna a mensagem
        else:
            flash('O email informado não está cadastrado.', category='error')
    return render_template("login.html", user=current_user)

#home do doador
@app.route("/home_doador", methods=["GET"])
@login_required
def home_doador():
    if request.method == "GET":
        return render_template("home_doador.html")

#home da instituicao
@app.route("/home_instituicao", methods=["GET"])
@login_required
def home_instituicao():
    if request.method == "GET":
        meus_pedidos=Pedidos.query.order_by(Pedidos.data).filter(Pedidos.instituicao==current_user.id).all()
        return render_template("home_instituicao.html", user=current_user, meus_pedidos=meus_pedidos)

#cadastro dos doadores"
@app.route("/cadastro_doador", methods=["POST", "GET"])
def cadastro_doador():
    if request.method == "POST":
        novo_doador = Usuarios(name=request.form['name'],
                               adress=" ",
                               cnpj=" ",
                               phone=" ",
                               email=request.form['email'],
                               user=request.form['user'],
                               password=generate_password_hash(request.form['password1'], method='sha256'),
                               categoria='D')
        try:
            db.session.add(novo_doador)
            db.session.commit()
            login_user(novo_doador, remember=True)
            flash("Cadastro efetuado!", category='success')
            return redirect('/novo_doador') #vai para a página pós cadastro do doador
        except SQLAlchemyError as e1:
            print(str(e1))
            db.session.rollback()
            return str(e1)
    else:
        return render_template("cadastro_doador.html") #html da página de cadastro do doador



#cadastro das instituições
@app.route("/cadastro_instituicao", methods=["POST", "GET"])
def cadastro_instituicao():
    if request.method == "POST":
        nova_instituicao = Usuarios(name=request.form['name'],
                                    adress=request.form['adress'],
                                    cnpj=request.form['cnpj'],
                                    phone=request.form['phone'],
                                    email=request.form['email'],
                                    user=" ",
                                    password=generate_password_hash(request.form['password1'], method='sha256'),
                                    categoria="I")
        try:
            db.session.add(nova_instituicao)
            db.session.commit()
            login_user(nova_instituicao, remember=True)
            flash("Cadastro efetuado!", category='success')
            return redirect('/nova_instituicao') #vai para a página pós cadastro da instituição
        except SQLAlchemyError as e2:
            print(str(e2))
            db.session.rollback()
            return str(e2)
    else:
        return render_template("cadastro_instituicao.html") #html da página de cadastro da instituicao

@app.route('/logout', methods=["GET"])
@login_required
def logout():
    if request.method == "GET":
        logout_user()
        return redirect('/')

@app.route('/publicar_pedido', methods=['POST', 'GET'])
@login_required
def publicar_pedido():
    if request.method == 'POST':
        novo_pedido = Pedidos(item=request.form['item'],
                              quantidade=request.form['quantidade'],
                              unidade=request.form['unidade'], 
                              instituicao = current_user.id, 
                              faltando = request.form['quantidade'])
        try:
            db.session.add(novo_pedido)
            db.session.commit()
            flash("Pedido criado com sucesso!", category='success')
            return redirect('/home_instituicao')
        except SQLAlchemyError as e3:
            print(str(e3))
            db.session.rollback()
            return str(e3)
    else:
        return render_template('home_instituicao.html', user=current_user)

@app.route('/apagar_pedido/<int:id>', methods=["GET"])
@login_required
def apagar_pedido(id):
    if request.method == "GET":
        pedido_apagado = Pedidos.query.get_or_404(id)

        try:
            db.session.delete(pedido_apagado)
            db.session.commit()
            return redirect('/home_instituicao')
        except SQLAlchemyError as e4:
            print(str(e4))
            db.session.rollback()
            return str(e4)

@app.route('/atualizar_pedido/<int:id>', methods=['GET', 'POST'])
@login_required
def atualizar_pedido(id):
    pedido = Pedidos.query.get_or_404(id)

    if request.method == 'POST':
        pedido = Pedidos(item=request.form['item'],
                              quantidade=request.form['quantidade'],
                              unidade=request.form['unidade'])

        try:
            db.session.commit()
            return redirect('/home_instituicao')
        except SQLAlchemyError as e5:
            print(str(e5))
            db.session.rollback()
            return str(e5)     
    else:
        return render_template('atualizar_pedido.html', pedido=pedido)           

@app.route('/todos_pedidos',methods=['GET'])
@login_required
def todos_pedidos():
    itens = Pedidos.query.all()

    return render_template("todos_pedidos.html",user=current_user,itens=itens)

@app.route('/doar-item', methods=['POST'])
@login_required
def doar_item():
    doacao = json.loads(request.data)
    itemId = doacao['itemId'] #pega o id do item associado ao botao
    qtd = doacao["qtd"]
    item = Pedidos.query.get(itemId) #encontra o item associado ao id
    if item: #se existe um item com aquele id...
#        db.session.delete(item)
#        db.session.commit()
        item.doado = item.doado + int(qtd)
        item.faltando = item.faltando - item.doado
        db.session.commit()

    return jsonify({}) #essa linha eh necessaria pra funcao funcionar    


if __name__ == "__main__":
    app.run(debug=True)