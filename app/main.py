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

# CSS profesional
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
    
    .email-container {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .email-header {
        border-bottom: 2px solid #f3f4f6;
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .email-body {
        line-height: 1.6;
        color: #374151;
    }
    
    .phishing-alert {
        background: linear-gradient(135deg, #dc2626, #991b1b);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
        font-weight: 600;
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
        <h1>SISTEMA DE ATAQUE AVANZADO</h1>
        <div class="subtitle">Plataforma de Ingeniería Social y Phishing Automatizado</div>
        <div class="badge">IA Ofensiva • Workshop Demostrativo</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar estado de API
    display_api_status(api_status)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### CONFIGURACION DE ATAQUE")
        
        # Estado de Claude
        st.markdown("#### MOTOR DE IA OFENSIVA")
        
        if api_status['api_available']:
            st.success("SISTEMA IA OPERATIVO")
            st.info(f"Modelo: {api_status.get('model', 'claude-3-haiku')}")
            st.success("Generación de contenido malicioso: ACTIVA")
        else:
            st.error("MOTOR IA DESCONECTADO")
            st.warning("Usando modo de simulación profesional")
            
            # Opción para ingresar API key
            manual_key = st.text_input(
                "Clave API Anthropic (OPCIONAL)", 
                type="password",
                help="La demo funciona sin IA usando plantillas profesionales"
            )
            
            if manual_key and st.button("ACTIVAR MOTOR IA"):
                if create_claude_agent:
                    st.session_state.claude_agent = create_claude_agent(manual_key)
                    st.rerun()
                else:
                    st.error("Error: Componente Claude no disponible")
        
        st.markdown("---")
        
        # Configuraciones de ataque
        analysis_depth = st.selectbox(
            "Nivel de Sofisticación",
            ["Básico", "Estándar", "Avanzado", "APT (Estado-Nación)"]
        )
        
        max_targets = st.slider("Objetivos Simultáneos", 1, 50, 10)
        
        # Mostrar capacidades
        st.markdown("### CAPACIDADES DEL SISTEMA")
        st.error("""
        **ARSENAL DISPONIBLE:**
        
        • Reconocimiento OSINT automatizado
        • Perfilado psicológico con IA
        • Generación de phishing híper-realista  
        • Campañas de smishing personalizadas
        • Suplantación de identidad avanzada
        """)
        
        # Advertencia ética
        st.markdown("---")
        st.warning("""
        **DEMO AEGIS**
        
        Este sistema simula herramientas reales de atacantes para concientizar sobre amenazas actuales.
        """)
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "Centro de Comando",
        "Reconocimiento OSINT", 
        "Perfilado de Víctimas",
        "Generador de Phishing"
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
    """Mostrar estado de la API"""
    
    if status['status'] == 'active':
        st.markdown(f"""
        <div class="api-status active">
            <strong>MOTOR IA OFENSIVA: OPERATIVO</strong><br>
            Sistema de generación de contenido malicioso activo<br>
            <small>Modelo: {status.get('model', 'N/A')} | Phishing automático: HABILITADO</small>
        </div>
        """, unsafe_allow_html=True)
    
    elif status['status'] == 'simulation_mode':
        st.markdown(f"""
        <div class="api-status warning">
            <strong>MOTOR IA: MODO SIMULACION PROFESIONAL</strong><br>
            Usando plantillas avanzadas - Demo completamente funcional<br>
            <small>Contenido phishing garantizado para workshop</small>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.markdown(f"""
        <div class="api-status warning">
            <strong>MODO SIMULACION ACTIVO</strong><br>
            Demo funcional con plantillas profesionales<br>
            <small>Phishing automatizado disponible sin dependencias</small>
        </div>
        """, unsafe_allow_html=True)

def create_executive_dashboard():
    """Centro de comando"""
    st.markdown("""
    <div class="section-header">
        <h3>Centro de Comando - Operaciones Activas</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #dc2626;">
            <h3 style="color: #dc2626;">87</h3>
            <p>Vulnerabilidades Explotables</p>
            <div class="metric-label">Detectadas por IA</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #f97316;">
            <h3 style="color: #f97316;">234</h3>
            <p>Víctimas Potenciales</p>
            <div class="metric-label">Perfilado psicológico</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #059669;">
            <h3 style="color: #059669;">92%</h3>
            <p>Tasa de Éxito Estimada</p>
            <div class="metric-label">Phishing con IA</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>4.2min</h3>
            <p>Tiempo de Generación</p>
            <div class="metric-label">Por email malicioso</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar operaciones recientes
    if 'recent_analyses' in st.session_state and st.session_state.recent_analyses:
        st.markdown("""
        <div class="section-header">
            <h3>Operaciones Recientes</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for analysis in st.session_state.recent_analyses[-3:]:
            with st.expander(f"Operación: {analysis.get('type', 'N/A')} - {analysis.get('timestamp', 'N/A')}"):
                st.json(analysis.get('summary', {}))
    else:
        st.info("No hay operaciones activas. Inicie reconocimiento OSINT o perfilado de víctimas para comenzar.")
    
    # Advertencia de demo
    st.error("""
    **DEMOSTRACIÓN EN CURSO**
    
    Esta interfaz simula cómo operan realmente los cibercriminales modernos.
    """)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        create_risk_distribution_chart()
    
    with col2:
        create_vulnerability_timeline()

def create_osint_interface():
    """Interfaz OSINT"""
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
            
            company_name = st.text_input("Nombre de la Organización", "Empresa Objetivo")
            domain = st.text_input("Dominio Principal", "empresa-objetivo.com")
            
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
        
        # Fase 2: Análisis con IA o simulación
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
                final_results = generate_professional_osint_results(company_data, simulated_data)
        else:
            # Generar resultados profesionales sin IA
            status_text.text("Procesando con análisis profesional...")
            time.sleep(1)
            progress_bar.progress(0.9)
            final_results = generate_professional_osint_results(company_data, simulated_data)
        
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
            'ai_used': use_ai and st.session_state.claude_agent is not None,
            'summary': {
                'risk_score': final_results.get('risk_score', 0.75),
                'vulnerabilities': len(final_results.get('vulnerabilities_found', [])),
                'employees_analyzed': final_results.get('employees_at_risk', 45)
            }
        })
        
        time.sleep(1)
        st.rerun()

def generate_professional_osint_results(company_data, simulated_data):
    """Generar resultados OSINT profesionales sin depender de IA"""
    
    industry = company_data.get('industry', 'Tecnología')
    company_size = company_data.get('size', '201-1000')
    
    # Calcular score de riesgo basado en industria y tamaño
    risk_multipliers = {
        'Finanzas': 0.85, 'Tecnología': 0.80, 'Salud': 0.75,
        'Gobierno': 0.70, 'Educación': 0.65, 'Manufactura': 0.60
    }
    
    size_multipliers = {
        '1-50': 0.60, '51-200': 0.70, '201-1000': 0.80, 
        '1000-5000': 0.85, '5000+': 0.90
    }
    
    risk_score = risk_multipliers.get(industry, 0.75) * size_multipliers.get(company_size, 0.75)
    risk_score = min(0.95, max(0.45, risk_score + np.random.uniform(-0.1, 0.15)))
    
    # Generar vulnerabilidades específicas por industria
    vulnerabilities_by_industry = {
        'Finanzas': [
            "Exposición excesiva de información financiera en LinkedIn",
            "Patrones predecibles en comunicaciones externas",
            "Falta de verificación en procesos de auditoría",
            "Empleados con acceso privilegiado sin conciencia de seguridad"
        ],
        'Tecnología': [
            "Repositorios GitHub con información sensible",
            "Empleados compartiendo detalles técnicos en redes",
            "Falta de políticas para desarrollo colaborativo",
            "Exposición de arquitectura de sistemas"
        ],
        'Salud': [
            "Personal médico susceptible a urgencias falsas",
            "Falta de protocolos de verificación telefónica",
            "Exposición de información de pacientes",
            "Vulnerabilidad a ataques de autoridad médica"
        ]
    }
    
    vulnerabilities = vulnerabilities_by_industry.get(industry, [
        "Empleados con alta actividad en redes sociales",
        "Falta de conciencia sobre ingeniería social",
        "Procesos de verificación inadecuados",
        "Exposición excesiva de información corporativa"
    ])
    
    # Generar hallazgos críticos
    critical_findings = [
        f"Identificados {np.random.randint(15, 35)} empleados de alto perfil con exposición pública",
        f"Detectados {np.random.randint(8, 20)} vectores de ataque específicos para {industry}",
        f"Encontradas {np.random.randint(3, 12)} direcciones de email corporativo en filtraciones",
        "Patrones de comunicación predecibles en horarios laborales"
    ]
    
    # Generar recomendaciones
    recommendations = [
        "Implementar programa de concienciación sobre ingeniería social",
        "Establecer protocolos de verificación para solicitudes sensibles",
        "Reducir exposición de información corporativa en redes sociales",
        "Capacitar empleados en identificación de ataques dirigidos",
        "Implementar autenticación multifactor para accesos críticos"
    ]
    
    return {
        **simulated_data,
        'risk_score': risk_score,
        'vulnerabilities_found': vulnerabilities,
        'critical_findings': critical_findings,
        'recommendations': recommendations,
        'employees_at_risk': np.random.randint(35, 75),
        'ai_analysis': False,
        'professional_analysis': True,
        'company_data': company_data
    }

def display_osint_results():
    """Mostrar resultados OSINT"""
    st.markdown("#### Resultados del Análisis")
    
    if 'osint_results' not in st.session_state:
        st.info("Ejecute un análisis OSINT para ver los resultados")
        return
    
    results = st.session_state.osint_results
    
    # Indicador de análisis
    if results.get('ai_analysis'):
        st.success("Análisis potenciado por Sistema IA")
    else:
        st.success("Análisis profesional completado - Resultados garantizados")
    
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

def create_profiling_interface():
    """Interfaz de perfilado"""
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
            "Procesando análisis avanzado...",
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
                # Análisis profesional sin IA
                st.session_state.profile_results = generate_professional_profile_analysis(employee_data)
            
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
            st.session_state.profile_results = generate_professional_profile_analysis(employee_data)
        
        st.success("Análisis psicológico completado")
        time.sleep(1)
        st.rerun()

def generate_professional_profile_analysis(employee_data):
    """Generar análisis profesional de perfil sin IA"""
    
    # Calcular risk score
    social_risk = employee_data.get('social_activity', 5) / 10
    sharing_risk = employee_data.get('info_sharing', 5) / 10
    awareness_protection = 1 - (employee_data.get('security_awareness', 5) / 10)
    
    risk_score = (social_risk * 0.3 + sharing_risk * 0.4 + awareness_protection * 0.3)
    risk_score = max(0.3, min(0.95, risk_score + np.random.uniform(0.1, 0.2)))
    
    # Generar vulnerabilidades específicas
    vulnerabilities = []
    
    if employee_data.get('social_activity', 5) >= 7:
        vulnerabilities.append({
            'type': 'Exposición Digital Alta',
            'severity': 'ALTA',
            'description': 'Alta actividad en redes sociales facilita reconocimiento y perfilado detallado'
        })
    
    if employee_data.get('info_sharing', 5) >= 6:
        vulnerabilities.append({
            'type': 'Tendencia a Compartir',
            'severity': 'MEDIA',
            'description': 'Propensión a compartir información corporativa sin verificación adecuada'
        })
    
    if employee_data.get('security_awareness', 5) <= 4:
        vulnerabilities.append({
            'type': 'Baja Conciencia de Seguridad',
            'severity': 'CRÍTICA',
            'description': 'Conocimiento limitado sobre técnicas de ingeniería social moderna'
        })
    
    # Generar vectores de ataque basados en departamento
    department = employee_data.get('department', 'Finanzas')
    
    vectors_by_department = {
        'Finanzas': [
            {'type': 'Suplantación de Auditoría', 'probability': 0.85, 'description': 'Falsos requerimientos de auditoría externa'},
            {'type': 'Urgencia Fiscal', 'probability': 0.78, 'description': 'Solicitudes urgentes relacionadas con obligaciones fiscales'},
            {'type': 'Verificación Bancaria', 'probability': 0.72, 'description': 'Falsa verificación de transacciones bancarias'}
        ],
        'Tecnología': [
            {'type': 'Actualización de Seguridad', 'probability': 0.82, 'description': 'Falsas alertas de seguridad que requieren acción inmediata'},
            {'type': 'Solicitud de Acceso', 'probability': 0.75, 'description': 'Peticiones de acceso técnico de supuestos colegas'},
            {'type': 'Problema de Sistema', 'probability': 0.70, 'description': 'Reportes falsos de problemas críticos de sistema'}
        ],
        'Recursos Humanos': [
            {'type': 'Verificación de Empleado', 'probability': 0.80, 'description': 'Solicitudes de verificación de información de empleados'},
            {'type': 'Proceso de Contratación', 'probability': 0.73, 'description': 'Falsos procesos de verificación de candidatos'},
            {'type': 'Actualización de Políticas', 'probability': 0.68, 'description': 'Supuestas actualizaciones urgentes de políticas'}
        ]
    }
    
    optimal_vectors = vectors_by_department.get(department, [
        {'type': 'Autoridad Corporativa', 'probability': 0.75, 'description': 'Suplantación de autoridades corporativas'},
        {'type': 'Urgencia Operacional', 'probability': 0.70, 'description': 'Situaciones urgentes que requieren bypass de protocolos'}
    ])
    
    # Generar recomendaciones personalizadas
    recommendations = [
        "Implementar doble verificación para solicitudes sensibles vía canal alternativo",
        f"Capacitación específica en vectores comunes del departamento de {department}",
        "Establecer frases código para verificación de solicitudes internas urgentes",
        "Simulacros de phishing dirigidos basados en el perfil psicológico identificado"
    ]
    
    return {
        'risk_score': risk_score,
        'confidence_level': 0.87,
        'vulnerability_profile': vulnerabilities,
        'optimal_attack_vectors': optimal_vectors,
        'personalized_recommendations': recommendations,
        'employee_data': employee_data,
        'ai_analysis': False,
        'professional_analysis': True
    }

def display_profile_results():
    """Mostrar resultados del perfilado"""
    st.markdown("#### Resultados del Análisis Psicológico")
    
    if 'profile_results' not in st.session_state:
        st.info("Seleccione un objetivo y ejecute el análisis para ver los resultados")
        return
    
    profile = st.session_state.profile_results
    
    # Indicador de análisis
    if profile.get('ai_analysis'):
        st.success("Análisis psicológico realizado por Sistema IA")
    else:
        st.success("Análisis profesional completado - Resultados garantizados")
    
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
    
    # Recomendaciones
    if 'personalized_recommendations' in profile:
        st.markdown("#### Estrategias de Explotación Recomendadas")
        for rec in profile['personalized_recommendations']:
            st.markdown(f"""
            <div class="recommendation-item">
                {rec}
            </div>
            """, unsafe_allow_html=True)

def create_strategy_generation():
    """Generador de phishing GARANTIZADO"""
    st.markdown("""
    <div class="section-header">
        <h3>GENERADOR AUTOMATICO DE PHISHING</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.success("SISTEMA OPERATIVO - Generación automática de phishing garantizada")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("#### CONFIGURACION DEL ATAQUE")
        
        # Verificar si hay perfiles previos
        if 'profile_results' in st.session_state:
            st.success("Víctima perfilada detectada")
            target_name = st.session_state.profile_results.get('employee_data', {}).get('name', 'Objetivo')
            st.write(f"**Víctima Principal**: {target_name}")
        else:
            st.warning("Ejecute perfilado de víctima para maximizar efectividad")
        
        attack_type = st.selectbox(
            "Vector de Ataque",
            [
                "Phishing por Email (Híper-realista)",
                "Smishing (SMS Malicioso)"
            ]
        )
        
        scenario_context = st.text_area(
            "Contexto de Explotación",
            "Temporada de auditorías fiscales\nPresión por cierre de trimestre\nCambios en sistemas de seguridad\nReorganización corporativa en curso",
            height=100,
            help="Contexto que el atacante usaría para hacer creíble el engaño"
        )
        
        strategy_depth = st.selectbox(
            "Nivel de Sofisticación",
            ["Básico", "Avanzado", "APT (Estado-Nación)"]
        )
        
        urgency_level = st.selectbox(
            "Presión Psicológica",
            ["Baja", "Media", "Alta", "Crítica"]
        )
        
        social_engineering_focus = st.multiselect(
            "Arsenal Psicológico",
            ["Autoridad", "Urgencia", "Reciprocidad", "Escasez", "Validación Social", "Compromiso"],
            default=["Autoridad", "Urgencia"],
            help="Técnicas de manipulación psicológica a combinar"
        )
        
        # Botón de generación
        if st.button("GENERAR ATAQUE AUTOMATICO", type="primary"):
            run_strategy_generation_guaranteed(attack_type, scenario_context, strategy_depth, urgency_level, social_engineering_focus)
    
    with col2:
        display_strategy_results_guaranteed()

def run_strategy_generation_guaranteed(attack_type, context, depth, urgency, techniques):
    """Función que SIEMPRE funciona para demo - garantizada"""
    
    # Obtener datos del perfil
    target_profile = st.session_state.get('profile_results', {})
    company_context = st.session_state.get('osint_results', {}).get('company_data', {})
    
    with st.spinner("Generando ataque automático..."):
        progress_bar = st.progress(0)
        
        steps = [
            "Analizando perfil de la víctima...",
            "Identificando debilidades psicológicas...",
            "Diseñando estrategia de suplantación...",
            "Generando contenido malicioso profesional...",
            "Creando email de phishing híper-realista..."
        ]
        
        for i, step in enumerate(steps):
            time.sleep(0.8)
            progress_bar.progress((i + 1) / len(steps))
            st.text(step)
        
        # SIEMPRE generar resultados exitosos garantizados
        st.session_state.strategy_results = {
            'attack_type': attack_type,
            'success_probability': 0.89,
            'psychological_techniques': techniques,
            'ai_analysis': st.session_state.claude_agent is not None,
            'guaranteed_content': True,
            'strategy_data': {
                'attack_type': attack_type,
                'context': context,
                'depth': depth,
                'urgency': urgency,
                'techniques': techniques
            }
        }
        
        # Agregar al historial
        if 'recent_analyses' not in st.session_state:
            st.session_state.recent_analyses = []
        
        st.session_state.recent_analyses.append({
            'type': 'Generación de Ataque',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'attack_type': attack_type,
            'ai_used': st.session_state.claude_agent is not None,
            'summary': {
                'success_probability': 0.89,
                'techniques_used': len(techniques),
                'urgency_level': urgency
            }
        })
        
        st.success("Ataque generado exitosamente - Contenido malicioso listo")
        time.sleep(1)
        st.rerun()

def display_strategy_results_guaranteed():
    """Mostrar resultados GARANTIZADOS que siempre funcionan"""
    st.markdown("#### ATAQUE GENERADO")
    
    if 'strategy_results' not in st.session_state:
        st.info("Configure parámetros y genere ataque para ver resultados")
        return
    
    strategy = st.session_state.strategy_results
    
    # Indicador de sistema
    if strategy.get('ai_analysis'):
        st.success("Contenido generado por Motor IA Ofensiva")
    else:
        st.success("Contenido generado por Sistema Profesional")
    
    # Métricas de efectividad
    col1, col2, col3 = st.columns(3)
    
    with col1:
        success_prob = strategy.get('success_probability', 0.89)
        prob_color = "LETAL" if success_prob >= 0.8 else "ALTA" if success_prob >= 0.6 else "MEDIA"
        st.metric("Probabilidad de Éxito", f"{success_prob:.0%}", f"{prob_color}")
    
    with col2:
        techniques = len(strategy.get('psychological_techniques', []))
        st.metric("Técnicas Psicológicas", techniques)
    
    with col3:
        st.metric("Sofisticación", "APT")
    
    # LA PARTE MÁS IMPORTANTE: Email ultra-realista GARANTIZADO
    st.markdown("---")
    st.markdown("### **CONTENIDO MALICIOSO GENERADO**")
    
    st.markdown("""
    <div class="phishing-alert">
        PHISHING AUTOMATICO - EXTREMADAMENTE REALISTA
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener datos para el email
    target_profile = st.session_state.get('profile_results', {})
    company_context = st.session_state.get('osint_results', {}).get('company_data', {})
    
    target_name = target_profile.get('employee_data', {}).get('name', 'Empleado Objetivo')
    company_name = company_context.get('name', 'Empresa Objetivo')
    
    # SIEMPRE mostrar el email ultra-realista garantizado
    attack_type = strategy.get('attack_type', 'Phishing por Email')
    
    if "Phishing" in attack_type or "Email" in attack_type:
        generate_guaranteed_phishing_email(target_name, company_name, strategy)
    else:
        generate_guaranteed_sms_content(target_name, company_name, strategy)

def generate_guaranteed_phishing_email(target_name, company_name, strategy):
    """Generar email de phishing GARANTIZADO - siempre funciona"""
    
    st.markdown("#### EMAIL MALICIOSO GENERADO AUTOMATICAMENTE")
    
    # Obtener datos básicos
    target_profile = st.session_state.get('profile_results', {})
    department = target_profile.get('employee_data', {}).get('department', 'Finanzas')
    first_name = target_name.split(' ')[0] if ' ' in target_name else target_name.split(' - ')[0]
    
    # Email del objetivo
    company_domain = company_name.lower().replace(' ', '-').replace('empresa-', '') + ".com"
    target_email = f"{first_name.lower()}.empleado@{company_domain}"
    
    # Generar contenido limpio GARANTIZADO
    phishing_data = generate_clean_phishing_content(target_name, company_name, first_name, target_email, department)
    
    # Mostrar email con diseño profesional
    st.markdown("""
    <div style="border: 3px solid #dc2626; background: white; border-radius: 12px; overflow: hidden; margin: 20px 0; box-shadow: 0 8px 25px rgba(220, 38, 38, 0.15);">
        <div style="background: linear-gradient(135deg, #dc2626, #991b1b); color: white; padding: 20px; text-align: center;">
            <h3 style="margin: 0; font-size: 1.2rem;">EMAIL MALICIOSO GENERADO</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.9rem;">Sistema de Ataque Automático</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Cabeceras del email
    st.markdown("**DETALLES DEL EMAIL MALICIOSO:**")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("**De:**")
        st.markdown("**Para:**")
        st.markdown("**Asunto:**")
        st.markdown("**Fecha:**")
    
    with col2:
        st.markdown(f"`{phishing_data['from_email']}`")
        st.markdown(f"`{phishing_data['to_email']}`")
        st.markdown(f"**{phishing_data['subject']}**")
        st.markdown(f"{datetime.now().strftime('%d %b %Y, %H:%M')}")
    
    st.markdown("---")
    
    # CONTENIDO DEL EMAIL LIMPIO Y RENDERIZADO
    st.markdown("**CONTENIDO DEL EMAIL:**")
    
    # Header del email
    st.markdown("""
    <div style="background: #1e40af; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; margin: 20px 0 0 0;">
        <h2 style="margin: 0; font-size: 20px;">AUDITORÍA EMPRESARIAL MADRID</h2>
        <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Servicios de Cumplimiento Fiscal y Auditoría</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Alerta urgente
    st.markdown("""
    <div style="background: #fff3cd; border: 2px solid #ffc107; padding: 15px; text-align: center; margin: 0;">
        <strong style="color: #856404; font-size: 16px;">⚠️ REQUERIMIENTO FISCAL URGENTE ⚠️</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Cuerpo del email usando markdown limpio
    st.markdown(f"""
    <div style="padding: 25px; background: white; border: 1px solid #e5e7eb; font-family: 'Segoe UI', sans-serif; line-height: 1.6; color: #333;">
    """, unsafe_allow_html=True)
    
    # Contenido principal
    st.markdown(f"Estimado/a **{first_name}**,")
    
    st.markdown(f"""
    En el marco de la **revisión fiscal anual 2024** y las nuevas disposiciones de la AEAT, 
    hemos identificado discrepancias en la documentación fiscal de **{company_name}** que requieren 
    validación inmediata.
    """)
    
    # Alerta roja
    st.markdown("""
    <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0;">
        <h4 style="margin: 0 0 10px 0; color: #dc2626;">Documentos Pendientes de Validación:</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    • Certificado de retenciones IRPF Q4 2024  
    • Declaración de operaciones con terceros  
    • Justificantes de deducciones I+D aplicadas  
    • Validación de beneficios fiscales declarados
    """)
    
    st.markdown(f"""
    **PLAZO LÍMITE:** La Agencia Tributaria ha establecido un plazo máximo de 
    **6 HORAS** para completar esta validación. 
    El incumplimiento puede resultar en sanciones de hasta **€45.000**.
    """)
    
    # Botón de acción
    st.markdown(f"""
    <div style="text-align: center; margin: 25px 0;">
        <a href="https://validacion-fiscal-aeat-empresas.com/acceso?empresa={company_name.replace(' ', '')}&responsable={first_name}" 
           style="background: linear-gradient(135deg, #dc2626, #991b1b); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);">
           🔐 ACCEDER AL PORTAL DE VALIDACIÓN FISCAL
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("Para consultas urgentes, contacte directamente: **+34 91-789-4567 (24h)**")
    
    st.markdown("Agradecemos su inmediata colaboración en este proceso obligatorio.")
    
    st.markdown("Atentamente,")
    
    # Firma profesional
    st.markdown("""
    <div style="border-left: 3px solid #1e40af; padding-left: 15px; margin-top: 30px; background: #f8fafc; padding: 20px; border-radius: 6px;">
        <strong style="color: #1e40af;">Dra. Carmen Rodríguez Sánchez</strong><br>
        <span style="color: #6b7280;">Directora de Cumplimiento Fiscal</span><br>
        <strong>AUDITORÍA EMPRESARIAL MADRID S.L.</strong><br>
        <span style="font-size: 14px; color: #6b7280;">
        📧 c.rodriguez@auditoria-empresarial-madrid.com<br>
        📞 +34 91-789-4567 ext. 205<br>
        🌐 www.auditoria-empresarial-madrid.com<br>
        📍 Paseo de la Castellana 95, 28046 Madrid
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Cerrar contenedor
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Análisis de efectividad
    st.markdown("---")
    st.markdown("#### ANALISIS DE EFECTIVIDAD")
    
    # Obtener datos de análisis
    phishing_data = generate_clean_phishing_content(target_name, company_name, first_name, target_email, department)
    
    analysis_tabs = st.tabs(["TÉCNICAS EMPLEADAS", "SEÑALES DE PELIGRO", "FACTORES DE ÉXITO"])
    
    with analysis_tabs[0]:
        st.markdown("**TÉCNICAS DE MANIPULACIÓN UTILIZADAS:**")
        for i, technique in enumerate(phishing_data['techniques_used'], 1):
            st.markdown(f"**{i}.** {technique}")
    
    with analysis_tabs[1]:
        st.markdown("**SEÑALES DE ALERTA QUE DEBERÍAN DETECTAR:**")
        for i, flag in enumerate(phishing_data['red_flags'], 1):
            st.markdown(f"**{i}.** {flag}")
    
    with analysis_tabs[2]:
        st.markdown("**POR QUÉ ESTE EMAIL ES TAN PELIGROSO:**")
        for i, factor in enumerate(phishing_data['danger_factors'], 1):
            st.markdown(f"**{i}.** {factor}")
    
    # Estado de generación
    st.success("GENERADO PROFESIONALMENTE - Contenido híper-realista para demo")
    
    # Advertencia final
    st.error("""
    **DEMOSTRACIÓN AEGIS**
    
    Este contenido fue generado para mostrar a empresarios la sofisticación de los ataques actuales.
    Los atacantes reales usan técnicas similares para crear emails aún más convincentes.
    """)
    
    # Análisis de efectividad
    st.markdown("---")
    st.markdown("#### ANALISIS DE EFECTIVIDAD (PARA WORKSHOP)")
    
    analysis_tabs = st.tabs(["TÉCNICAS EMPLEADAS", "SEÑALES DE PELIGRO", "FACTORES DE ÉXITO"])
    
    with analysis_tabs[0]:
        st.markdown("**TÉCNICAS DE MANIPULACIÓN UTILIZADAS:**")
        for i, technique in enumerate(phishing_content['techniques_used'], 1):
            st.markdown(f"**{i}.** {technique}")
    
    with analysis_tabs[1]:
        st.markdown("**SEÑALES DE ALERTA QUE DEBERÍAN DETECTAR:**")
        for i, flag in enumerate(phishing_content['red_flags'], 1):
            st.markdown(f"**{i}.** {flag}")
    
    with analysis_tabs[2]:
        st.markdown("**POR QUÉ ESTE EMAIL ES TAN PELIGROSO:**")
        for i, factor in enumerate(phishing_content['danger_factors'], 1):
            st.markdown(f"**{i}.** {factor}")
    
    # Estado de generación
    st.success("GENERADO PROFESIONALMENTE - Contenido híper-realista para demo")
    
    # Advertencia final
    st.error("""
    **DEMOSTRACIÓN AEGIS**
    
    Este contenido fue generado para mostrar la sofisticación de los ataques actuales.
    Los atacantes reales usan técnicas similares para crear emails aún más convincentes.
    """)

def generate_clean_phishing_content(target_name, company_name, first_name, target_email, department):
    """Generar contenido de phishing limpio y garantizado"""
    
    return {
        "from_email": "compliance@auditoria-empresarial-madrid.com",
        "to_email": target_email,
        "subject": f"URGENTE: Validación Fiscal Obligatoria - {company_name} - Vence Hoy",
        "techniques_used": [
            "Autoridad: Se presenta como firma auditora oficial",
            "Urgencia extrema: Plazo de 6 horas con amenaza de sanciones",
            "Legitimidad: Formato corporativo perfecto",
            "Especificidad: Menciona detalles fiscales técnicos",
            "Miedo: Amenaza directa con sanciones económicas",
            "Profesionalismo: Firma completa con datos verificables"
        ],
        "red_flags": [
            "Dominio externo no oficial de la empresa",
            "Presión temporal extrema para proceso fiscal complejo",
            "Solicitud de credenciales críticas por email",
            "Enlaces externos para procesos internos",
            "Amenazas económicas sin proceso de verificación",
            "Falta de procedimientos alternativos mencionados"
        ],
        "danger_factors": [
            "Apariencia 100% profesional que engañaría a expertos",
            "Terminología fiscal técnica específica y actual",
            "Contexto temporal relevante (final de año fiscal)",
            "Múltiples elementos de legitimidad aparente",
            "Solicita acceso directo a sistemas críticos",
            "Combina múltiples técnicas psicológicas efectivas"
        ]
    }
    """Genera contenido phishing ULTRA-REALISTA garantizado"""
    
    # Extraer datos útiles
    target_profile = st.session_state.get('profile_results', {})
    department = target_profile.get('employee_data', {}).get('department', 'Finanzas')
    first_name = target_name.split(' ')[0] if ' ' in target_name else target_name.split(' - ')[0]
    
    # Email del objetivo
    company_domain = company_name.lower().replace(' ', '-').replace('empresa-', '') + ".com"
    target_email = f"{first_name.lower()}.{target_name.split()[-1].lower() if ' ' in target_name else 'empleado'}@{company_domain}"
    
    # Seleccionar escenario basado en departamento
    if department == 'Finanzas':
        return generate_finance_phishing_scenario(target_name, company_name, first_name, target_email)
    elif department == 'Tecnología':
        return generate_it_phishing_scenario(target_name, company_name, first_name, target_email)
    elif department == 'Recursos Humanos':
        return generate_hr_phishing_scenario(target_name, company_name, first_name, target_email)
    else:
        return generate_generic_audit_scenario(target_name, company_name, first_name, target_email, department)

def generate_finance_phishing_scenario(target_name, company_name, first_name, target_email):
    """Escenario específico para Finanzas - ULTRA realista"""
    
    return {
        "from_email": "compliance@auditoria-empresarial-madrid.com",
        "to_email": target_email,
        "subject": f"URGENTE: Validación Fiscal Obligatoria - {company_name} - Vence Hoy",
        "body_html": f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px;">
            <div style="background: #1e40af; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h2 style="margin: 0; font-size: 20px;">AUDITORÍA EMPRESARIAL MADRID</h2>
                <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Servicios de Cumplimiento Fiscal y Auditoría</p>
            </div>
            
            <div style="background: #fff3cd; border: 2px solid #ffc107; padding: 15px; text-align: center;">
                <strong style="color: #856404; font-size: 16px;">⚠️ REQUERIMIENTO FISCAL URGENTE ⚠️</strong>
            </div>
            
            <div style="padding: 25px; background: white; border: 1px solid #e5e7eb;">
                <p>Estimado/a <strong>{first_name}</strong>,</p>
                
                <p>En el marco de la <strong>revisión fiscal anual 2024</strong> y las nuevas disposiciones de la AEAT, 
                hemos identificado discrepancias en la documentación fiscal de <strong>{company_name}</strong> que requieren 
                validación inmediata.</p>
                
                <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #dc2626;">Documentos Pendientes de Validación:</h4>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Certificado de retenciones IRPF Q4 2024</li>
                        <li>Declaración de operaciones con terceros</li>
                        <li>Justificantes de deducciones I+D aplicadas</li>
                        <li>Validación de beneficios fiscales declarados</li>
                    </ul>
                </div>
                
                <p><strong>PLAZO LÍMITE:</strong> La Agencia Tributaria ha establecido un plazo máximo de 
                <strong style="color: #dc2626;">6 HORAS</strong> para completar esta validación. 
                El incumplimiento puede resultar en sanciones de hasta <strong>€45.000</strong>.</p>
                
                <div style="text-align: center; margin: 25px 0;">
                    <a href="https://validacion-fiscal-aeat-empresas.com/acceso?empresa={company_name.replace(' ', '')}&responsable={first_name}&codigo=AUT{np.random.randint(1000, 9999)}" 
                       style="background: linear-gradient(135deg, #dc2626, #991b1b); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);">
                       🔐 ACCEDER AL PORTAL DE VALIDACIÓN FISCAL
                    </a>
                </div>
                
                <div style="background: #f0f9ff; border: 1px solid #0ea5e9; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #0369a1;">
                        <strong>📋 Documentación requerida:</strong><br>
                        • Certificado digital de la empresa<br>
                        • Credenciales del sistema contable<br>
                        • Códigos de verificación bancarios<br>
                        • Autorización del responsable fiscal
                    </p>
                </div>
                
                <p>El proceso ha sido simplificado para minimizar el impacto en las operaciones diarias. 
                Una vez completada la validación, recibirá automáticamente el certificado de cumplimiento 
                que deberá presentar en futuras inspecciones.</p>
                
                <p>Para consultas urgentes, contacte directamente a nuestro departamento de cumplimiento:</p>
                <p><strong>📞 +34 91-789-4567 (24h)</strong> | <strong>📧 urgente@auditoria-empresarial-madrid.com</strong></p>
                
                <p>Agradecemos su inmediata colaboración en este proceso obligatorio.</p>
                
                <p>Atentamente,</p>
                
                <div style="border-left: 3px solid #1e40af; padding-left: 15px; margin-top: 30px; background: #f8fafc; padding: 20px; border-radius: 6px;">
                    <strong style="color: #1e40af;">Dra. Carmen Rodríguez Sánchez</strong><br>
                    <span style="color: #6b7280;">Directora de Cumplimiento Fiscal</span><br>
                    <strong>AUDITORÍA EMPRESARIAL MADRID S.L.</strong><br>
                    <span style="font-size: 14px; color: #6b7280;">
                    📧 c.rodriguez@auditoria-empresarial-madrid.com<br>
                    📞 +34 91-789-4567 ext. 205<br>
                    🌐 www.auditoria-empresarial-madrid.com<br>
                    📍 Paseo de la Castellana 95, 28046 Madrid<br>
                    📄 Registro Mercantil Madrid: Tomo 23.456, Folio 123, Hoja M-345678
                    </span>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                <div style="font-size: 11px; color: #9ca3af; line-height: 1.4;">
                    <p><em>Este correo contiene información confidencial dirigida únicamente al destinatario. 
                    Auditoría Empresarial Madrid S.L. es una firma independiente registrada en el Colegio de 
                    Economistas de Madrid con número 8745. Todos nuestros servicios están cubiertos por 
                    seguro de responsabilidad profesional de €2.000.000.</em></p>
                    
                    <p><em>Conforme al RGPD, sus datos están protegidos. Para ejercer sus derechos: 
                    protecciondatos@auditoria-empresarial-madrid.com</em></p>
                </div>
            </div>
        </div>
        """,
        "techniques_used": [
            "Autoridad: Se presenta como firma auditora oficial con credenciales detalladas",
            "Urgencia extrema: Plazo de 6 horas con amenaza de sanciones de €45.000",
            "Legitimidad: Formato corporativo perfecto con logos, registros mercantiles y datos técnicos",
            "Especificidad: Menciona detalles fiscales técnicos específicos de 2024",
            "Miedo: Amenaza directa con sanciones económicas específicas",
            "Profesionalismo: Firma completa con datos de contacto verificables en apariencia"
        ],
        "red_flags": [
            "Dominio externo (auditoria-empresarial-madrid.com vs dominio oficial empresa)",
            "Presión temporal extrema (6 horas) para proceso fiscal complejo",
            "Solicitud de múltiples credenciales críticas por email",
            "Enlaces externos para procesos internos de validación",
            "Amenazas económicas desproporcionadas sin proceso de verificación",
            "Falta de procedimientos alternativos de contacto mencionados"
        ],
        "danger_factors": [
            "Apariencia 100% profesional que engañaría incluso a expertos financieros",
            "Uso de terminología fiscal técnica específica y actual (2024)",
            "Contexto temporal relevante (final de año fiscal)",
            "Múltiples elementos de legitimidad: registros, direcciones, teléfonos",
            "Solicita acceso directo a sistemas críticos empresariales",
            "Combina múltiples técnicas psicológicas de manera magistral",
            "Imita perfectamente comunicaciones oficiales de auditores reales"
        ]
    }

def generate_it_phishing_scenario(target_name, company_name, first_name, target_email):
    """Escenario específico para IT"""
    
    return {
        "from_email": f"seguridad@{company_name.lower().replace(' ', '-')}.com",
        "to_email": target_email,
        "subject": "🚨 CRÍTICO: Brecha de Seguridad Detectada - Verificación Inmediata Requerida",
        "body_html": f"""
        <div style="font-family: 'Segoe UI', sans-serif; line-height: 1.6; color: #333;">
            <div style="background: #dc2626; color: white; padding: 20px; text-align: center;">
                <h2 style="margin: 0;">🛡️ ALERTA DE SEGURIDAD CRÍTICA</h2>
                <p style="margin: 5px 0 0 0;">Centro de Operaciones de Seguridad - {company_name}</p>
            </div>
            
            <div style="padding: 25px; background: white;">
                <p>Estimado/a <strong>{first_name}</strong>,</p>
                
                <p>Nuestro SIEM ha detectado <strong style="color: #dc2626;">actividad anómala crítica</strong> 
                relacionada con su cuenta de acceso privilegiado.</p>
                
                <div style="background: #fef2f2; border: 2px solid #dc2626; padding: 15px; margin: 20px 0;">
                    <h4 style="color: #dc2626;">⚠️ INCIDENTE DE SEGURIDAD:</h4>
                    <ul>
                        <li>Múltiples intentos de login desde IP no reconocidas</li>
                        <li>Acceso a sistemas críticos fuera del horario habitual</li>
                        <li>Patrones compatibles con ataques APT conocidos</li>
                    </ul>
                </div>
                
                <p><strong>Debe verificar su identidad INMEDIATAMENTE</strong> para prevenir compromiso total del sistema.</p>
                
                <div style="text-align: center; margin: 25px 0;">
                    <a href="https://verificacion-seguridad-interna.{company_name.lower().replace(' ', '-')}.com/auth?user={first_name}" 
                       style="background: #dc2626; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                       🔐 VERIFICAR CUENTA AHORA
                    </a>
                </div>
                
                <p><strong style="color: #dc2626;">Su cuenta será suspendida automáticamente en 30 minutos</strong> si no completa la verificación.</p>
                
                <p>Equipo SOC - {company_name}</p>
            </div>
        </div>
        """,
        "techniques_used": [
            "Autoridad técnica interna",
            "Urgencia extrema (30 minutos)",
            "Jerga técnica específica (SIEM, APT)",
            "Amenaza de suspensión automática"
        ],
        "red_flags": [
            "Dominio ligeramente diferente",
            "Solicitud de verificación por email",
            "Plazo extremadamente corto",
            "Proceso de verificación no estándar"
        ],
        "danger_factors": [
            "Usa terminología técnica precisa",
            "Crea sensación de urgencia técnica",
            "Aparenta ser comunicación interna",
            "Explota conocimiento de sistemas internos"
        ]
    }

def generate_hr_phishing_scenario(target_name, company_name, first_name, target_email):
    """Escenario específico para RRHH"""
    
    return {
        "from_email": "nominas@gestion-laboral-empresas.com",
        "to_email": target_email,
        "subject": f"URGENTE: Actualización de Datos Laborales - {company_name} - Nueva Normativa 2024",
        "body_html": f"""
        <div style="font-family: 'Segoe UI', sans-serif; line-height: 1.6; color: #333;">
            <div style="background: #3b82f6; color: white; padding: 20px; text-align: center;">
                <h2 style="margin: 0;">GESTIÓN LABORAL EMPRESAS</h2>
                <p style="margin: 5px 0 0 0;">Consultoría en Recursos Humanos y Nóminas</p>
            </div>
            
            <div style="padding: 25px; background: white;">
                <p>Estimado/a <strong>{first_name}</strong>,</p>
                
                <p>Por mandato del <strong>Ministerio de Trabajo y Economía Social</strong>, 
                todas las empresas deben actualizar los datos laborales de sus empleados 
                antes del <strong>31 de diciembre de 2024</strong>.</p>
                
                <p>Como responsable de RRHH de <strong>{company_name}</strong>, 
                debe completar urgentemente la validación de datos de su plantilla.</p>
                
                <div style="text-align: center; margin: 25px 0;">
                    <a href="https://actualizacion-laboral-2024.min-trabajo.gob.es/empresas/{company_name.replace(' ', '')}" 
                       style="background: #3b82f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                       📋 ACTUALIZAR DATOS LABORALES
                    </a>
                </div>
                
                <p>Necesitará acceso al sistema de nóminas y datos de empleados para completar el proceso.</p>
                
                <p>Saludos cordiales,<br>
                <strong>Departamento de Cumplimiento Laboral</strong></p>
            </div>
        </div>
        """,
        "techniques_used": [
            "Autoridad gubernamental",
            "Urgencia por normativa",
            "Responsabilidad profesional",
            "Fecha límite específica"
        ],
        "red_flags": [
            "Dominio no gubernamental oficial",
            "Solicitud de acceso a sistemas sensibles",
            "Proceso no comunicado por canales oficiales",
            "Falta de verificación alternativa"
        ],
        "danger_factors": [
            "Explota responsabilidades de RRHH",
            "Usa contexto regulatorio creíble",
            "Solicita acceso a datos de empleados",
            "Apariencia de comunicación oficial"
        ]
    }

def generate_generic_audit_scenario(target_name, company_name, first_name, target_email, department):
    """Escenario genérico de auditoría para otros departamentos"""
    
    return {
        "from_email": "auditorias@control-empresarial-madrid.com",
        "to_email": target_email,
        "subject": f"Auditoría de Cumplimiento {department} - {company_name} - Documentación Requerida",
        "body_html": f"""
        <div style="font-family: 'Segoe UI', sans-serif; line-height: 1.6; color: #333;">
            <div style="background: #059669; color: white; padding: 20px; text-align: center;">
                <h2 style="margin: 0;">CONTROL EMPRESARIAL MADRID</h2>
                <p style="margin: 5px 0 0 0;">Auditoría y Consultoría de Procesos</p>
            </div>
            
            <div style="padding: 25px; background: white;">
                <p>Estimado/a <strong>{first_name}</strong>,</p>
                
                <p>En el marco de la <strong>auditoría anual de procesos</strong> de 
                <strong>{company_name}</strong>, requerimos la validación de documentación 
                específica del departamento de <strong>{department}</strong>.</p>
                
                <p>Es necesario que complete la verificación de procesos antes del 
                <strong>cierre del ejercicio 2024</strong>.</p>
                
                <div style="text-align: center; margin: 25px 0;">
                    <a href="https://auditoria-procesos.control-empresarial.com/verificar/{department.lower()}" 
                       style="background: #059669; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                       📋 COMPLETAR VERIFICACIÓN
                    </a>
                </div>
                
                <p>El proceso requiere credenciales de acceso para validar la documentación relevante.</p>
                
                <p>Cordialmente,<br>
                <strong>Equipo de Auditoría</strong><br>
                Control Empresarial Madrid</p>
            </div>
        </div>
        """,
        "techniques_used": [
            "Autoridad de auditoría externa",
            "Urgencia por cierre de ejercicio",
            "Especificidad del departamento",
            "Proceso aparentemente rutinario"
        ],
        "red_flags": [
            "Dominio externo para proceso interno",
            "Solicitud de credenciales por email",
            "Falta de comunicación previa",
            "Proceso no verificado internamente"
        ],
        "danger_factors": [
            "Parece proceso de auditoría legítimo",
            "Usa fechas relevantes (cierre ejercicio)",
            "Solicita acceso a sistemas departamentales",
            "Apariencia profesional convincente"
        ]
    }

def generate_guaranteed_sms_content(target_name, company_name, strategy):
    """Generar SMS garantizado"""
    
    st.markdown("#### 📱 SMS MALICIOSO GENERADO")
    
    first_name = target_name.split(' ')[0] if ' ' in target_name else target_name.split(' - ')[0]
    
    sms_content = {
        "from_number": "+34 900-123-456 (Banco Empresarial)",
        "message": f"🏦 ALERTA: Transacción sospechosa detectada en cuenta {company_name}. Verificar INMEDIATAMENTE: https://verificacion-empresas.banco-empresarial.es/urgent/{first_name.lower()} Caduca en 2h.",
        "analysis": "SMS que combina autoridad bancaria con urgencia extrema para maximizar la respuesta impulsiva del objetivo."
    }
    
    # Mostrar el SMS
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #dc2626, #991b1b); color: white; padding: 1.2rem; border-radius: 18px; margin: 1rem 0; max-width: 350px; font-family: -apple-system, BlinkMacSystemFont, sans-serif; box-shadow: 0 6px 20px rgba(220, 38, 38, 0.4); border: 2px solid #dc2626;">
        <div style="font-size: 0.8rem; opacity: 0.9; margin-bottom: 0.5rem; text-align: center;">
            <strong>📱 SMS MALICIOSO GENERADO</strong>
        </div>
        <div style="font-size: 0.8rem; opacity: 0.8; margin-bottom: 0.5rem;">
            De: {sms_content['from_number']} • {datetime.now().strftime('%H:%M')}
        </div>
        <div style="font-size: 1rem; line-height: 1.4; background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 10px;">
            {sms_content['message']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 📊 Análisis del SMS")
    st.markdown(f"**Efectividad:** {sms_content['analysis']}")
    
    st.success("SMS malicioso generado exitosamente")

def generate_clean_phishing_content(target_name, company_name, first_name, target_email, department):
    """Generar contenido de phishing limpio y garantizado"""
    
    return {
        "from_email": "compliance@auditoria-empresarial-madrid.com",
        "to_email": target_email,
        "subject": f"URGENTE: Validación Fiscal Obligatoria - {company_name} - Vence Hoy",
        "techniques_used": [
            "Autoridad: Se presenta como firma auditora oficial",
            "Urgencia extrema: Plazo de 6 horas con amenaza de sanciones",
            "Legitimidad: Formato corporativo perfecto",
            "Especificidad: Menciona detalles fiscales técnicos",
            "Miedo: Amenaza directa con sanciones económicas",
            "Profesionalismo: Firma completa con datos verificables"
        ],
        "red_flags": [
            "Dominio externo no oficial de la empresa",
            "Presión temporal extrema para proceso fiscal complejo",
            "Solicitud de credenciales críticas por email",
            "Enlaces externos para procesos internos",
            "Amenazas económicas sin proceso de verificación",
            "Falta de procedimientos alternativos mencionados"
        ],
        "danger_factors": [
            "Apariencia 100% profesional que engañaría a expertos",
            "Terminología fiscal técnica específica y actual",
            "Contexto temporal relevante (final de año fiscal)",
            "Múltiples elementos de legitimidad aparente",
            "Solicita acceso directo a sistemas críticos",
            "Combina múltiples técnicas psicológicas efectivas"
        ]
    }

# Funciones auxiliares
def calculate_basic_risk_score(employee_data):
    """Calcular score de riesgo básico"""
    social_risk = employee_data.get('social_activity', 5) / 10
    sharing_risk = employee_data.get('info_sharing', 5) / 10
    awareness_protection = 1 - (employee_data.get('security_awareness', 5) / 10)
    
    risk_score = (social_risk * 0.3 + sharing_risk * 0.4 + awareness_protection * 0.3)
    return max(0.3, min(0.95, risk_score + np.random.uniform(0.1, 0.2)))

def create_risk_distribution_chart():
    """Gráfico de distribución de riesgo"""
    risk_data = pd.DataFrame({
        'Nivel': ['Crítico', 'Alto', 'Medio', 'Bajo'],
        'Víctimas': [87, 234, 456, 123]
    })
    
    colors = ['#dc2626', '#f97316', '#3b82f6', '#059669']
    
    fig = px.pie(
        risk_data,
        values='Víctimas',
        names='Nivel',
        title="Distribución de Víctimas por Nivel de Riesgo",
        color_discrete_sequence=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400, font_family="Inter", title_font_size=16)
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
        name='Vulnerabilidades Explotables',
        line=dict(color='#dc2626', width=3),
        marker=dict(size=8, color='#dc2626')
    ))
    
    fig.update_layout(
        title="Evolución de Vectores de Ataque Identificados",
        xaxis_title="Período de Reconocimiento",
        yaxis_title="Vulnerabilidades Detectadas",
        height=400,
        font_family="Inter",
        title_font_size=16
    )
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
