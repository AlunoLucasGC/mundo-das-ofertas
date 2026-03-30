import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# Aqui dizemos que o banco será um arquivo chamado 'ofertas.db' dentro da pasta do projeto.
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ofertas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- O MODELO DO PRODUTO (A "Planta" da tabela) ---
# Isso cria a estrutura da tabela no banco de dados.
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True) # ID único para cada produto
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.String(20), nullable=False)
    img_url = db.Column(db.String(300), nullable=False) # Link da foto
    link_afiliado = db.Column(db.String(300), nullable=False) # Seu link do ML
    categoria = db.Column(db.String(50))

# --- AS PÁGINAS (ROTAS) ---

# Página 1: A vitrine que todo mundo vê
@app.route('/')
def index():
    # Pega todos os produtos que você cadastrou no banco
    lista_de_produtos = Produto.query.all()
    return render_template('index.html', produtos=lista_de_produtos)

# Página 2: O seu painel secreto para adicionar produtos
@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        # Pega o que você digitou no formulário
        novo = Produto(
            nome=request.form['nome'],
            preco=request.form['preco'],
            img_url=request.form['img_url'],
            link_afiliado=request.form['link_afiliado'],
            categoria=request.form['categoria']
        )
        db.session.add(novo) # Prepara para salvar
        db.session.commit()  # Salva de verdade no banco!
        return redirect(url_for('index')) # Volta para a vitrine
    
    return render_template('adicionar.html')

# Rota para deletar um produto específico
@app.route('/deletar/<int:id>')
def deletar(id):
    # Procura o produto pelo ID no banco de dados
    produto_para_deletar = Produto.query.get_or_404(id)
    
    try:
        db.session.delete(produto_para_deletar) # Marca para apagar
        db.session.commit() # Confirma a exclusão
        return redirect(url_for('index')) # Volta para a página inicial
    except:
        return "Houve um problema ao deletar o produto."

# Esse trecho cria o arquivo do banco de dados na primeira vez que você rodar
# Isso garante que as tabelas sejam criadas mesmo usando Gunicorn no Render
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)