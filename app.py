import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ofertas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELO DO PRODUTO ---
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.String(20), nullable=False)
    img_url = db.Column(db.String(300), nullable=False)
    link_afiliado = db.Column(db.String(300), nullable=False)
    categoria = db.Column(db.String(50))

# --- ROTAS (A LÓGICA DO SITE) ---

# 1. Vitrine Pública: O que os seguidores veem
@app.route('/')
def index():
    lista_de_produtos = Produto.query.all()
    return render_template('index.html', produtos=lista_de_produtos)

# 2. Painel Admin: Onde você gerencia tudo (Link: /admin-secreto-ofertas)
@app.route('/admin-secreto-ofertas')
def admin():
    lista_de_produtos = Produto.query.all()
    return render_template('admin.html', produtos=lista_de_produtos)

# 3. Lógica para Adicionar: Recebe os dados do formulário no Admin
@app.route('/adicionar', methods=['POST'])
def adicionar():
    novo = Produto(
        nome=request.form['nome'],
        preco=request.form['preco'],
        img_url=request.form['img_url'],
        link_afiliado=request.form['link_afiliado'],
        categoria=request.form['categoria']
    )
    db.session.add(novo)
    db.session.commit()
    # Após adicionar, ele te joga de volta para o painel de controle
    return redirect(url_for('admin'))

# 4. Lógica para Deletar: Remove o produto e volta para o Admin
@app.route('/deletar/<int:id>')
def deletar(id):
    produto_para_deletar = Produto.query.get_or_404(id)
    try:
        db.session.delete(produto_para_deletar)
        db.session.commit()
        return redirect(url_for('admin'))
    except:
        return "Houve um problema ao deletar o produto."

# Cria o banco de dados e as tabelas (Importante para o Render)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)