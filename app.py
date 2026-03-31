import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
database_url = os.environ.get('DATABASE_URL')

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ofertas.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELO DO PRODUTO (Limites Aumentados) ---
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(500), nullable=False)        # Aumentado para 500
    preco = db.Column(db.String(20), nullable=False)
    img_url = db.Column(db.String(1000), nullable=False)      # Aumentado para 1000
    link_afiliado = db.Column(db.String(1000), nullable=False) # Aumentado para 1000
    categoria = db.Column(db.String(100))

# --- ROTAS ---

@app.route('/')
def index():
    lista_de_produtos = Produto.query.all()
    return render_template('index.html', produtos=lista_de_produtos)

@app.route('/admin-secreto-ofertas')
def admin():
    lista_de_produtos = Produto.query.all()
    return render_template('admin.html', produtos=lista_de_produtos)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    # CORREÇÃO: Troca vírgula por ponto para não quebrar o cálculo do desconto
    preco_bruto = request.form['preco']
    preco_limpo = preco_bruto.replace(',', '.')

    novo = Produto(
        nome=request.form['nome'],
        preco=preco_limpo, 
        img_url=request.form['img_url'],
        link_afiliado=request.form['link_afiliado'],
        categoria=request.form['categoria']
    )
    db.session.add(novo)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/deletar/<int:id>')
def deletar(id):
    produto_para_deletar = Produto.query.get_or_404(id)
    try:
        db.session.delete(produto_para_deletar)
        db.session.commit()
        return redirect(url_for('admin'))
    except:
        return "Houve um problema ao deletar o produto."

# --- APLICAÇÃO DAS MUDANÇAS NO RENDER ---
with app.app_context():
    # ATENÇÃO: Descomente a linha abaixo (tire o #) apenas para o PRÓXIMO push.
    # Isso vai apagar o banco antigo e criar o novo com os espaços maiores.
    db.drop_all() 
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)