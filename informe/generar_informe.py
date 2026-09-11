"""Genera el informe final del proyecto en PDF y DOCX.

Uso:
    python informe/generar_informe.py

Salidas:
    informe/informe_final.pdf
    informe/informe_final.docx

Edita el bloque CONFIG_CURSO con los datos reales del equipo.
"""

import json
from pathlib import Path

USE_REPORTLAB = True
try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Paragraph, PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle,
    )
    from reportlab.graphics.shapes import Drawing, Rect, String, Line
except ImportError:  # pragma: no cover
    USE_REPORTLAB = False

try:
    import docx
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Cm, Pt, RGBColor
    USE_DOCX = True
except ImportError:  # pragma: no cover
    USE_DOCX = False

# --------------------------------------------------------------------------
# CONFIG DEL CURSO (EDITAR)
# --------------------------------------------------------------------------
CONFIG_CURSO = {
    "universidad": "UNIVERSIDAD  TECNOLÓGICA NACIONAL",
    "facultad": "Facultad Regional Buenos Aires",
    "asignatura": "Inteligencia Artificial",
    "docente": "Lic. Nombre del Docente",
    "titulo": "IA-Tutor: Servidor de inferencia local con LLM de código abierto",
    "subtitulo": "Aplicativo web asistente académico con Ollama y Llama 3.2",
    "integrantes": ["Nombre Apellido 1", "Nombre Apellido 2", "Nombre Apellido 3", "Nombre Apellido 4"],
    "periodo": "Curso 2026",
    "fecha": "Septiembre 2026",
    "repositorio": "https://github.com/usuario/ia-tutor",
}

BASE = Path(__file__).resolve().parent.parent
JSON_RESULTADOS = BASE / "pruebas" / "resultados.json"


def cargar_metricas():
    datos = {
        "peticiones": "N",
        "latencia_promedio_s": "—",
        "tokens_s_promedio": "—",
        "modelo": "llama3.2 (Q4_K_M)",
        "verificadas": False,
    }
    if JSON_RESULTADOS.exists():
        try:
            r = json.loads(JSON_RESULTADOS.read_text(encoding="utf-8"))
            resid = r["resumen_por_peticion"]
            datos.update(
                peticiones=str(r["peticiones"]),
                latencia_promedio_s=str(resid["latencia_promedio_s"]),
                tokens_s_promedio=str(resid["tokens_s_promedio"]),
                modelo=r.get("modelo", datos["modelo"]),
                verificadas=True,
            )
        except Exception:  # noqa: BLE001
            pass
    return datos


CONFIG_CURSO["metricas"] = cargar_metricas()


