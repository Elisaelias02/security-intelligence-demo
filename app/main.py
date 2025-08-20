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
    
    # Header principal - Estilo "sistema del atacante"
    st.markdown("""
    <div class="main-header">
        <h1>🎯 SISTEMA DE ATAQUE AVANZADO</h1>
        <div class="subtitle">Plataforma de Ingeniería Social y Phishing Automatizado</div>
        <div class="badge">IA Ofensiva • Workshop Demostrativo</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar estado de API
    display_api_status(api_status)
    
    # Sidebar estilo "atacante"
    with st.sidebar:
        st.markdown("### ⚡ Configuración de Ataque")
        
        # Estado de Claude - más agresivo
        st.markdown("#### 🤖 Motor de IA Ofensiva")
        
        if api_status['api_available']:
            st.success("🎯 Sistema IA OPERATIVO")
            st.info(f"🧠 Modelo: {api_status.get('model', 'claude-3-haiku')}")
            st.success("✅ Generación de contenido malicioso: ACTIVA")
        else:
            st.error("❌ Motor IA DESCONECTADO")
            st.warning("⚠️ Funcionalidad limitada sin IA")
            
            # Opción para ingresar API key - más directo
            manual_key = st.text_input(
                "🔑 Clave API Anthropic (REQUERIDA)", 
                type="password",
                help="Sin IA no hay demo real. La generación automática de phishing requiere Claude."
            )
            
            if manual_key and st.button("🚀 ACTIVAR MOTOR IA"):
                if create_claude_agent:
                    st.session_state.claude_agent = create_claude_agent(manual_key)
                    st.rerun()
                else:
                    st.error("Error: Componente Claude no disponible")
        
        st.markdown("---")
        
        # Configuraciones de ataque
        analysis_depth = st.selectbox(
            "🎯 Nivel de Sofisticación",
            ["Básico", "Estándar", "Avanzado", "APT (Estado-Nación)"]
        )
        
        max_targets = st.slider("🎪 Objetivos Simultáneos", 1, 50, 10)
        
        # Mostrar "capacidades maliciosas"
        st.markdown("### 💀 Capacidades del Sistema")
        st.error("""
        **🎯 Arsenal Disponible:**
        
        🕵️ Reconocimiento OSINT automatizado
        🧠 Perfilado psicológico con IA
        📧 Generación de phishing híper-realista  
        📱 Campañas de smishing personalizadas
        🎭 Suplantación de identidad avanzada
        """)
        
        # Advertencia ética
        st.markdown("---")
        st.warning("""
        ⚖️ **DEMO EDUCATIVA**
        
        Este sistema simula herramientas reales de atacantes para concientizar sobre amenazas actuales.
        """)
    
    # Tabs principales - estilo "operaciones ofensivas"
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Centro de Comando",
        "🕵️ Reconocimiento OSINT", 
        "🧠 Perfilado de Víctimas",
        "📧 Generador de Phishing"
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
    """Mostrar estado de la API estilo 'sistema del atacante'"""
    
    if status['status'] == 'active':
        st.markdown(f"""
        <div class="api-status active">
            <strong>🎯 MOTOR IA OFENSIVA: OPERATIVO</strong><br>
            Sistema de generación de contenido malicioso activo<br>
            <small>🧠 Modelo: {status.get('model', 'N/A')} | 📧 Phishing automático: HABILITADO</small>
        </div>
        """, unsafe_allow_html=True)
    
    elif status['status'] == 'simulation_mode':
        st.markdown(f"""
        <div class="api-status warning">
            <strong>⚠️ MOTOR IA: MODO LIMITADO</strong><br>
            Generación automática de phishing DESHABILITADA<br>
            <small>🚨 Para demo completa, active el motor IA</small>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.markdown(f"""
        <div class="api-status error">
            <strong>❌ MOTOR IA: OFFLINE</strong><br>
            {status['message']}<br>
            <small>💀 Sin IA no hay phishing automático - Demo limitada</small>
        </div>
        """, unsafe_allow_html=True)

def create_executive_dashboard():
    """Centro de comando estilo 'atacante'"""
    st.markdown("""
    <div class="section-header">
        <h3>🎯 Centro de Comando - Operaciones Activas</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas estilo "operaciones maliciosas"
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
    
    # Mostrar "operaciones recientes"
    if 'recent_analyses' in st.session_state and st.session_state.recent_analyses:
        st.markdown("""
        <div class="section-header">
            <h3>📊 Operaciones Recientes</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for analysis in st.session_state.recent_analyses[-3:]:
            with st.expander(f"🎯 Operación: {analysis.get('type', 'N/A')} - {analysis.get('timestamp', 'N/A')}"):
                st.json(analysis.get('summary', {}))
    else:
        st.info("🎪 No hay operaciones activas. Inicie reconocimiento OSINT o perfilado de víctimas para comenzar.")
    
    # Advertencia de demo
    st.error("""
    🎭 **DEMOSTRACIÓN EDUCATIVA EN CURSO**
    
    Esta interfaz simula cómo operan realmente los cibercriminales modernos.
    Los empresarios pueden ver la sofisticación de las amenazas actuales.
    """)
    
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
    """Generador de phishing automático - estilo 'atacante'"""
    st.markdown("""
    <div class="section-header">
        <h3>📧 Generador Automático de Phishing</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar IA disponible PRIMERO
    if not st.session_state.claude_agent:
        st.error("""
        🚨 **MOTOR IA REQUERIDO PARA DEMO**
        
        La generación automática de phishing es el núcleo de esta demostración.
        Sin IA, no hay contenido realista para mostrar a los empresarios.
        
        **Configure la clave API en el sidebar para continuar.**
        """)
        
        with st.expander("🔧 ¿Cómo configurar la API?"):
            st.markdown("""
            **Pasos para activar el motor IA:**
            
            1. 🔑 **Obtener clave API**: Regístrese en https://console.anthropic.com
            2. 📝 **Copiar clave**: En el dashboard, vaya a "API Keys"
            3. 🔧 **Configurar**: Pegue la clave en el sidebar izquierdo
            4. 🚀 **Activar**: Haga clic en "ACTIVAR MOTOR IA"
            
            **⚠️ Sin API, la demo pierde todo su impacto educativo.**
            """)
        
        st.warning("""
        💡 **Para el Workshop:**
        - La IA genera emails 100% realistas
        - Personalización automática por víctima  
        - Técnicas de ingeniería social avanzadas
        - Sin IA = Sin demo impactante
        """)
        return
    
    st.success("🎯 **Motor IA Operativo** - Generación automática de phishing habilitada")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("#### ⚙️ Configuración del Ataque")
        
        # Verificar si hay perfiles previos
        if 'profile_results' in st.session_state:
            st.success("🎯 Víctima perfilada detectada")
            target_name = st.session_state.profile_results.get('employee_data', {}).get('name', 'Objetivo')
            st.write(f"**🎪 Víctima Principal**: {target_name}")
        else:
            st.warning("⚠️ Ejecute perfilado de víctima para maximizar efectividad")
        
        attack_type = st.selectbox(
            "🎭 Vector de Ataque",
            [
                "📧 Phishing por Email (Híper-realista)",
                "📱 Smishing (SMS Malicioso)"
            ]
        )
        
        scenario_context = st.text_area(
            "🎬 Contexto de Explotación",
            "Temporada de auditorías fiscales\nPresión por cierre de trimestre\nCambios en sistemas de seguridad\nReorganización corporativa en curso",
            height=100,
            help="Contexto que el atacante usaría para hacer creíble el engaño"
        )
        
        strategy_depth = st.selectbox(
            "💀 Nivel de Sofisticación",
            ["🔰 Básico", "⚡ Avanzado", "💀 APT (Estado-Nación)"]
        )
        
        urgency_level = st.selectbox(
            "⏰ Presión Psicológica",
            ["🟢 Baja", "🟡 Media", "🟠 Alta", "🔴 Crítica"]
        )
        
        social_engineering_focus = st.multiselect(
            "🧠 Arsenal Psicológico",
            ["👑 Autoridad", "⚡ Urgencia", "🤝 Reciprocidad", "💎 Escasez", "👥 Validación Social", "🎯 Compromiso"],
            default=["👑 Autoridad", "⚡ Urgencia"],
            help="Técnicas de manipulación psicológica a combinar"
        )
        
        # Botón de generación más dramático
        if st.button("🚀 GENERAR ATAQUE AUTOMÁTICO", type="primary"):
            run_strategy_generation_forced_ai(attack_type, scenario_context, strategy_depth, urgency_level, social_engineering_focus)
    
    with col2:
        display_strategy_results_attacker_style()

def run_strategy_generation_forced_ai(attack_type, context, depth, urgency, techniques):
    """Generar estrategia SIEMPRE con IA - forzado para demo"""
    
    # VERIFICACIÓN CRÍTICA: Sin IA no hay demo
    if not st.session_state.claude_agent:
        st.error("🚨 MOTOR IA REQUERIDO - Configurar en sidebar")
        return
    
    # Obtener datos del perfil si están disponibles
    target_profile = st.session_state.get('profile_results', {})
    company_context = st.session_state.get('osint_results', {}).get('company_data', {})
    
    with st.spinner("🎯 Generando ataque automático con IA..."):
        progress_bar = st.progress(0)
        
        steps = [
            "🕵️ Analizando perfil de la víctima...",
            "🧠 Identificando debilidades psicológicas...",
            "🎭 Diseñando estrategia de suplantación...",
            "🤖 Motor IA generando contenido malicioso...",
            "📧 Creando email de phishing híper-realista..."
        ]
        
        for i, step in enumerate(steps):
            time.sleep(0.8)
            progress_bar.progress((i + 1) / len(steps))
            st.text(step)
        
        try:
            # SIEMPRE usar Claude - es fundamental para la demo
            strategy_data = {
                'attack_type': attack_type,
                'context': context,
                'depth': depth,
                'urgency': urgency,
                'techniques': techniques,
                'target_profile': target_profile,
                'company_context': company_context
            }
            
            # Llamar al agente Claude con los argumentos correctos
            claude_strategy = st.session_state.claude_agent.generate_attack_simulation(
                target_profile, company_context
            )
            
            st.session_state.strategy_results = {
                **claude_strategy,
                'strategy_data': strategy_data,
                'ai_analysis': True,
                'forced_ai': True  # Marca que fue forzado para demo
            }
            
            # Agregar al historial
            if 'recent_analyses' not in st.session_state:
                st.session_state.recent_analyses = []
            
            st.session_state.recent_analyses.append({
                'type': '🎯 Generación de Ataque',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'attack_type': attack_type,
                'ai_used': True,  # Siempre True para demo
                'summary': {
                    'success_probability': st.session_state.strategy_results.get('success_probability', 0.85),
                    'techniques_used': len(techniques),
                    'urgency_level': urgency
                }
            })
            
        except Exception as e:
            st.error(f"🚨 Error en motor IA: {e}")
            st.error("Sin IA no hay demo efectiva. Verifique configuración.")
            return
        
        st.success("🎯 Ataque generado exitosamente - Contenido malicioso listo")
        time.sleep(1)
        st.rerun()

def display_strategy_results_attacker_style():
    """Mostrar resultados estilo 'atacante' con énfasis en phishing"""
    st.markdown("#### 🎯 Ataque Generado")
    
    if 'strategy_results' not in st.session_state:
        st.info("⚡ Configure parámetros y genere ataque para ver resultados")
        return
    
    strategy = st.session_state.strategy_results
    
    # Indicador de IA - siempre debería estar activo para demo
    if strategy.get('ai_analysis'):
        st.success("🤖 Contenido generado por Motor IA Ofensiva")
        
        # Métricas de "efectividad del ataque"
        col1, col2, col3 = st.columns(3)
        
        with col1:
            success_prob = strategy.get('success_probability', 0.85)
            prob_color = "💀 Letal" if success_prob >= 0.8 else "🔥 Alta" if success_prob >= 0.6 else "⚡ Media"
            st.metric("🎯 Probabilidad de Éxito", f"{success_prob:.0%}", f"{prob_color}")
        
        with col2:
            techniques = len(strategy.get('psychological_techniques', []))
            st.metric("🧠 Técnicas Psicológicas", techniques)
        
        with col3:
            complexity = strategy.get('complexity_level', 'APT')
            st.metric("💀 Sofisticación", complexity)
        
        # LA PARTE MÁS IMPORTANTE: Generación de contenido malicioso
        st.markdown("---")
        st.markdown("### 🎭 **CONTENIDO MALICIOSO GENERADO**")
        st.error("**⚠️ PHISHING AUTOMÁTICO - EXTREMADAMENTE REALISTA**")
        
        # SIEMPRE generar contenido con IA
        generate_attack_content_section_forced(strategy)
        
    else:
        # Esto NO debería pasar en la demo
        st.error("🚨 ERROR: Motor IA no disponible - Demo comprometida")
        st.error("Configure clave API para demostración completa")

def generate_attack_content_section_forced(strategy):
    """Generar contenido SIEMPRE con IA - núcleo de la demo"""
    
    # Obtener datos del contexto
    target_profile = st.session_state.get('profile_results', {})
    company_context = st.session_state.get('osint_results', {}).get('company_data', {})
    
    target_name = target_profile.get('employee_data', {}).get('name', 'Empleado Objetivo')
    company_name = company_context.get('name', 'Empresa Objetivo')
    
    # Determinar tipo de ataque
    attack_type = strategy.get('strategy_data', {}).get('attack_type', '📧 Phishing por Email (Híper-realista)')
    
    if "📧" in attack_type or "Phishing" in attack_type:
        generate_phishing_email_content_attacker(target_name, company_name, strategy)
    elif "📱" in attack_type or "Smishing" in attack_type:
        generate_smishing_content_attacker(target_name, company_name, strategy)

def generate_phishing_email_content_attacker(target_name, company_name, strategy):
    """Generar email de phishing con IA - estilo 'herramienta de atacante'"""
    
    st.markdown("#### 📧 Email Malicioso Generado Automáticamente")
    
    # Intentar generar con IA, con fallback si falla
    phishing_content = generate_ai_phishing_email_forced(target_name, company_name, strategy)
    
    if not phishing_content:
        st.error("🚨 Error en motor IA - Usando contenido de emergencia")
        # Obtener datos básicos para fallback
        target_profile = st.session_state.get('profile_results', {})
        department = target_profile.get('employee_data', {}).get('department', 'Finanzas')
        phishing_content = generate_fallback_phishing_content(target_name, company_name, department)
    
    # Verificar que tenemos contenido válido
    if not phishing_content:
        st.error("🚨 No se pudo generar contenido - Verifique configuración")
        return
    
    # Mostrar el email con estilo más dramático
    st.markdown(f"""
    <div class="email-container" style="border: 3px solid #dc2626; background: linear-gradient(135deg, #ffffff, #fef2f2);">
        <div style="background: #dc2626; color: white; padding: 10px; margin: -2rem -2rem 1rem -2rem; border-radius: 8px 8px 0 0;">
            <h4 style="margin: 0; text-align: center;">🎯 EMAIL MALICIOSO GENERADO POR IA</h4>
        </div>
        
        <div class="email-header" style="border-bottom: 2px solid #dc2626;">
            <div style="display: grid; grid-template-columns: 1fr 3fr; gap: 1rem; margin-bottom: 1rem;">
                <div style="font-weight: 600; color: #374151;">
                    <div style="margin-bottom: 0.5rem;">📧 De:</div>
                    <div style="margin-bottom: 0.5rem;">🎯 Para:</div>
                    <div style="margin-bottom: 0.5rem;">📋 Asunto:</div>
                    <div style="margin-bottom: 0.5rem;">📅 Fecha:</div>
                </div>
                <div style="color: #6b7280;">
                    <div style="margin-bottom: 0.5rem; color: #dc2626; font-weight: 600;">{phishing_content.get('from_email', 'N/A')}</div>
                    <div style="margin-bottom: 0.5rem;">{phishing_content.get('to_email', 'N/A')}</div>
                    <div style="margin-bottom: 0.5rem; font-weight: 600; color: #dc2626;">{phishing_content.get('subject', 'N/A')}</div>
                    <div style="margin-bottom: 0.5rem;">{datetime.now().strftime('%d %b %Y, %H:%M')}</div>
                </div>
            </div>
        </div>
        
        <div class="email-body">
            {phishing_content.get('body', 'Contenido no disponible')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Análisis de efectividad para empresarios
    st.markdown("#### 🔍 Análisis de Efectividad (Para Workshop)")
    
    analysis_tabs = st.tabs(["🧠 Técnicas IA Utilizadas", "⚠️ Por Qué Funciona", "🎯 Factores de Éxito"])
    
    with analysis_tabs[0]:
        st.markdown("**🤖 Técnicas de IA Empleadas:**")
        for technique in phishing_content.get('techniques_used', []):
            if isinstance(technique, dict):
                st.markdown(f"• **{technique.get('name', 'N/A')}**: {technique.get('description', 'N/A')}")
            else:
                st.markdown(f"• **{technique}**")
    
    with analysis_tabs[1]:
        st.markdown("**⚠️ Por Qué Este Email Es Tan Peligroso:**")
        for red_flag in phishing_content.get('red_flags', []):
            st.markdown(f"• 🚨 {red_flag}")
    
    with analysis_tabs[2]:
        st.markdown("**🎯 Factores Que Lo Hacen Casi Indetectable:**")
        for improvement in phishing_content.get('danger_factors', []):
            st.markdown(f"• 💀 {improvement}")

def generate_ai_phishing_email_forced(target_name, company_name, strategy):
    """Generar email con IA MEJORADO para demo"""
    
    if not st.session_state.claude_agent:
        st.error("🚨 Motor IA requerido")
        return None
    
    try:
        # Contexto más específico para la demo
        target_profile = st.session_state.get('profile_results', {})
        department = target_profile.get('employee_data', {}).get('department', 'Finanzas')
        urgency_level = strategy.get('strategy_data', {}).get('urgency', 'Alta')
        techniques = strategy.get('strategy_data', {}).get('techniques', ['Autoridad', 'Urgencia'])
        context = strategy.get('strategy_data', {}).get('context', '')
        
        # Prompt MEJORADO específicamente para la demo
        prompt = f"""
        MISIÓN CRÍTICA: Genera el email de phishing MÁS REALISTA posible para demostrar a empresarios la sofisticación actual de los ataques.

        CONTEXTO DE WORKSHOP:
        - Audiencia: Empresarios y ejecutivos
        - Objetivo: Mostrar lo convincentes que son los ataques modernos
        - Debe ser EXTREMADAMENTE profesional y creíble
        
        DATOS DEL OBJETIVO:
        - Víctima: {target_name}
        - Empresa: {company_name}
        - Departamento: {department}
        - Nivel urgencia: {urgency_level}
        - Técnicas: {', '.join(techniques)}
        - Contexto: {context}

        REQUISITOS ESPECÍFICOS:
        1. SOLO empresas FICTICIAS (sin Deloitte, KPMG, etc.)
        2. HÍPER-PROFESIONAL: Formato corporativo perfecto
        3. ESPECÍFICO: Usar detalles del departamento {department}
        4. PSICOLÓGICAMENTE EFECTIVO: Combinar {', '.join(techniques)}
        5. ACTUAL: Contexto relevante para 2024/2025
        6. CONVINCENTE: Que engañe incluso a expertos

        ELEMENTOS CRÍTICOS:
        - Empresa auditora/consultora FICTICIA pero ultra-creíble
        - Asunto irresistible relacionado con {department}
        - Firma completa con logos, datos, disclaimers
        - Enlaces maliciosos específicos
        - Presión temporal apropiada para {urgency_level}

        FORMATO JSON OBLIGATORIO:
        {{
            "from_email": "email de empresa FICTICIA muy creíble",
            "to_email": "email construido desde {target_name} y {company_name}",
            "subject": "asunto IRRESISTIBLE específico para {department}",
            "body": "HTML corporativo perfecto, logos ficticios, firma detallada",
            "techniques_used": [
                {{"name": "técnica", "description": "aplicación específica en el email"}}
            ],
            "red_flags": ["señal sutil 1", "señal sutil 2", "señal sutil 3"],
            "danger_factors": ["factor peligroso 1", "factor 2", "factor 3"]
        }}

        CRÍTICO: Este email debe convencer incluso a empresarios experimentados. Máximo realismo.
        """
        
        # Usar modelo disponible y con parámetros más conservadores
        response = st.session_state.claude_agent.client.messages.create(
            model="claude-3-haiku-20240307",  # Cambiar a modelo disponible
            max_tokens=3000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        
        # Limpiar JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        result = json.loads(content.strip())
        
        # Validación final anti-empresas reales
        forbidden_companies = ['deloitte', 'kpmg', 'pwc', 'ey', 'accenture', 'mckinsey', 'santander', 'bbva', 'telefonica']
        email_text = result.get('body', '').lower()
        
        for company in forbidden_companies:
            if company in email_text:
                result['body'] = result['body'].replace(company.capitalize(), f"Consultora{company.capitalize()[:-2]}ex")
                result['from_email'] = result['from_email'].replace(company, f"{company[:-2]}ex")
        
        return result
        
    except Exception as e:
        st.error(f"🚨 Error en motor IA: {e}")
        # Devolver contenido de fallback para que la demo continúe
        return generate_fallback_phishing_content(target_name, company_name, department)

def generate_fallback_phishing_content(target_name, company_name, department):
    """Contenido de fallback si la IA falla - para que la demo continúe"""
    
    first_name = target_name.split(' ')[0] if ' ' in target_name else target_name.split(' - ')[0]
    target_email = f"{first_name.lower()}.objetivo@{company_name.lower().replace(' ', '-')}.com"
    
    return {
        "from_email": "auditoria@grupo-consultores-madrid.com",
        "to_email": target_email,
        "subject": f"URGENTE: Validación {department} - Acción Requerida Hoy",
        "body": f"""
        <div style="font-family: 'Segoe UI', sans-serif; line-height: 1.6; color: #333;">
            <div style="background: #1e40af; color: white; padding: 15px; margin-bottom: 20px;">
                <h2 style="margin: 0;">Grupo Consultores Madrid</h2>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Auditoría y Compliance Empresarial</p>
            </div>
            
            <p>Estimado/a <strong>{first_name}</strong>,</p>
            
            <p>Como responsable del área de <strong>{department}</strong> en {company_name}, debe completar urgentemente la validación de documentos corporativos requerida por las nuevas normativas 2025.</p>
            
            <div style="background: #fef2f2; border: 2px solid #dc2626; padding: 15px; margin: 20px 0; border-radius: 6px;">
                <p style="margin: 0; font-weight: 600; color: #dc2626;">⚠️ ACCIÓN CRÍTICA REQUERIDA</p>
                <p style="margin: 8px 0 0 0;">Plazo límite: <strong>HOY antes de las 18:00</strong></p>
            </div>
            
            <p>Para evitar sanciones regulatorias, acceda al portal seguro de validación:</p>
            
            <div style="text-align: center; margin: 25px 0;">
                <a href="https://validacion-empresarial.grupo-consultores.com/secure/{first_name.lower()}" 
                   style="background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                   🔐 VALIDAR DOCUMENTOS AHORA
                </a>
            </div>
            
            <p>Saludos cordiales,</p>
            <div style="margin-top: 20px; padding: 15px; border-left: 3px solid #1e40af; background: #f8fafc;">
                <strong>Ana María Rodríguez</strong><br>
                Directora de Compliance<br>
                Grupo Consultores Madrid<br>
                📧 a.rodriguez@grupo-consultores-madrid.com<br>
                📞 +34 91-XXX-XXXX
            </div>
        </div>
        """,
        "techniques_used": [
            {"name": "Autoridad", "description": "Se presenta como consultora oficial de compliance"},
            {"name": "Urgencia", "description": "Plazo extremo (mismo día) para crear presión"},
            {"name": "Miedo", "description": "Amenaza con sanciones regulatorias"},
            {"name": "Legitimidad", "description": "Formato corporativo profesional con firma detallada"}
        ],
        "red_flags": [
            "Presión temporal extrema (mismo día)",
            "Dominio de email no verificable oficialmente",
            "Solicitud de acceso a portal externo",
            "Amenazas desproporcionadas por email",
            "Falta de canales de verificación alternativos"
        ],
        "danger_factors": [
            "Apariencia extremadamente profesional",
            "Uso de información específica del departamento",
            "Contexto temporal creíble (nuevas normativas 2025)",
            "Combinación efectiva de múltiples técnicas psicológicas",
            "Portal falso con URL convincente"
        ]
    }

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
                
                # Corregir llamada al método Claude
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
    """Mostrar resultados de estrategia con generación completa de contenido"""
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
        
        # NUEVA SECCIÓN: Generación de contenido malicioso
        generate_attack_content_section(strategy)
        
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
        
        # Indicadores de éxito
        if 'success_indicators' in strategy:
            st.markdown("#### Indicadores de Éxito")
            for indicator in strategy['success_indicators']:
                st.markdown(f"• {indicator}")
    
    else:
        st.warning("Estrategia básica - Sistema IA no disponible")
        
        # Generar contenido básico incluso sin IA
        generate_basic_attack_content()

def generate_attack_content_section(strategy):
    """Generar la sección principal con contenido de ataque realista"""
    
    st.markdown("---")
    st.markdown("### 📧 Contenido de Ataque Generado")
    st.error("**⚠️ CONTENIDO PARA ANÁLISIS EDUCATIVO - USO EXCLUSIVO EN WORKSHOP EMPRESARIAL**")
    
    # Obtener datos del perfil y empresa
    target_profile = st.session_state.get('profile_results', {})
    company_context = st.session_state.get('osint_results', {}).get('company_data', {})
    
    target_name = target_profile.get('employee_data', {}).get('name', 'Empleado Objetivo')
    company_name = company_context.get('name', 'Empresa Objetivo')
    
    # Determinar tipo de ataque
    attack_type = strategy.get('strategy_data', {}).get('attack_type', 'Phishing por Correo Electrónico')
    
    if "Phishing" in attack_type:
        generate_phishing_email_content(target_name, company_name, strategy)
    elif "Smishing" in attack_type:
        generate_smishing_content(target_name, company_name, strategy)

def generate_phishing_email_content(target_name, company_name, strategy):
    """Generar contenido realista de email de phishing usando IA mejorada"""
    
    st.markdown("#### 📧 Email de Phishing Generado")
    
    # Usar Claude con prompts mejorados si está disponible
    if st.session_state.claude_agent:
        phishing_content = generate_ai_phishing_email_improved(target_name, company_name, strategy)
    else:
        phishing_content = generate_realistic_phishing_email_improved(target_name, company_name)
    
    # Mostrar el email en un formato realista mejorado
    st.markdown(f"""
    <div class="email-container">
        <div class="email-header">
            <div style="display: grid; grid-template-columns: 1fr 3fr; gap: 1rem; margin-bottom: 1rem;">
                <div style="font-weight: 600; color: #374151;">
                    <div style="margin-bottom: 0.5rem;">De:</div>
                    <div style="margin-bottom: 0.5rem;">Para:</div>
                    <div style="margin-bottom: 0.5rem;">Asunto:</div>
                    <div style="margin-bottom: 0.5rem;">Fecha:</div>
                </div>
                <div style="color: #6b7280;">
                    <div style="margin-bottom: 0.5rem;">{phishing_content['from_email']}</div>
                    <div style="margin-bottom: 0.5rem;">{phishing_content['to_email']}</div>
                    <div style="margin-bottom: 0.5rem; font-weight: 600; color: #dc2626;">{phishing_content['subject']}</div>
                    <div style="margin-bottom: 0.5rem;">{datetime.now().strftime('%d %b %Y, %H:%M')}</div>
                </div>
            </div>
        </div>
        
        <div class="email-body">
            {phishing_content['body']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Análisis del contenido
    st.markdown("#### 🔍 Análisis del Contenido para Workshop")
    
    analysis_tabs = st.tabs(["Técnicas Utilizadas", "Señales de Alerta", "Puntos de Mejora"])
    
    with analysis_tabs[0]:
        st.markdown("**Técnicas de Ingeniería Social Empleadas:**")
        for technique in phishing_content['techniques_used']:
            st.markdown(f"• **{technique['name']}**: {technique['description']}")
    
    with analysis_tabs[1]:
        st.markdown("**Señales de Alerta que los Empleados Deben Detectar:**")
        for red_flag in phishing_content['red_flags']:
            st.markdown(f"• ⚠️ {red_flag}")
    
    with analysis_tabs[2]:
        st.markdown("**Aspectos que Hacen este Email Particularmente Peligroso:**")
        for improvement in phishing_content['danger_factors']:
            st.markdown(f"• 🎯 {improvement}")

def generate_ai_phishing_email_improved(target_name, company_name, strategy):
    """Generar email de phishing con IA usando prompts mejorados"""
    
    try:
        # Obtener contexto adicional
        target_profile = st.session_state.get('profile_results', {})
        department = target_profile.get('employee_data', {}).get('department', 'Finanzas')
        urgency_level = strategy.get('strategy_data', {}).get('urgency', 'Alta')
        techniques = strategy.get('strategy_data', {}).get('techniques', ['Autoridad', 'Urgencia'])
        context = strategy.get('strategy_data', {}).get('context', '')
        
        # Prompt mejorado y más específico
        prompt = f"""
        CONTEXTO: Eres un experto en ciberseguridad creando contenido EDUCATIVO para un workshop empresarial sobre concientización en seguridad.

        OBJETIVO: Genera un email de phishing REALISTA y PROFESIONAL para demostrar técnicas de ingeniería social a empresarios.

        DATOS DEL ESCENARIO:
        - Empleado objetivo: {target_name}
        - Empresa: {company_name}
        - Departamento: {department}
        - Nivel de urgencia: {urgency_level}
        - Técnicas a demostrar: {', '.join(techniques)}
        - Contexto empresarial: {context}

        REQUISITOS ESPECÍFICOS:
        1. NO uses nombres de empresas reales (Deloitte, KPMG, etc.)
        2. Crea nombres de empresas ficticias pero creíbles
        3. El email debe ser MUY convincente y profesional
        4. Incluye elementos específicos del departamento ({department})
        5. Usa un pretexto actual y relevante para 2024
        6. El tono debe ser corporativo y urgente

        ELEMENTOS A INCLUIR:
        - Remitente: Empresa auditora ficticia o consultora interna
        - Asunto: Específico y urgente relacionado con {department}
        - Cuerpo: Profesional, con logos ficticios, firmas detalladas
        - Call-to-action: Enlace o solicitud de información
        - Firma: Completa con datos ficticios pero realistas

        FORMATO DE RESPUESTA JSON:
        {{
            "from_email": "email del remitente (empresa ficticia)",
            "to_email": "email del objetivo basado en {target_name} y {company_name}",
            "subject": "asunto específico y urgente",
            "body": "cuerpo completo del email en HTML profesional",
            "techniques_used": [
                {{"name": "técnica", "description": "cómo se aplica específicamente"}}
            ],
            "red_flags": ["señal de alerta específica 1", "señal 2", "señal 3"],
            "danger_factors": ["factor peligroso 1", "factor 2", "factor 3"]
        }}

        IMPORTANTE: 
        - Solo empresas FICTICIAS
        - Extremadamente profesional
        - Para educación en workshop empresarial
        - Debe parecer 100% legítimo a primera vista
        """
        
        response = st.session_state.claude_agent.client.messages.create(
            model="claude-3-haiku-20240307",  # Cambiar a modelo disponible
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        
        # Limpiar JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        result = json.loads(content.strip())
        
        # Validar que no hay empresas reales
        forbidden_companies = ['deloitte', 'kpmg', 'pwc', 'ey', 'accenture', 'mckinsey', 'santander', 'bbva']
        email_text = result.get('body', '').lower()
        
        for company in forbidden_companies:
            if company in email_text:
                # Reemplazar con versión ficticia
                result['body'] = result['body'].replace(company.capitalize(), f"Consultoría {company.capitalize()[:-1]}ex")
        
        return result
        
    except Exception as e:
        st.error(f"Error generando contenido con IA: {e}")
        return generate_realistic_phishing_email_improved(target_name, company_name)

def generate_realistic_phishing_email_improved(target_name, company_name):
    """Generar email de phishing realista mejorado sin IA"""
    
    # Obtener datos del perfil si están disponibles
    target_profile = st.session_state.get('profile_results', {})
    department = target_profile.get('employee_data', {}).get('department', 'Finanzas')
    
    # Generar contenido realista basado en el perfil
    first_name = target_name.split(' ')[0] if ' ' in target_name else target_name.split(' - ')[0]
    
    # Email objetivo
    target_email = f"{first_name.lower()}.{target_name.split(' ')[1].lower() if ' ' in target_name else 'objetivo'}@{company_name.lower().replace(' ', '-')}.com"
    
    # Diferentes escenarios según el departamento (SIN empresas reales)
    if department == 'Finanzas':
        scenario = {
            "from_email": "auditoria@grupoconsultores-madrid.com",
            "to_email": target_email,
            "subject": "URGENTE: Validación Fiscal Requerida - Cierre Q4 2024",
            "body": f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px;">
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjQwIiB2aWV3Qm94PSIwIDAgMTIwIDQwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxMjAiIGhlaWdodD0iNDAiIGZpbGw9IiMxZTQwYWYiLz48dGV4dCB4PSI2MCIgeT0iMjQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSJib2xkIj5BdWRpdG9yQ29ycDwvdGV4dD48L3N2Zz4=" alt="AuditorCorp" style="height: 40px;">
                    <h2 style="color: #1e40af; margin: 10px 0 5px 0; font-size: 18px;">Grupo Auditores & Consultores Madrid</h2>
                </div>
                
                <p>Estimado/a <strong>{first_name}</strong>,</p>
                
                <p>Nos dirigimos a usted en su calidad de responsable financiero de <strong>{company_name}</strong> para informarle sobre la <span style="background-color: #fef3c7; padding: 2px 6px; border-radius: 3px;"><strong>validación fiscal obligatoria Q4 2024</strong></span> que debe completarse antes del <strong style="color: #dc2626;">31 de diciembre</strong>.</p>
                
                <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0; border-radius: 4px;">
                    <p style="margin: 0; font-weight: 600; color: #dc2626;">⚠️ ACCIÓN CRÍTICA REQUERIDA</p>
                    <p style="margin: 5px 0 0 0; font-size: 14px;">Su empresa tiene pendiente la validación de documentos fiscales para evitar sanciones del organismo tributario.</p>
                </div>
                
                <p>Hemos identificado discrepancias menores en la documentación fiscal de su organización que requieren validación inmediata. Según las nuevas normativas 2024, es obligatorio completar este proceso para:</p>
                
                <ul style="margin: 15px 0; padding-left: 25px;">
                    <li>Certificar estados financieros del ejercicio actual</li>
                    <li>Validar transacciones internacionales reportadas</li>
                    <li>Confirmar cumplimiento normativo fiscal</li>
                    <li>Evitar penalizaciones por incumplimiento (hasta €50.000)</li>
                </ul>
                
                <p><strong>Para facilitar este proceso urgente</strong>, hemos habilitado un portal seguro donde puede revisar y confirmar la documentación:</p>
                
                <div style="text-align: center; margin: 25px 0;">
                    <a href="https://portal-validacion-fiscal.auditorcorp-madrid.com/secure/validate?empresa={company_name.replace(' ', '')}&responsable={first_name}" 
                       style="background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; display: inline-block; box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);">
                       🔐 ACCEDER AL PORTAL SEGURO
                    </a>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 12px; border-radius: 6px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #856404;">
                        <strong>⏰ Tiempo límite:</strong> Este enlace de validación expira en <strong>6 horas</strong> por motivos de seguridad.
                    </p>
                </div>
                
                <p>Para completar la validación, necesitará proporcionar:</p>
                <ul style="font-size: 14px; color: #6b7280;">
                    <li>Credenciales de acceso al sistema fiscal corporativo</li>
                    <li>Códigos de verificación bancarios asociados</li>
                    <li>Confirmación de identidad del responsable financiero</li>
                </ul>
                
                <p>Si tiene alguna consulta sobre este proceso, puede contactarnos directamente respondiendo a este correo o llamando al <strong>+34 91-XXX-XXXX</strong> (horario: 9:00-18:00).</p>
                
                <p>Agradecemos su inmediata atención a este requerimiento normativo.</p>
                
                <p>Cordialmente,</p>
                
                <div style="border-left: 3px solid #1e40af; padding-left: 20px; margin-top: 25px; background: #f8fafc; padding: 15px; border-radius: 6px;">
                    <strong style="color: #1e40af;">Ana María Rodríguez Fernández</strong><br>
                    <span style="color: #6b7280;">Directora de Cumplimiento Fiscal</span><br>
                    <strong>Grupo Auditores & Consultores Madrid</strong><br>
                    📧 a.rodriguez@grupoconsultores-madrid.com<br>
                    📞 +34 91-XXX-XXXX ext. 205<br>
                    🌐 www.grupoconsultores-madrid.com<br>
                    📍 Calle Serrano 95, 28006 Madrid
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                <div style="font-size: 11px; color: #9ca3af; line-height: 1.4;">
                    <p><em>Este correo contiene información confidencial dirigida únicamente al destinatario. Si ha recibido este mensaje por error, 
                    por favor elimínelo y notifique al remitente. Grupo Auditores & Consultores Madrid es una firma independiente 
                    especializada en servicios de auditoría y consultoría fiscal para empresas medianas y grandes.</em></p>
                    
                    <p><em>Conforme a la LOPD y RGPD, sus datos están protegidos. Para ejercer sus derechos o darse de baja, 
                    contacte con protecciondatos@grupoconsultores-madrid.com</em></p>
                </div>
            </div>
            """
        }
    else:
        # Escenario para otros departamentos (también sin empresas reales)
        scenario = {
            "from_email": f"sistemas.seguridad@{company_name.lower().replace(' ', '-')}.com",
            "to_email": target_email,
            "subject": "Actualización Crítica de Seguridad - Validación Requerida",
            "body": f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333;">
                <div style="background: #dc2626; color: white; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                    <h2 style="margin: 0; font-size: 18px;">🛡️ ALERTA DE SEGURIDAD - {company_name.upper()}</h2>
                </div>
                
                <p>Estimado/a <strong>{first_name}</strong>,</p>
                
                <p>El Departamento de Seguridad Informática ha detectado <strong style="color: #dc2626;">múltiples intentos de acceso no autorizado</strong> dirigidos a cuentas del departamento de {department}.</p>
                
                <div style="background: #fef2f2; border: 2px solid #dc2626; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: 600; color: #dc2626;">⚠️ ACCIÓN INMEDIATA REQUERIDA</p>
                    <p style="margin: 8px 0 0 0;">Su cuenta ha sido marcada para verificación de seguridad obligatoria.</p>
                </div>
                
                <p><strong>Actividad sospechosa detectada:</strong></p>
                <ul>
                    <li>Intentos de login desde ubicaciones no reconocidas</li>
                    <li>Patrones de acceso anómalos en horarios nocturnos</li>
                    <li>Solicitudes de cambio de contraseña no autorizadas</li>
                </ul>
                
                <p>Para mantener la seguridad de nuestros sistemas y proteger la información corporativa, debe <strong>verificar su identidad inmediatamente</strong> a través del portal seguro:</p>
                
                <div style="text-align: center; margin: 25px 0;">
                    <a href="https://portal-seguridad-interna.{company_name.lower().replace(' ', '-')}.com/verificar-identidad?usuario={first_name}" 
                       style="background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                       🔐 VERIFICAR CUENTA AHORA
                    </a>
                </div>
                
                <p><strong style="color: #dc2626;">IMPORTANTE:</strong> Si no completa esta verificación en las próximas <strong>2 horas</strong>, su cuenta será suspendida automáticamente por medidas de seguridad.</p>
                
                <p>En caso de dudas, contacte inmediatamente al Helpdesk de Seguridad: <strong>ext. 999</strong></p>
                
                <p>Saludos,<br>
                <strong>Equipo de Ciberseguridad</strong><br>
                {company_name}</p>
            </div>
            """
        }
    
    # Agregar análisis común
    scenario.update({
        "techniques_used": [
            {"name": "Autoridad", "description": "Se presenta como entidad oficial (auditora o IT interno)"},
            {"name": "Urgencia", "description": "Plazos extremadamente cortos para crear presión"},
            {"name": "Miedo", "description": "Amenaza con sanciones económicas o suspensión de cuenta"},
            {"name": "Legitimidad", "description": "Formato profesional con logos, firmas detalladas y datos técnicos"},
            {"name": "Especificidad", "description": "Menciona detalles específicos del departamento y empresa"}
        ],
        "red_flags": [
            "Dominio de email ligeramente diferente al oficial de la empresa",
            "Presión temporal extrema (2-6 horas)",
            "Solicitud de credenciales por correo electrónico",
            "Enlaces que redirigen a dominios externos",
            "Amenazas desproporcionadas (sanciones, suspensiones)",
            "Falta de procesos de verificación alternativos mencionados"
        ],
        "danger_factors": [
            "Apariencia extremadamente profesional que genera confianza inmediata",
            "Uso de información real de la empresa y empleado objetivo",
            "Contexto temporal relevante (cierre de año, auditorías)",
            "Múltiples elementos de presión psicológica combinados",
            "Solicitud directa de credenciales de acceso críticas",
            "Imitación convincente de procesos empresariales reales"
        ]
    })
    
    return scenario

def generate_smishing_content(target_name, company_name, strategy):
    """Generar contenido realista de SMS de smishing"""
    
    st.markdown("#### 📱 Mensaje SMS de Smishing Generado")
    
    # Usar Claude con prompts mejorados si está disponible
    if st.session_state.claude_agent:
        sms_content = generate_ai_smishing_sms_improved(target_name, company_name, strategy)
    else:
        sms_content = generate_realistic_smishing_sms_improved(target_name, company_name)
    
    # Mostrar el SMS en formato móvil
    st.markdown(f"""
    <div style="background: #007bff; color: white; padding: 1rem; border-radius: 18px; margin: 1rem 0; max-width: 350px; font-family: -apple-system, BlinkMacSystemFont, sans-serif; box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);">
        <div style="font-size: 0.8rem; opacity: 0.8; margin-bottom: 0.5rem;">
            Desde: {sms_content['from_number']} • {datetime.now().strftime('%H:%M')}
        </div>
        <div style="font-size: 1rem; line-height: 1.4;">
            {sms_content['message']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Variaciones del mensaje
    st.markdown("#### 🔄 Variaciones del Ataque")
    st.markdown("**El atacante podría enviar múltiples versiones para maximizar efectividad:**")
    
    colors = ['#28a745', '#17a2b8', '#ffc107', '#6f42c1']
    for i, variation in enumerate(sms_content['variations']):
        color = colors[i % len(colors)]
        st.markdown(f"""
        <div style="background: {color}; color: white; padding: 0.8rem; border-radius: 15px; margin: 0.5rem 0; max-width: 320px; font-size: 0.9rem;">
            <strong>Variación {i+1}:</strong><br>
            {variation}
        </div>
        """, unsafe_allow_html=True)
    
    # Análisis del SMS
    st.markdown("#### 🔍 Análisis del Contenido SMS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Técnicas Empleadas:**")
        for technique in sms_content['techniques_used']:
            st.markdown(f"• **{technique}**")
    
    with col2:
        st.markdown("**Señales de Alerta:**")
        for red_flag in sms_content['red_flags']:
            st.markdown(f"• ⚠️ {red_flag}")

def generate_ai_smishing_sms_improved(target_name, company_name, strategy):
    """Generar SMS de smishing con IA mejorada"""
    
    try:
        # Obtener contexto
        target_profile = st.session_state.get('profile_results', {})
        department = target_profile.get('employee_data', {}).get('department', 'Finanzas')
        urgency_level = strategy.get('strategy_data', {}).get('urgency', 'Alta')
        
        prompt = f"""
        CONTEXTO: Crea contenido SMS de smishing para workshop empresarial de concientización.

        DATOS:
        - Objetivo: {target_name}
        - Empresa: {company_name} 
        - Departamento: {department}
        - Urgencia: {urgency_level}

        REQUISITOS:
        1. NO uses nombres de bancos o empresas REALES
        2. Crea entidades ficticias pero creíbles
        3. SMS cortos pero muy convincentes
        4. Diferentes variaciones del mismo ataque
        5. Para uso educativo en workshop

        FORMATO JSON:
        {{
            "from_number": "número ficticio de entidad creíble",
            "message": "mensaje principal (máx 160 caracteres)",
            "variations": ["variación 1", "variación 2", "variación 3"],
            "techniques_used": ["técnica 1", "técnica 2", "técnica 3"],
            "red_flags": ["señal de alerta 1", "señal 2", "señal 3"]
        }}

        Importante: Solo entidades FICTICIAS, para educación empresarial.
        """
        
        response = st.session_state.claude_agent.client.messages.create(
            model="claude-3-haiku-20240307",  # Usar modelo disponible
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        
        result = json.loads(content.strip())
        
        # Validar que no hay entidades reales
        forbidden_entities = ['santander', 'bbva', 'bankia', 'caixabank', 'hacienda', 'aeat']
        message_text = result.get('message', '').lower()
        
        for entity in forbidden_entities:
            if entity in message_text:
                result['message'] = result['message'].replace(entity.capitalize(), f"{entity.capitalize()}Ficticio")
        
        return result
        
    except Exception as e:
        st.error(f"Error generando SMS con IA: {e}")
        return generate_realistic_smishing_sms_improved(target_name, company_name)

def generate_realistic_smishing_sms_improved(target_name, company_name):
    """Generar SMS de smishing realista mejorado sin IA"""
    
    first_name = target_name.split(' ')[0] if ' ' in target_name else target_name.split(' - ')[0]
    
    return {
        "from_number": "+34 900-XXX-XXX (Entidad Financiera)",
        "message": f"🏦 ALERTA SEGURIDAD: Detectamos acceso sospechoso cuenta empresarial {company_name}. Verificar INMEDIATAMENTE: https://validacion-empresas.entidadfinanciera.es/verify?user={first_name.lower()} Caduca en 1h.",
        "variations": [
            f"⚠️ {company_name}: Cuenta bloqueada por actividad inusual. Desbloquear ahora: https://empresas-seguras.com/unlock/{first_name} - URGENTE",
            f"Notificación Fiscal: Devolución pendiente €2.340 para {company_name}. Gestionar en 24h: https://tramites-fiscales.gob.es/devolucion?nif={first_name}2024",
            f"IT-{company_name}: Actualización seguridad crítica requerida. Instalar certificado: https://actualizaciones-{company_name.lower().replace(' ', '')}.com/cert - Vence hoy"
        ],
        "techniques_used": [
            "Urgencia extrema (1 hora límite)",
            "Autoridad (entidades financieras y fiscales)",
            "Miedo (bloqueo de cuenta empresarial)",
            "Especificidad (nombres reales de empresa y persona)"
        ],
        "red_flags": [
            "Número no oficial de la entidad",
            "URLs con dominios alternativos o sospechosos",
            "Plazos de tiempo extremadamente cortos",
            "Solicitudes de acción inmediata por SMS",
            "Amenazas desproporcionadas",
            "Falta de canales de verificación oficiales mencionados"
        ]
    }

def generate_basic_attack_content():
    """Contenido básico SIN IA - mostrar limitaciones"""
    st.markdown("#### 🚨 Motor IA DESCONECTADO")
    st.error("""
    **💀 SIN IA = SIN DEMO REAL**
    
    Los atacantes modernos usan IA para generar contenido híper-realista.
    Sin el motor IA, esta demo pierde su impacto educativo.
    """)
    
    st.markdown("**📧 Ejemplo Básico (Sin Personalización IA):**")
    st.code("""
    De: auditoria@consultora-generica.com
    Para: victima@empresa.com
    Asunto: Verificación Urgente Requerida
    
    Estimado usuario,
    
    Necesita validar documentos inmediatamente...
    Enlace: [portal-generico]
    
    Atentamente,
    Consultora Genérica
    """, language="text")
    
    st.warning("""
    ⚖️ **Diferencia con IA:**
    
    🚫 Sin personalización psicológica
    🚫 Sin detalles específicos del objetivo  
    🚫 Sin contexto empresarial real
    🚫 Sin técnicas avanzadas de manipulación
    
    ✅ **Con IA:** Emails que engañan incluso a expertos
    """)
    
    st.error("🔧 **Configure clave API para demo completa**")

def create_osint_interface():
    """Interfaz OSINT estilo 'operaciones de reconocimiento'"""
    st.markdown("""
    <div class="section-header">
        <h3>🕵️ Reconocimiento OSINT - Recopilación de Inteligencia</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("🎯 Recopilación automática de información pública para identificar objetivos y vulnerabilidades explotables")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("#### 🎪 Configuración del Objetivo")
        
        with st.form("osint_form"):
            st.markdown("**🎯 Información de la Víctima Corporativa**")
            
            company_name = st.text_input("🏢 Organización Objetivo", "Empresa Objetivo")
            domain = st.text_input("🌐 Dominio Principal", "empresa-objetivo.com")
            
            col_a, col_b = st.columns(2)
            with col_a:
                industry = st.selectbox("🏭 Sector", [
                    "Tecnología", "Finanzas", "Salud", "Educación", 
                    "Retail", "Manufactura", "Consultoría", "Gobierno"
                ])
            with col_b:
                company_size = st.selectbox("👥 Tamaño", [
                    "1-50", "51-200", "201-1000", "1000-5000", "5000+"
                ])
            
            location = st.text_input("📍 Ubicación Principal", "Madrid, España")
            
            st.markdown("**🕵️ Fuentes de Reconocimiento**")
            sources = []
            
            col_c, col_d = st.columns(2)
            with col_c:
                if st.checkbox("👔 LinkedIn", True): sources.append("LinkedIn")
                if st.checkbox("🌐 Sitio Web Corporativo", True): sources.append("Website")
                if st.checkbox("🐦 Twitter/X"): sources.append("Twitter")
                if st.checkbox("📘 Facebook"): sources.append("Facebook")
            
            with col_d:
                if st.checkbox("💻 GitHub"): sources.append("GitHub")
                if st.checkbox("🔍 Registros DNS"): sources.append("DNS")
                if st.checkbox("📰 Noticias y Prensa"): sources.append("News")
                if st.checkbox("💼 Ofertas de Empleo"): sources.append("Jobs")
            
            ai_analysis = st.checkbox("🤖 Procesamiento con IA Ofensiva", True)
            
            submit_button = st.form_submit_button("🚀 INICIAR RECONOCIMIENTO", type="primary")
            
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

def create_profiling_interface():
    """Interfaz de perfilado estilo 'análisis de víctimas'"""
    st.markdown("""
    <div class="section-header">
        <h3>🧠 Perfilado Psicológico de Víctimas</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("🎯 Análisis psicológico automatizado para identificar debilidades explotables en ingeniería social")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("#### 🎪 Selección de Víctima")
        
        # Lista de empleados objetivo
        if 'osint_results' in st.session_state:
            employee_count = st.session_state.osint_results.get('employees_at_risk', 10)
            employee_options = [f"🎯 Víctima {i+1} - {['CEO', 'CFO', 'CTO', 'Director', 'Gerente', 'Analista'][i%6]}" 
                             for i in range(min(employee_count, 15))]
        else:
            employee_options = [
                "🎯 María González - CFO",
                "🎯 Carlos Rodríguez - Director IT", 
                "🎯 Ana Martínez - Gerente RRHH",
                "🎯 Luis Hernández - Coordinador Operaciones"
            ]
        
        selected_employee = st.selectbox("👤 Víctima a Perfilar", employee_options)
        
        st.markdown("#### 📊 Datos de Vulnerabilidad")
        
        with st.form("profile_form"):
            
            social_activity = st.slider("📱 Exposición en Redes", 1, 10, 7, 
                                      help="Nivel de actividad y exposición en redes sociales")
            info_sharing = st.slider("🗣️ Tendencia a Compartir", 1, 10, 6,
                                   help="Propensión a compartir información corporativa")
            security_awareness = st.slider("🛡️ Conciencia de Seguridad", 1, 10, 4,
                                         help="Nivel de conocimiento en ciberseguridad")
            
            department = st.selectbox("🏢 Departamento", 
                                    ["Finanzas", "Tecnología", "Recursos Humanos", "Ventas", "Marketing", "Operaciones", "Legal"])
            
            interests = st.multiselect("🎯 Intereses Identificados",
                                     ["Tecnología", "Deportes", "Viajes", "Familia", "Finanzas", 
                                      "Entretenimiento", "Educación", "Arte", "Música"],
                                     default=["Tecnología", "Viajes"])
            
            communication_style = st.selectbox("💬 Estilo de Comunicación",
                                              ["Formal", "Casual", "Técnico", "Emocional", "Directo"])
            
            work_schedule = st.selectbox("⏰ Horario de Trabajo",
                                       ["Estándar 9-17", "Flexible", "Nocturno", "Fines de Semana", "Disponibilidad 24/7"])
            
            risk_factors = st.multiselect("⚠️ Vectores de Explotación",
                                        ["Oversharing en LinkedIn", "Información personal pública", 
                                         "Acceso privilegiado", "Contactos externos frecuentes",
                                         "Patrones predecibles", "Baja verificación de solicitudes"])
            
            analyze_button = st.form_submit_button("🧠 ANALIZAR VÍCTIMA", type="primary")
            
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

def generate_smishing_content_attacker(target_name, company_name, strategy):
    """Generar SMS de smishing estilo 'atacante'"""
    
    st.markdown("#### 📱 SMS Malicioso Generado")
    
    # Usar IA mejorada si está disponible
    if st.session_state.claude_agent:
        sms_content = generate_ai_smishing_sms_improved(target_name, company_name, strategy)
    else:
        st.error("🚨 Motor IA requerido para smishing personalizado")
        return
    
    # Mostrar el SMS con estilo más dramático
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #dc2626, #991b1b); color: white; padding: 1.2rem; border-radius: 18px; margin: 1rem 0; max-width: 350px; font-family: -apple-system, BlinkMacSystemFont, sans-serif; box-shadow: 0 6px 20px rgba(220, 38, 38, 0.4); border: 2px solid #dc2626;">
        <div style="font-size: 0.8rem; opacity: 0.9; margin-bottom: 0.5rem; text-align: center;">
            📱 <strong>SMS MALICIOSO GENERADO</strong>
        </div>
        <div style="font-size: 0.8rem; opacity: 0.8; margin-bottom: 0.5rem;">
            De: {sms_content['from_number']} • {datetime.now().strftime('%H:%M')}
        </div>
        <div style="font-size: 1rem; line-height: 1.4; background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 10px;">
            {sms_content['message']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Variaciones del ataque
    st.markdown("#### 🔄 Campañas Automáticas")
    st.markdown("**🎯 El sistema generaría múltiples variaciones para maximizar efectividad:**")
    
    colors = ['#28a745', '#17a2b8', '#ffc107', '#6f42c1']
    for i, variation in enumerate(sms_content['variations']):
        color = colors[i % len(colors)]
        st.markdown(f"""
        <div style="background: {color}; color: white; padding: 0.8rem; border-radius: 15px; margin: 0.5rem 0; max-width: 340px; font-size: 0.9rem; border: 2px solid {color};">
            <strong>🎪 Campaña {i+1}:</strong><br>
            {variation}
        </div>
        """, unsafe_allow_html=True)
    
    # Análisis de efectividad
    st.markdown("#### 🔍 Análisis de Efectividad")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🧠 Técnicas Empleadas:**")
        for technique in sms_content['techniques_used']:
            st.markdown(f"• **{technique}**")
    
    with col2:
        st.markdown("**⚠️ Señales de Peligro:**")
        for red_flag in sms_content['red_flags']:
            st.markdown(f"• 🚨 {red_flag}")

# Mantener las funciones auxiliares con pequeños ajustes de tono
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
        vulnerabilities.append("🎯 Alta exposición en redes sociales - Vector de ataque directo")
    
    if employee_data.get('info_sharing', 5) >= 6:
        vulnerabilities.append("🗣️ Propensión a compartir información corporativa - Explotable")
    
    if employee_data.get('security_awareness', 5) <= 4:
        vulnerabilities.append("🛡️ Baja conciencia sobre ingeniería social - Víctima ideal")
    
    return vulnerabilities

def generate_basic_vectors(employee_data):
    """Generar vectores básicos"""
    vectors = ["📧 Phishing dirigido personalizado", "👔 Ingeniería social vía LinkedIn"]
    
    if 'Familia' in employee_data.get('interests', []):
        vectors.append("👨‍👩‍👧‍👦 Pretextos familiares - Alta efectividad emocional")
    
    return vectors

def generate_basic_strategy(attack_type, urgency, techniques):
    """Generar estrategia básica"""
    return {
        "🎭 Vector de Ataque": attack_type,
        "⏰ Presión Psicológica": urgency,
        "🧠 Arsenal Empleado": ", ".join(techniques),
        "🎯 Personalización": "Adaptado al perfil psicológico de la víctima",
        "📊 Tasa de Éxito Estimada": f"{np.random.uniform(0.65, 0.85):.0%}"
    }

def create_risk_distribution_chart():
    """Gráfico de distribución de riesgo estilo 'atacante'"""
    risk_data = pd.DataFrame({
        'Nivel': ['💀 Crítico', '🔥 Alto', '⚡ Medio', '🟢 Bajo'],
        'Víctimas': [87, 234, 456, 123]
    })
    
    colors = ['#dc2626', '#f97316', '#3b82f6', '#059669']
    
    fig = px.pie(
        risk_data,
        values='Víctimas',
        names='Nivel',
        title="🎯 Distribución de Víctimas por Nivel de Riesgo",
        color_discrete_sequence=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400, font_family="Inter", title_font_size=16)
    st.plotly_chart(fig, use_container_width=True)

def create_vulnerability_timeline():
    """Timeline de vulnerabilidades estilo 'operaciones'"""
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
        title="📈 Evolución de Vectores de Ataque Identificados",
        xaxis_title="Período de Reconocimiento",
        yaxis_title="Vulnerabilidades Detectadas",
        height=400,
        font_family="Inter",
        title_font_size=16
    )
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
