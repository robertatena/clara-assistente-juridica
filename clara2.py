import streamlit as st
import re
import PyPDF2
from io import BytesIO, StringIO
from docx import Document

# Configurações
st.set_page_config(page_title="Clara 2.0", layout="centered")
st.title("📄 Clara – Análise Contratual Inteligente")
st.markdown("""
Versão melhorada que detecta mais cláusulas problemáticas e suporta PDFs.
""")

# Funções de leitura
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
    return "\n".join([page.extract_text() for page in pdf_reader.pages])

def read_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# Detecção melhorada
def detectar_clausulas(texto):
    regras = [
        (r"(não pode|impossibilidade de) cancelar", "Proibição de cancelamento - potencialmente abusiva"),
        (r"(renova|prorroga).*automática", "Renovação automática - requer aviso prévio"),
        (r"(reajuste|aumento).*unilateral", "Reajuste unilateral - abusivo"),
        (r"multa.*(acima de|superior a|de )\s*10%", "Multa excessiva - limite normalmente é 2% a 10%"),
        (r"foro.*(exterior|estrangeiro)", "Foro em país estrangeiro - abusivo para residentes no Brasil"),
        (r"(isenção|não responde).*responsabilidade", "Isenção total de responsabilidade - inválida"),
        (r"(perda|bloqueio).*(acesso|serviço).*sem reembolso", "Corte de serviço sem reembolso - abusivo"),
        (r"juros.*(acima de|superior a)\s*1%", "Juros abusivos - limite normalmente é 1% ao mês"),
        (r"(veda|proíbe).*reclamação", "Proibição de reclamação - direito básico do consumidor"),
        (r"(altera|modifica).*contrato.*unilateral", "Alteração unilateral - abusiva")
    ]
    return [desc for (padrao, desc) in regras if re.search(padrao, texto, re.IGNORECASE)]

# Interface
uploaded_file = st.file_uploader("Envie seu contrato (TXT, DOCX ou PDF)", type=["txt", "docx", "pdf"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.pdf'):
            texto = read_pdf(uploaded_file)
        elif uploaded_file.name.endswith('.docx'):
            texto = read_docx(uploaded_file)
        else:
            texto = StringIO(uploaded_file.getvalue().decode("utf-8")).read()

        problemas = detectar_clausulas(texto)
        
        st.subheader("🔍 Resultados")
        if problemas:
            st.warning("Cláusulas problemáticas encontradas:")
            for i, problema in enumerate(problemas, 1):
                st.markdown(f"{i}. {problema}")
            st.error("⚠️ Recomendamos revisão jurídica antes de assinar!")
        else:
            st.success("✅ Nenhuma cláusula claramente abusiva identificada")
            
    except Exception as e:
        st.error(f"Erro ao processar: {str(e)}")

st.markdown("""
---
ℹ️ Esta análise não substitui consultoria jurídica profissional.
""")