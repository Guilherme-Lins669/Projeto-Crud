from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

# CONFIGURAÇÃO DO APP
app = Flask(__name__)

# BANCO DE DADOS
def get_db_connection():
    conn = sqlite3.connect('tarefas.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            data_criacao TEXT,
            data_vencimento TEXT,
            prioridade TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()


# ROTAS

# LISTAR TAREFAS (ORDENADAS POR PRIORIDADE)
@app.route('/')
def index():
    conn = get_db_connection()
    tarefas = conn.execute('''
        SELECT * FROM tarefas
        ORDER BY 
            CASE prioridade
                WHEN 'Alta' THEN 1
                WHEN 'Média' THEN 2
                WHEN 'Baixa' THEN 3
            END
    ''').fetchall()
    conn.close()
    return render_template('index.html', tarefas=tarefas)

# ADICIONAR TAREFA
@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        data_vencimento = request.form['data_vencimento']
        prioridade = request.form['prioridade']

        if titulo:
            conn = get_db_connection()
            conn.execute('INSERT INTO tarefas (titulo, descricao, data_criacao, data_vencimento, prioridade, status) VALUES (?, ?, ?, ?, ?, ?)',
                         (titulo, descricao, datetime.now(), data_vencimento, prioridade, 'Pendente'))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('add.html')

# EDITAR TAREFA
@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    tarefa = conn.execute('SELECT * FROM tarefas WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        data_vencimento = request.form['data_vencimento']
        prioridade = request.form['prioridade']
        status = request.form['status']

        conn.execute('UPDATE tarefas SET titulo=?, descricao=?, data_vencimento=?, prioridade=?, status=? WHERE id=?',
                     (titulo, descricao, data_vencimento, prioridade, status, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', tarefa=tarefa)

# EXCLUIR TAREFA
@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tarefas WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# EXECUÇÃO
if __name__ == '__main__':
    app.run(debug=True)
