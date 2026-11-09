import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

conn = sqlite3.connect('votacao.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, nome TEXT, email TEXT UNIQUE, senha TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS propostas (id INTEGER PRIMARY KEY, titulo TEXT, descricao TEXT, autor_id INTEGER, data TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS votos (id INTEGER PRIMARY KEY, usuario_id INTEGER, proposta_id INTEGER, voto TEXT, UNIQUE(usuario_id, proposta_id))''')
conn.commit()

def hash_senha(s): return hashlib.sha256(s.encode()).hexdigest()
if 'uid' not in st.session_state: st.session_state.uid = None

st.set_page_config(page_title="Votação de Leis", page_icon="⚖️")
st.title("⚖️ Votação de Leis - 2D e 2E")
menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro de Usuário", "Propostas", "Nova Proposta", "Sair"])

if menu == "Cadastro de Usuário":
    st.header("Cadastro")
    nome = st.text_input("Nome"); email = st.text_input("Email"); senha = st.text_input("Senha", type="password")
    if st.button("Cadastrar"):
        try:
            c.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)", (nome,email,hash_senha(senha))); conn.commit(); st.success("Cadastrado! Vá para Login.")
        except: st.error("Email já existe!")

elif menu == "Login":
    st.header("Login")
    email = st.text_input("Email"); senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        c.execute("SELECT id,nome FROM usuarios WHERE email=? AND senha=?", (email, hash_senha(senha))); u = c.fetchone()
        if u: st.session_state.uid = u[0]; st.session_state.nome = u[1]; st.success(f"Bem-vindo, {u[1]}! Vá em Propostas")
        else: st.error("Login inválido")

elif menu == "Propostas":
    if not st.session_state.uid: st.warning("Faça login primeiro")
    else:
        st.header("Propostas"); c.execute("SELECT p.id,p.titulo,p.descricao,u.nome,p.data FROM propostas p JOIN usuarios u ON p.autor_id=u.id ORDER BY p.id DESC")
        for id,tit,desc,autor,data in c.fetchall():
            c.execute("SELECT COUNT(*) FROM votos WHERE proposta_id=? AND voto='favor'", (id,)); fav = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM votos WHERE proposta_id=? AND voto='contra'", (id,)); contra = c.fetchone()[0]
            c.execute("SELECT voto FROM votos WHERE proposta_id=? AND usuario_id=?", (id, st.session_state.uid)); meu = c.fetchone()
            with st.container(border=True):
                st.subheader(tit); st.write(desc); st.caption(f"Autor: {autor} | {data}"); st.write(f"✅ {fav} a favor | ❌ {contra} contra")
                if not meu:
                    col1,col2 = st.columns(2)
                    if col1.button("A Favor", key=f"f{id}"): c.execute("INSERT INTO votos VALUES (NULL,?,?,?)", (st.session_state.uid,id,'favor')); conn.commit(); st.rerun()
                    if col2.button("Contra", key=f"c{id}"): c.execute("INSERT INTO votos VALUES (NULL,?,?,?)", (st.session_state.uid,id,'contra')); conn.commit(); st.rerun()
                else: st.info(f"Você votou: {meu[0]}")

elif menu == "Nova Proposta":
    if not st.session_state.uid: st.warning("Faça login primeiro")
    else:
        st.header("Nova Proposta"); tit = st.text_input("Título"); desc = st.text_area("Descrição")
        if st.button("Cadastrar Proposta"): c.execute("INSERT INTO propostas VALUES (NULL,?,?,?,?)", (tit,desc,st.session_state.uid,datetime.now().strftime("%d/%m/%Y"))); conn.commit(); st.success("Proposta cadastrada!")

elif menu == "Sair": st.session_state.uid = None; st.success("Deslogado")
