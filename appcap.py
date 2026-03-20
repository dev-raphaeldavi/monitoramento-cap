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
if 'widget_busca' not in st.session_state: st.session_state.widget_busca = "" # Controlador do texto no campo

# Função mágica que zera a pesquisa ANTES do sistema carregar a nova página
def limpar_pesquisa():
    st.session_state.widget_busca = ""
    st.session_state.input_busca = ""

# 2. IDENTIDADE VISUAL E CSS CUSTOMIZADO BLINDADO
st.markdown("""
    <style>
    :root {
        --azul-escuro: #003366;
        --azul-claro: #00AEEF;
        --laranja: #F7941E;
        --laranja-escuro: #D46A00; 
        --verde-regular: #28A745;
        --vermelho-irregular: #FF4B4B;
        --fundo-card: #ffffff;
    }
    .stApp { background-color: #FFFFFF !important; }
    .block-container { padding-top: 2rem !important; padding-bottom: 1rem !important; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 98% !important; }
    header[data-testid="stHeader"] { background-color: transparent !important; }
    .stAppDeployButton { display: none !important; }
    [data-testid="collapsedControl"] svg { color: #000000 !important; fill: #000000 !important; stroke: #000000 !important; }
    [data-testid="collapsedControl"] { background-color: rgba(0,0,0,0.05) !important; border-radius: 5px; }
    .titulo-principal { color: var(--azul-escuro); font-size: 60px !important; font-weight: 900; margin-top: 0px !important; margin-bottom: 0px !important; padding-bottom: 0px !important; line-height: 1.1; }
    .subtitulo { color: var(--azul-claro); font-size: 30px !important; font-weight: 600; margin-top: 0px !important; margin-bottom: 10px !important; }
    
    @media (max-width: 768px) {
        .titulo-principal { font-size: 32px !important; text-align: center; }
        .subtitulo { font-size: 18px !important; text-align: center; margin-bottom: 20px !important; }
        .block-container { padding-top: 3.5rem !important; }
    }
    
    /* ==========================================================
       CSS BLINDADO: BOTÕES DA HOME (IDÊNTICOS AOS QUADRINHOS)
       ========================================================== */
    button[kind="primary"] {
        background: linear-gradient(135deg, #003366 0%, #001a33 100%) !important;
        border: none !important;
        border-left: 5px solid #00AEEF !important;
        border-radius: 10px !important;
        color: white !important;
        height: 140px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }
    button[kind="primary"] div[data-testid="stMarkdownContainer"] p {
        font-size: 26px !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        text-transform: uppercase !important;
        margin: 0 !important;
    }
    /* Hover leve: Clareia o azul e deixa a borda laranja, texto permanece branco */
    button[kind="primary"]:hover {
        transform: translateY(-3px) !important;
        background: linear-gradient(135deg, #004488 0%, #002244 100%) !important; 
        box-shadow: 0 8px 15px rgba(0,0,0,0.2) !important;
        border-left: 5px solid var(--laranja) !important; 
        color: white !important;
    }
    button[kind="primary"]:hover div[data-testid="stMarkdownContainer"] p {
        color: white !important;
    }
    /* Clique: Fica escuro */
    button[kind="primary"]:active, button[kind="primary"]:focus {
        background: linear-gradient(135deg, #001a33 0%, #000000 100%) !important; 
        border: none !important;
        border-left: 5px solid #00AEEF !important;
        box-shadow: inset 0 3px 5px rgba(0,0,0,0.5) !important;
        color: white !important;
    }

    /* Estilos Gerais (Barra Lateral e outros botões) */
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"],
    section[data-testid="stSidebar"] div[data-testid="stLinkButton"] > a {
        background-color: transparent !important;
        border: 1px solid var(--laranja-escuro) !important;
        color: var(--laranja-escuro) !important;
        border-radius: 4px !important;
        padding: 4px 8px !important;
        font-weight: 600;
        font-size: 13px !important;
        box-shadow: none !important;
        min-height: 32px !important;
        transition: 0.2s;
        text-decoration: none !important;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover,
    section[data-testid="stSidebar"] div[data-testid="stLinkButton"] > a:hover {
        border-color: var(--laranja) !important;
        color: var(--laranja) !important;
        background-color: rgba(247, 148, 30, 0.1) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stDownloadButton"] > button {
        background-color: transparent !important;
        border: 1px solid var(--laranja-escuro) !important;
        color: var(--laranja-escuro) !important;
        border-radius: 4px !important;
        padding: 4px 8px !important;
        font-weight: bold;
        font-size: 13px !important;
        transition: 0.2s;
    }
    section[data-testid="stSidebar"] div[data-testid="stDownloadButton"] > button:hover {
        border-color: var(--laranja) !important;
        background-color: var(--laranja) !important;
        color: #ffffff !important;
    }
    div.block-container div[data-testid="stDownloadButton"] > button {
        background-color: transparent !important;
        border: 1px solid #000000 !important;
        color: #000000 !important;
        border-radius: 4px !important;
        padding: 4px 8px !important;
        font-weight: bold;
        font-size: 13px !important;
        transition: 0.2s;
    }
    div.block-container div[data-testid="stDownloadButton"] > button:hover {
        background-color: var(--laranja) !important;
        border-color: var(--laranja) !important;
        color: #ffffff !important;
    }

    .metric-box { background: linear-gradient(135deg, #003366 0%, #001a33 100%); border-left: 5px solid #00AEEF; padding: 20px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; height: 140px; display: flex; flex-direction: column; justify-content: center; }
    .metric-title { font-size: 13px; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; color: #b3e6ff; letter-spacing: 0.5px; }
    .metric-value { font-size: 40px; font-weight: 900; margin: 0; line-height: 1; color: #ffffff; }
    .status-card { padding: 25px; border-radius: 12px; color: white; text-align: center; font-size: 1.8rem; font-weight: bold; margin-bottom: 25px; box-shadow: 0 6px 12px rgba(0,0,0,0.15); text-transform: uppercase; letter-spacing: 1px; }
    .status-regular { background-color: var(--verde-regular); }
    .status-irregular { background-color: var(--vermelho-irregular); }
    .info-card { background-color: var(--fundo-card); padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; border-left: 6px solid var(--azul-claro); box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 15px; height: 100%; }
    .info-label { color: var(--azul-escuro); font-size: 0.9rem; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }
    .info-value { color: #333333; font-size: 1.2rem; font-weight: 500; }
    .assinatura-app { position: fixed; bottom: 15px; left: 20px; color: #888888; font-size: 14px; font-weight: bold; z-index: 100; }
    </style>
""", unsafe_allow_html=True)

