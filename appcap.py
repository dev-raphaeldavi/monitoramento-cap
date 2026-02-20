import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Monitor de Captações PISF", page_icon="💧", layout="wide", initial_sidebar_state="expanded")

# Controle de tela (Busca vs Dashboard)
if 'modo_exibicao' not in st.session_state: 
    st.session_state.modo_exibicao = 'dashboard' # Agora o padrão inicial é mostrar as métricas!
if 'input_busca' not in st.session_state: 
    st.session_state.input_busca = ""

# 2. IDENTIDADE VISUAL E CSS CUSTOMIZADO
st.markdown("""
    <style>
    :root {
        --azul-escuro: #003366;
        --azul-claro: #00AEEF;
        --laranja: #F7941E;
        --verde-regular: #28A745;
        --vermelho-irregular: #FF4B4B;
        --fundo-card: #ffffff;
    }
    
    .stApp { background-color: #FFFFFF !important; }
    
    .block-container {
        padding-top: 2rem !important; 
        padding-bottom: 1rem !important; 
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 98% !important;
    }
    
    header[data-testid="stHeader"] { background-color: transparent !important; }
    .stAppDeployButton { display: none !important; }
    
    /* 🚨 DEIXA O BOTÃO DO MENU LATERAL PRETO E VISÍVEL NO CELULAR 🚨 */
    [data-testid="collapsedControl"] svg {
        color: #000000 !important;
        fill: #000000 !important;
        stroke: #000000 !important;
    }
    [data-testid="collapsedControl"] {
        background-color: rgba(0,0,0,0.05) !important;
        border-radius: 5px;
    }
    
    .titulo-principal { color: var(--azul-escuro); font-size: 60px !important; font-weight: 900; margin-top: 0px !important; margin-bottom: 0px !important; padding-bottom: 0px !important; line-height: 1.1; }
    .subtitulo { color: var(--azul-claro); font-size: 30px !important; font-weight: 600; margin-top: 0px !important; margin-bottom: 10px !important; }
    
    @media (max-width: 768px) {
        .titulo-principal { font-size: 32px !important; text-align: center; }
        .subtitulo { font-size: 18px !important; text-align: center; margin-bottom: 20px !important; }
        .block-container { padding-top: 3.5rem !important; }
    }
    
    /* CAIXA DE MÉTRICAS (DASHBOARD) */
    .metric-box {
        background: linear-gradient(135deg, #003366 0%, #001a33 100%);
        border-left: 5px solid #00AEEF;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-title { font-size: 13px; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; color: #b3e6ff; letter-spacing: 0.5px; }
    .metric-value { font-size: 40px; font-weight: 900; margin: 0; line-height: 1; color: #ffffff; }
    
    /* CARDS DE BUSCA */
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

# 4. FUNÇÃO CAÇADORA DE CABEÇALHOS
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        df = pd.read_csv(URL_PLANILHA, dtype=str, sep=',', encoding='utf-8-sig', header=None)
        
        linha_cabecalho = 0
        for index, row in df.iterrows():
            valores_linha = [str(x).strip().upper() for x in row.values]
            if 'ID' in valores_linha:
                linha_cabecalho = index
                break
        
        nomes_limpos = []
        for col in df.iloc[linha_cabecalho].values:
            nome = str(col).replace('\n', ' ').replace('\r', '') 
            nome = ' '.join(nome.split()).upper() 
            nomes_limpos.append(nome)
            
        df.columns = nomes_limpos
        df = df.iloc[linha_cabecalho + 1:].reset_index(drop=True)

        # LÓGICA DE REGULARIDADE BLINDADA
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

# 5. INICIA APP
df = carregar_dados()

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
    
    # ==========================================================
    # EXTRATOR BLINDADO (Evita erros com colunas duplicadas ou vazias)
    # ==========================================================
    def extrator_seguro(dataframe, nomes_possiveis):
        for nome in nomes_possiveis:
            if nome in dataframe.columns:
                coluna = dataframe[nome]
                if isinstance(coluna, pd.DataFrame): # Se tiver duas colunas com o mesmo nome, pega a primeira
                    coluna = coluna.iloc[:, 0]
                return coluna.fillna('').astype(str).str.upper()
        return pd.Series([''] * len(dataframe), index=dataframe.index)

    serie_sit = extrator_seguro(df, ['SITUAÇÃO', 'SITUACAO'])
    serie_eixo = extrator_seguro(df, ['EIXO'])
    serie_sistema = extrator_seguro(df, ['SISTEMA'])
    serie_locais = serie_eixo + " " + serie_sistema # Junta as duas colunas para achar o local onde quer que esteja escrito

    # Lógica Matemática Segura (True ou False)
    mask_reg = df['IS_REGULAR'] == True
    mask_irreg = df['IS_REGULAR'] == False
    
    mask_operando = serie_sit.str.contains('OPERA', na=False)
    mask_inativas = serie_sit.str.contains('DESATI|NÃO INST|NAO INST', na=False)
    
    mask_agreste = serie_locais.str.contains('AGRESTE', na=False)
    mask_leste = serie_locais.str.contains('LESTE', na=False)

    # 7. BARRA LATERAL (MENU)
    with st.sidebar:
        st.markdown(f"<h2 style='color: #ffa500; margin-bottom:5px;'>🔍 Buscar Captação</h2>", unsafe_allow_html=True)
        tipo_busca = st.radio("Método de busca:", ["Por ID", "Por Proprietário", "Por Estrutura (WBS)"], label_visibility="collapsed")
        
        # O campo de texto atualiza a tela automaticamente se digitarem nele
        busca = st.text_input("Digite aqui e tecle ENTER:")
        if busca.strip() != "":
            st.session_state.input_busca = busca
            st.session_state.modo_exibicao = 'busca'
            
        st.markdown("---")
        
        # O ÚNICO BOTÃO QUE VOCÊ PRECISA PARA VER AS MÉTRICAS
        if st.button("📊 ABRIR PAINEL DE MÉTRICAS", use_container_width=True):
            st.session_state.modo_exibicao = 'dashboard'
            st.session_state.input_busca = "" # Limpa a busca para mostrar o painel limpo
        
        st.caption(f"<div style='margin-top:20px'>Base Total: **{len(df)} registros**</div>", unsafe_allow_html=True)
        st.markdown('<div class="assinatura-app">App por Raphael Davi - Versão 1.0</div>', unsafe_allow_html=True)

    # ==========================================================
    # TELA 1: DASHBOARD COMPLETO DE MÉTRICAS (Múltiplos Cards)
    # ==========================================================
    if st.session_state.modo_exibicao == 'dashboard':
        st.markdown("<h2 style='color: #00AEEF;'>Painel Geral de Indicadores</h2>", unsafe_allow_html=True)
        
        # Função para desenhar as caixinhas bonitas
        def card_metrica(titulo, valor):
            return f'<div class="metric-box"><div class="metric-title">{titulo}</div><div class="metric-value">{valor}</div></div>'
            
        # Linha 1 de métricas
        colA, colB, colC = st.columns(3)
        with colA: st.markdown(card_metrica("QUANTIDADE DE PONTOS", len(df)), unsafe_allow_html=True)
        with colB: st.markdown(card_metrica("TOTAL COM CONTRATO", len(df[mask_reg])), unsafe_allow_html=True)
        with colC: st.markdown(card_metrica("TOTAL SEM CONTRATO", len(df[mask_irreg])), unsafe_allow_html=True)
        
        # Linha 2 de métricas
        colD, colE, colF = st.columns(3)
        with colD: st.markdown(card_metrica("TOTAL COM CONTRATO (OPERANDO)", len(df[mask_reg & mask_operando])), unsafe_allow_html=True)
        with colE: st.markdown(card_metrica("TOTAL COM CONTRATO (NÃO INSTALADO)", len(df[mask_reg & mask_inativas])), unsafe_allow_html=True)
        with colF: st.markdown(card_metrica("TOTAL SEM CONTRATO (OPERANDO)", len(df[mask_irreg & mask_operando])), unsafe_allow_html=True)
        
        # Linha 3 de métricas
        colG, colH, colI = st.columns(3)
        with colG: st.markdown(card_metrica("TOTAL SEM CONTRATO (DESATIVADO)", len(df[mask_irreg & mask_inativas])), unsafe_allow_html=True)
        with colH: st.markdown(card_metrica("TOTAL DE PONTOS RAMAL DO AGRESTE", len(df[mask_agreste])), unsafe_allow_html=True)
        with colI: st.markdown(card_metrica("TOTAL DE PONTOS EIXO LESTE", len(df[mask_leste])), unsafe_allow_html=True)

    # ==========================================================
    # TELA 2: MODO BUSCA TRADICIONAL (Aparece quando digita o ID)
    # ==========================================================
    elif st.session_state.modo_exibicao == 'busca' and st.session_state.input_busca.strip() != "":
        termo = st.session_state.input_busca.strip()
        
        if tipo_busca == "Por ID":
            resultados = df[df['ID'].astype(str).str.strip() == termo]
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
                st.info(f"🔍 Encontramos **{len(resultados)}** captações correspondentes. Selecione uma na lista abaixo:")
                opcoes_lista = [(idx, f"ID: {row.get('ID', '-')} | Nome: {row.get('PROPRIETÁRIO', '-')} | WBS: {row.get('ESTRUTURA (WBS)', '-')}") for idx, row in resultados.iterrows()]
                escolha = st.selectbox("Lista de Resultados:", opcoes_lista, format_func=lambda x: x[1])
                ponto = resultados.loc[escolha[0]]
            else:
                ponto = resultados.iloc[0]
                if tipo_busca != "Por ID": st.success("✅ Apenas 1 captação encontrada! Mostrando detalhes abaixo.")

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
                st.markdown(criar_card("Ø Tubo (mm)", ponto.get('Ø TUBO (MM)', ponto.get('Ø TUBO (MM)'))), unsafe_allow_html=True)

else:
    st.info("🔄 Carregando dados do servidor Google Drive...")