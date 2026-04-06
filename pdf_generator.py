# pdf_generator.py

import os
import subprocess
import datetime
from fpdf import FPDF

# ============================================================
#   RUTAS DE FLUX2
# ============================================================
FLUX_EXEC  = "/home/jenni/flux2.c/flux"
FLUX_MODEL = "/home/jenni/flux2.c/flux-klein-4b"
FLUX_CWD   = "/home/jenni/flux2.c"

PROMPT_PORTADA = (
    "Abstract representation of Spanish law and justice. "
    "Scales of justice, subtle map of Spain, soft blue and gold tones. "
    "Modern flat design, clean geometric shapes. No text, no labels."
)

# Ruta fija: la portada se genera una sola vez y se reutiliza
PORTADA_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portada_flux.png")

# ============================================================
#   SANITIZAR TEXTO: elimina caracteres fuera de latin-1
# ============================================================

def _sanitizar(texto: str) -> str:
    """Reemplaza caracteres Unicode problemáticos por equivalentes latin-1."""
    reemplazos = {
        "\u2014": "-",   # raya em —
        "\u2013": "-",   # raya en –
        "\u2018": "'",   "\u2019": "'",
        "\u201c": '"',   "\u201d": '"',
        "\u2022": "-",   "\u2026": "...",
        "\u00b7": "-",   "\u2010": "-",
        "\u2011": "-",   "\u2012": "-",
        "\u2015": "-",   "\u00e2": "a",
        "\u00e9": "e",   "\u00ed": "i",
        "\u00f3": "o",   "\u00fa": "u",
        "\u00e1": "a",   "\u00fc": "u",
        "\u00f1": "n",   "\u00c1": "A",
        "\u00c9": "E",   "\u00cd": "I",
        "\u00d3": "O",   "\u00da": "U",
        "\u00d1": "N",
    }
    for orig, repl in reemplazos.items():
        texto = texto.replace(orig, repl)
    return texto.encode("latin-1", errors="replace").decode("latin-1")

# ============================================================
#   FLUX: GENERAR IMAGEN (solo si no existe ya)
# ============================================================

def generar_portada_flux():
    """Genera la portada con Flux solo si no existe ya en caché."""
    if os.path.exists(PORTADA_CACHE):
        print("✔ Reutilizando portada en caché:", PORTADA_CACHE)
        return PORTADA_CACHE

    cmd = [FLUX_EXEC, "-d", FLUX_MODEL, "-p", PROMPT_PORTADA, "-o", PORTADA_CACHE]
    print("Generando portada con Flux (puede tardar varios minutos)…")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=FLUX_CWD)

    if result.returncode != 0:
        print("⚠️  Flux no disponible, se omite la portada.")
        return None

    print("✔ Portada generada en:", PORTADA_CACHE)
    return PORTADA_CACHE


# ============================================================
#   CLASE PDF CON FOOTER AUTOMÁTICO
#   Heredar FPDF y sobreescribir footer() es la forma correcta
#   de añadir pie de página sin solapamiento ni páginas en blanco.
# ============================================================

class InformePDF(FPDF):
    MARGEN = 20  # mm en los 4 lados

    def __init__(self):
        super().__init__()
        self.es_portada = True  # la primera página no lleva pie
        self.fecha_str  = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        # Margen inferior amplio para que el auto_page_break
        # salte ANTES de entrar en la zona del pie (15mm)
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(self.MARGEN, self.MARGEN, self.MARGEN)

    def add_page(self, *args, **kwargs):
        super().add_page(*args, **kwargs)
        if self.page_no() > 1:
            self.es_portada = False

    def footer(self):
        """Se llama automáticamente al cerrar cada página."""
        if self.es_portada or self.page_no() == 1:
            return
        self.set_y(-13)
        self.set_font("Arial", "", 8)
        self.set_text_color(160, 160, 160)
        num = self.page_no() - 1  # -1 porque la portada no cuenta
        self.cell(0, 8,
                  f"Asistente Legal IA  |  {self.fecha_str}  |  Pág. {num}",
                  align="C")
        self.set_text_color(0, 0, 0)


# ============================================================
#   UTILIDADES
# ============================================================

