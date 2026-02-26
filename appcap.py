import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import os
from datetime import datetime, timedelta, timezone

# 1. CONFIGURAÇÃO DA PÁGINA E CONTROLE DE ESTADOS
st.set_page_config(page_title="Monitor de Captações PISF", page_icon="💧", layout="wide", initial_sidebar_state="expanded")

if 'modo_exibicao' not in st.session_state: st.session_state.modo_exibicao = 'dashboard' 
if 'input_busca' not in st.session_state: st.session_state.input_busca = ""

# 2. IDENTIDADE VISUAL E CSS CUSTOMIZADO
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
    
    section[data-testid="stSidebar"] div.stButton > button {
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
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
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

# 4. FUNÇÃO CAÇADORA DE CABEÇALHOS E BLINDAGEM DE DADOS
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

# 5. GERADOR DE PDF CUSTOMIZADO (COM COR DINÂMICA E FUSO CORRETO)
class PDFRelatorio(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8) 
        
        # 🚨 CORREÇÃO DO FUSO HORÁRIO PARA RECIFE/PE (GMT-3)
        fuso_br = timezone(timedelta(hours=-3))
        data_atual = datetime.now(fuso_br).strftime("%d/%m/%Y às %H:%M")
        
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

    titulo = f"Relatório de Captações - WBS: {wbs_nome}" if wbs_nome else "Relatório Geral de Captações (Toda a Obra)"
    
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
    
    # CABEÇALHO DA TABELA
    pdf.set_font("Helvetica", 'B', 8) 
    pdf.set_fill_color(0, 51, 102) 
    pdf.set_text_color(255, 255, 255)
    
    pdf.cell(w=12, h=8, txt="ID", border=1, fill=True, align='C')
    pdf.cell(w=60, h=8, txt="NOME DO PROPRIETARIO", border=1, fill=True, align='C')
    pdf.cell(w=35, h=8, txt="WBS", border=1, fill=True, align='C')
    pdf.cell(w=18, h=8, txt="ESTACA", border=1, fill=True, align='C')
    pdf.cell(w=45, h=8, txt="COORDENADAS", border=1, fill=True, align='C')
    pdf.cell(w=15, h=8, txt="ZONA", border=1, fill=True, align='C')
    pdf.cell(w=15, h=8, txt="LADO", border=1, fill=True, align='C')
    pdf.cell(w=75, h=8, txt="SITUACAO", border=1, fill=True, align='C')
    pdf.ln()

    pdf.set_font("Helvetica", '', 7.5)
    
    # DADOS DA TABELA (COM CORES DINÂMICAS)
    for _, row in df_filtrado.iterrows():
        
        # 🚨 SE FOR IRREGULAR (SEM CONTRATO) = VERMELHO. SE FOR REGULAR = PRETO.
        if row.get('IS_REGULAR') == False:
            pdf.set_text_color(220, 0, 0) # Vermelho forte e legível
        else:
            pdf.set_text_color(0, 0, 0) # Preto normal
            
        coord = f"{limpar_texto(row.get('LAT'))} / {limpar_texto(row.get('LONG'))}"
        wbs_atual = limpar_texto(row.get('ESTRUTURA (WBS)', row.get('ESTRUTURA', '')))[:20]
        
        pdf.cell(w=12, h=8, txt=limpar_texto(row.get('ID')), border=1, align='C')
        pdf.cell(w=60, h=8, txt=limpar_texto(row.get('PROPRIETÁRIO'))[:35], border=1)
        pdf.cell(w=35, h=8, txt=wbs_atual, border=1, align='C') 
        pdf.cell(w=18, h=8, txt=limpar_texto(row.get('ESTACA')), border=1, align='C')
        pdf.cell(w=45, h=8, txt=coord, border=1, align='C')
        pdf.cell(w=15, h=8, txt=limpar_texto(row.get('ZONA')), border=1, align='C')
        pdf.cell(w=15, h=8, txt=limpar_texto(row.get('LADO')), border=1, align='C')
        pdf.cell(w=75, h=8, txt=limpar_texto(row.get('SITUAÇÃO'))[:45], border=1, align='C')
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
    st.markdown('<p class="titulo-principal">💧 Monitoramento das Captações - EIXO LESTE</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitulo">Sistema de Consulta e Fiscalização - PISF</p>', unsafe_allow_html=True)
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

    # 7. BARRA LATERAL (MENU E GERADOR DE RELATÓRIOS)
    with st.sidebar:
        st.markdown(f"<h2 style='color: #ffa500; margin-bottom:5px; font-size: 18px;'>BUSCAR CAPTAÇÃO</h2>", unsafe_allow_html=True)
        tipo_busca = st.radio("Método de busca:", ["Por ID", "Por Proprietário", "Por Estrutura (WBS)"], label_visibility="collapsed")
        
        busca = st.text_input("Digite aqui e tecle ENTER:")
        if busca.strip() != "":
            st.session_state.input_busca = busca
            st.session_state.modo_exibicao = 'busca'
            
        st.markdown("---")
        
        if st.button("ABRIR PAINEL DE INDICADORES", use_container_width=True):
            st.session_state.modo_exibicao = 'dashboard'
            st.session_state.input_busca = "" 
            
        if st.button("PONTOS IRREGULARES POR ESTRUTURA", use_container_width=True):
            st.session_state.modo_exibicao = 'irregulares_wbs'
            st.session_state.input_busca = "" 
        
        st.markdown("---")
        
        st.markdown(f"<h2 style='color: #ffa500; margin-bottom:5px; font-size: 18px;'>CENTRAL DE RELATÓRIOS</h2>", unsafe_allow_html=True)
        
        with st.expander("Abrir Filtros de Relatório", expanded=False):
            wbs_relatorio = st.text_input("Estrutura (WBS) - Opcional:", placeholder="Deixe branco p/ GERAL")
            filtro_contrato = st.selectbox("Contrato:", ["Todos", "Apenas Regulares", "Apenas Irregulares"])
            filtro_operacao = st.selectbox("Situação:", ["Todas", "Em Operação", "Inativos/Desativados"])
            
            if st.button("PROCESSAR E GERAR PDF", use_container_width=True):
                df_pdf = df.copy()
                if wbs_relatorio.strip() != "":
                    col_wbs = extrator_seguro(df_pdf, ['ESTRUTURA (WBS)', 'ESTRUTURA'])
                    df_pdf = df_pdf[col_wbs.str.contains(wbs_relatorio.strip(), case=False, na=False)]
                
                if filtro_contrato == "Apenas Regulares": df_pdf = df_pdf[df_pdf['IS_REGULAR'] == True]
                elif filtro_contrato == "Apenas Irregulares": df_pdf = df_pdf[df_pdf['IS_REGULAR'] == False]
                
                sit_pdf = extrator_seguro(df_pdf, ['SITUAÇÃO', 'SITUACAO'])
                if filtro_operacao == "Em Operação":
                    df_pdf = df_pdf[sit_pdf.str.contains('OPERA', na=False)]
                elif filtro_operacao == "Inativos/Desativados":
                    df_pdf = df_pdf[sit_pdf.str.contains('DESATI|NÃO INST|NAO INST', na=False)]
                
                if df_pdf.empty:
                    st.error("Nenhum ponto encontrado com esses filtros.")
                else:
                    st.success(f"Pronto! {len(df_pdf)} pontos processados.")
                    subtitulo = f"Contrato: {filtro_contrato} | Operação: {filtro_operacao} | Ordem: Estaca"
                    pdf_bytes = gerar_pdf(df_pdf, wbs_relatorio.strip(), subtitulo)
                    
                    st.download_button(
                        label=f"BAIXAR PDF AGORA",
                        data=pdf_bytes,
                        file_name=f"Relatorio_{'WBS_'+wbs_relatorio.strip() if wbs_relatorio.strip() else 'GERAL'}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        
        st.caption(f"<div style='margin-top:20px'>Base Total: **{len(df)} registros**</div>", unsafe_allow_html=True)
        st.markdown('<div class="assinatura-app">App por Raphael Davi - Versão 1.0 C</div>', unsafe_allow_html=True)

    # ==========================================================
    # TELA 1: DASHBOARD DE INDICADORES GERAIS
    # ==========================================================
    if st.session_state.modo_exibicao == 'dashboard':
        st.markdown("<h2 style='color: #00AEEF;'>Painel Geral de Indicadores</h2>", unsafe_allow_html=True)
        def card_metrica(titulo, valor): return f'<div class="metric-box"><div class="metric-title">{titulo}</div><div class="metric-value">{valor}</div></div>'
        colA, colB, colC = st.columns(3)
        with colA: st.markdown(card_metrica("QUANTIDADE DE PONTOS", len(df)), unsafe_allow_html=True)
        with colB: st.markdown(card_metrica("TOTAL COM CONTRATO", len(df[mask_reg])), unsafe_allow_html=True)
        with colC: st.markdown(card_metrica("TOTAL SEM CONTRATO", len(df[mask_irreg])), unsafe_allow_html=True)
        colD, colE, colF = st.columns(3)
        with colD: st.markdown(card_metrica("TOTAL COM CONTRATO (OPERANDO)", len(df[mask_reg & mask_operando])), unsafe_allow_html=True)
        with colE: st.markdown(card_metrica("TOTAL COM CONTRATO (DESATIVADO)", len(df[mask_reg & mask_inativas])), unsafe_allow_html=True)
        with colF: st.markdown(card_metrica("TOTAL SEM CONTRATO (OPERANDO)", len(df[mask_irreg & mask_operando])), unsafe_allow_html=True)
        colG, colH, colI = st.columns(3)
        with colG: st.markdown(card_metrica("TOTAL SEM CONTRATO (NÃO INSTALADO)", len(df[mask_irreg & mask_inativas])), unsafe_allow_html=True)
        with colH: st.markdown(card_metrica("TOTAL DE PONTOS RAMAL DO AGRESTE", len(df[mask_agreste])), unsafe_allow_html=True)
        with colI: st.markdown(card_metrica("TOTAL DE PONTOS EIXO LESTE", len(df[mask_leste])), unsafe_allow_html=True)

    # ==========================================================
    # TELA 2: TELA DE IRREGULARES POR WBS COM QUADRINHOS
    # ==========================================================
    elif st.session_state.modo_exibicao == 'irregulares_wbs':
        st.markdown("<h2 style='color: #FF4B4B;'>🚨 Monitor de Pontos Irregulares por Estrutura (WBS)</h2>", unsafe_allow_html=True)
        st.markdown('<p style="color: black;">Abaixo estão listadas todas as estruturas que possuem captações sem contrato. Clique no botão de download abaixo do quadro para gerar o relatório específico da WBS.</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        df_irregulares = df[mask_irreg].copy()
        col_wbs_irreg = extrator_seguro(df_irregulares, ['ESTRUTURA (WBS)', 'ESTRUTURA'])
        df_irregulares['WBS_CLEAN'] = col_wbs_irreg
        
        contagem_wbs = df_irregulares['WBS_CLEAN'].value_counts()
        
        if contagem_wbs.empty:
            st.success("🎉 Excelente! Não há nenhum ponto irregular cadastrado na base de dados no momento.")
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
                        label=f"BAIXAR PDF ({wbs_label})",
                        data=pdf_bytes_wbs,
                        file_name=f"Irregulares_WBS_{wbs_label}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"dl_wbs_{i}"
                    )
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
