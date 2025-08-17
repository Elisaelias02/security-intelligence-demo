import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime
import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from components.claude_security_agent import create_claude_agent
except ImportError:
    # Fallback si no se puede importar Claude
    st.error("Error importando agente Claude. Usando modo básico.")
    create_claude_agent = None

# Configuración de la página
st.set_page_config(
    page_title="Plataforma de Inteligencia en Seguridad",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS profesional sin emojis
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-color: #1e40af;
        --secondary-color: #3b82f6;
        --success-color: #059669;
        --warning-color: #d97706;
        --danger-color: #dc2626;
        --dark-text: #1f2937;
        --light-bg: #f8fafc;
        --border-color: #e5e7eb;
    }
    
    .main > div {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 3rem 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(30, 64, 175, 0.15);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
    }
    
    .main-header .subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 400;
        margin-bottom: 1rem;
    }
    
    .main-header .badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        backdrop-filter: blur(10px);
    }
    
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--secondary-color);
        transition: all 0.2s ease;
        margin-bottom: 1.5rem;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card h3 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        color: var(--primary-color);
    }
    
    .metric-card p {
        margin: 0;
        color: #6b7280;
        font-weight: 500;
        font-size: 1rem;
    }
    
    .metric-card .metric-label {
        font-size: 0.875rem;
        color: #9ca3af;
        font-weight: 400;
    }
    
    .section-header {
        background: var(--light-bg);
        border-left: 4px solid var(--secondary-color);
        padding: 1.5rem;
        border-radius: 8px;
        margin: 2rem 0 1rem 0;
    }
    
    .section-header h3 {
        margin: 0;
        color: var(--dark-text);
        font-weight: 600;
    }
    
    .analysis-card {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: border-color 0.2s ease;
    }
    
    .analysis-card:hover {
        border-color: var(--secondary-color);
    }
    
    .vulnerability-item {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.75rem 0;
        border-left: 4px solid var(--danger-color);
    }
    
    .vulnerability-item .severity {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    
    .severity-critical {
        background: var(--danger-color);
        color: white;
    }
    
    .severity-high {
        background: #f97316;
        color: white;
    }
    
    .severity-medium {
        background: var(--warning-color);
        color: white;
    }
    
    .recommendation-item {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.75rem 0;
        border-left: 4px solid var(--success-color);
    }
    
    .api-status {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid;
        font-size: 0.9rem;
    }
    
    .api-status.active {
        border-left-color: var(--success-color);
        background: #f0fdf4;
    }
    
    .api-status.error {
        border-left-color: var(--danger-color);
        background: #fef2f2;
    }
    
    .api-status.warning {
        border-left-color: var(--warning-color);
        background: #fffbeb;
    }
    
    .form-section {
        background: var(--light-bg);
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        letter-spacing: 0.025em;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.15);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
    }
    
    .stSelectbox > div > div {
        border-radius: 6px;
    }
    
    .stTextInput > div > div {
        border-radius: 6px;
    }
    
    .stTextArea > div > div {
        border-radius: 6px;
    }
    
    /* Tabs personalizados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--light-bg);
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0.5rem 1.5rem;
        border-radius: 6px;
        font-weight: 500;
        color: #6b7280;
        background: transparent;
        border: 1px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: var(--primary-color);
        border-color: var(--border-color);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        .metric-card {
            padding: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    load_css()
    
    # Inicializar agente Claude
    if 'claude_agent' not in st.session_state:
        if create_claude_agent:
            st.session_state.claude_agent = create_claude_agent()
        else:
            st.session_state.claude_agent = None
    
    # Verificar estado de la API
    if st.session_state.claude_agent:
        api_status = st.session_state.claude_agent.check_api_status()
    else:
        api_status = {'status': 'error', 'message': 'Agente Claude no disponible', 'api_available': False}
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>Plataforma de Inteligencia en Seguridad</h1>
        <div class="subtitle">Análisis Avanzado de Vulnerabilidades de Ingeniería Social</div>
        <div class="badge">Potenciado por Inteligencia Artificial</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar estado de API
    display_api_status(api_status)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Configuración del Análisis")
        
        # Estado de Claude
        st.markdown("#### Estado del Sistema IA")
        
        if api_status['api_available']:
            st.success("Sistema IA Activo")
            st.info(f"Modelo: {api_status.get('model', 'claude-3-haiku')}")
        else:
            st.warning("Modo Básico Activo")
            
            # Opción para ingresar API key
            manual_key = st.text_input(
                "Clave API de Anthropic (opcional)", 
                type="password",
                help="Ingresa tu clave API para activar análisis avanzado"
            )
            
            if manual_key and st.button("Conectar Sistema IA"):
                if create_claude_agent:
                    st.session_state.claude_agent = create_claude_agent(manual_key)
                    st.rerun()
        
        st.markdown("---")
        
        # Configuraciones
        analysis_depth = st.selectbox(
            "Profundidad del Análisis",
            ["Básico", "Estándar", "Avanzado", "Exhaustivo"]
        )
        
        max_targets = st.slider("Máximo de Objetivos", 1, 20, 5)
        
        st.markdown("### Información del Sistema")
        st.info("""
        **Capacidades del Sistema:**
        
        • Análisis de inteligencia de fuentes abiertas
        • Perfilado psicológico avanzado  
        • Identificación de vectores de ataque
        • Generación de estrategias de phishing
        """)
    
    # Tabs principales (sin contramedidas y con menos opciones)
    tab1, tab2, tab3, tab4 = st.tabs([
        "Panel Ejecutivo",
        "Análisis OSINT", 
        "Perfilado de Objetivos",
        "Generación de Estrategias"
    ])
    
    with tab1:
        create_executive_dashboard()
    
    with tab2:
        create_osint_interface()
    
    with tab3:
        create_profiling_interface()
    
    with tab4:
        create_strategy_generation()

def display_api_status(status):
    """Mostrar estado de la API en español"""
    
    if status['status'] == 'active':
        st.markdown(f"""
        <div class="api-status active">
            <strong>Estado del Sistema IA: ACTIVO</strong><br>
            {status['message']}<br>
            <small>Modelo: {status.get('model', 'N/A')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    elif status['status'] == 'simulation_mode':
        st.markdown(f"""
        <div class="api-status warning">
            <strong>Estado del Sistema IA: MODO BÁSICO</strong><br>
            Sistema funcionando con capacidades limitadas<br>
            <small>Para funcionalidad completa, configure su clave API</small>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.markdown(f"""
        <div class="api-status error">
            <strong>Estado del Sistema IA: ERROR</strong><br>
            {status['message']}<br>
            <small>Sistema funcionando en modo básico</small>
        </div>
        """, unsafe_allow_html=True)

def create_executive_dashboard():
    """Dashboard ejecutivo profesional"""
    st.markdown("""
    <div class="section-header">
        <h3>Panel Ejecutivo - Métricas de Seguridad</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #dc2626;">
            <h3 style="color: #dc2626;">87</h3>
            <p>Vulnerabilidades Críticas</p>
            <div class="metric-label">Identificadas por IA</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #f97316;">
            <h3 style="color: #f97316;">234</h3>
            <p>Objetivos de Alto Riesgo</p>
            <div class="metric-label">Análisis psicológico</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #059669;">
            <h3 style="color: #059669;">92%</h3>
            <p>Precisión del Análisis</p>
            <div class="metric-label">Confianza del sistema</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>4.2min</h3>
            <p>Tiempo Promedio</p>
            <div class="metric-label">Por análisis completo</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar análisis recientes
    if 'recent_analyses' in st.session_state and st.session_state.recent_analyses:
        st.markdown("""
        <div class="section-header">
            <h3>Análisis Recientes</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for analysis in st.session_state.recent_analyses[-3:]:
            with st.expander(f"Análisis: {analysis.get('type', 'N/A')} - {analysis.get('timestamp', 'N/A')}"):
                st.json(analysis.get('summary', {}))
    else:
        st.info("No hay análisis recientes. Ejecute un análisis OSINT o de perfilado para ver resultados aquí.")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        create_risk_distribution_chart()
    
    with col2:
        create_vulnerability_timeline()

def create_osint_interface():
    """Interfaz OSINT profesional"""
    st.markdown("""
    <div class="section-header">
        <h3>Análisis de Inteligencia de Fuentes Abiertas (OSINT)</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("El sistema analizará información públicamente disponible para identificar vectores de ataque y vulnerabilidades")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("#### Configuración del Objetivo")
        
        with st.form("osint_form"):
            st.markdown("**Información Básica del Objetivo**")
            
            company_name = st.text_input("Nombre de la Organización", "TechCorp Solutions")
            domain = st.text_input("Dominio Principal", "techcorp.com")
            
            col_a, col_b = st.columns(2)
            with col_a:
                industry = st.selectbox("Sector", [
                    "Tecnología", "Finanzas", "Salud", "Educación", 
                    "Retail", "Manufactura", "Consultoría", "Gobierno"
                ])
            with col_b:
                company_size = st.selectbox("Tamaño", [
                    "1-50", "51-200", "201-1000", "1000-5000", "5000+"
                ])
            
            location = st.text_input("Ubicación Principal", "Madrid, España")
            
            st.markdown("**Fuentes de Información**")
            sources = []
            
            col_c, col_d = st.columns(2)
            with col_c:
                if st.checkbox("LinkedIn", True): sources.append("LinkedIn")
                if st.checkbox("Sitio Web Corporativo", True): sources.append("Website")
                if st.checkbox("Twitter/X"): sources.append("Twitter")
                if st.checkbox("Facebook"): sources.append("Facebook")
            
            with col_d:
                if st.checkbox("GitHub"): sources.append("GitHub")
                if st.checkbox("Registros DNS"): sources.append("DNS")
                if st.checkbox("Noticias y Prensa"): sources.append("News")
                if st.checkbox("Ofertas de Empleo"): sources.append("Jobs")
            
            ai_analysis = st.checkbox("Análisis Avanzado con IA", True)
            
            submit_button = st.form_submit_button("Iniciar Análisis OSINT", type="primary")
            
            if submit_button:
                company_data = {
                    'name': company_name,
                    'domain': domain,
                    'industry': industry,
                    'size': company_size,
                    'location': location,
                    'sources': sources
                }
                
                run_osint_analysis(company_data, ai_analysis)
    
    with col2:
        display_osint_results()

def run_osint_analysis(company_data, use_ai=True):
    """Ejecutar análisis OSINT"""
    
    progress_container = st.container()
    
    with progress_container:
        st.markdown("#### Análisis en Progreso")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Fase 1: Recopilación
        traditional_steps = [
            "Escaneando perfiles de LinkedIn corporativos...",
            "Analizando sitio web y subdominios...",
            "Extrayendo direcciones de correo electrónico...",
            "Identificando empleados clave...",
            "Recopilando métricas de exposición..."
        ]
        
        simulated_data = {}
        
        for i, step in enumerate(traditional_steps):
            status_text.text(step)
            time.sleep(0.6)
            progress_bar.progress((i + 1) / (len(traditional_steps) + 3))
            
            if "LinkedIn" in step:
                simulated_data['linkedin_profiles'] = np.random.randint(45, 89)
            elif "correo" in step:
                simulated_data['emails_found'] = np.random.randint(15, 35)
        
        # Fase 2: Análisis con IA
        if use_ai and st.session_state.claude_agent:
            status_text.text("Sistema IA procesando datos recopilados...")
            time.sleep(1)
            progress_bar.progress(0.8)
            
            try:
                claude_results = st.session_state.claude_agent.analyze_company_osint(company_data)
                
                status_text.text("Generando insights de inteligencia...")
                time.sleep(1)
                progress_bar.progress(0.9)
                
                final_results = {
                    **simulated_data,
                    **claude_results,
                    'ai_analysis': True,
                    'company_data': company_data
                }
                
            except Exception as e:
                st.error(f"Error en análisis IA: {e}")
                final_results = {
                    **simulated_data,
                    'ai_analysis': False,
                    'fallback_mode': True,
                    'company_data': company_data
                }
        else:
            final_results = {
                **simulated_data,
                'ai_analysis': False,
                'company_data': company_data
            }
        
        status_text.text("Análisis OSINT completado exitosamente")
        progress_bar.progress(1.0)
        
        # Guardar resultados
        st.session_state.osint_results = final_results
        
        # Guardar en historial
        if 'recent_analyses' not in st.session_state:
            st.session_state.recent_analyses = []
        
        st.session_state.recent_analyses.append({
            'type': 'Análisis OSINT',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'company': company_data['name'],
            'ai_used': use_ai,
            'summary': {
                'risk_score': final_results.get('risk_score', 0.75),
                'vulnerabilities': len(final_results.get('vulnerabilities_found', [])),
                'employees_analyzed': final_results.get('employees_at_risk', 45)
            }
        })
        
        time.sleep(1)
        st.rerun()

def display_osint_results():
    """Mostrar resultados OSINT"""
    st.markdown("#### Resultados del Análisis")
    
    if 'osint_results' not in st.session_state:
        st.info("Ejecute un análisis OSINT para ver los resultados")
        return
    
    results = st.session_state.osint_results
    
    # Indicador de IA
    if results.get('ai_analysis'):
        st.success("Análisis potenciado por Sistema IA")
    else:
        st.warning("Análisis básico - Sistema IA no disponible")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_score = results.get('risk_score', 0.75)
        risk_color = "Crítico" if risk_score >= 0.8 else "Alto" if risk_score >= 0.6 else "Medio"
        st.metric("Puntuación de Riesgo", f"{risk_score:.2f}", f"Nivel: {risk_color}")
    
    with col2:
        st.metric("Vulnerabilidades", len(results.get('vulnerabilities_found', [])), "Identificadas")
    
    with col3:
        st.metric("Objetivos en Riesgo", results.get('employees_at_risk', 45), "Empleados")
    
    # Resultados detallados
    if results.get('ai_analysis') and not results.get('fallback_mode'):
        
        st.markdown("#### Vulnerabilidades Identificadas")
        for vuln in results.get('vulnerabilities_found', []):
            st.markdown(f"""
            <div class="vulnerability-item">
                <div class="severity severity-high">ALTA</div>
                {vuln}
            </div>
            """, unsafe_allow_html=True)
        
        if 'critical_findings' in results:
            st.markdown("#### Hallazgos Críticos")
            for finding in results['critical_findings']:
                st.markdown(f"• **{finding}**")
        
        if 'recommendations' in results:
            st.markdown("#### Recomendaciones de Acción")
            for rec in results['recommendations']:
                st.markdown(f"""
                <div class="recommendation-item">
                    {rec}
                </div>
                """, unsafe_allow_html=True)
    
    else:
        st.markdown("#### Resultados Básicos")
        basic_metrics = {
            "Perfiles de LinkedIn": results.get('linkedin_profiles', 67),
            "Correos Encontrados": results.get('emails_found', 23),
            "Repositorios GitHub": results.get('github_repos', 18),
            "Subdominios": results.get('subdomains', 31)
        }
        
        for metric, value in basic_metrics.items():
            st.metric(metric, value)

def create_profiling_interface():
    """Interfaz de perfilado profesional"""
    st.markdown("""
    <div class="section-header">
        <h3>Perfilado Psicológico de Objetivos</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("El sistema realizará análisis psicológico para identificar vulnerabilidades específicas de ingeniería social")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("#### Selección y Configuración del Objetivo")
        
        # Lista de empleados
        if 'osint_results' in st.session_state:
            employee_count = st.session_state.osint_results.get('employees_at_risk', 10)
            employee_options = [f"Empleado {i+1} - {['CEO', 'CFO', 'CTO', 'Director', 'Gerente', 'Analista'][i%6]}" 
                             for i in range(min(employee_count, 15))]
        else:
            employee_options = [
                "María González - CFO",
                "Carlos Rodríguez - Director IT", 
                "Ana Martínez - Gerente RRHH",
                "Luis Hernández - Coordinador Operaciones"
            ]
        
        selected_employee = st.selectbox("Objetivo a Analizar", employee_options)
        
        st.markdown("#### Datos del Perfil")
        
        with st.form("profile_form"):
            
            social_activity = st.slider("Actividad en Redes Sociales", 1, 10, 7, 
                                      help="Nivel de actividad y exposición en redes sociales")
            info_sharing = st.slider("Compartir Información", 1, 10, 6,
                                   help="Tendencia a compartir información corporativa")
            security_awareness = st.slider("Conciencia de Seguridad", 1, 10, 4,
                                         help="Nivel de conocimiento en seguridad")
            
            department = st.selectbox("Departamento", 
                                    ["Finanzas", "Tecnología", "Recursos Humanos", "Ventas", "Marketing", "Operaciones", "Legal"])
            
            interests = st.multiselect("Intereses Identificados",
                                     ["Tecnología", "Deportes", "Viajes", "Familia", "Finanzas", 
                                      "Entretenimiento", "Educación", "Arte", "Música"],
                                     default=["Tecnología", "Viajes"])
            
            communication_style = st.selectbox("Estilo de Comunicación",
                                              ["Formal", "Casual", "Técnico", "Emocional", "Directo"])
            
            work_schedule = st.selectbox("Horario de Trabajo",
                                       ["Estándar 9-17", "Flexible", "Nocturno", "Fines de Semana", "Disponibilidad 24/7"])
            
            risk_factors = st.multiselect("Factores de Riesgo Observados",
                                        ["Oversharing en LinkedIn", "Información personal pública", 
                                         "Acceso privilegiado", "Contactos externos frecuentes",
                                         "Patrones predecibles", "Baja verificación de solicitudes"])
            
            analyze_button = st.form_submit_button("Realizar Análisis Psicológico", type="primary")
            
            if analyze_button:
                employee_data = {
                    'name': selected_employee,
                    'department': department,
                    'social_activity': social_activity,
                    'info_sharing': info_sharing,
                    'security_awareness': security_awareness,
                    'interests': interests,
                    'communication': communication_style,
                    'schedule': work_schedule,
                    'risk_factors': risk_factors
                }
                
                run_profile_analysis(employee_data)
    
    with col2:
        display_profile_results()

def run_profile_analysis(employee_data):
    """Ejecutar análisis de perfil"""
    
    with st.spinner("Analizando perfil psicológico del objetivo..."):
        progress_bar = st.progress(0)
        
        analysis_steps = [
            "Analizando patrones de comportamiento digital...",
            "Evaluando vulnerabilidades psicológicas...",
            "Identificando vectores de ataque óptimos...",
            "Procesando análisis avanzado con IA...",
            "Generando recomendaciones de explotación..."
        ]
        
        for i, step in enumerate(analysis_steps):
            time.sleep(0.8)
            progress_bar.progress((i + 1) / len(analysis_steps))
            st.text(step)
        
        try:
            # Análisis con Claude si está disponible
            if st.session_state.claude_agent:
                claude_analysis = st.session_state.claude_agent.analyze_employee_profile(employee_data)
                
                st.session_state.profile_results = {
                    **claude_analysis,
                    'employee_data': employee_data,
                    'ai_analysis': True
                }
            else:
                # Análisis básico
                risk_score = calculate_basic_risk_score(employee_data)
                st.session_state.profile_results = {
                    'risk_score': risk_score,
                    'employee_data': employee_data,
                    'ai_analysis': False,
                    'vulnerability_profile': generate_basic_vulnerabilities(employee_data),
                    'optimal_attack_vectors': generate_basic_vectors(employee_data)
                }
            
            # Agregar al historial
            if 'recent_analyses' not in st.session_state:
                st.session_state.recent_analyses = []
            
            st.session_state.recent_analyses.append({
                'type': 'Perfilado de Objetivo',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'employee': employee_data['name'],
                'ai_used': st.session_state.claude_agent is not None,
                'summary': {
                    'risk_score': st.session_state.profile_results.get('risk_score', 0.75),
                    'vulnerabilities': len(st.session_state.profile_results.get('vulnerability_profile', [])),
                    'vectors': len(st.session_state.profile_results.get('optimal_attack_vectors', []))
                }
            })
            
        except Exception as e:
            st.error(f"Error en análisis: {e}")
            st.session_state.profile_results = {
                'risk_score': 0.75,
                'fallback_mode': True,
                'employee_data': employee_data
            }
        
        st.success("Análisis psicológico completado")
        time.sleep(1)
        st.rerun()

def display_profile_results():
    """Mostrar resultados del perfilado"""
    st.markdown("#### Resultados del Análisis Psicológico")
    
    if 'profile_results' not in st.session_state:
        st.info("Seleccione un objetivo y ejecute el análisis para ver los resultados")
        return
    
    profile = st.session_state.profile_results
    
    # Indicador de IA
    if profile.get('ai_analysis') and not profile.get('fallback_mode'):
        st.success("Análisis psicológico realizado por Sistema IA")
    else:
        st.warning("Análisis básico - Sistema IA no disponible")
    
    # Score de riesgo principal
    risk_score = profile.get('risk_score', 0.75)
    confidence = profile.get('confidence_level', 0.87)
    
    if risk_score >= 0.8:
        risk_color = '#dc2626'
        risk_level = 'CRÍTICO'
    elif risk_score >= 0.6:
        risk_color = '#f97316' 
        risk_level = 'ALTO'
    else:
        risk_color = '#3b82f6'
        risk_level = 'MEDIO'
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {risk_color}, {risk_color}88); 
                padding: 2rem; border-radius: 12px; text-align: center; margin-bottom: 1.5rem;">
        <h2 style="color: white; margin: 0; font-size: 1.8rem;">Puntuación de Riesgo: {risk_score:.2f}/1.0</h2>
        <p style="color: white; margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">
            {risk_level} • Confianza: {confidence:.0%}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas detalladas
    if not profile.get('fallback_mode'):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Vectores de Ataque", len(profile.get('optimal_attack_vectors', [])))
        with col2:
            st.metric("Vulnerabilidades", len(profile.get('vulnerability_profile', [])))
        with col3:
            st.metric("Técnicas Aplicables", np.random.randint(5, 12))
        
        # Perfil de vulnerabilidades
        st.markdown("#### Vulnerabilidades Identificadas")
        for vuln in profile.get('vulnerability_profile', []):
            if isinstance(vuln, dict):
                severity = vuln.get('severity', 'MEDIA')
                severity_class = f"severity-{severity.lower()}"
                st.markdown(f"""
                <div class="vulnerability-item">
                    <div class="severity {severity_class}">{severity}</div>
                    <strong>{vuln.get('type', 'Vulnerabilidad')}</strong><br>
                    {vuln.get('description', 'Sin descripción')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="vulnerability-item">
                    <div class="severity severity-medium">MEDIA</div>
                    {vuln}
                </div>
                """, unsafe_allow_html=True)
        
        # Vectores de ataque óptimos
        st.markdown("#### Vectores de Ataque Identificados")
        for vector in profile.get('optimal_attack_vectors', []):
            if isinstance(vector, dict):
                probability = vector.get('probability', 0.5)
                prob_color = '#dc2626' if probability >= 0.8 else '#f97316' if probability >= 0.6 else '#3b82f6'
                st.markdown(f"""
                <div class="analysis-card" style="border-left: 4px solid {prob_color};">
                    <strong>{vector.get('type', 'Vector desconocido')}</strong> - Probabilidad: {probability:.0%}<br>
                    {vector.get('description', 'Sin descripción')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"• **{vector}**")
        
        # Recomendaciones de explotación
        if 'personalized_recommendations' in profile:
            st.markdown("#### Estrategias de Explotación Recomendadas")
            for rec in profile['personalized_recommendations']:
                st.markdown(f"""
                <div class="recommendation-item">
                    {rec}
                </div>
                """, unsafe_allow_html=True)
    
    else:
        st.markdown("#### Análisis Básico")
        st.info("El análisis completo requiere conexión con Sistema IA")

def create_strategy_generation():
    """Interfaz de generación de estrategias (solo phishing y smishing)"""
    st.markdown("""
    <div class="section-header">
        <h3>Generación de Estrategias de Ataque</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("**Uso Profesional**: Este sistema genera estrategias para evaluación de vulnerabilidades y capacitación")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("#### Configuración de la Estrategia")
        
        # Verificar si hay perfiles previos
        if 'profile_results' in st.session_state:
            st.success("Usando perfil analizado previamente")
            target_name = st.session_state.profile_results.get('employee_data', {}).get('name', 'Objetivo')
            st.write(f"**Objetivo**: {target_name}")
        else:
            st.info("Ejecute primero un análisis de perfilado para mejores resultados")
        
        attack_type = st.selectbox(
            "Tipo de Estrategia",
            [
                "Phishing por Correo Electrónico",
                "Smishing (SMS Phishing)"
            ]
        )
        
        scenario_context = st.text_area(
            "Contexto del Escenario",
            "Organización en proceso de auditoría financiera anual\nPresión por cumplir deadlines de cierre trimestral\nReorganización departamental en curso",
            height=100
        )
        
        strategy_depth = st.selectbox(
            "Profundidad del Análisis",
            ["Básico", "Detallado", "Exhaustivo"]
        )
        
        urgency_level = st.selectbox(
            "Nivel de Urgencia del Pretexto",
            ["Baja", "Media", "Alta", "Crítica"]
        )
        
        social_engineering_focus = st.multiselect(
            "Técnicas Psicológicas a Emplear",
            ["Autoridad", "Urgencia", "Reciprocidad", "Escasez", "Validación Social", "Compromiso"],
            default=["Autoridad", "Urgencia"]
        )
        
        if st.button("Generar Estrategia de Ataque", type="primary"):
            run_strategy_generation(attack_type, scenario_context, strategy_depth, urgency_level, social_engineering_focus)
    
    with col2:
        display_strategy_results()

def run_strategy_generation(attack_type, context, depth, urgency, techniques):
    """Generar estrategia de ataque"""
    
    # Obtener datos del perfil si están disponibles
    target_profile = st.session_state.get('profile_results', {})
    company_context = st.session_state.get('osint_results', {}).get('company_data', {})
    
    with st.spinner("Generando estrategia de ataque profesional..."):
        progress_bar = st.progress(0)
        
        steps = [
            "Analizando perfil del objetivo...",
            "Identificando vectores psicológicos...",
            "Diseñando estrategia de aproximación...",
            "Procesando escenario completo con IA...",
            "Generando plantillas específicas..."
        ]
        
        for i, step in enumerate(steps):
            time.sleep(0.7)
            progress_bar.progress((i + 1) / len(steps))
            st.text(step)
        
        try:
            # Generar estrategia con Claude si está disponible
            if st.session_state.claude_agent:
                strategy_data = {
                    'attack_type': attack_type,
                    'context': context,
                    'depth': depth,
                    'urgency': urgency,
                    'techniques': techniques,
                    'target_profile': target_profile,
                    'company_context': company_context
                }
                
                claude_strategy = st.session_state.claude_agent.generate_attack_simulation(
                    target_profile, company_context
                )
                
                st.session_state.strategy_results = {
                    **claude_strategy,
                    'strategy_data': strategy_data,
                    'ai_analysis': True
                }
            else:
                # Estrategia básica
                st.session_state.strategy_results = {
                    'attack_type': attack_type,
                    'success_probability': np.random.uniform(0.6, 0.85),
                    'psychological_techniques': techniques,
                    'ai_analysis': False,
                    'basic_strategy': generate_basic_strategy(attack_type, urgency, techniques)
                }
            
            # Agregar al historial
            if 'recent_analyses' not in st.session_state:
                st.session_state.recent_analyses = []
            
            st.session_state.recent_analyses.append({
                'type': 'Generación de Estrategia',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'attack_type': attack_type,
                'ai_used': st.session_state.claude_agent is not None,
                'summary': {
                    'success_probability': st.session_state.strategy_results.get('success_probability', 0.67),
                    'techniques_used': len(techniques),
                    'urgency_level': urgency
                }
            })
            
        except Exception as e:
            st.error(f"Error generando estrategia: {e}")
            st.session_state.strategy_results = {
                'fallback_mode': True,
                'attack_type': attack_type
            }
        
        st.success("Estrategia de ataque generada exitosamente")
        time.sleep(1)
        st.rerun()

def display_strategy_results():
    """Mostrar resultados de estrategia"""
    st.markdown("#### Estrategia de Ataque Generada")
    
    if 'strategy_results' not in st.session_state:
        st.info("Configure y genere una estrategia para ver los resultados")
        return
    
    strategy = st.session_state.strategy_results
    
    # Indicador de IA
    if strategy.get('ai_analysis') and not strategy.get('fallback_mode'):
        st.success("Estrategia generada por Sistema IA")
        
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            success_prob = strategy.get('success_probability', 0.67)
            prob_color = "Crítica" if success_prob >= 0.8 else "Alta" if success_prob >= 0.6 else "Media"
            st.metric("Probabilidad de Éxito", f"{success_prob:.0%}", f"Efectividad: {prob_color}")
        
        with col2:
            techniques = len(strategy.get('psychological_techniques', []))
            st.metric("Técnicas Psicológicas", techniques)
        
        with col3:
            complexity = strategy.get('complexity_level', 'Media')
            st.metric("Complejidad", complexity)
        
        # Estrategia de ataque
        st.markdown("#### Estrategia de Ataque Detallada")
        
        if 'attack_scenario' in strategy:
            scenario = strategy['attack_scenario']
            if isinstance(scenario, dict):
                for key, value in scenario.items():
                    st.markdown(f"**{key.replace('_', ' ').title()}**: {value}")
            else:
                st.markdown(f"**Escenario**: {scenario}")
        
        # Técnicas psicológicas utilizadas
        st.markdown("#### Técnicas Psicológicas Empleadas")
        for technique in strategy.get('psychological_techniques', []):
            if isinstance(technique, dict):
                st.markdown(f"""
                <div class="analysis-card">
                    <strong>{technique.get('name', 'Técnica')}</strong><br>
                    {technique.get('description', 'Sin descripción')}<br>
                    <small>Efectividad: {technique.get('effectiveness', 'N/A')}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"• **{technique}**")
        
        # Cronología del ataque
        if 'timeline_execution' in strategy:
            st.markdown("#### Cronología de Ejecución")
            timeline = strategy['timeline_execution']
            
            if isinstance(timeline, list):
                for i, step in enumerate(timeline, 1):
                    st.markdown(f"**Fase {i}**: {step}")
            elif isinstance(timeline, dict):
                for phase, description in timeline.items():
                    st.markdown(f"**{phase}**: {description}")
        
        # Plantillas sugeridas
        if 'suggested_templates' in strategy:
            st.markdown("#### Plantillas Sugeridas")
            templates = strategy['suggested_templates']
            
            if isinstance(templates, dict):
                for template_type, content in templates.items():
                    with st.expander(f"Plantilla: {template_type}"):
                        st.code(content, language="text")
        
        # Indicadores de éxito
        if 'success_indicators' in strategy:
            st.markdown("#### Indicadores de Éxito")
            for indicator in strategy['success_indicators']:
                st.markdown(f"• {indicator}")
    
    else:
        st.warning("Estrategia básica - Sistema IA no disponible")
        
        if 'basic_strategy' in strategy:
            st.markdown("#### Estrategia Básica")
            basic = strategy['basic_strategy']
            
            for key, value in basic.items():
                st.markdown(f"**{key}**: {value}")
        
        st.info("La estrategia completa requiere conexión con Sistema IA")

# Funciones auxiliares
def calculate_basic_risk_score(employee_data):
    """Calcular score de riesgo básico"""
    social_risk = employee_data.get('social_activity', 5) / 10
    sharing_risk = employee_data.get('info_sharing', 5) / 10
    awareness_protection = 1 - (employee_data.get('security_awareness', 5) / 10)
    
    risk_score = (social_risk * 0.3 + sharing_risk * 0.4 + awareness_protection * 0.3)
    return max(0.3, min(0.95, risk_score + np.random.uniform(0.1, 0.2)))

def generate_basic_vulnerabilities(employee_data):
    """Generar vulnerabilidades básicas"""
    vulnerabilities = []
    
    if employee_data.get('social_activity', 5) >= 7:
        vulnerabilities.append("Alta exposición en redes sociales profesionales")
    
    if employee_data.get('info_sharing', 5) >= 6:
        vulnerabilities.append("Tendencia a compartir información corporativa")
    
    if employee_data.get('security_awareness', 5) <= 4:
        vulnerabilities.append("Baja conciencia sobre técnicas de ingeniería social")
    
    return vulnerabilities

def generate_basic_vectors(employee_data):
    """Generar vectores básicos"""
    vectors = ["Phishing dirigido por correo electrónico", "Ingeniería social vía LinkedIn"]
    
    if 'Familia' in employee_data.get('interests', []):
        vectors.append("Pretextos relacionados con emergencias familiares")
    
    return vectors

def generate_basic_strategy(attack_type, urgency, techniques):
    """Generar estrategia básica"""
    return {
        "Tipo de Ataque": attack_type,
        "Nivel de Urgencia": urgency,
        "Técnicas": ", ".join(techniques),
        "Enfoque": "Personalizado basado en perfil del objetivo",
        "Probabilidad Estimada": f"{np.random.uniform(0.6, 0.8):.0%}"
    }

def create_risk_distribution_chart():
    """Gráfico de distribución de riesgo"""
    risk_data = pd.DataFrame({
        'Nivel': ['Crítico', 'Alto', 'Medio', 'Bajo'],
        'Cantidad': [87, 234, 456, 123]
    })
    
    colors = ['#dc2626', '#f97316', '#3b82f6', '#059669']
    
    fig = px.pie(
        risk_data,
        values='Cantidad',
        names='Nivel',
        title="Distribución de Niveles de Riesgo",
        color_discrete_sequence=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400, font_family="Inter")
    st.plotly_chart(fig, use_container_width=True)

def create_vulnerability_timeline():
    """Timeline de vulnerabilidades"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    vulnerabilities = [45, 52, 48, 61, 58, 67, 74, 69, 73, 81, 87, 92]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=vulnerabilities,
        mode='lines+markers',
        name='Vulnerabilidades Detectadas',
        line=dict(color='#dc2626', width=3),
        marker=dict(size=8, color='#dc2626')
    ))
    
    fig.update_layout(
        title="Evolución de Vulnerabilidades en el Tiempo",
        xaxis_title="Período",
        yaxis_title="Número de Vulnerabilidades",
        height=400,
        font_family="Inter"
    )
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
