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

# --- MODELO DO PRODUTO (Atualizado com Preço Antigo) ---
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(500), nullable=False)
    preco = db.Column(db.String(20), nullable=False)
    preco_antigo = db.Column(db.String(20)) # <-- Nova Coluna
    img_url = db.Column(db.String(1000), nullable=False)
    link_afiliado = db.Column(db.String(1000), nullable=False)
    categoria = db.Column(db.String(100))

# --- ROTAS ---

@app.route('/')
def index():
    # Lógica de Filtro por Categoria
    cat = request.args.get('categoria')
    if cat:
        lista = Produto.query.filter_by(categoria=cat).order_by(Produto.id.desc()).all()
    else:
        lista = Produto.query.order_by(Produto.id.desc()).all()
    
    # Pegamos todas as categorias únicas para mostrar no menu
    categorias = db.session.query(Produto.categoria).distinct().all()
    categorias_limpas = [c[0] for c in categorias if c[0]]
    
    return render_template('index.html', produtos=lista, categorias=categorias_limpas)

@app.route('/admin-secreto-ofertas')
def admin():
    lista_de_produtos = Produto.query.order_by(Produto.id.desc()).all()
    return render_template('admin.html', produtos=lista_de_produtos)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    # Limpeza de preços (vírgula por ponto)
    p_atual = request.form['preco'].replace(',', '.')
    p_antigo = request.form['preco_antigo'].replace(',', '.')

    novo = Produto(
        nome=request.form['nome'],
        preco=p_atual,
        preco_antigo=p_antigo,
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
    db.session.delete(produto_para_deletar)
    db.session.commit()
    return redirect(url_for('admin'))

# --- APLICAÇÃO DAS MUDANÇAS ---
with app.app_context():
    # ATENÇÃO: Descomente a linha abaixo (tire o #) apenas para o PRÓXIMO push
    # para criar a nova coluna 'preco_antigo' no Render.
    #db.drop_all() 
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)