# 3. LINK DA PLANILHA
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQk-RTbvVDPlwxIJFaEKeR1WPRaNSFGioF8DIYD1_mQ-M6a7O20-7TXmx8fBAlDg/pub?gid=502195603&single=true&output=csv"

# 4. FUNÇÃO DE CARREGAMENTO E TRATAMENTO
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

# 5. GERADOR DE PDF CUSTOMIZADO
class PDFRelatorio(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8) 
        self.set_text_color(100, 100, 100)
        hora_recife = datetime.utcnow() - timedelta(hours=3)
        data_atual = hora_recife.strftime("%d/%m/%Y às %H:%M")
        self.cell(w=0, h=10, txt=f'Gerado em: {data_atual}   |   Página {self.page_no()}', align='C')

def gerar_pdf(df_filtrado, wbs_nome, subtitulo):
    df_filtrado = df_filtrado.copy()
    df_filtrado['TEMP_ESTACA'] = extrator_seguro(df_filtrado, ['ESTACA'])
    df_filtrado = df_filtrado.sort_values(by='TEMP_ESTACA')

    pdf = PDFRelatorio(orientation='L')
    pdf.add_page()
    
    try:
        pdf.image("logo.png", x=88.5, y=10, w=120)
    except:
        pass
    
    pdf.ln(45)
    
    def limpar_texto(texto):
        if pd.isna(texto) or str(texto).strip().upper() in ['NAN', 'NONE', '']: return "-"
        return str(texto).encode('latin-1', 'replace').decode('latin-1')

    titulo = f"Relatório de Captações - WBS: {wbs_nome}" if wbs_nome else "Relatório Geral de Captações"
    
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w=0, h=10, txt=limpar_texto(titulo), ln=1, align='C')
    
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w=0, h=6, txt=limpar_texto(f"Filtros: {subtitulo}"), ln=1, align='C')
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w=0, h=8, txt=limpar_texto(f"Total de pontos encontrados: {len(df_filtrado)}"), ln=1, align='C')
    pdf.ln(3)
    
    pdf.set_font("Helvetica", 'B', 8) 
    pdf.set_fill_color(0, 51, 102) 
    pdf.set_text_color(255, 255, 255)
    
    pdf.cell(w=12, h=8, txt="ID", border=1, fill=True, align='C')
    pdf.cell(w=50, h=8, txt="NOME DO PROPRIETARIO", border=1, fill=True, align='C')
    pdf.cell(w=35, h=8, txt="CONTRATO", border=1, fill=True, align='C')
    pdf.cell(w=22, h=8, txt="WBS", border=1, fill=True, align='C')
    pdf.cell(w=40, h=8, txt="ESTACA", border=1, fill=True, align='C')
    pdf.cell(w=30, h=8, txt="COORDENADAS", border=1, fill=True, align='C')
    pdf.cell(w=10, h=8, txt="ZONA", border=1, fill=True, align='C')
    pdf.cell(w=10, h=8, txt="LADO", border=1, fill=True, align='C')
    pdf.cell(w=68, h=8, txt="SITUACAO", border=1, fill=True, align='C')
    pdf.ln()

    pdf.set_font("Helvetica", '', 7)
    
    for _, row in df_filtrado.iterrows():
        if row.get('IS_REGULAR') == False:
            pdf.set_text_color(255, 0, 0)
        else:
            pdf.set_text_color(0, 0, 0)
            
        coord = f"{limpar_texto(row.get('LAT'))} / {limpar_texto(row.get('LONG'))}"
        wbs_atual = limpar_texto(row.get('ESTRUTURA (WBS)', row.get('ESTRUTURA', '')))
        estaca_atual = limpar_texto(row.get('ESTACA'))
        nome_prop = limpar_texto(row.get('PROPRIETÁRIO'))
        contrato_atual = limpar_texto(row.get('CONTRATO'))
        situacao = limpar_texto(row.get('SITUAÇÃO'))
        
        pdf.cell(w=12, h=8, txt=limpar_texto(row.get('ID'))[:6], border=1, align='C')
        pdf.cell(w=50, h=8, txt=nome_prop[:28], border=1)
        pdf.cell(w=35, h=8, txt=contrato_atual[:20], border=1, align='C')
        pdf.cell(w=22, h=8, txt=wbs_atual[:12], border=1, align='C')
        pdf.cell(w=40, h=8, txt=estaca_atual[:25], border=1, align='C')
        pdf.cell(w=30, h=8, txt=coord[:18], border=1, align='C')
        pdf.cell(w=10, h=8, txt=limpar_texto(row.get('ZONA'))[:4], border=1, align='C')
        pdf.cell(w=10, h=8, txt=limpar_texto(row.get('LADO'))[:4], border=1, align='C')
        pdf.cell(w=68, h=8, txt=situacao[:40], border=1, align='C')
        pdf.ln()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            pdf_bytes = f.read()
    os.remove(tmp.name)
    return pdf_bytes