# --------------------------------------------------------------------------
# TEXTO DEL INFORME
# --------------------------------------------------------------------------
def contenido():
    m = CONFIG_CURSO["metricas"]
    return {
        "introduccion": [
            "El presente trabajo aborda el despliegue de un servidor de inferencia de inteligencia "
            "artificial generativa utilizando exclusivamente modelos de código abierto. El objetivo "
            "es adquirir competencias prácticas en la configuración de infraestructura local, la "
            "integración de grandes modelos de lenguaje (LLM) a través de APIs REST y el desarrollo "
            "de un aplicativo cliente que consuma dichas capacidades en tiempo real.",
            "Como caso de uso se implementó «IA-Tutor», un asistente académico interactivo que "
            "responde preguntas de estudiantes sobre matemática, programación, historia y ciencias. "
            "La aplicación presenta las respuestas en tiempo real mediante streaming de texto, "
            "permitiendo al usuario ajustar parámetros del modelo (temperatura y longitud máxima "
            "de la respuesta).",
            "La solución se compone de tres elementos: (i) Ollama como servidor de inferencia del "
            "LLM; (ii) un gateway desarrollado en FastAPI que expone una API REST con streaming y "
            "acumula métricas de rendimiento; y (iii) un front-end web (HTML/CSS/JavaScript) "
            "encargado de la interfaz de usuario.",
        ],
        "arquitectura": [
            "El sistema sigue una arquitectura de tres capas: Cliente (navegador web), Servidor de "
            "IA (gateway FastAPI) y Modelo (Ollama con llama3.2). El navegador envía peticiones "
            "HTTP al gateway, que solicita la generación al servidor Ollama vía su API /api/chat "
            "con streaming habilitado. Cada fragmento generado se reenvía al cliente como "
            "texto/event-stream (SSE), logrando una experiencia de escritura en tiempo real.",
            "El gateway también centraliza el registro de métricas (latencia, tokens por segundo, "
            "tiempo hasta el primer token y tasa de errores), expuestas en el endpoint "
            "/api/metrics y visibles en el panel lateral del aplicativo.",
        ],
        "ficha": [
            "Se seleccionó Llama 3.2 de Meta, una familia de modelos de propósito general "
            "publicados con licencia de código abierto (Meta Llama Community License). La variante "
            "de 3B parámetros cuantizada en GGUF 4-bit (Q4_K_M) permite su ejecución en el hardware "
            "disponible (GPU RTX 3050 con 6 GB de VRAM) con un uso de memoria de aproximadamente "
            "2 GB, dejando espacio para el contexto.",
        ],
        "ficha_tabla": [
            ("Modelo", "llama3.2"),
            ("Desarrollador", "Meta AI"),
            ("Parámetros", "3 mil millones (3B)"),
            ("Licencia", "Meta Llama Community License (código abierto)"),
            ("Formato de carga", "GGUF cuantizado — Q4_K_M (~2 GB)"),
            ("Contexto soportado", "128K tokens (config: máximo de respuesta 2048)"),
            ("Servidor de inferencia", "Ollama 0.x (http://localhost:11434)"),
            ("CPU", "Intel Core i5-13420H (8 núcleos)"),
            ("GPU", "NVIDIA GeForce RTX 3050 Laptop 6 GB"),
            ("RAM del equipo", "16 GB"),
            ("Interfaz de exposición", "REST /api/chat con streaming nativo"),
        ],
        "justificacion_modelo": [
            "La elección responde a tres criterios: (1) compatibilidad con el hardware —un modelo "
            "3B en 4 bits corre con soltura en 6 GB de VRAM y también por CPU si es necesario—; "
            "(2) calidad de respuestas en español y razonamiento básico, suficientes para un tutor "
            "académico; y (3) madurez de su integración con Ollama, que ofrece una API REST estable, "
            "versatilidad de cuantizaciones y bajo costo de mantenimiento.",
            "La temperatura se ajustó por defecto en 0.7, un equilibrio entre determinismo y "
            "creatividad adecuado para el diálogo instructivo; el aplicativo permite variarla "
            "entre 0 y 1.5 según el caso de uso (por ejemplo, 0.2 para explicaciones exactas).",
        ],
        "guia": [
            "El despliegue se puede realizar por tres vías equivalentes. A continuación se detalla "
            "la configuración completa del entorno.",
        ],
        "guia_pasos": [
            ("1. Instalar Ollama",
             "Descargar el instalador oficial desde https://ollama.com/download y completar la "
             "instalación. En Linux/macOS: curl -fsSL https://ollama.com/install.sh | sh."),
            ("2. Descargar el modelo",
             "Ejecutar en una terminal:  \tollama pull llama3.2\n"
             "Este comando descarga el peso cuantizado Q4_K_M (≈2 GB) al repositorio local."),
            ("3. Preparar el entorno Python",
             "python -m venv .venv\n"
             "pip install -r server/requirements.txt\n"
             "Se instalan FastAPI, Uvicorn y httpx."),
            ("4. Ejecutar el servidor",
             "uvicorn server.main:app --host 0.0.0.0 --port 8000\n"
             "El gateway levanta en http://localhost:8000 y se conecta a Ollama en el puerto 11434."),
            ("5. Despliegue alternativo con Docker",
             "docker compose up -d --build\n"
             "Levanta el contenedor de Ollama (con soporte GPU opcional via NVIDIA Container "
             "Toolkit) y el contenedor del gateway."),
        ],
        "pruebas": [
            "Se ejecutaron pruebas funcionales sobre cada endpoint mediante el script "
            "pruebas/test_api.py (health, lista de modelos, chat streaming). Además se diseñó un "
            "benchmark (pruebas/benchmark.py) que mide latencia end-to-end y tokens por segundo "
            "para distintos prompts académicos.",
        ],
        "pruebas_tabla": [
            ("Métrica", "Valor obtenido"),
            ("Peticiones evaluadas", m["peticiones"]),
            ("Latencia promedio por respuesta", m["latencia_promedio_s"] + " s" if m["latencia_promedio_s"] != "—" else "—"),
            ("Rendimiento promedio", m["tokens_s_promedio"] + " tok/s" if m["tokens_s_promedio"] != "—" else "—"),
            ("Modelo", m["modelo"]),
        ],
        "capturas": [
            "Evidencia visual: el aplicativo funciona en un navegador en http://localhost:8000, "
            "mostrando la conversación del tutor, el panel de parámetros y el panel de métricas "
            "en vivo. Se adjuntan capturas de pantalla del estado de ejecución como anexo en la "
            "entrega.",
        ],
        "conclusiones": [
            "Se logró desplegar de forma local y funcional un servidor de inferencia de IA "
            "generativa basado exclusivamente en componentes de código abierto, cumpliendo los "
            "cuatro objetivos de aprendizaje: configuración de infraestructura, integración por "
            "API REST, desarrollo de un aplicativo cliente y documentación del rendimiento.",
            "Entre las limitaciones detectadas se destaca que el hardware disponible (GPU 6 GB) "
            "restringe el tamaño del modelo: un LLM mayor (8B o 70B cuantizado) produciría "
            "respuestas más profundas, pero no cabe en VRAM y degradaría la latencia por "
            "ejecución en CPU. Se observaron además respuestas ocasionales con sesgos típicos de "
            "la familia Llama y errores factuales en temas muy específicos, que el rol de 'tutor' "
            "mitiga parcialmente al indicar al modelo que pida aclaraciones.",
            "Como trabajo futuro se plantea: (i) migrar a vLLM o TGI con un modelo 7-8B "
            "cuantizado sobre una GPU con más VRAM o en la nube; (ii) agregar Retrieval "
            "Augmented Generation (RAG) para responder sobre apuntes y bibliografía del curso; "
            "(iii) persistir las conversaciones y exportar historiales en PDF; y (iv) añadir "
            "evaluación automática de la calidad de las respuestas (BLEU / ROUGE / GPT-eval).",
        ],
    }


