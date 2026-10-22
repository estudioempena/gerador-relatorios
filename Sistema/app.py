import importlib
import os
import shutil
from datetime import datetime
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageOps

import gerador
importlib.reload(gerador)

PASTA_SISTEMA = Path(__file__).resolve().parent
LOGO_PATH = PASTA_SISTEMA / "logo_empena.png"

load_dotenv(PASTA_SISTEMA / ".env")

# Suporta tanto st.secrets (Nuvem) quanto .env (Computador Local)
try:
    SENHA_CONFIGURADA = st.secrets["SENHA_ACESSO"]
except Exception:
    SENHA_CONFIGURADA = os.getenv("SENHA_ACESSO", "empena123")

st.set_page_config(
    page_title="Gerador de Relatórios | Estúdio Empena",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- ESTILIZAÇÃO VISUAL: CLASH DISPLAY REGULAR & SEMIBOLD ---
st.markdown(
    """
    <style>
    @import url('https://api.fontshare.com/v2/css?f[]=clash-display@400,600&display=swap');

    /* Força fundo claro da aplicação */
    .stApp {
        background-color: #FFFFFF;
        color: #111111;
    }

    /* Tipografia Clash Display Regular (400) para textos de leitura, inputs e labels */
    .stMarkdown p, .stMarkdown span, label, input, textarea, .stCaption, [data-baseweb="input"] input {
        font-family: 'Clash Display', -apple-system, sans-serif !important;
        font-weight: 400 !important;
        color: #1E1E1E;
    }

    /* Títulos em Clash Display Semibold (600) */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Clash Display', sans-serif !important;
        font-weight: 600 !important;
        color: #111111 !important;
        letter-spacing: 0.02em;
    }

    /* Botões com fonte limpa e alinhada */
    .stButton button, .stDownloadButton button {
        font-family: 'Clash Display', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 4px !important;
    }

    /* Botão primário com fundo preto institucional */
    .stButton button[kind="primary"] {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid #111111 !important;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #2D2D2D !important;
        border-color: #2D2D2D !important;
    }

    /* Preserva rigorosamente os ícones nativos do Streamlit */
    [data-testid="stIcon"],
    [data-testid="stIcon"] *,
    .material-symbols-rounded,
    [class*="material-symbols"],
    button[aria-label*="password" i] span,
    button[aria-label*="senha" i] span {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        font-weight: normal !important;
        letter-spacing: normal !important;
        white-space: nowrap !important;
    }

    /* Entradas de texto e áreas de texto com bordas limpas */
    input[type="text"], input[type="password"], textarea {
        background-color: #FAFAFA !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 4px !important;
    }
    input[type="text"]:focus, input[type="password"]:focus, textarea:focus {
        border-color: #111111 !important;
        background-color: #FFFFFF !important;
    }

    /* Divisória elegante */
    hr {
        border-color: #EFEFEF !important;
        margin: 1.5rem 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- CONTROLE DE AUTENTICAÇÃO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    _, col_login, _ = st.columns([1, 1.8, 1])

    with col_login:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_container_width=True)

        st.markdown(
            "<h4 style='text-align: center; margin-top: 1rem; margin-bottom: 1.5rem; letter-spacing: 0.05em;'>ACESSO RESTRITO</h4>",
            unsafe_allow_html=True,
        )

        with st.form("form_login"):
            senha_digitada = st.text_input("Senha da Equipe", type="password", placeholder="Digite sua senha")
            botao_entrar = st.form_submit_button("Acessar", type="primary", use_container_width=True)

            if botao_entrar:
                if senha_digitada == SENHA_CONFIGURADA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Senha incorreta. Verifique e tente novamente.")
    st.stop()

# --- HEADER INSTITUCIONAL ---
col_logo, col_titulo, col_logout = st.columns([1.2, 3, 0.8], vertical_alignment="center")

with col_logo:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=130)

with col_titulo:
    st.markdown(
        "<h3 style='margin:0; padding:0; letter-spacing: 0.04em;'>GERADOR DE RELATÓRIOS</h3>",
        unsafe_allow_html=True,
    )

with col_logout:
    if st.button("Sair 🔒", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

st.divider()

# 1. Informações Gerais
st.subheader("1. Informações Gerais do Documento")
col_info_1, col_info_2 = st.columns(2)

data_padrao = datetime.now().strftime("%d . %m . %Y")
sugestao_nome = f"relatorio_{datetime.now().strftime('%Y%m%d')}"

with col_info_1:
    titulo_geral = st.text_input(
        "Título do Relatório",
        placeholder="Ex: RELATÓRIO TÉCNICO DE VISTORIA",
        help="Título exibido no topo do relatório (se deixar vazio, usa 'RELATÓRIO TÉCNICO DE VISTORIA').",
    )
    nome_arquivo = st.text_input(
        "Nome do Arquivo Base",
        placeholder=f"Ex: {sugestao_nome}",
        help="Nome do arquivo final (se deixar vazio, usa a data do dia).",
    )

with col_info_2:
    data_documento = st.text_input(
        "Data do Documento",
        placeholder=f"Ex: {data_padrao} (deixe vazio para usar a data de hoje)",
        help="Data inserida no cabeçalho do papel timbrado.",
    )

st.divider()

# 2. Gerenciamento de Blocos de Conteúdo
st.subheader("2. Blocos de Conteúdo")

if "qtd_blocos" not in st.session_state:
    st.session_state.qtd_blocos = 2

col_btn_1, col_btn_2, _ = st.columns([1.5, 1.5, 3])
with col_btn_1:
    if st.button("➕ Adicionar Bloco"):
        st.session_state.qtd_blocos += 1
        st.rerun()
with col_btn_2:
    if st.button("➖ Remover Bloco") and st.session_state.qtd_blocos > 1:
        st.session_state.qtd_blocos -= 1
        st.rerun()

blocos_dados = []

for idx in range(st.session_state.qtd_blocos):
    with st.expander(f"📌 Bloco {idx + 1}", expanded=True):
        subtitulo = st.text_input(
            f"Título / Seção do Bloco {idx + 1}",
            placeholder=f"Ex: {idx + 1}. Vistoria da Fachada Externa",
            key=f"subtitulo_{idx}",
        )

        texto = st.text_area(
            f"Texto do Bloco {idx + 1}",
            placeholder="Digite o conteúdo desta seção. Quebre linhas normalmente para criar novos parágrafos.",
            height=120,
            key=f"texto_{idx}",
        )

        arquivos_fotos = st.file_uploader(
            f"Fotos do Bloco {idx + 1} (Disposição em pares)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key=f"fotos_{idx}",
        )

        fotos_bloco = []
        if arquivos_fotos:
            st.caption(f"{len(arquivos_fotos)} foto(s) carregada(s):")
            for f_idx, arq_foto in enumerate(arquivos_fotos):
                col_preview, col_legenda = st.columns([1, 3])
                with col_preview:
                    img_preview = Image.open(arq_foto)
                    img_preview = ImageOps.exif_transpose(img_preview)
                    st.image(img_preview, width=120)
                with col_legenda:
                    legenda = st.text_input(
                        f"Legenda da Foto {f_idx + 1} ({arq_foto.name})",
                        placeholder=f"Ex: Figura {idx + 1}.{f_idx + 1}: Fissura identificada no reboco",
                        key=f"legenda_{idx}_{f_idx}",
                    )
                fotos_bloco.append({"arquivo": arq_foto, "legenda": legenda})

        blocos_dados.append(
            {
                "titulo": subtitulo,
                "texto": texto,
                "fotos": fotos_bloco,
            }
        )

st.divider()

# Botão de Geração
if st.button("🚀 Gerar Relatório Completo (DOCX + PDF)", type="primary", use_container_width=True):
    titulo_final = titulo_geral.strip() or "RELATÓRIO TÉCNICO DE VISTORIA"
    data_final = data_documento.strip() or data_padrao
    nome_final = nome_arquivo.strip() or sugestao_nome

    pasta_temp = gerador.PASTA_SAIDA / "_temp_uploads"
    pasta_temp.mkdir(parents=True, exist_ok=True)

    with st.spinner("Construindo documento DOCX e gerando PDF..."):
        try:
            blocos_processados = []

            for b_idx, b in enumerate(blocos_dados):
                fotos_processadas = []
                for f_idx, f_info in enumerate(b["fotos"]):
                    arq = f_info["arquivo"]
                    caminho_salvo = pasta_temp / arq.name

                    with Image.open(arq) as img_raw:
                        img_ok = ImageOps.exif_transpose(img_raw)
                        fmt = img_raw.format or "JPEG"
                        if fmt == "JPEG" and img_ok.mode in ("RGBA", "P"):
                            img_ok = img_ok.convert("RGB")
                        img_ok.save(caminho_salvo, format=fmt, quality=95)

                    legenda_texto = f_info["legenda"].strip()
                    if not legenda_texto:
                        legenda_texto = f"Figura {b_idx + 1}.{f_idx + 1}"

                    fotos_processadas.append(
                        {
                            "caminho": str(caminho_salvo),
                            "legenda": legenda_texto,
                        }
                    )

                blocos_processados.append(
                    {
                        "titulo": b["titulo"],
                        "texto": b["texto"],
                        "fotos": fotos_processadas,
                    }
                )

            caminho_docx, caminho_pdf = gerador.gerar_relatorio(
                titulo_geral=titulo_final,
                blocos=blocos_processados,
                data_documento=data_final,
                nome_base=nome_final,
                gerar_pdf=True,
            )

            st.success("✅ Relatório gerado com sucesso!")
            st.info(f"📁 **Arquivo salvo em:** `{caminho_docx.name}` e `{caminho_pdf.name}`")

            col_down_1, col_down_2 = st.columns(2)

            with col_down_1:
                with open(caminho_docx, "rb") as f_docx:
                    st.download_button(
                        label="📥 Baixar Arquivo DOCX",
                        data=f_docx.read(),
                        file_name=caminho_docx.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )

            if caminho_pdf and caminho_pdf.exists():
                with col_down_2:
                    with open(caminho_pdf, "rb") as f_pdf:
                        st.download_button(
                            label="📥 Baixar Arquivo PDF",
                            data=f_pdf.read(),
                            file_name=caminho_pdf.name,
                            mime="application/pdf",
                            use_container_width=True,
                        )

        except Exception as err:
            st.error(f"❌ Não foi possível gerar os documentos: {err}")
        finally:
            if pasta_temp.exists():
                shutil.rmtree(pasta_temp, ignore_errors=True)
