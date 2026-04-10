import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import os
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO DA PÁGINA E CONTROLE DE ESTADOS
st.set_page_config(page_title="Monitor de Captações PISF", page_icon="💧", layout="wide", initial_sidebar_state="expanded")

if 'modo_exibicao' not in st.session_state: st.session_state.modo_exibicao = 'home' 
if 'eixo_selecionado' not in st.session_state: st.session_state.eixo_selecionado = None 
if 'input_busca' not in st.session_state: st.session_state.input_busca = ""

# Função para resetar navegação e busca
def resetar_para_home():
    st.session_state.modo_exibicao = 'home'
    st.session_state.eixo_selecionado = None
    st.session_state.input_busca = ""
    if 'widget_busca' in st.session_state:
        st.session_state.widget_busca = ""

# 2. IDENTIDADE VISUAL E CSS (BOTOES IGUAL AOS INDICADORES)
st.markdown("""
    <style>
    :root {
        --azul-escuro: #003366;
        --azul-claro: #00AEEF;
        --laranja: #F7941E;
    }
    .titulo-principal { color: var(--azul-escuro); font-size: 60px !important; font-weight: 900; line-height: 1.1; margin: 0; }
    .subtitulo { color: var(--azul-claro); font-size: 30px !important; font-weight: 600; margin-bottom: 10px; }

    /* ESTILIZAÇÃO DOS BOTÕES TIPO CARD (HOME) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #003366 0%, #001a33 100%) !important;
        border: none !important;
        border-left: 5px solid #00AEEF !important;
        border-radius: 10px !important;
        color: white !important;
        height: 140px !important;
        width: 100% !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"] p {
        font-size: 24px !important;
        font-weight: 900 !important;
        color: white !important;
        text-transform: uppercase;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-3px) !important;
        border-left: 5px solid var(--laranja) !important;
        background: linear-gradient(135deg, #004488 0%, #002244 100%) !important;
    }
    /* CORREÇÃO DO BUG DE "CONGELAR" ESCURO */
    div.stButton > button[kind="primary"]:focus:not(:active) {
        background: linear-gradient(135deg, #003366 0%, #001a33 100%) !important;
        color: white !important;
    }

    /* Cards de métricas (Indicadores) */
    .metric-box { background: linear-gradient(135deg, #003366 0%, #001a33 100%); border-left: 5px solid #00AEEF; padding: 20px; border-radius: 10px; color: white; text-align: center; height: 140px; display: flex; flex-direction: column; justify-content: center; margin-bottom: 20px; }
    .metric-title { font-size: 13px; font-weight: bold; color: #b3e6ff; text-transform: uppercase; }
    .metric-value { font-size: 40px; font-weight: 900; }
    </style>
""", unsafe_allow_html=True)

# 3. CABEÇALHO DINÂMICO
col_t, col_l = st.columns([2, 1])
with col_t:
    if st.session_state.modo_exibicao == 'dashboard_eixo' and st.session_state.eixo_selecionado:
        header_display = f"Monitoramento das Captações PISF - {st.session_state.eixo_selecionado.upper()}"
    else:
        header_display = "Monitoramento das Captações PISF"
    
    st.markdown(f'<p class="titulo-principal">💧 {header_display}</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitulo">Sistema de Consulta e Fiscalização</p>', unsafe_allow_html=True)

# 4. LINK DA PLANILHA ATUALIZADO (GOOGLE DRIVE CSV EXPORT)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1rDWdTJN_R_YngJ1OIdGWi2dULnEFtUGb/export?format=csv"