# --------------------------------------------------------------------------
# PDF (reportlab)
# --------------------------------------------------------------------------
def generar_pdf(ruta: Path):
    c = contenido()
    hoja = SimpleDocTemplate(
        str(ruta), pagesize=A4,
        leftMargin=2.4 * cm, rightMargin=2.4 * cm,
        topMargin=2.2 * cm, bottomMargin=2.2 * cm,
        title=CONFIG_CURSO["titulo"], author="IA-Tutor",
    )
    estilos = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=estilos["Heading1"], fontSize=15, spaceAfter=10, textColor=colors.HexColor("#0f2a52"))
    h2 = ParagraphStyle("H2", parent=estilos["Heading2"], fontSize=12.5, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1d4ed8"))
    parr = ParagraphStyle("Par", parent=estilos["BodyText"], fontSize=10, leading=15, alignment=TA_JUSTIFY, spaceAfter=8)
    mono = ParagraphStyle("Mono", parent=estilos["Code"], fontSize=8.5, leading=13, backColor=colors.HexColor("#f1f5f9"), borderPadding=5)
    centro = ParagraphStyle("Centro", parent=estilos["BodyText"], alignment=TA_CENTER)

    def cabecera_pie(cnt, doc):
        doc.canv.saveState()
        doc.canv.setFont("Helvetica", 7.5)
        doc.canv.setFillColor(colors.grey)
        doc.canv.drawString(2.4 * cm, 1.1 * cm, "IA-Tutor · Inteligencia Artificial · Informe Final")
        doc.canv.drawRightString(A4[0] - 2.4 * cm, 1.1 * cm, f"Página {doc.page}")
        doc.canv.setStrokeColor(colors.HexColor("#cbd5e1"))
        doc.canv.line(2.4 * cm, 1.25 * cm, A4[0] - 2.4 * cm, 1.25 * cm)
        doc.canv.restoreState()

    def diagrama():
        d = Drawing(460, 140)
        ancho = 430
        block_ancho = 150
        alto = 42
        y = 80
        # Cliente
        d.add(Rect(0, y, block_ancho, alto))
        d.add(String(block_ancho / 2, y + 18, "CLIENTE", textAnchor="middle", fontSize=10, fontName="Helvetica-Bold"))
        d.add(String(block_ancho / 2, y + 7, "Navegador web · HTML/CSS/JS", textAnchor="middle", fontSize=6.5))
        # Linea a gateway
        d.add(Line(block_ancho + 3, y + 20, (ancho - block_ancho) / 2 - 3, y + 20))
        d.add(String((block_ancho + (ancho - block_ancho) / 2) / 2, y + 27, "HTTP / JSON", textAnchor="middle", fontSize=6.5))
        # Gateway
        gw_x = (ancho - block_ancho) / 2
        d.add(Rect(gw_x, y, block_ancho, alto))
        d.add(String(gw_x + block_ancho / 2, y + 18, "SERVIDOR DE IA", textAnchor="middle", fontSize=10, fontName="Helvetica-Bold"))
        d.add(String(gw_x + block_ancho / 2, y + 7, "FastAPI · /api/chat · métricas", textAnchor="middle", fontSize=6.5))
        # Linea a Ollama
        o_x = ancho - block_ancho
        d.add(Line(gw_x + block_ancho + 3, y + 20, o_x - 3, y + 20))
        d.add(String((gw_x + block_ancho + o_x) / 2, y + 27, "REST + streaming", textAnchor="middle", fontSize=6.5))
        # Ollama
        d.add(Rect(o_x, y, block_ancho, alto))
        d.add(String(o_x + block_ancho / 2, y + 18, "MODELO LLM", textAnchor="middle", fontSize=10, fontName="Helvetica-Bold"))
        d.add(String(o_x + block_ancho / 2, y + 7, "Ollama · llama3.2 (GGUF 4-bit)", textAnchor="middle", fontSize=6.5))
        # Flujo de respuesta (devolución)
        d.add(String(ancho / 2, 42, "▲ Flujo de respuesta (streaming token a token)", textAnchor="middle", fontSize=7))
        d.add(Line(ancho / 2, 34, ancho / 2, 8))
        d.add(String(ancho / 2, 20, "Figura 1. Diagrama de componentes del sistema.", textAnchor="middle", fontSize=7.5, fontName="Helvetica-Oblique"))
        return d

    def tabla(filas, anchos, header=True):
        t = Table(filas, colWidths=anchos)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")) if header else ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white) if header else ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        return t

    elems = []
    # ----- PORTADA -----
    elems.append(Spacer(1, 4 * cm))
    elems.append(Paragraph(CONFIG_CURSO["universidad"], ParagraphStyle("U", parent=centro, fontSize=16, textColor=colors.HexColor("#0f2a52"), fontWeight="bold")))
    elems.append(Paragraph(CONFIG_CURSO["facultad"], ParagraphStyle("F", parent=centro, fontSize=11)))
    elems.append(Spacer(1, 0.4 * cm))
    elems.append(Paragraph(CONFIG_CURSO["asignatura"], ParagraphStyle("A", parent=centro, fontSize=12, textColor=colors.grey)))
    elems.append(Spacer(1, 1.6 * cm))
    elems.append(Paragraph(CONFIG_CURSO["titulo"], ParagraphStyle("T", parent=centro, fontSize=19, textColor=colors.HexColor("#0f2a52"), fontWeight="bold", leading=24)))
    elems.append(Paragraph(CONFIG_CURSO["subtitulo"], ParagraphStyle("S", parent=centro, fontSize=12, textColor=colors.HexColor("#1d4ed8"))))
    elems.append(Spacer(1, 2.4 * cm))
    elems.append(Paragraph("Integrantes:", ParagraphStyle("I", parent=centro, fontSize=10, textColor=colors.grey)))
    for nombre in CONFIG_CURSO["integrantes"]:
        elems.append(Paragraph(nombre, ParagraphStyle("IN", parent=centro, fontSize=11, spaceAfter=4)))
    elems.append(Spacer(1, 1.4 * cm))
    elems.append(Paragraph(f"{CONFIG_CURSO['periodo']} · {CONFIG_CURSO['fecha']}", ParagraphStyle("F2", parent=centro, fontSize=10, textColor=colors.grey)))
    elems.append(PageBreak())

    # ----- 1. INTRODUCCIÓN -----
    elems.append(Paragraph("1. Introducción y Caso de Uso", h1))
    for p in c["introduccion"]:
        elems.append(Paragraph(p, parr))

    # ----- 2. ARQUITECTURA -----
    elems.append(Paragraph("2. Arquitectura del Sistema", h1))
    for p in c["arquitectura"]:
        elems.append(Paragraph(p, parr))
    elems.append(Spacer(1, 0.4 * cm))
    elems.append(diagrama())
    elems.append(Spacer(1, 0.3 * cm))

    # ----- 3. FICHA TÉCNICA -----
    elems.append(Paragraph("3. Ficha Técnica del Modelo", h1))
    for p in c["ficha"]:
        elems.append(Paragraph(p, parr))
    elems.append(tabla(c["ficha_tabla"], [6 * cm, 9.2 * cm], header=False))
    elems.append(Spacer(1, 0.3 * cm))
    elems.append(Paragraph("Tabla 1. Parámetros técnicos del modelo y hardware.", ParagraphStyle("Cap", parent=centro, fontSize=8.5, textColor=colors.grey, spaceAfter=8)))
    for p in c["justificacion_modelo"]:
        elems.append(Paragraph(p, parr))

    # ----- 4. INSTALACIÓN -----
    elems.append(Paragraph("4. Guía de Instalación y Despliegue", h1))
    for p in c["guia"]:
        elems.append(Paragraph(p, parr))
    for titulo, cuerpo in c["guia_pasos"]:
        elems.append(Paragraph(titulo, h2))
        for linea in cuerpo.split("\n"):
            linea = linea.strip().replace("\t", "    ")
            if not linea:
                continue
            palabra_comando = linea.split()[0] if linea.split() else ""
            es_comando = any(palabra_comando.startswith(tk) for tk in (
                "ollama", "python", "pip", "uvicorn", "docker", "curl", "powershell", "bash", "source",
            )) or palabra_comando.startswith(".venv")
            if es_comando:
                elems.append(Paragraph(linea, mono))
            else:
                elems.append(Paragraph(linea, parr))
    elems.append(Spacer(1, 0.2 * cm))
    elems.append(Paragraph(
        "Comandos usados (replicables en PowerShell o bash). El archivo docker-compose.yml "
        "reproduce el mismo entorno de forma contenerizada.",
        ParagraphStyle("Nota", parent=parr, fontSize=9, textColor=colors.grey),
    ))

    # ----- 5. PRUEBAS Y MÉTRICAS -----
    elems.append(Paragraph("5. Pruebas y Métricas de Rendimiento", h1))
    for p in c["pruebas"]:
        elems.append(Paragraph(p, parr))
    elems.append(tabla(c["pruebas_tabla"], [9 * cm, 6.2 * cm]))
    elems.append(Spacer(1, 0.3 * cm))
    if not CONFIG_CURSO["metricas"]["verificadas"]:
        elems.append(Paragraph(
            "Nota: complete los valores ejecutando python pruebas/benchmark.py -n 5 -t 256 "
            "y vuelva a generar este informe.",
            ParagraphStyle("Nota", parent=parr, fontSize=9, textColor=colors.HexColor("#b91c1c")),
        ))
    elems.append(Spacer(1, 0.2 * cm))
    for p in c["capturas"]:
        elems.append(Paragraph(p, parr))

    # ----- 6. CONCLUSIONES -----
    elems.append(Paragraph("6. Conclusiones y Trabajo Futuro", h1))
    for p in c["conclusiones"]:
        elems.append(Paragraph(p, parr))

    elems.append(Spacer(1, 1 * cm))
    elems.append(Paragraph(
        "Repositorio del proyecto: " + CONFIG_CURSO["repositorio"],
        ParagraphStyle("Repo", parent=centro, fontSize=9, textColor=colors.HexColor("#1d4ed8")),
    ))

    hoja.build(elems, onFirstPage=cabecera_pie, onLaterPages=cabecera_pie)


# --------------------------------------------------------------------------
# DOCX (python-docx)
# --------------------------------------------------------------------------
def generar_docx(ruta: Path):
    c = contenido()
    doc = Document()
    for seccion in doc.sections:
        seccion.left_margin = Cm(2.4)
        seccion.right_margin = Cm(2.4)
        seccion.top_margin = Cm(2.2)
        seccion.bottom_margin = Cm(2.2)

    azul = RGBColor(0x1D, 0x4E, 0xD8)
    gris = RGBColor(0x64, 0x74, 0x8B)

    def titulo(texto, tam=16, color=azul, alinear=WD_ALIGN_PARAGRAPH.LEFT, antes=10, despues=6):
        p = doc.add_paragraph()
        p.alignment = alinear
        p.paragraph_format.space_before = Pt(antes)
        p.paragraph_format.space_after = Pt(despues)
        r = p.add_run(texto)
        r.bold = True
        r.font.size = Pt(tam)
        r.font.color.rgb = color
        return p

    def parr(texto, tam=11):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(texto)
        r.font.size = Pt(tam)
        return p

    def codigo(texto):
        texto = texto.replace("\t", "    ")
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.7)
        r = p.add_run(texto)
        r.font.name = "Consolas"
        r.font.size = Pt(9)
        r.font.color.rgb = azul
        return p

    def tabla(filas, anchos):
        t = doc.add_table(rows=len(filas), cols=2)
        t.style = "Light Grid Accent 1"
        for i, (a, b) in enumerate(filas):
            t.rows[i].cells[0].text = str(a)
            t.rows[i].cells[1].text = str(b)
        return t

    # ----- PORTADA -----
    titulo(CONFIG_CURSO["universidad"], 18, azul, WD_ALIGN_PARAGRAPH.CENTER, 60, 2)
    titulo(CONFIG_CURSO["facultad"], 12, gris, WD_ALIGN_PARAGRAPH.CENTER, 0, 2)
    titulo(CONFIG_CURSO["asignatura"], 13, gris, WD_ALIGN_PARAGRAPH.CENTER, 0, 40)
    titulo(CONFIG_CURSO["titulo"], 20, azul, WD_ALIGN_PARAGRAPH.CENTER, 0, 6)
    titulo(CONFIG_CURSO["subtitulo"], 12, azul, WD_ALIGN_PARAGRAPH.CENTER, 0, 30)
    titulo("Integrantes:", 12, gris, WD_ALIGN_PARAGRAPH.CENTER, 20, 4)
    for nombre in CONFIG_CURSO["integrantes"]:
        titulo(nombre, 12, None, WD_ALIGN_PARAGRAPH.CENTER, 0, 2)
    titulo(f"{CONFIG_CURSO['periodo']} · {CONFIG_CURSO['fecha']}", 11, gris, WD_ALIGN_PARAGRAPH.CENTER, 20, 0)
    doc.add_page_break()

    # ----- 1 -----
    titulo("1. Introducción y Caso de Uso", 15)
    for p in c["introduccion"]:
        parr(p)

    # ----- 2 -----
    titulo("2. Arquitectura del Sistema", 15)
    for p in c["arquitectura"]:
        parr(p)
    t_arq = doc.add_table(rows=1, cols=4)
    t_arq.style = "Light Grid Accent 1"
    fila_1 = t_arq.rows[0].cells
    fila_1[0].text = "CLIENTE\nNavegador web"
    fila_1[1].text = "HTTP/JSON →"
    fila_1[2].text = "SERVIDOR DE IA\nFastAPI · /api/chat"
    fila_1[3].text = "REST + streaming →"
    t_arq2 = doc.add_table(rows=1, cols=1)
    t_arq2.style = "Light Grid Accent 1"
    t_arq2.rows[0].cells[0].text = "MODELO LLM\nOllama · llama3.2 (GGUF 4-bit) en http://localhost:11434"
    parr("Figura 1. Diagrama de componentes del sistema (sentido Cliente → Servidor IA → Modelo).")
    doc.add_page_break()

    # ----- 3 -----
    titulo("3. Ficha Técnica del Modelo", 15)
    for p in c["ficha"]:
        parr(p)
    tabla(c["ficha_tabla"], [6, 9])
    parr("Tabla 1. Parámetros técnicos del modelo y hardware.")
    for p in c["justificacion_modelo"]:
        parr(p)

    # ----- 4 -----
    titulo("4. Guía de Instalación y Despliegue", 15)
    for p in c["guia"]:
        parr(p)
    for step_titulo, cuerpo in c["guia_pasos"]:
        titulo(step_titulo, 12, gris)
        for linea in cuerpo.split("\n"):
            linea = linea.strip().replace("\t", "    ")
            if not linea:
                continue
            palabra_comando = linea.split()[0] if linea.split() else ""
            es_comando = any(palabra_comando.startswith(tk) for tk in (
                "ollama", "python", "pip", "uvicorn", "docker", "curl",
            )) or palabra_comando.startswith(".venv")
            if es_comando:
                codigo(linea)
            else:
                parr(linea, 10.5)

    # ----- 5 -----
    titulo("5. Pruebas y Métricas de Rendimiento", 15)
    for p in c["pruebas"]:
        parr(p)
    tabla(c["pruebas_tabla"], [9, 6])
    for p in c["capturas"]:
        parr(p)

    # ----- 6 -----
    titulo("6. Conclusiones y Trabajo Futuro", 15)
    for p in c["conclusiones"]:
        parr(p)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Repositorio del proyecto: " + CONFIG_CURSO["repositorio"])
    r.font.size = Pt(10)
    r.font.color.rgb = azul

    doc.save(str(ruta))


if __name__ == "__main__":
    print("Generando informe…")
    if USE_REPORTLAB:
        generar_pdf(BASE / "informe" / "informe_final.pdf")
        print("  OK PDF: informe/informe_final.pdf")
    else:
        print("  AVISO: reportlab no disponible, no se genera PDF.")
    if USE_DOCX:
        generar_docx(BASE / "informe" / "informe_final.docx")
        print("  OK DOCX: informe/informe_final.docx")
    else:
        print("  AVISO: python-docx no disponible, no se genera DOCX.")