def _etiqueta(pdf, texto):
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(20, 60, 120)
    pdf.cell(0, 6, _sanitizar(texto).upper(), ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)


def _texto(pdf, texto, size=11):
    """multi_cell respeta márgenes y hace wrap automático."""
    pdf.set_font("Arial", "", size)
    pdf.multi_cell(0, 7, _sanitizar(texto))
    pdf.ln(3)


def _linea(pdf):
    pdf.set_draw_color(200, 200, 200)
    ancho_util = pdf.w - 2 * pdf.MARGEN
    pdf.line(pdf.get_x(), pdf.get_y(),
             pdf.get_x() + ancho_util, pdf.get_y())
    pdf.ln(6)


def _imagen(pdf, ruta, ancho_max=160):
    if not ruta or not os.path.exists(ruta):
        pdf.set_font("Arial", "I", 11)
        pdf.set_text_color(180, 180, 180)
        pdf.cell(0, 10, "(Imagen de portada no disponible)", ln=True, align="C")
        pdf.set_text_color(0, 0, 0)
        return
    x = (pdf.w - ancho_max) / 2
    pdf.image(ruta, x=x, w=ancho_max)
    pdf.ln(8)


# ============================================================
#   FUNCIÓN PRINCIPAL
# ============================================================

def save_report_to_pdf(informe_texto: str, historial: list) -> str:
    """
    Genera el informe final redactado por Ollama.
    Incluye portada Flux, el texto del informe y un anexo con las consultas originales.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"informe_final_{timestamp}.pdf"

    ruta_portada = generar_portada_flux()

    pdf = InformePDF()

    # -------- PORTADA --------
    pdf.add_page()
    pdf.ln(25)
    pdf.set_font("Arial", "B", 28)
    pdf.cell(0, 15, "INFORME LEGAL", ln=True, align="C")

    pdf.set_font("Arial", "", 13)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Informe generado por Asistente IA", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 8, datetime.datetime.now().strftime("%d/%m/%Y"), ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    _imagen(pdf, ruta_portada, ancho_max=150)

    # -------- INFORME REDACTADO --------
    pdf.add_page()
    _etiqueta(pdf, "Informe Legal")
    pdf.ln(2)
    _texto(pdf, informe_texto, size=11)

    # -------- ANEXO: CONSULTAS ORIGINALES --------
    pdf.add_page()
    _etiqueta(pdf, "Anexo - Consultas originales")
    pdf.ln(4)

    for i, item in enumerate(historial, 1):
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(20, 60, 120)
        pdf.cell(0, 7, f"Consulta {i}", ln=True)
        pdf.set_text_color(0, 0, 0)

        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, "Pregunta:", ln=True)
        _texto(pdf, item["question"], size=10)

        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, "Respuesta:", ln=True)
        _texto(pdf, item["answer"], size=10)

        _linea(pdf)

    pdf.output(filename)
    print(f"📄 Informe final generado: {filename}")
    return filename


def save_answer_to_pdf(answer: str, question: str = "") -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"informe_{timestamp}.pdf"

    ruta_portada = generar_portada_flux()

    pdf = InformePDF()

    # -------- PORTADA --------
    pdf.add_page()
    pdf.ln(25)
    pdf.set_font("Arial", "B", 28)
    pdf.cell(0, 15, "INFORME LEGAL", ln=True, align="C")

    pdf.set_font("Arial", "", 13)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Consulta generada por Asistente IA", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 8, datetime.datetime.now().strftime("%d/%m/%Y"), ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    _imagen(pdf, ruta_portada, ancho_max=150)

    # -------- CONTENIDO --------
    pdf.add_page()

    _etiqueta(pdf, "Pregunta")
    if question:
        _texto(pdf, question, size=13)
    else:
        pdf.set_font("Arial", "I", 11)
        pdf.set_text_color(150, 150, 150)
        pdf.multi_cell(0, 7, "(consulta no especificada)")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

    _linea(pdf)

    _etiqueta(pdf, "Respuesta")
    _texto(pdf, answer, size=11)

    pdf.output(filename)
    print(f"📄 PDF generado: {filename}")
    return filename