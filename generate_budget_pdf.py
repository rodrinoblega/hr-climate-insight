#!/usr/bin/env python3
"""
Generates a PDF budget proposal for HR Climate Insight project.
"""

from fpdf import FPDF
from datetime import datetime


class BudgetPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 20)
        self.cell(0, 10, 'HR Climate Insight', align='C', ln=True)
        self.set_font('Helvetica', '', 12)
        self.cell(0, 8, 'Presupuesto MVP', align='C', ln=True)
        self.ln(5)
        self.set_draw_color(100, 100, 100)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Pagina {self.page_no()}', align='C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, ln=True, fill=True)
        self.ln(3)

    def add_phase(self, status, title, hours, items):
        self.set_font('Helvetica', 'B', 11)
        if status == "done":
            self.set_text_color(34, 139, 34)  # Green
            status_text = "[COMPLETADO]"
        else:
            self.set_text_color(70, 130, 180)  # Blue
            status_text = "[PENDIENTE]"

        self.cell(0, 8, f"{status_text} {title} - {hours} hs", ln=True)
        self.set_text_color(0, 0, 0)

        self.set_font('Helvetica', '', 10)
        for item in items:
            self.cell(10)  # Indent
            self.cell(0, 6, f"  * {item}", ln=True)
        self.ln(3)

    def add_table(self, headers, data, col_widths):
        # Header
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(220, 220, 220)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, border=1, fill=True, align='C')
        self.ln()

        # Data
        self.set_font('Helvetica', '', 10)
        for row in data:
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, str(cell), border=1, align='C')
            self.ln()
        self.ln(5)


def generate_budget():
    pdf = BudgetPDF()
    pdf.add_page()

    # Date
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, f"Fecha: {datetime.now().strftime('%B %Y')}", ln=True)
    pdf.cell(0, 6, "Validez: 30 dias", ln=True)
    pdf.ln(10)

    # Project Description
    pdf.section_title("DESCRIPCION DEL PROYECTO")
    pdf.set_font('Helvetica', '', 10)
    description = """Desarrollo de una aplicacion web para automatizar la generacion de informes de clima laboral a partir de encuestas en formato Excel.

Funcionalidades principales:
  * Carga de archivos Excel (exportados de Google Forms)
  * Analisis automatico con inteligencia artificial
  * Generacion de graficos de distribucion de respuestas
  * Informe profesional en formato Word (.docx)
  * Editor de prompt integrado para personalizacion"""
    pdf.multi_cell(0, 6, description)
    pdf.ln(10)

    # Development Phases
    pdf.section_title("DESARROLLO")

    # Phase 1
    pdf.add_phase("done", "FASE 1: Core Backend", "22", [
        "Parser de Excel con deteccion automatica",
        "Filtro de anonimato (n>=5)",
        "Generacion de graficos automaticos",
        "Generacion de informes DOCX profesionales",
        "Integracion con OpenAI API",
        "Prompt maestro configurable"
    ])
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(34, 139, 34)
    pdf.cell(0, 6, "Estado: Ya desarrollado - BONIFICADO", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # Phase 2
    pdf.add_phase("pending", "FASE 2: Interfaz Web", "16", [
        "Aplicacion web con formulario simple",
        "Carga de archivo Excel",
        "Campos de entrada (empresa, pais, ciudad)",
        "Descarga de informe generado",
        "Sistema de acceso con contrasena",
        "Manejo de errores y feedback al usuario",
        "Deploy en servidor"
    ])

    # Phase 3
    pdf.add_phase("pending", "FASE 3: Editor de Prompt", "7", [
        "Visualizacion del prompt actual",
        "Editor de texto integrado",
        "Guardar cambios sin tocar codigo",
        "Opcion de restaurar prompt original"
    ])

    # Phase 4
    pdf.add_phase("pending", "FASE 4: Testing y Entrega", "10", [
        "Testing con multiples formatos de encuesta",
        "Ajustes y correcciones",
        "Documentacion de uso",
        "Capacitacion inicial"
    ])

    # Summary Table
    pdf.add_page()
    pdf.section_title("RESUMEN DE HORAS")

    pdf.add_table(
        ["Fase", "Horas", "Estado"],
        [
            ["Fase 1: Core Backend", "22 hs", "Bonificado"],
            ["Fase 2: Interfaz Web", "16 hs", "Pendiente"],
            ["Fase 3: Editor de Prompt", "7 hs", "Pendiente"],
            ["Fase 4: Testing y Entrega", "10 hs", "Pendiente"],
            ["TOTAL PENDIENTE", "33 hs", "-"],
        ],
        [80, 50, 50]
    )

    # Total
    pdf.section_title("TOTAL")
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, "Horas de trabajo: 33 hs", ln=True)
    pdf.cell(0, 8, "Valor hora: $10 USD", ln=True)
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_fill_color(200, 230, 200)
    pdf.cell(0, 15, "TOTAL: $330 USD", ln=True, align='C', fill=True)
    pdf.ln(10)

    # Recurring Costs
    pdf.section_title("COSTOS RECURRENTES (a cargo del cliente)")
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 7, "* API OpenAI: ~$0.01-0.12 USD por informe generado", ln=True)
    pdf.cell(0, 7, "  (el cliente utiliza su propia API key)", ln=True)
    pdf.cell(0, 7, "* Hosting: a definir", ln=True)
    pdf.ln(8)

    # Deliverables
    pdf.section_title("ENTREGABLES")
    pdf.set_font('Helvetica', '', 10)
    deliverables = [
        "Aplicacion web funcional y desplegada",
        "Codigo fuente completo",
        "Documentacion de uso",
        "Capacitacion inicial (1 sesion)"
    ]
    for item in deliverables:
        pdf.cell(0, 7, f"  [OK] {item}", ln=True)
    pdf.ln(8)

    # Payment
    pdf.section_title("FORMA DE PAGO")
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 7, "* 50% al inicio del proyecto: $165 USD", ln=True)
    pdf.cell(0, 7, "* 50% a la entrega final: $165 USD", ln=True)
    pdf.ln(8)

    # Notes
    pdf.section_title("NOTAS")
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 7, "* El cliente debe proveer su propia API key de OpenAI", ln=True)
    pdf.cell(0, 7, "* El prompt puede ser personalizado desde la interfaz", ln=True)
    pdf.cell(0, 7, "* Ajustes menores post-entrega incluidos (hasta 2 semanas)", ln=True)

    # Save
    output_path = "presupuesto_hr_climate_insight.pdf"
    pdf.output(output_path)
    return output_path


if __name__ == "__main__":
    path = generate_budget()
    print(f"PDF generado: {path}")
