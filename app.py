#!/usr/bin/env python3
"""
HR Climate Insight - Web Interface
Streamlit-based web application for generating climate survey reports.
Branded for Henear AI Agency.
"""

import streamlit as st
import tempfile
import os
import base64
from pathlib import Path
from datetime import datetime

# Import backend functions
from main import generate_report
import config


# ============== TRANSLATIONS ==============
TRANSLATIONS = {
    "en": {
        "page_title": "HR Climate Insight",
        "subtitle": "Automatic climate survey report generator",
        "access": "Access",
        "enter_password": "Enter password:",
        "wrong_password": "Incorrect password",
        "input_data": "Input Data",
        "upload_excel": "Survey Excel file",
        "upload_help": "Upload the Excel file exported from Google Forms",
        "upload_drag": "Drag and drop your file here",
        "upload_or": "or",
        "upload_browse": "Browse files",
        "upload_limit": "Limit: 200MB per file • XLSX, XLS",
        "company_data": "Company Data",
        "company_name": "Company name",
        "company_placeholder": "e.g. Acme Corp",
        "country": "Country",
        "country_placeholder": "e.g. Argentina",
        "city": "City",
        "city_placeholder": "e.g. Buenos Aires",
        "include_charts": "Include charts",
        "charts_help": "Generate bar charts for the questions",
        "generate_report": "Generate Report",
        "upload_error": "Please upload an Excel file",
        "company_error": "Please enter the company name",
        "country_error": "Please enter the country",
        "city_error": "Please enter the city",
        "generating": "Generating report... This may take a moment.",
        "success": "Report generated successfully!",
        "download": "Download Report (.docx)",
        "error_file": "Error: File not found",
        "error_validation": "Validation error",
        "error_unexpected": "Unexpected error",
        "dark_mode": "Dark mode",
        "light_mode": "Light mode",
    },
    "es": {
        "page_title": "HR Climate Insight",
        "subtitle": "Generador automático de informes de clima laboral",
        "access": "Acceso",
        "enter_password": "Ingresa la contraseña:",
        "wrong_password": "Contraseña incorrecta",
        "input_data": "Datos de entrada",
        "upload_excel": "Archivo Excel de la encuesta",
        "upload_help": "Sube el archivo Excel exportado de Google Forms",
        "upload_drag": "Arrastra y suelta tu archivo aquí",
        "upload_or": "o",
        "upload_browse": "Buscar archivos",
        "upload_limit": "Límite: 200MB por archivo • XLSX, XLS",
        "company_data": "Datos de la empresa",
        "company_name": "Nombre de la empresa",
        "company_placeholder": "Ej: Acme Corp",
        "country": "País",
        "country_placeholder": "Ej: Argentina",
        "city": "Ciudad",
        "city_placeholder": "Ej: Buenos Aires",
        "include_charts": "Incluir gráficos",
        "charts_help": "Genera gráficos de barras para las preguntas",
        "generate_report": "Generar Informe",
        "upload_error": "Por favor, sube un archivo Excel",
        "company_error": "Por favor, ingresa el nombre de la empresa",
        "country_error": "Por favor, ingresa el país",
        "city_error": "Por favor, ingresa la ciudad",
        "generating": "Generando informe... Esto puede tomar unos momentos.",
        "success": "¡Informe generado exitosamente!",
        "download": "Descargar Informe (.docx)",
        "error_file": "Error: Archivo no encontrado",
        "error_validation": "Error de validación",
        "error_unexpected": "Error inesperado",
        "dark_mode": "Modo oscuro",
        "light_mode": "Modo claro",
    }
}


def get_text(key: str) -> str:
    """Get translated text based on current language."""
    lang = st.session_state.get("language", "es")
    return TRANSLATIONS[lang].get(key, key)