# 6. CABEÇALHO DA INTERFACE
col_texto, col_logo = st.columns([1.8, 1]) 
with col_texto:
    titulo_header = "Monitoramento das Captações PISF"
    if st.session_state.eixo_selecionado and st.session_state.modo_exibicao == 'dashboard_eixo':
        titulo_header += f" - {st.session_state.eixo_selecionado.upper()}"
        
    st.markdown(f'<p class="titulo-principal">💧 {titulo_header}</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitulo">Sistema de Consulta e Fiscalização</p>', unsafe_allow_html=True)
with col_logo:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        pass
st.markdown("---")

if not df.empty:
    
    serie_sit = extrator_seguro(df, ['SITUAÇÃO', 'SITUACAO'])
    serie_eixo = extrator_seguro(df, ['EIXO'])
    serie_sistema = extrator_seguro(df, ['SISTEMA'])
    serie_locais = serie_eixo + " " + serie_sistema 

    mask_reg = df['IS_REGULAR'] == True
    mask_irreg = df['IS_REGULAR'] == False
    mask_operando = serie_sit.str.contains('OPERA', na=False)
    mask_inativas = serie_sit.str.contains('DESATI|NÃO INST|NAO INST', na=False)
    mask_agreste = serie_locais.str.contains('AGRESTE', na=False)
    mask_leste = serie_locais.str.contains('LESTE', na=False)
    mask_norte = serie_eixo.str.contains('NORTE', na=False)

    serie_placa = extrator_seguro(df, ['PLACA INSTALADA', 'PLACA'])
    mask_placa = serie_placa.str.contains('SIM|X|S', na=False)
    mask_padronizadas = df.apply(lambda r: str(r.get('OBSERVAÇÃO CPISF', r.get('OBSERVACAO CPISF', ''))).strip() == "Captação padronizada instalada.", axis=1)

    # MASCARA MATERIAL COMPRADO
    serie_material = extrator_seguro(df, ['MATERIAL COMPRADO', 'MATERIAL'])
    mask_material_sim = serie_material.str.contains('SIM|X|S', na=False)

    # 7. BARRA LATERAL (MENU E GERADOR DE RELATÓRIOS)
    with st.sidebar:
        
        if st.button("🏠 PONTOS PISF (EIXOS)", use_container_width=True, on_click=limpar_pesquisa):
            st.session_state.modo_exibicao = 'home'
            st.session_state.eixo_selecionado = None
            
        st.markdown("---")
        
        st.markdown(f"<h2 style='color: #ffa500; margin-bottom:5px; font-size: 18px;'>BUSCAR CAPTAÇÃO</h2>", unsafe_allow_html=True)
        tipo_busca = st.radio("Método de busca:", ["Por ID", "Por Proprietário", "Por Estrutura (WBS)"], label_visibility="collapsed")
        
        busca = st.text_input("Digite aqui e tecle ENTER:", key="widget_busca")
        if busca.strip() != "":
            st.session_state.input_busca = busca.strip()
            st.session_state.modo_exibicao = 'busca'
            st.session_state.eixo_selecionado = None
            
        st.markdown("---")
        
        if st.button("ABRIR PAINEL DE INDICADORES (GERAL)", use_container_width=True, on_click=limpar_pesquisa):
            st.session_state.modo_exibicao = 'dashboard'
            st.session_state.eixo_selecionado = None

        if st.button("PONTOS IRREGULARES POR ESTRUTURA", use_container_width=True, on_click=limpar_pesquisa):
            st.session_state.modo_exibicao = 'irregulares_wbs'
            
        if st.button("PONTOS COM PLACA INSTALADA", use_container_width=True, on_click=limpar_pesquisa):
            st.session_state.modo_exibicao = 'placas'
            
        if st.button("PONTOS COM INSTALAÇÃO PADRONIZADA", use_container_width=True, on_click=limpar_pesquisa):
            st.session_state.modo_exibicao = 'padronizadas'

        # ==========================================================
        # NOVO NOME DO BOTÃO
        # ==========================================================
        if st.button("MATERIAIS DISPONÍVEIS", use_container_width=True, on_click=limpar_pesquisa):
            st.session_state.modo_exibicao = 'materiais'
            
        st.markdown("---")
        
        st.markdown(f"<h2 style='color: #ffa500; margin-bottom:5px; font-size: 18px;'>FERRAMENTAS EXTERNAS</h2>", unsafe_allow_html=True)
        st.link_button("📝 EMISSOR DE TERMOS (NOVA GUIA)", "https://emitirtermo-rcykhrjdx7iakqzkexzxrp.streamlit.app/", use_container_width=True)
        
        st.markdown("---")
        
        st.markdown(f"<h2 style='color: #ffa500; margin-bottom:5px; font-size: 18px;'>CENTRAL DE RELATÓRIOS</h2>", unsafe_allow_html=True)
        
        with st.expander("Abrir Filtros de Relatório", expanded=False):
            wbs_relatorio = st.text_input("Estrutura (WBS) - Opcional:", placeholder="Deixe branco p/ GERAL")
            filtro_contrato = st.selectbox("Contrato:", ["Todos", "Com Contrato", "Sem Contrato"])
            filtro_operacao = st.selectbox("Situação:", ["Todas", "Em Operação", "Não Instalados/Desativados"])
            filtro_material = st.selectbox("Material Comprado:", ["Todos", "Sim", "Não"])
            
            if st.button("PROCESSAR E GERAR PDF", use_container_width=True):
                df_pdf = df.copy()
                
                if st.session_state.eixo_selecionado:
                    if st.session_state.eixo_selecionado == 'Leste': df_pdf = df_pdf[mask_leste]
                    elif st.session_state.eixo_selecionado == 'Norte': df_pdf = df_pdf[mask_norte]
                    elif st.session_state.eixo_selecionado == 'Ramal do Agreste': df_pdf = df_pdf[mask_agreste]

                if wbs_relatorio.strip() != "":
                    col_wbs = extrator_seguro(df_pdf, ['ESTRUTURA (WBS)', 'ESTRUTURA'])
                    df_pdf = df_pdf[col_wbs.str.contains(wbs_relatorio.strip(), case=False, na=False)]
                
                if filtro_contrato == "Com Contrato": df_pdf = df_pdf[df_pdf['IS_REGULAR'] == True]
                elif filtro_contrato == "Sem Contrato": df_pdf = df_pdf[df_pdf['IS_REGULAR'] == False]
                
                sit_pdf = extrator_seguro(df_pdf, ['SITUAÇÃO', 'SITUACAO'])
                if filtro_operacao == "Em Operação":
                    df_pdf = df_pdf[sit_pdf.str.contains('OPERA', na=False)]
                elif filtro_operacao == "Não Instalados/Desativados":
                    df_pdf = df_pdf[sit_pdf.str.contains('DESATI|NÃO INST|NAO INST', na=False)]

                mat_pdf = extrator_seguro(df_pdf, ['MATERIAL COMPRADO', 'MATERIAL'])
                if filtro_material == "Sim":
                    df_pdf = df_pdf[mat_pdf.str.contains('SIM|X|S', na=False)]
                elif filtro_material == "Não":
                    df_pdf = df_pdf[~mat_pdf.str.contains('SIM|X|S', na=False)]
                
                if df_pdf.empty:
                    st.error("Nenhum ponto encontrado com esses filtros.")
                else:
                    st.success(f"Pronto! {len(df_pdf)} pontos processados.")
                    
                    eixo_str = f"[{st.session_state.eixo_selecionado}] " if st.session_state.eixo_selecionado else ""
                    subtitulo = f"{eixo_str}Contrato: {filtro_contrato} | Operação: {filtro_operacao} | Material: {filtro_material} | Ordem: Estaca"
                    pdf_bytes = gerar_pdf(df_pdf, wbs_relatorio.strip(), subtitulo)
                    
                    st.download_button(
                        label=f"BAIXAR PDF",
                        data=pdf_bytes,
                        file_name=f"Relatorio_{'WBS_'+wbs_relatorio.strip() if wbs_relatorio.strip() else 'GERAL'}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        
        st.caption(f"<div style='margin-top:20px'>Base Total: **{len(df)} registros**</div>", unsafe_allow_html=True)
        st.markdown('<div class="assinatura-app">App por Raphael Davi - Versão 2.0</div>', unsafe_allow_html=True)

    def card_metrica(titulo, valor): return f'<div class="metric-box"><div class="metric-title">{titulo}</div><div class="metric-value">{valor}</div></div>'

    # ==========================================================
    # TELA 0: HOME
    # ==========================================================
    if st.session_state.modo_exibicao == 'home':
        st.markdown("<h2 style='text-align: center; color: #003366; margin-bottom: 40px;'>Selecione o EIXO para visualizar os indicadores:</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("EIXO NORTE", type="primary", use_container_width=True, on_click=limpar_pesquisa):
                st.session_state.eixo_selecionado = 'Norte'
                st.session_state.modo_exibicao = 'dashboard_eixo'
                st.rerun() 
                
        with col2:
            if st.button("EIXO LESTE", type="primary", use_container_width=True, on_click=limpar_pesquisa):
                st.session_state.eixo_selecionado = 'Leste'
                st.session_state.modo_exibicao = 'dashboard_eixo'
                st.rerun() 
                
        with col3:
            if st.button("RAMAL DO AGRESTE", type="primary", use_container_width=True, on_click=limpar_pesquisa):
                st.session_state.eixo_selecionado = 'Ramal do Agreste'
                st.session_state.modo_exibicao = 'dashboard_eixo'
                st.rerun() 

    # ==========================================================
    # TELA 1.1: DASHBOARD ESPECÍFICO DE UM EIXO
    # ==========================================================
    elif st.session_state.modo_exibicao == 'dashboard_eixo':
        eixo_str = st.session_state.eixo_selecionado
        st.markdown(f"<h2 style='color: #00AEEF;'>Painel de Indicadores - {eixo_str.upper()}</h2>", unsafe_allow_html=True)
        
        if eixo_str == 'Norte': df_eixo = df[mask_norte]
        elif eixo_str == 'Leste': df_eixo = df[mask_leste]
        else: df_eixo = df[mask_agreste]
        
        mask_reg_e = df_eixo['IS_REGULAR'] == True
        mask_irreg_e = df_eixo['IS_REGULAR'] == False
        
        serie_sit_e = extrator_seguro(df_eixo, ['SITUAÇÃO', 'SITUACAO'])
        mask_operando_e = serie_sit_e.str.contains('OPERA', na=False)
        mask_inativas_e = serie_sit_e.str.contains('DESATI|NÃO INST|NAO INST', na=False)
        
        serie_placa_e = extrator_seguro(df_eixo, ['PLACA INSTALADA', 'PLACA'])
        mask_placa_e = serie_placa_e.str.contains('SIM|X|S', na=False)
        
        mask_padronizadas_e = df_eixo.apply(lambda r: str(r.get('OBSERVAÇÃO CPISF', r.get('OBSERVACAO CPISF', ''))).strip() == "Captação padronizada instalada.", axis=1)

        colA, colB, colC = st.columns(3)
        with colA: st.markdown(card_metrica(f"QUANTIDADE DE PONTOS - {eixo_str.upper()}", len(df_eixo)), unsafe_allow_html=True)
        with colB: st.markdown(card_metrica("TOTAL COM CONTRATO", len(df_eixo[mask_reg_e])), unsafe_allow_html=True)
        with colC: st.markdown(card_metrica("TOTAL SEM CONTRATO", len(df_eixo[mask_irreg_e])), unsafe_allow_html=True)
        
        colD, colE, colF = st.columns(3)
        with colD: st.markdown(card_metrica("COM CONTRATO (OPERANDO)", len(df_eixo[mask_reg_e & mask_operando_e])), unsafe_allow_html=True)
        with colE: st.markdown(card_metrica("COM CONTRATO (NÃO INSTALADO)", len(df_eixo[mask_reg_e & mask_inativas_e])), unsafe_allow_html=True)
        with colF: st.markdown(card_metrica("SEM CONTRATO (OPERANDO)", len(df_eixo[mask_irreg_e & mask_operando_e])), unsafe_allow_html=True)
        
        colG, colH, colI = st.columns(3)
        with colG: st.markdown(card_metrica("SEM CONTRATO (DESATIVADO)", len(df_eixo[mask_irreg_e & mask_inativas_e])), unsafe_allow_html=True)
        with colH: st.markdown(card_metrica("CAPTAÇÕES COM PLACA INSTALADA", len(df_eixo[mask_placa_e])), unsafe_allow_html=True)
        with colI: st.markdown(card_metrica("CAPTAÇÕES PADRONIZADAS", len(df_eixo[mask_padronizadas_e])), unsafe_allow_html=True)

    # ==========================================================
    # TELA 1: DASHBOARD DE INDICADORES GERAIS
    # ==========================================================
    elif st.session_state.modo_exibicao == 'dashboard':
        st.markdown("<h2 style='color: #00AEEF;'>Painel Geral de Indicadores (Toda a Obra)</h2>", unsafe_allow_html=True)
        
        colA, colB, colC = st.columns(3)
        with colA: st.markdown(card_metrica("QUANTIDADE DE PONTOS - GERAL", len(df)), unsafe_allow_html=True)
        with colB: st.markdown(card_metrica("TOTAL COM CONTRATO", len(df[mask_reg])), unsafe_allow_html=True)
        with colC: st.markdown(card_metrica("TOTAL SEM CONTRATO", len(df[mask_irreg])), unsafe_allow_html=True)
        
        colD, colE, colF = st.columns(3)
        with colD: st.markdown(card_metrica("TOTAL COM CONTRATO (OPERANDO)", len(df[mask_reg & mask_operando])), unsafe_allow_html=True)
        with colE: st.markdown(card_metrica("TOTAL COM CONTRATO (NÃO INSTALADO)", len(df[mask_reg & mask_inativas])), unsafe_allow_html=True)
        with colF: st.markdown(card_metrica("TOTAL SEM CONTRATO (OPERANDO)", len(df[mask_irreg & mask_operando])), unsafe_allow_html=True)
        
        colG, colH, colI = st.columns(3)
        with colG: st.markdown(card_metrica("TOTAL SEM CONTRATO (DESATIVADO)", len(df[mask_irreg & mask_inativas])), unsafe_allow_html=True)
        with colH: st.markdown(card_metrica("CAPTAÇÕES COM PLACA INSTALADA", len(df[mask_placa])), unsafe_allow_html=True)
        with colI: st.markdown(card_metrica("CAPTAÇÕES PADRONIZADAS", len(df[mask_padronizadas])), unsafe_allow_html=True)
        
        colJ, colK, colL = st.columns(3)
        with colJ: st.markdown(card_metrica("TOTAL DE PONTOS EIXO NORTE", len(df[mask_norte])), unsafe_allow_html=True)
        with colK: st.markdown(card_metrica("TOTAL DE PONTOS EIXO LESTE", len(df[mask_leste])), unsafe_allow_html=True)
        with colL: st.markdown(card_metrica("TOTAL DE PONTOS RAMAL DO AGRESTE", len(df[mask_agreste])), unsafe_allow_html=True)

    # ==========================================================
    # TELA 2: TELA DE IRREGULARES POR WBS
    # ==========================================================
    elif st.session_state.modo_exibicao == 'irregulares_wbs':
        st.markdown("<h2 style='color: #FF4B4B;'>🚨 Monitor de Pontos Irregulares por Estrutura (WBS)</h2>", unsafe_allow_html=True)
        st.markdown('<p style="color: black;">Abaixo estão listadas todas as estruturas que possuem captações sem contrato. Clique no botão de download abaixo do quadro para gerar o relatório específico da WBS.</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        df_irregulares = df[mask_irreg].copy()
        
        if st.session_state.eixo_selecionado:
            if st.session_state.eixo_selecionado == 'Leste': df_irregulares = df_irregulares[mask_leste]
            elif st.session_state.eixo_selecionado == 'Norte': df_irregulares = df_irregulares[mask_norte]
            elif st.session_state.eixo_selecionado == 'Ramal do Agreste': df_irregulares = df_irregulares[mask_agreste]

        col_wbs_irreg = extrator_seguro(df_irregulares, ['ESTRUTURA (WBS)', 'ESTRUTURA'])
        df_irregulares['WBS_CLEAN'] = col_wbs_irreg
        contagem_wbs = df_irregulares['WBS_CLEAN'].value_counts()
        
        if contagem_wbs.empty:
            st.success("🎉 Excelente! Não há nenhum ponto irregular nesta seleção.")
        else:
            cols = st.columns(4)
            for i, (wbs_nome, qtde) in enumerate(contagem_wbs.items()):
                wbs_label = str(wbs_nome).strip()
                if wbs_label == "": wbs_label = "NÃO INFORMADA"
                
                with cols[i % 4]:
                    st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-title">WBS: {wbs_label}</div>
                            <div class="metric-value" style="font-size: 28px;">{qtde} Pontos</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    df_wbs_especifica = df_irregulares[df_irregulares['WBS_CLEAN'] == wbs_nome]
                    pdf_bytes_wbs = gerar_pdf(df_wbs_especifica, wbs_label, "Apenas Irregulares | Ordem: Estaca")
                    
                    st.download_button(
                        label=f"BAIXAR PDF",
                        data=pdf_bytes_wbs,
                        file_name=f"Irregulares_WBS_{wbs_label}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"dl_wbs_{i}"
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================================
    # TELA BOTOES ADICIONAIS: PLACAS
    # ==========================================================
    elif st.session_state.modo_exibicao == 'placas':
        st.markdown("<h2 style='color: #00AEEF;'>📋 Monitor de Pontos com Placa Instalada por Estrutura (WBS)</h2>", unsafe_allow_html=True)
        st.markdown('<p style="color: black;">Abaixo estão listadas todas as estruturas que possuem captações com placa instalada. Clique no botão de download abaixo do quadro para gerar o relatório específico da WBS.</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        df_placas = df[mask_placa].copy()
        
        if st.session_state.eixo_selecionado:
            if st.session_state.eixo_selecionado == 'Leste': df_placas = df_placas[mask_leste]
            elif st.session_state.eixo_selecionado == 'Norte': df_placas = df_placas[mask_norte]
            elif st.session_state.eixo_selecionado == 'Ramal do Agreste': df_placas = df_placas[mask_agreste]

        col_wbs_placas = extrator_seguro(df_placas, ['ESTRUTURA (WBS)', 'ESTRUTURA'])
        df_placas['WBS_CLEAN'] = col_wbs_placas
        contagem_wbs = df_placas['WBS_CLEAN'].value_counts()
        
        if contagem_wbs.empty:
            st.info("Nenhum ponto com placa instalada encontrado nesta seleção.")
        else:
            cols = st.columns(4)
            for i, (wbs_nome, qtde) in enumerate(contagem_wbs.items()):
                wbs_label = str(wbs_nome).strip()
                if wbs_label == "": wbs_label = "NÃO INFORMADA"
                
                with cols[i % 4]:
                    st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-title">WBS: {wbs_label}</div>
                            <div class="metric-value" style="font-size: 28px;">{qtde} Pontos</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    df_wbs_especifica = df_placas[df_placas['WBS_CLEAN'] == wbs_nome]
                    pdf_bytes_wbs = gerar_pdf(df_wbs_especifica, wbs_label, "Com Placa Instalada | Ordem: Estaca")
                    
                    st.download_button(
                        label=f"BAIXAR PDF",
                        data=pdf_bytes_wbs,
                        file_name=f"Placas_WBS_{wbs_label}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"dl_placa_wbs_{i}"
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================================
    # TELA BOTOES ADICIONAIS: PADRONIZADAS
    # ==========================================================
    elif st.session_state.modo_exibicao == 'padronizadas':
        st.markdown("<h2 style='color: #28A745;'>🛠️ Monitor de Captações Padronizadas por Estrutura (WBS)</h2>", unsafe_allow_html=True)
        st.markdown('<p style="color: black;">Abaixo estão listadas todas as estruturas que possuem captações com instalação padronizada. Clique no botão de download abaixo do quadro para gerar o relatório específico da WBS.</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        df_padrao = df[mask_padronizadas].copy()
        
        if st.session_state.eixo_selecionado:
            if st.session_state.eixo_selecionado == 'Leste': df_padrao = df_padrao[mask_leste]
            elif st.session_state.eixo_selecionado == 'Norte': df_padrao = df_padrao[mask_norte]
            elif st.session_state.eixo_selecionado == 'Ramal do Agreste': df_padrao = df_padrao[mask_agreste]

        col_wbs_padrao = extrator_seguro(df_padrao, ['ESTRUTURA (WBS)', 'ESTRUTURA'])
        df_padrao['WBS_CLEAN'] = col_wbs_padrao
        contagem_wbs = df_padrao['WBS_CLEAN'].value_counts()
        
        if contagem_wbs.empty:
            st.info("Nenhuma captação padronizada encontrada nesta seleção.")
        else:
            cols = st.columns(4)
            for i, (wbs_nome, qtde) in enumerate(contagem_wbs.items()):
                wbs_label = str(wbs_nome).strip()
                if wbs_label == "": wbs_label = "NÃO INFORMADA"
                
                with cols[i % 4]:
                    st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-title">WBS: {wbs_label}</div>
                            <div class="metric-value" style="font-size: 28px;">{qtde} Pontos</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    df_wbs_especifica = df_padrao[df_padrao['WBS_CLEAN'] == wbs_nome]
                    pdf_bytes_wbs = gerar_pdf(df_wbs_especifica, wbs_label, "Captações Padronizadas | Ordem: Estaca")
                    
                    st.download_button(
                        label=f"BAIXAR PDF",
                        data=pdf_bytes_wbs,
                        file_name=f"Padronizadas_WBS_{wbs_label}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"dl_padrao_wbs_{i}"
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================================
    # NOVO: TELA BOTOES ADICIONAIS: MATERIAIS DISPONÍVEIS
    # ==========================================================
    elif st.session_state.modo_exibicao == 'materiais':
        st.markdown("<h2 style='color: #F7941E;'>📦 Monitor de Materiais Disponíveis para Instalação (WBS)</h2>", unsafe_allow_html=True)
        st.markdown('<p style="color: black;">Abaixo estão as estruturas com quantitativo de materiais comprados. O sistema isola automaticamente os pontos que <b>já receberam a instalação padronizada</b>.<br>Clique no botão de download para gerar a lista <b>apenas dos pontos que possuem material disponível aguardando instalação</b>.</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        df_materiais = df.copy()
        if st.session_state.eixo_selecionado:
            if st.session_state.eixo_selecionado == 'Leste': df_materiais = df_materiais[mask_leste]
            elif st.session_state.eixo_selecionado == 'Norte': df_materiais = df_materiais[mask_norte]
            elif st.session_state.eixo_selecionado == 'Ramal do Agreste': df_materiais = df_materiais[mask_agreste]

        col_wbs_mat = extrator_seguro(df_materiais, ['ESTRUTURA (WBS)', 'ESTRUTURA'])
        df_materiais['WBS_CLEAN'] = col_wbs_mat
        
        wbs_unicos = df_materiais['WBS_CLEAN'].unique()
        wbs_unicos = [w for w in wbs_unicos if str(w).strip() != "" and str(w).strip().upper() != "NAN"]
        
        if len(wbs_unicos) == 0:
            st.info("Nenhuma estrutura encontrada nesta seleção.")
        else:
            cols = st.columns(4)
            for i, wbs_nome in enumerate(sorted(wbs_unicos)):
                # Filtra a estrutura específica
                df_wbs_especifica = df_materiais[df_materiais['WBS_CLEAN'] == wbs_nome]
                
                # Mascara 1: Tem material comprado?
                serie_mat_wbs = extrator_seguro(df_wbs_especifica, ['MATERIAL COMPRADO', 'MATERIAL'])
                mask_mat_sim = serie_mat_wbs.str.contains('SIM|X|S', na=False)
                
                # Mascara 2: Já é padronizada instalada?
                mask_pad_wbs = df_wbs_especifica.apply(lambda r: str(r.get('OBSERVAÇÃO CPISF', r.get('OBSERVACAO CPISF', ''))).strip() == "Captação padronizada instalada.", axis=1)
                
                # Lógica Combinada
                mask_disponivel = mask_mat_sim & (~mask_pad_wbs) # Tem material E NÃO tá instalada
                mask_instalado = mask_mat_sim & mask_pad_wbs     # Tem material E já tá instalada
                mask_sem_mat = ~mask_mat_sim                     # Não tem material comprado ainda
                
                qtd_disponivel = mask_disponivel.sum()
                qtd_instalado = mask_instalado.sum()
                qtd_sem = mask_sem_mat.sum()
                
                with cols[i % 4]:
                    st.markdown(f"""
                        <div class="metric-box" style="height: auto; padding: 15px; margin-bottom: 15px;">
                            <div class="metric-title" style="margin-bottom: 5px; font-size: 15px;">WBS: {wbs_nome}</div>
                            <div style="font-size: 16px; font-weight: bold; color: #28A745; margin-bottom: 3px;">✅ Disp. p/ Instalar: {qtd_disponivel}</div>
                            <div style="font-size: 14px; color: #A0A0A0; margin-bottom: 3px;">🛠️ Já Instalado: {qtd_instalado}</div>
                            <div style="font-size: 14px; color: #FF4B4B;">❌ Sem Material: {qtd_sem}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    df_wbs_down = df_wbs_especifica[mask_disponivel]
                    
                    if not df_wbs_down.empty:
                        pdf_bytes_wbs = gerar_pdf(df_wbs_down, wbs_nome, "Materiais Disponíveis (Aguardando Instalação) | Ordem: Estaca")
                        st.download_button(
                            label=f"BAIXAR PDF",
                            data=pdf_bytes_wbs,
                            file_name=f"Materiais_Disponiveis_WBS_{wbs_nome}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"dl_mat_wbs_{i}"
                        )
                    else:
                        st.button("NENHUM DISPONÍVEL", disabled=True, key=f"dl_mat_wbs_dis_{i}", use_container_width=True)
                        
                    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================================
    # TELA 3: MODO BUSCA TRADICIONAL
    # ==========================================================
    elif st.session_state.modo_exibicao == 'busca' and st.session_state.input_busca.strip() != "":
        termo = st.session_state.input_busca.strip()
        
        if tipo_busca == "Por ID": resultados = df[df['ID'].astype(str).str.strip() == termo]
        elif tipo_busca == "Por Proprietário":
            col_prop = extrator_seguro(df, ['PROPRIETÁRIO', 'PROPRIETARIO'])
            resultados = df[col_prop.str.contains(termo, case=False, na=False)]
        elif tipo_busca == "Por Estrutura (WBS)":
            col_wbs = extrator_seguro(df, ['ESTRUTURA (WBS)', 'ESTRUTURA'])
            resultados = df[col_wbs.str.contains(termo, case=False, na=False)]

        if resultados.empty:
            st.warning(f"⚠️ Nenhum registro encontrado para '{termo}'. Verifique a digitação.")
        else:
            if len(resultados) > 1:
                if tipo_busca == "Por Estrutura (WBS)":
                    qtd_com = len(resultados[resultados['IS_REGULAR'] == True])
                    qtd_sem = len(resultados[resultados['IS_REGULAR'] == False])
                    col_sit_res = extrator_seguro(resultados, ['SITUAÇÃO', 'SITUACAO'])
                    qtd_op = len(resultados[col_sit_res.str.contains('OPERA', na=False)])
                    st.info(f"🔍 Encontramos **{len(resultados)}** pontos correspondentes ({qtd_com} COM CONTRATO, {qtd_sem} SEM CONTRATO E {qtd_op} EM OPERAÇÃO). Selecione uma na lista abaixo:")
                else:
                    st.info(f"🔍 Encontramos **{len(resultados)}** pontos correspondentes. Selecione uma na lista abaixo:")
                    
                opcoes_lista = [(idx, f"ID: {row.get('ID', '-')} | Nome: {row.get('PROPRIETÁRIO', '-')} | WBS: {row.get('ESTRUTURA (WBS)', '-')}") for idx, row in resultados.iterrows()]
                escolha = st.selectbox("Lista de Resultados:", opcoes_lista, format_func=lambda x: x[1])
                ponto = resultados.loc[escolha[0]]
            else:
                ponto = resultados.iloc[0]
                if tipo_busca != "Por ID": st.success("✅ Apenas 1 ponto encontrado! Mostrando detalhes abaixo.")

            st.markdown("---")
            is_regular = ponto['IS_REGULAR']
            num_contrato = str(ponto.get('CONTRATO', '')).strip().upper()
            termos_invalidos = ['NAN', 'NÃO ID.', 'NAO ID.', 'NÃO IDENTIFICADO', 'NENHUM', 'NONE', '']

            if is_regular:
                texto_contrato = num_contrato if num_contrato not in termos_invalidos else "Válido"
                st.markdown(f'<div class="status-card status-regular">✅ REGULAR <br><span style="font-size: 1.2rem;">Contrato: {texto_contrato}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-card status-irregular">❌ IRREGULAR <br><span style="font-size: 1.2rem;">Situação: Sem Contrato Regularizado</span></div>', unsafe_allow_html=True)

            def criar_card(label, valor):
                if pd.isna(valor) or str(valor).strip().upper() in ['NAN', 'NONE', '']: valor = "Não informado"
                return f'<div class="info-card"><div class="info-label">{label}</div><div class="info-value">{valor}</div></div>'

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(criar_card("Proprietário", ponto.get('PROPRIETÁRIO')), unsafe_allow_html=True)
                st.markdown(criar_card("Situação Operacional", ponto.get('SITUAÇÃO')), unsafe_allow_html=True)
                st.markdown(criar_card("Uso da Água", ponto.get('USO DA ÁGUA')), unsafe_allow_html=True)
                st.markdown(criar_card("Vazão Estimada (m³/mês)", ponto.get('VAZÃO ESTIMADA (M3/MÊS)')), unsafe_allow_html=True)
            with col2:
                st.markdown(criar_card("Estrutura (WBS)", ponto.get('ESTRUTURA (WBS)')), unsafe_allow_html=True)
                st.markdown(criar_card("Localização (Estaca)", ponto.get('ESTACA')), unsafe_allow_html=True)
                st.markdown(criar_card("Eixo / Lado / Zona", f"{str(ponto.get('EIXO')).replace('nan', '-')} / {str(ponto.get('LADO')).replace('nan', '-')} / {str(ponto.get('ZONA')).replace('nan', '-')}"), unsafe_allow_html=True)
                st.markdown(criar_card("Coordenadas", f"Lat: {ponto.get('LAT')} <br> Long: {ponto.get('LONG')}"), unsafe_allow_html=True)
            with col3:
                st.markdown(criar_card("Município", ponto.get('MUNICÍPIO')), unsafe_allow_html=True)
                st.markdown(criar_card("Sistema", ponto.get('SISTEMA')), unsafe_allow_html=True)
                st.markdown(criar_card("Placa Instalada?", ponto.get('PLACA INSTALADA')), unsafe_allow_html=True)
                st.markdown(criar_card("Material Comprado", ponto.get('MATERIAL COMPRADO')), unsafe_allow_html=True)

            st.markdown(criar_card("Observação CPISF", ponto.get('OBSERVAÇÃO CPISF', ponto.get('OBSERVACAO CPISF'))), unsafe_allow_html=True)

else:
    st.info("🔄 Carregando dados do servidor Google Drive...")