@st.cache_data(ttl=60)
def carregar_dados():
    try:
        df = pd.read_csv(URL_PLANILHA, dtype=str, sep=',', encoding='utf-8-sig', header=None)
        linha_cabecalho = 0
        for index, row in df.iterrows():
            if 'ID' in [str(x).strip().upper() for x in row.values]:
                linha_cabecalho = index
                break
        
        nomes_limpos = []
        for col in df.iloc[linha_cabecalho].values:
            nome = str(col).replace('\n', ' ').replace('\r', '') 
            nomes_limpos.append(' '.join(nome.split()).upper())
            
        df.columns = nomes_limpos
        df = df.iloc[linha_cabecalho + 1:].reset_index(drop=True)

        df = df[~df['ID'].astype(str).str.strip().str.upper().isin(['NAN', 'NONE', ''])]
        df = df[df['ID'].notna()]
        df = df[df['ID'].astype(str).str.strip() != ""]

        def classificar_regular(row):
            c_assinado = str(row.get('CONTRATO ASSINADO', '')).strip().upper()
            num_contrato = str(row.get('CONTRATO', '')).strip().upper()
            sem_contrato_x = str(row.get('SEM CONTRATO ASSINADO', row.get('SEM CONTRATO', ''))).strip().upper()
            termos_invalidos = ['NAN', 'NÃO ID.', 'NAO ID.', 'NÃO IDENTIFICADO', 'NENHUM', 'NONE', '']
            if sem_contrato_x == 'X': return False
            if c_assinado != 'X' and num_contrato in termos_invalidos: return False
            return True
        
        df['IS_REGULAR'] = df.apply(classificar_regular, axis=1)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a planilha: {e}")
        return pd.DataFrame()

df = carregar_dados()

def extrator_seguro(dataframe, nomes_possiveis):
    for nome in nomes_possiveis:
        if nome in dataframe.columns:
            coluna = dataframe[nome]
            if isinstance(coluna, pd.DataFrame): coluna = coluna.iloc[:, 0]
            return coluna.fillna('').astype(str).str.upper()
    return pd.Series([''] * len(dataframe), index=dataframe.index)

# 5. BARRA LATERAL
with st.sidebar:
    if st.button("🏠 PONTOS PISF (EIXOS)", use_container_width=True):
        resetar_para_home()
        st.rerun()
    
    st.markdown("---")
    busca = st.text_input("Buscar Captação:", key="widget_busca")
    if busca:
        st.session_state.input_busca = busca
        st.session_state.modo_exibicao = 'busca'
        st.session_state.eixo_selecionado = None

    if st.button("ABRIR PAINEL DE INDICADORES (GERAL)", use_container_width=True):
        st.session_state.modo_exibicao = 'dashboard_geral'
        st.session_state.eixo_selecionado = None
        st.rerun()

# 6. NAVEGAÇÃO DE TELAS
if st.session_state.modo_exibicao == 'home':
    st.markdown("<h3 style='text-align: center; color: #003366; margin-top: 40px;'>Selecione o EIXO para visualizar os indicadores:</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("EIXO NORTE", type="primary", use_container_width=True):
            st.session_state.eixo_selecionado = 'Norte'
            st.session_state.modo_exibicao = 'dashboard_eixo'
            st.rerun()
            
    with c2:
        if st.button("EIXO LESTE", type="primary", use_container_width=True):
            st.session_state.eixo_selecionado = 'Leste'
            st.session_state.modo_exibicao = 'dashboard_eixo'
            st.rerun()
            
    with c3:
        if st.button("RAMAL DO AGRESTE", type="primary", use_container_width=True):
            st.session_state.eixo_selecionado = 'Ramal do Agreste'
            st.session_state.modo_exibicao = 'dashboard_eixo'
            st.rerun()

elif st.session_state.modo_exibicao == 'dashboard_eixo':
    st.markdown(f"#### Indicadores Analíticos: {st.session_state.eixo_selecionado}")
    # Conteúdo das métricas do eixo aqui...

elif st.session_state.modo_exibicao == 'dashboard_geral':
    st.markdown("#### Painel Geral de Indicadores")
    # Conteúdo do painel geral aqui...

elif st.session_state.modo_exibicao == 'busca':
    st.markdown(f"#### Resultados para: {st.session_state.input_busca}")
    # Lógica de busca e exibição de detalhes aqui...