# ============== STYLING ==============
def get_styles(dark_mode: bool, browse_text: str = "Browse files") -> str:
    """Return CSS styles based on theme."""

    if dark_mode:
        bg_primary = "#0a0a0a"
        bg_secondary = "#1a1a2e"
        bg_card = "#16213e"
        text_primary = "#ffffff"
        text_secondary = "#a0a0a0"
        accent = "#4fd1c5"
        accent_hover = "#38b2ac"
        border_color = "#2d3748"
    else:
        bg_primary = "#ffffff"
        bg_secondary = "#f7fafc"
        bg_card = "#ffffff"
        text_primary = "#1a202c"
        text_secondary = "#718096"
        accent = "#319795"
        accent_hover = "#2c7a7b"
        border_color = "#e2e8f0"

    return f"""
    <style>
        /* Hide Streamlit elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{display: none;}}

        /* Main container */
        .stApp {{
            background: {bg_primary};
        }}

        /* Text colors */
        .stApp, .stApp p, .stApp label, .stApp span {{
            color: {text_primary} !important;
        }}

        /* Headers */
        h1, h2, h3 {{
            color: {text_primary} !important;
        }}

        /* Input fields */
        .stTextInput > div > div > input {{
            background-color: {bg_secondary} !important;
            color: {text_primary} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
        }}

        .stTextInput > div > div > input::placeholder {{
            color: {text_secondary} !important;
            opacity: 1 !important;
        }}

        /* Hide "Press enter to apply" text */
        .stTextInput [data-testid="InputInstructions"] {{
            display: none !important;
        }}

        .stTextInput > div > div > input:focus {{
            border-color: {accent} !important;
            box-shadow: 0 0 0 1px {accent} !important;
        }}

        /* File uploader */
        .stFileUploader > div {{
            background-color: {bg_secondary} !important;
            border: 2px dashed {border_color} !important;
            border-radius: 12px !important;
        }}

        .stFileUploader > div:hover {{
            border-color: {accent} !important;
        }}

        /* File uploader dropzone inner */
        .stFileUploader [data-testid="stFileUploaderDropzone"] {{
            background-color: {bg_secondary} !important;
        }}

        .stFileUploader [data-testid="stFileUploaderDropzone"] > div {{
            background-color: {bg_secondary} !important;
        }}

        .stFileUploader section {{
            background-color: {bg_secondary} !important;
        }}

        .stFileUploader section > div {{
            background-color: {bg_secondary} !important;
        }}

        /* Uploaded file name text - force all text visible */
        .stFileUploader [data-testid="stFileUploaderFile"],
        .stFileUploader [data-testid="stFileUploaderFile"] *,
        .stFileUploader div[data-testid="stFileUploaderFile"] span,
        .stFileUploader div[data-testid="stFileUploaderFile"] p,
        .stFileUploader div[data-testid="stFileUploaderFile"] small,
        .stFileUploader div[data-testid="stFileUploaderFile"] div {{
            color: {text_secondary} !important;
            background-color: transparent !important;
        }}

        /* File delete button */
        .stFileUploader button[data-testid="stFileUploaderDeleteBtn"] {{
            color: {text_secondary} !important;
        }}

        .stFileUploader button[data-testid="stFileUploaderDeleteBtn"]:hover {{
            color: #f56565 !important;
        }}

        /* Hide default file uploader text */
        .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] {{
            display: none !important;
        }}

        /* Custom upload box */
        .custom-upload-box {{
            text-align: center;
            padding: 1rem;
            margin-bottom: -1rem;
        }}
        .custom-upload-box .upload-main {{
            font-size: 1rem;
            color: {text_primary};
            margin-bottom: 0.5rem;
        }}
        .custom-upload-box .upload-limit {{
            font-size: 0.8rem;
            color: {text_secondary};
        }}

        /* Replace Browse files button text */
        .stFileUploader [data-testid="stFileUploaderDropzone"] button {{
            font-size: 0 !important;
            background-color: {accent} !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1.5rem !important;
        }}
        .stFileUploader [data-testid="stFileUploaderDropzone"] button::after {{
            content: "{browse_text}";
            font-size: 0.875rem !important;
            color: white !important;
        }}
        .stFileUploader [data-testid="stFileUploaderDropzone"] button:hover {{
            background-color: {accent_hover} !important;
        }}

        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {accent} 0%, {accent_hover} 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}

        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(79, 209, 197, 0.4) !important;
        }}

        /* Download button */
        .stDownloadButton > button {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }}

        /* Form submit button (Generate Report) */
        .stFormSubmitButton > button {{
            background: linear-gradient(135deg, {accent} 0%, {accent_hover} 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}

        .stFormSubmitButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(79, 209, 197, 0.4) !important;
        }}

        /* Form container */
        .stForm {{
            background-color: {bg_card} !important;
            padding: 2rem !important;
            border-radius: 16px !important;
            border: 1px solid {border_color} !important;
        }}

        /* Checkbox */
        .stCheckbox > label {{
            color: {text_primary} !important;
        }}

        /* Selectbox (language dropdown) */
        .stSelectbox > div > div {{
            background-color: {bg_secondary} !important;
            border-color: {border_color} !important;
        }}

        .stSelectbox > div > div > div {{
            background-color: {bg_secondary} !important;
            color: {text_primary} !important;
        }}

        .stSelectbox [data-baseweb="select"] {{
            background-color: {bg_secondary} !important;
        }}

        .stSelectbox [data-baseweb="select"] > div {{
            background-color: {bg_secondary} !important;
            border-color: {border_color} !important;
        }}

        /* Selectbox dropdown menu */
        [data-baseweb="popover"] {{
            background-color: {bg_secondary} !important;
        }}

        [data-baseweb="popover"] li {{
            background-color: {bg_secondary} !important;
            color: {text_primary} !important;
        }}

        [data-baseweb="popover"] li:hover {{
            background-color: {accent} !important;
        }}

        /* Theme toggle button - force dark background */
        button[kind="secondary"],
        button[data-testid="baseButton-secondary"],
        .stButton button {{
            background-color: {bg_secondary} !important;
            background: {bg_secondary} !important;
            color: {text_primary} !important;
            border: 1px solid {border_color} !important;
            box-shadow: none !important;
        }}

        button[kind="secondary"]:hover,
        button[data-testid="baseButton-secondary"]:hover {{
            background-color: {accent} !important;
            background: {accent} !important;
            color: white !important;
            border-color: {accent} !important;
        }}

        /* Divider */
        hr {{
            border-color: {border_color} !important;
        }}

        /* Success/Error messages */
        .stSuccess {{
            background-color: rgba(72, 187, 120, 0.1) !important;
            border: 1px solid #48bb78 !important;
        }}

        .stError {{
            background-color: rgba(245, 101, 101, 0.1) !important;
            border: 1px solid #f56565 !important;
        }}

        /* Custom header */
        .custom-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 0;
            margin-bottom: 2rem;
        }}

        .logo-container {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .logo-container img {{
            height: 50px;
        }}

        .controls {{
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }}

        .control-btn {{
            background: {bg_secondary};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 0.5rem 1rem;
            cursor: pointer;
            color: {text_primary};
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }}

        .control-btn:hover {{
            background: {accent};
            color: white;
            border-color: {accent};
        }}

        .control-btn.active {{
            background: {accent};
            color: white;
            border-color: {accent};
        }}

        /* Subtitle */
        .subtitle {{
            color: {text_secondary} !important;
            font-size: 1.1rem;
            margin-top: -1rem;
            margin-bottom: 2rem;
        }}

        /* Card styling */
        .card {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
        }}
    </style>
    """


def get_logo_base64() -> str:
    """Load and encode logo as base64."""
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


# ============== APP CONFIGURATION ==============
st.set_page_config(
    page_title="HR Climate Insight | Henear",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ============== SESSION STATE INITIALIZATION ==============
if "language" not in st.session_state:
    st.session_state.language = "es"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False  # Default to light mode


# ============== APPLY STYLES ==============
st.markdown(get_styles(st.session_state.dark_mode, get_text("upload_browse")), unsafe_allow_html=True)


# ============== HEADER WITH CONTROLS ==============
def render_header():
    """Render the header with logo and controls."""
    logo_b64 = get_logo_base64()
    dark_mode = st.session_state.get("dark_mode", False)

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        # In dark mode, invert the logo colors so it's visible
        logo_filter = "invert(1)" if dark_mode else "none"
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="header-logo" style="height: 40px; filter: {logo_filter};">' if logo_b64 else ""

        # Get text color based on theme
        text_color = "#ffffff" if dark_mode else "#1a202c"

        st.markdown(
            f'''
            <div style="display: flex; align-items: center; gap: 10px;">
                {logo_html}
                <span style="font-size: 2.2rem; font-weight: 700; color: {text_color};">Henear</span>
            </div>
            ''',
            unsafe_allow_html=True
        )

    with col2:
        # Language toggle
        lang_options = {"es": "ES 🇪🇸", "en": "EN 🇬🇧"}
        current_lang = st.session_state.language
        new_lang = st.selectbox(
            "Language",
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=0 if current_lang == "es" else 1,
            label_visibility="collapsed"
        )
        if new_lang != current_lang:
            st.session_state.language = new_lang
            st.rerun()

    with col3:
        # Theme toggle
        theme_label = "🌙" if st.session_state.dark_mode else "☀️"
        if st.button(theme_label, help=get_text("dark_mode") if not st.session_state.dark_mode else get_text("light_mode")):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()


# ============== PASSWORD CHECK ==============
def check_password() -> bool:
    """Returns True if the user has entered the correct password."""

    def password_entered():
        if st.session_state["password"] == st.secrets.get("password"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        render_header()
        st.markdown(f"## 🔐 {get_text('access')}")
        st.text_input(
            get_text("enter_password"),
            type="password",
            on_change=password_entered,
            key="password"
        )
        return False

    elif not st.session_state["password_correct"]:
        render_header()
        st.markdown(f"## 🔐 {get_text('access')}")
        st.text_input(
            get_text("enter_password"),
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error(get_text("wrong_password"))
        return False

    return True


# ============== MAIN APP ==============
def main():
    """Main application logic."""

    render_header()

    # Title
    dark_mode = st.session_state.get("dark_mode", False)
    title_color = "#ffffff" if dark_mode else "#1a202c"
    st.markdown(
        f'<h2 style="font-size: 1.3rem; font-weight: 600; color: {title_color}; margin-bottom: 0;">📊 {get_text("page_title")}</h2>',
        unsafe_allow_html=True
    )
    st.markdown(f'<p class="subtitle">{get_text("subtitle")}</p>', unsafe_allow_html=True)

    # Form
    with st.form("report_form"):
        st.subheader(f"📁 {get_text('input_data')}")

        # Custom file uploader instructions
        st.markdown(f"""
        <div class="custom-upload-box">
            <p class="upload-main">{get_text("upload_drag")}</p>
            <p class="upload-limit">{get_text("upload_limit")}</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            get_text("upload_excel"),
            type=["xlsx", "xls"],
            help=get_text("upload_help"),
            label_visibility="collapsed"
        )

        st.subheader(f"🏢 {get_text('company_data')}")

        col1, col2 = st.columns(2)

        with col1:
            empresa = st.text_input(
                get_text("company_name"),
                placeholder=get_text("company_placeholder")
            )
            pais = st.text_input(
                get_text("country"),
                placeholder=get_text("country_placeholder")
            )

        with col2:
            ciudad = st.text_input(
                get_text("city"),
                placeholder=get_text("city_placeholder")
            )
            include_charts = st.checkbox(
                get_text("include_charts"),
                value=True,
                help=get_text("charts_help")
            )

        submitted = st.form_submit_button(
            f"🚀 {get_text('generate_report')}",
            use_container_width=True
        )

    # Process form
    if submitted:
        # Validation
        if not uploaded_file:
            st.error(get_text("upload_error"))
            return

        if not empresa:
            st.error(get_text("company_error"))
            return

        if not pais:
            st.error(get_text("country_error"))
            return

        if not ciudad:
            st.error(get_text("city_error"))
            return

        # Generate report
        with st.spinner(get_text("generating")):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                with tempfile.TemporaryDirectory() as tmp_output_dir:
                    output_path = generate_report(
                        input_file=tmp_path,
                        empresa=empresa,
                        pais=pais,
                        ciudad=ciudad,
                        output_dir=tmp_output_dir,
                        include_charts=include_charts
                    )

                    with open(output_path, "rb") as f:
                        docx_data = f.read()

                    os.unlink(tmp_path)

                st.success(f"✅ {get_text('success')}")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                empresa_slug = empresa.lower().replace(" ", "_")
                filename = f"informe_{empresa_slug}_{timestamp}.docx"

                st.download_button(
                    label=f"📥 {get_text('download')}",
                    data=docx_data,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

            except FileNotFoundError as e:
                st.error(f"{get_text('error_file')}: {e}")
            except ValueError as e:
                st.error(f"{get_text('error_validation')}: {e}")
            except Exception as e:
                st.error(f"{get_text('error_unexpected')}: {e}")
                st.exception(e)


# ============== RUN APP ==============
if __name__ == "__main__":
    if check_password():
        main()
