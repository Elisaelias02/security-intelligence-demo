import streamlit as st
import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.claude_security_agent import create_claude_agent
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Security Intelligence Platform - Powered by Claude",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado (mismo que antes)
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-color: #1e3a8a;
        --secondary-color: #3b82f6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --claude-color: #ff6b35;
    }
    
    .main > div { font-family: 'Inter', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--claude-color) 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(30, 58, 138, 0.15);
    }
    
    .claude-badge {
        display: inline-block;
        background: var(--claude-color);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.5rem;
    }
    
    .api-status {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .api-status.active { border-left-color: var(--success-color); }
    .api-status.error { border-left-color: var(--danger-color); }
    .api-status.simulation { border-left-color: var(--warning-color); }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 4px solid var(--secondary-color);
        transition: transform 0.2s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card h3 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        color: var(--primary-color);
    }
    
    .analysis-result {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .vulnerability-item {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 6px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-left: 4px solid #ef4444;
    }
    
    .recommendation-item {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 6px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-left: 4px solid #10b981;
    }
    
    .risk-critical { border-left-color: var(--danger-color) !important; }
    .risk-high { border-left-color: #f97316 !important; }
    .risk-medium { border-left-color: var(--warning-color) !important; }
    .risk-low { border-left-color: var(--success-color) !important; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

def main():
    load_css()
    
    # Inicializar agente Claude
    if 'claude_agent' not in st.session_state:
        st.session_state.claude_agent = create_claude_agent()
    
    # Verificar estado de la API
    api_status = st.session_state.claude_agent.check_api_status()
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ Security Intelligence Platform</h1>
        <div class="claude-badge">Powered by Claude AI</div>
        <p>Análisis Avanzado de Vulnerabilidades de Ingeniería Social</p>
        <small>Enterprise Grade • Real-time Analysis • AI-Powered Insights</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar estado de API
    display_api_status(api_status)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuración del Análisis")
        
        # Configuración de Claude
        st.markdown("####  Claude AI Settings")
        
        if api_status['api_available']:
            st.success("✅ Claude API Activa")
            st.info(f"Modelo: {api_status.get('model', 'claude-3-haiku')}")
        else:
            st.warning("⚠️ Modo Simulación Activa")
            
            # Opción para ingresar API key manual
            manual_key = st.text_input(
                "API Key de Anthropic (opcional)", 
                type="password",
                help="Ingresa tu API key para usar Claude real"
            )
            
            if manual_key and st.button("🔄 Conectar Claude"):
                st.session_state.claude_agent = create_claude_agent(manual_key)
                st.rerun()
        
        st.markdown("---")
        
        # Configuraciones de análisis
        analysis_depth = st.selectbox(
            "🎯 Profundidad del Análisis",
            ["Rápido", "Estándar", "Profundo", "Exhaustivo"]
        )
        
        enable_realtime = st.checkbox("🔄 Análisis en Tiempo Real", True)
        
        max_targets = st.slider("👥 Máximo de Objetivos", 1, 20, 5)
        
        st.markdown("### ℹ️ Información")
        st.info("""
        **Claude AI Integration**
        
        • Análisis inteligente con LLM
        • Insights contextuales avanzados  
        • Recomendaciones personalizadas
        • Simulaciones educativas realistas
        """)
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard Ejecutivo",
        "🔍 Análisis OSINT", 
        "👥 Perfilado con IA",
        "⚡ Simulación Inteligente",
        "🛡️ Contramedidas IA"
    ])
    
    with tab1:
        create_executive_dashboard()
    
    with tab2:
        create_claude_osint_interface()
    
    with tab3:
        create_claude_profiling_interface()
    
    with tab4:
        create_claude_attack_simulation()
    
    with tab5:
        create_claude_countermeasures()

def display_api_status(status):
    """Mostrar estado de la API"""
    
    if status['status'] == 'active':
        st.markdown(f"""
        <div class="api-status active">
            <strong> Claude AI Status: ACTIVO</strong><br>
            {status['message']}<br>
            <small>Modelo: {status.get('model', 'N/A')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    elif status['status'] == 'simulation_mode':
        st.markdown(f"""
        <div class="api-status simulation">
            <strong>⚠️ Claude AI Status: MODO SIMULACIÓN</strong><br>
            {status['message']}<br>
            <small>Para usar Claude real, configura tu API key en Secrets</small>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.markdown(f"""
        <div class="api-status error">
            <strong>❌ Claude AI Status: ERROR</strong><br>
            {status['message']}<br>
            <small>Fallback a modo simulación activado</small>
        </div>
        """, unsafe_allow_html=True)

def create_executive_dashboard():
    """Dashboard ejecutivo con métricas de Claude"""
    st.markdown("### 📈 Dashboard Ejecutivo - Análisis con Claude AI")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card risk-critical">
            <h3>87</h3>
            <p>Vulnerabilidades Críticas</p>
            <small>Detectadas por Claude</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card risk-high">
            <h3>234</h3>
            <p>Empleados Alto Riesgo</p>
            <small>Análisis psicológico IA</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card risk-low">
            <h3>92%</h3>
            <p>Precisión del Análisis</p>
            <small>Confianza Claude AI</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>4.2min</h3>
            <p>Tiempo de Análisis</p>
            <small>Promedio con IA</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar análisis recientes
    if 'recent_analyses' in st.session_state and st.session_state.recent_analyses:
        st.markdown("###  Análisis Recientes con Claude")
        
        for analysis in st.session_state.recent_analyses[-3:]:  # Últimos 3
            with st.expander(f" {analysis.get('type', 'Análisis')} - {analysis.get('timestamp', 'N/A')}"):
                st.json(analysis.get('summary', {}))
    else:
        st.info("No hay análisis recientes. Ejecuta un análisis OSINT o de perfilado para ver resultados aquí.")
    
    # Gráficos estándar
    col1, col2 = st.columns(2)
    
    with col1:
        create_risk_distribution_chart()
    
    with col2:
        create_vulnerability_timeline()

def create_claude_osint_interface():
    """Interfaz OSINT potenciada por Claude"""
    st.markdown("### 🔍 Análisis OSINT Inteligente con Claude")
    st.info("**Claude AI** analizará la información recopilada para identificar patrones y vulnerabilidades avanzadas")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("#### Configuración del Análisis")
        
        with st.form("claude_osint_form"):
            company_name = st.text_input(" Nombre de la Empresa", "TechCorp Solutions")
            domain = st.text_input("🌐 Dominio Principal", "techcorp.com")
            
            col_a, col_b = st.columns(2)
            with col_a:
                industry = st.selectbox(" Industria", [
                    "Tecnología", "Finanzas", "Salud", "Educación", 
                    "Retail", "Manufactura", "Consultoría", "Gobierno"
                ])
            with col_b:
                company_size = st.selectbox("👥 Tamaño", [
                    "1-50", "51-200", "201-1000", "1000-5000", "5000+"
                ])
            
            location = st.text_input("📍 Ubicación Principal", "Madrid, España")
            
            st.markdown("**🔍 Fuentes de Información**")
            sources = []
            
            col_c, col_d = st.columns(2)
            with col_c:
                if st.checkbox("🔗 LinkedIn", True): sources.append("LinkedIn")
                if st.checkbox("🌐 Sitio Web", True): sources.append("Website")
                if st.checkbox("🐦 Twitter/X"): sources.append("Twitter")
                if st.checkbox("📘 Facebook"): sources.append("Facebook")
            
            with col_d:
                if st.checkbox("💻 GitHub"): sources.append("GitHub")
                if st.checkbox("🌐 DNS/Subdominios"): sources.append("DNS")
                if st.checkbox("📰 Noticias"): sources.append("News")
                if st.checkbox("💼 Ofertas Trabajo"): sources.append("Jobs")
            
            claude_analysis = st.checkbox(" Análisis Avanzado con Claude", True)
            
            submit_button = st.form_submit_button(" Iniciar Análisis OSINT con IA", type="primary")
            
            if submit_button:
                company_data = {
                    'name': company_name,
                    'domain': domain,
                    'industry': industry,
                    'size': company_size,
                    'location': location,
                    'sources': sources
                }
                
                run_claude_osint_analysis(company_data, claude_analysis)
    
    with col2:
        display_claude_osint_results()

def run_claude_osint_analysis(company_data, use_claude=True):
    """Ejecutar análisis OSINT con Claude"""
    
    progress_container = st.container()
    
    with progress_container:
        st.markdown("#### 🔄 Análisis OSINT en Progreso...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Fase 1: Recopilación tradicional
        traditional_steps = [
            "🔍 Escaneando LinkedIn corporativo...",
            "🌐 Analizando sitio web y subdominios...",
            "📧 Extrayendo direcciones de email...",
            "👥 Identificando empleados clave...",
            "📊 Recopilando métricas básicas..."
        ]
        
        simulated_data = {}
        
        for i, step in enumerate(traditional_steps):
            status_text.text(step)
            time.sleep(0.6)
            progress_bar.progress((i + 1) / (len(traditional_steps) + 3))
            
            # Simular datos recopilados
            if "LinkedIn" in step:
                simulated_data['linkedin_profiles'] = np.random.randint(45, 89)
            elif "email" in step:
                simulated_data['emails_found'] = np.random.randint(15, 35)
        
        # Fase 2: Análisis con Claude (si está habilitado)
        if use_claude:
            status_text.text(" Claude AI analizando datos recopilados...")
            time.sleep(1)
            progress_bar.progress(0.8)
            
            try:
                claude_results = st.session_state.claude_agent.analyze_company_osint(company_data)
                
                status_text.text(" Claude generando insights avanzados...")
                time.sleep(1)
                progress_bar.progress(0.9)
                
                # Combinar datos simulados con análisis de Claude
                final_results = {
                    **simulated_data,
                    **claude_results,
                    'claude_analysis': True,
                    'company_data': company_data
                }
                
            except Exception as e:
                st.error(f"Error en análisis de Claude: {e}")
                final_results = {
                    **simulated_data,
                    'claude_analysis': False,
                    'fallback_mode': True,
                    'company_data': company_data
                }
        else:
            final_results = {
                **simulated_data,
                'claude_analysis': False,
                'company_data': company_data
            }
        
        # Finalizar
        status_text.text("✅ Análisis OSINT completado con éxito!")
        progress_bar.progress(1.0)
        
        # Guardar resultados
        st.session_state.osint_results = final_results
        
        # Guardar en historial
        if 'recent_analyses' not in st.session_state:
            st.session_state.recent_analyses = []
        
        st.session_state.recent_analyses.append({
            'type': 'OSINT Analysis',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'company': company_data['name'],
            'claude_used': use_claude,
            'summary': {
                'risk_score': final_results.get('risk_score', 0.75),
                'vulnerabilities': len(final_results.get('vulnerabilities_found', [])),
                'employees_analyzed': final_results.get('employees_at_risk', 45)
            }
        })
        
        time.sleep(1)
        st.rerun()

def display_claude_osint_results():
    """Mostrar resultados de OSINT con Claude"""
    st.markdown("####  Resultados del Análisis")
    
    if 'osint_results' not in st.session_state:
        st.info(" Ejecuta un análisis OSINT para ver los resultados")
        return
    
    results = st.session_state.osint_results
    
    # Indicador de Claude
    if results.get('claude_analysis'):
        st.success(" **Análisis potenciado por Claude AI**")
    else:
        st.warning("⚠️ **Análisis básico** - Claude no disponible")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_score = results.get('risk_score', 0.75)
        risk_color = "🔴" if risk_score >= 0.8 else "🟡" if risk_score >= 0.6 else "🟢"
        st.metric("Risk Score", f"{risk_color} {risk_score:.2f}", f"Confianza: {results.get('confidence_level', 0.87):.0%}")
    
    with col2:
        st.metric("Vulnerabilidades", len(results.get('vulnerabilities_found', [])), "↑ Críticas identificadas")
    
    with col3:
        st.metric("Empleados en Riesgo", results.get('employees_at_risk', 45), "↑ Análisis IA")
    
    # Resultados detallados si Claude fue usado
    if results.get('claude_analysis') and not results.get('fallback_mode'):
        
        # Vulnerabilidades encontradas
        st.markdown("#### ⚠️ Vulnerabilidades Identificadas por Claude")
        for vuln in results.get('vulnerabilities_found', []):
            st.markdown(f"""
            <div class="vulnerability-item">
                ⚠️ {vuln}
            </div>
            """, unsafe_allow_html=True)
        
        # Hallazgos críticos
        if 'critical_findings' in results:
            st.markdown("#### 🔍 Hallazgos Críticos")
            for finding in results['critical_findings']:
                st.markdown(f"• **{finding}**")
        
        # Análisis por departamento
        if 'department_risks' in results:
            st.markdown("####  Riesgos por Departamento")
            dept_data = results['department_risks']
            
            if isinstance(dept_data, dict):
                df_dept = pd.DataFrame(list(dept_data.items()), columns=['Departamento', 'Riesgo'])
                
                fig = px.bar(
                    df_dept, 
                    x='Departamento', 
                    y='Riesgo',
                    color='Riesgo',
                    color_continuous_scale='Reds',
                    title="Nivel de Riesgo por Departamento"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Recomendaciones de Claude
        st.markdown("#### 🛡️ Recomendaciones de Claude")
        for rec in results.get('recommendations', []):
            st.markdown(f"""
            <div class="recommendation-item">
                🛡️ {rec}
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Resultados básicos
        st.markdown("####  Resultados Básicos")
        basic_metrics = {
            "LinkedIn Profiles": results.get('linkedin_profiles', 67),
            "Emails Found": results.get('emails_found', 23),
            "GitHub Repos": results.get('github_repos', 18),
            "Subdomains": results.get('subdomains', 31)
        }
        
        for metric, value in basic_metrics.items():
            st.metric(metric, value)

def create_claude_profiling_interface():
    """Interfaz de perfilado con Claude"""
    st.markdown("### 👥 Perfilado Psicológico Avanzado con Claude")
    st.info("**Claude AI** realizará análisis psicológico profundo para identificar vulnerabilidades específicas")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("####  Selección y Configuración")
        
        # Lista de empleados (de OSINT previo o predefinida)
        if 'osint_results' in st.session_state:
            employee_count = st.session_state.osint_results.get('employees_at_risk', 10)
            employee_options = [f"Empleado {i+1} - Cargo {['CEO', 'CFO', 'CTO', 'Director', 'Gerente', 'Analista'][i%6]}" 
                             for i in range(min(employee_count, 15))]
        else:
            employee_options = [
                "María González - CFO",
                "Carlos Rodríguez - Director IT", 
                "Ana Martínez - Gerente RRHH",
                "Luis Hernández - Coord. Operaciones"
            ]
        
        selected_employee = st.selectbox(" Empleado a Analizar", employee_options)
        
        st.markdown("####  Datos del Perfil")
        
        with st.form("claude_profile_form"):
            
            # Métricas deslizables
            social_activity = st.slider(" Actividad en RRSS", 1, 10, 7, 
                                      help="Nivel de actividad en redes sociales")
            info_sharing = st.slider(" Compartir Información", 1, 10, 6,
                                   help="Tendencia a compartir información corporativa")
            security_awareness = st.slider("🛡️ Conciencia de Seguridad", 1, 10, 4,
                                         help="Nivel de conocimiento en seguridad")
            
            # Datos adicionales
            department = st.selectbox(" Departamento", 
                                    ["Finanzas", "IT", "RRHH", "Ventas", "Marketing", "Operaciones", "Legal"])
            
            interests = st.multiselect(" Intereses Identificados",
                                     ["Tecnología", "Deportes", "Viajes", "Familia", "Finanzas", 
                                      "Entretenimiento", "Educación", "Arte", "Música"],
                                     default=["Tecnología", "Viajes"])
            
            communication_style = st.selectbox(" Estilo de Comunicación",
                                              ["Formal", "Casual", "Técnico", "Emocional", "Directo"])
            
            work_schedule = st.selectbox(" Horario de Trabajo",
                                       ["9-17 Estándar", "Flexible", "Nocturno", "Fines de Semana", "24/7 Disponible"])
            
            risk_factors = st.multiselect("⚠ Factores de Riesgo Observados",
                                        ["Oversharing en LinkedIn", "Información personal pública", 
                                         "Acceso privilegiado", "Contactos externos frecuentes",
                                         "Patrones predecibles", "Baja verificación de solicitudes"])
            
            analyze_button = st.form_submit_button(" Análisis Psicológico con Claude", type="primary")
            
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
                
                run_claude_profile_analysis(employee_data)
    
    with col2:
        display_claude_profile_results()

def run_claude_profile_analysis(employee_data):
    """Ejecutar análisis de perfil con Claude"""
    
    with st.spinner(" Claude analizando perfil psicológico..."):
        progress_bar = st.progress(0)
        
        analysis_steps = [
            "Analizando patrones de comportamiento digital...",
            "Evaluando vulnerabilidades psicológicas...",
            "Identificando vectores de ataque óptimos...",
            "Claude procesando análisis avanzado...",
            "Generando recomendaciones personalizadas..."
        ]
        
        for i, step in enumerate(analysis_steps):
            time.sleep(0.8)
            progress_bar.progress((i + 1) / len(analysis_steps))
            st.text(step)
        
        try:
            # Análisis con Claude
            claude_analysis = st.session_state.claude_agent.analyze_employee_profile(employee_data)
            
            # Guardar resultados
            st.session_state.profile_results = {
                **claude_analysis,
                'employee_data': employee_data,
                'claude_analysis': True
            }
            
            # Agregar al historial
            if 'recent_analyses' not in st.session_state:
                st.session_state.recent_analyses = []
            
            st.session_state.recent_analyses.append({
                'type': 'Employee Profile',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'employee': employee_data['name'],
                'claude_used': True,
                'summary': {
                    'risk_score': claude_analysis.get('risk_score', 0.75),
                    'vulnerabilities': len(claude_analysis.get('vulnerability_profile', [])),
                    'vectors': len(claude_analysis.get('optimal_attack_vectors', []))
                }
            })
            
        except Exception as e:
            st.error(f"Error en análisis de Claude: {e}")
            st.session_state.profile_results = {
                'risk_score': 0.75,
                'fallback_mode': True,
                'employee_data': employee_data
            }
        
        st.success(" Análisis psicológico completado")
        time.sleep(1)
        st.rerun()

def display_claude_profile_results():
    """Mostrar resultados del perfilado con Claude"""
    st.markdown("####  Resultados del Análisis Psicológico")
    
    if 'profile_results' not in st.session_state:
        st.info(" Selecciona un empleado y ejecuta el análisis para ver los resultados")
        return
    
    profile = st.session_state.profile_results
    
    # Indicador de Claude
    if profile.get('claude_analysis') and not profile.get('fallback_mode'):
        st.success(" **Análisis psicológico realizado por Claude AI**")
    else:
        st.warning("⚠ **Análisis básico** - Usando modo fallback")
    
    # Score de riesgo principal
    risk_score = profile.get('risk_score', 0.75)
    confidence = profile.get('confidence_level', 0.87)
    
    risk_color = '#ef4444' if risk_score >= 0.8 else '#f59e0b' if risk_score >= 0.6 else '#3b82f6'
    risk_level = 'CRÍTICO' if risk_score >= 0.8 else 'ALTO' if risk_score >= 0.6 else 'MEDIO'
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {risk_color}, {risk_color}88); 
                padding: 1.5rem; border-radius: 12px; text-align: center; margin-bottom: 1rem;">
        <h2 style="color: white; margin: 0;">Score de Riesgo: {risk_score:.2f}/1.0</h2>
        <p style="color: white; margin: 0.5rem 0 0 0; opacity: 0.9;">
            {risk_level} • Confianza: {confidence:.0%}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas detalladas
    if not profile.get('fallback_mode'):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🎯 Vectores de Ataque", len(profile.get('optimal_attack_vectors', [])))
        with col2:
            st.metric("⚠️ Vulnerabilidades", len(profile.get('vulnerability_profile', [])))
        with col3:
            st.metric("🛡️ Contramedidas", len(profile.get('personalized_recommendations', [])))
        
        # Perfil de vulnerabilidades
        st.markdown("#### ⚠️ Perfil de Vulnerabilidades")
        for vuln in profile.get('vulnerability_profile', []):
            if isinstance(vuln, dict):
                severity_color = {'CRÍTICA': '#ef4444', 'ALTA': '#f59e0b', 'MEDIA': '#3b82f6'}.get(vuln.get('severity', 'MEDIA'), '#3b82f6')
                st.markdown(f"""
                <div class="vulnerability-item" style="border-left-color: {severity_color};">
                    <strong>{vuln.get('type', 'Vulnerabilidad')}</strong> - {vuln.get('severity', 'MEDIA')}<br>
                    {vuln.get('description', 'Sin descripción')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="vulnerability-item">
                    ⚠️ {vuln}
                </div>
                """, unsafe_allow_html=True)
        
        # Vectores de ataque óptimos
        st.markdown("####  Vectores de Ataque Identificados")
        for vector in profile.get('optimal_attack_vectors', []):
            if isinstance(vector, dict):
                probability = vector.get('probability', 0.5)
                prob_color = '#ef4444' if probability >= 0.8 else '#f59e0b' if probability >= 0.6 else '#3b82f6'
                st.markdown(f"""
                <div class="analysis-result" style="border-left: 4px solid {prob_color};">
                    <strong>{vector.get('type', 'Vector desconocido')}</strong> - Probabilidad: {probability:.0%}<br>
                    {vector.get('description', 'Sin descripción')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"• **{vector}**")
        
        # Recomendaciones personalizadas
        st.markdown("####🛡 Recomendaciones Personalizadas de Claude")
        for rec in profile.get('personalized_recommendations', []):
            st.markdown(f"""
            <div class="recommendation-item">
                🛡 {rec}
            </div>
            """, unsafe_allow_html=True)
        
        # Factores psicológicos
        if 'psychological_factors' in profile:
            st.markdown("####  Análisis Psicológico")
            factors = profile['psychological_factors']
            
            if isinstance(factors, list):
                for factor in factors:
                    st.markdown(f"• {factor}")
            elif isinstance(factors, dict):
                for key, value in factors.items():
                    st.markdown(f"• **{key}**: {value}")
    
    else:
        # Mostrar resultados básicos en modo fallback
        st.markdown("####  Análisis Básico")
        st.info("Análisis completo requiere conexión con Claude AI")

def create_claude_attack_simulation():
    """Simulación de ataques con Claude"""
    st.markdown("###  Ataques con Claude")
    st.warning("**Claude generará análisis de técnicas para fines de capacitación únicamente")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("#### 🎯 Configuración de Simulación")
        
        # Verificar si hay perfiles previos
        if 'profile_results' in st.session_state:
            st.success(" Usando perfil analizado previamente")
            target_name = st.session_state.profile_results.get('employee_data', {}).get('name', 'Empleado')
            st.write(f"**Objetivo**: {target_name}")
        else:
            st.info(" Ejecuta primero un análisis de perfilado para mejores resultados")
        
        attack_type = st.selectbox(
            " Tipo de Ataque",
            [
                "📧 Email Phishing Dirigido",
                "📱 Vishing (Voice Phishing)",
                "💬 Smishing (SMS)",
                "🔗 LinkedIn Social Engineering",
                "🌐 Watering Hole Attack",
                "👥 Pretexting Personalizado"
            ]
        )
        
        scenario_context = st.text_area(
            " Contexto del Escenario",
            "Empresa en proceso de auditoría financiera anual\nPresión por cumplir deadlines de cierre trimestral\nReorganización departamental en curso",
            height=100
        )
        
        simulation_depth = st.selectbox(
            "🔍 Profundidad del Análisis",
            ["Básico", "Detallado", "Exhaustivo"]
        )
        
        if st.button(" Generar Simulación con Claude", type="primary"):
            run_claude_attack_simulation(attack_type, scenario_context, simulation_depth)
    
    with col2:
        display_claude_simulation_results()

def run_claude_attack_simulation(attack_type, context, depth):
    """Ejecutar simulación de ataque con Claude"""
    
    # Obtener datos del perfil si están disponibles
    target_profile = st.session_state.get('profile_results', {})
    company_context = st.session_state.get('osint_results', {}).get('company_data', {})
    
    with st.spinner(" Claude generando simulación educativa..."):
        progress_bar = st.progress(0)
        
        steps = [
            "Analizando perfil del objetivo...",
            "Identificando vectores psicológicos...",
            "Diseñando estrategia de aproximación...",
            "Claude procesando escenario completo...",
            "Generando contramedidas específicas..."
        ]
        
        for i, step in enumerate(steps):
            time.sleep(0.7)
            progress_bar.progress((i + 1) / len(steps))
            st.text(step)
        
        try:
            # Generar simulación con Claude
            simulation_data = {
                'attack_type': attack_type,
                'context': context,
                'depth': depth,
                'target_profile': target_profile,
                'company_context': company_context
            }
            
            claude_simulation = st.session_state.claude_agent.generate_attack_simulation(
                target_profile, company_context
            )
            
            # Guardar resultados
            st.session_state.simulation_results = {
                **claude_simulation,
                'simulation_data': simulation_data,
                'claude_analysis': True
            }
            
            # Agregar al historial
            if 'recent_analyses' not in st.session_state:
                st.session_state.recent_analyses = []
            
            st.session_state.recent_analyses.append({
                'type': 'Attack Simulation',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'attack_type': attack_type,
                'claude_used': True,
                'summary': {
                    'success_probability': claude_simulation.get('success_probability', 0.67),
                    'techniques_used': len(claude_simulation.get('psychological_techniques', [])),
                    'countermeasures': len(claude_simulation.get('defensive_measures', []))
                }
            })
            
        except Exception as e:
            st.error(f"Error en simulación de Claude: {e}")
            st.session_state.simulation_results = {
                'fallback_mode': True,
                'attack_type': attack_type
            }
        
        st.success(" Simulación educativa completada")
        time.sleep(1)
        st.rerun()

def display_claude_simulation_results():
    """Mostrar resultados de simulación con Claude"""
    st.markdown("####  Resultados de la Simulación")
    
    if 'simulation_results' not in st.session_state:
        st.info(" Configura y ejecuta una simulación para ver los resultados")
        return
    
    simulation = st.session_state.simulation_results
    
    # Indicador de Claude
    if simulation.get('claude_analysis') and not simulation.get('fallback_mode'):
        st.success(" **Simulación generada por Claude AI**")
        
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            success_prob = simulation.get('success_probability', 0.67)
            prob_color = "🔴" if success_prob >= 0.8 else "🟡" if success_prob >= 0.6 else "🟢"
            st.metric("Probabilidad de Éxito", f"{prob_color} {success_prob:.0%}")
        
        with col2:
            techniques = len(simulation.get('psychological_techniques', []))
            st.metric("Técnicas Psicológicas", techniques)
        
        with col3:
            countermeasures = len(simulation.get('defensive_measures', []))
            st.metric("Contramedidas", countermeasures)
        
        # Escenario de ataque
        st.markdown("####  Escenario de Ataque Educativo")
        
        if 'attack_scenario' in simulation:
            scenario = simulation['attack_scenario']
            if isinstance(scenario, dict):
                for key, value in scenario.items():
                    st.markdown(f"**{key.replace('_', ' ').title()}**: {value}")
            else:
                st.markdown(f"**Escenario**: {scenario}")
        
        # Técnicas psicológicas utilizadas
        st.markdown("####  Técnicas Psicológicas Analizadas")
        for technique in simulation.get('psychological_techniques', []):
            if isinstance(technique, dict):
                st.markdown(f"""
                <div class="analysis-result">
                    <strong>{technique.get('name', 'Técnica')}</strong><br>
                    {technique.get('description', 'Sin descripción')}<br>
                    <small>Efectividad: {technique.get('effectiveness', 'N/A')}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"• {technique}")
        
        # Cronología del ataque
        if 'timeline_execution' in simulation:
            st.markdown("#### ⏱ Cronología del Ataque Simulado")
            timeline = simulation['timeline_execution']
            
            if isinstance(timeline, list):
                for i, step in enumerate(timeline, 1):
                    st.markdown(f"**Paso {i}**: {step}")
            elif isinstance(timeline, dict):
                for phase, description in timeline.items():
                    st.markdown(f"**{phase}**: {description}")
        
        # Señales de alerta ignoradas
        if 'red_flags_ignored' in simulation:
            st.markdown("####  Señales de Alerta que se Pasarían por Alto")
            for flag in simulation['red_flags_ignored']:
                st.markdown(f"""
                <div class="vulnerability-item">
                     {flag}
                </div>
                """, unsafe_allow_html=True)
        
        # Contramedidas específicas
        st.markdown("#### 🛡 Contramedidas Específicas")
        for measure in simulation.get('defensive_measures', []):
            st.markdown(f"""
            <div class="recommendation-item">
                🛡 {measure}
            </div>
            """, unsafe_allow_html=True)
        
        # Insights educativos
        if 'educational_insights' in simulation:
            st.markdown("####  Insights Educativos")
            insights = simulation['educational_insights']
            
            if isinstance(insights, list):
                for insight in insights:
                    st.info(f" {insight}")
            elif isinstance(insights, dict):
                for category, insight in insights.items():
                    st.info(f"**{category}**: {insight}")
        
        # Disclaimer
        st.markdown("---")
        st.warning(f" {simulation.get('disclaimer', 'Simulación educativa únicamente')}")
    
    else:
        st.warning(" **Simulación básica** - Claude no disponible")
        st.info("La simulación completa requiere conexión con Claude AI para generar escenarios realistas y contramedidas específicas.")

def create_claude_countermeasures():
    """Interfaz de contramedidas con Claude"""
    st.markdown("### 🛡️ Contramedidas Inteligentes con Claude AI")
    st.info("**Claude AI** generará un plan integral de contramedidas basado en todos los análisis previos")
    
    # Verificar análisis previos
    has_osint = 'osint_results' in st.session_state
    has_profile = 'profile_results' in st.session_state
    has_simulation = 'simulation_results' in st.session_state
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### 📊 Estado de Análisis")
        
        st.markdown(f"""
        **Análisis Disponibles:**
        - {'✅' if has_osint else '❌'} Análisis OSINT
        - {'✅' if has_profile else '❌'} Perfilado de Empleados  
        - {'✅' if has_simulation else '❌'} Simulación de Ataques
        """)
        
        if not any([has_osint, has_profile, has_simulation]):
            st.warning("⚠ Ejecuta al menos un análisis previo para generar contramedidas específicas")
            return
        
        st.markdown("#### ⚙️ Configuración del Plan")
        
        with st.form("countermeasures_form"):
            budget_range = st.selectbox(
                " Rango de Presupuesto",
                ["$10K - $25K", "$25K - $50K", "$50K - $100K", "$100K+", "Sin límite específico"]
            )
            
            implementation_timeline = st.selectbox(
                " Timeline de Implementación",
                ["Inmediato (1-2 semanas)", "Corto plazo (1-2 meses)", "Mediano plazo (3-6 meses)", "Largo plazo (6+ meses)"]
            )
            
            priority_focus = st.multiselect(
                " Áreas de Enfoque Prioritario",
                ["Capacitación de Personal", "Tecnología y Herramientas", "Políticas y Procedimientos", 
                 "Monitoreo y Detección", "Respuesta a Incidentes", "Evaluación Continua"],
                default=["Capacitación de Personal", "Tecnología y Herramientas"]
            )
            
            organization_size = st.selectbox(
                " Tamaño de Organización",
                ["Pequeña (1-50)", "Mediana (51-200)", "Grande (201-1000)", "Empresa (1000+)"]
            )
            
            industry_specific = st.checkbox(" Incluir requerimientos específicos de industria", True)
            
            generate_plan = st.form_submit_button(" Generar Plan Integral con Claude", type="primary")
            
            if generate_plan:
                plan_config = {
                    'budget_range': budget_range,
                    'timeline': implementation_timeline,
                    'priorities': priority_focus,
                    'org_size': organization_size,
                    'industry_specific': industry_specific
                }
                
                run_claude_countermeasures_analysis(plan_config)
    
    with col2:
        display_claude_countermeasures_results()

def run_claude_countermeasures_analysis(config):
    """Generar plan de contramedidas con Claude"""
    
    # Recopilar todos los análisis previos
    analysis_data = {}
    
    if 'osint_results' in st.session_state:
        analysis_data['osint'] = st.session_state.osint_results
    
    if 'profile_results' in st.session_state:
        analysis_data['profile'] = st.session_state.profile_results
    
    if 'simulation_results' in st.session_state:
        analysis_data['simulation'] = st.session_state.simulation_results
    
    analysis_data['config'] = config
    
    with st.spinner(" Claude generando plan integral de contramedidas..."):
        progress_bar = st.progress(0)
        
        steps = [
            "Analizando resultados de evaluaciones previas...",
            "Identificando vulnerabilidades críticas...",
            "Priorizando contramedidas por impacto...",
            "Claude calculando ROI y timeline...",
            "Generando plan de implementación detallado...",
            "Creando métricas de seguimiento..."
        ]
        
        for i, step in enumerate(steps):
            time.sleep(0.8)
            progress_bar.progress((i + 1) / len(steps))
            st.text(step)
        
        try:
            # Generar contramedidas con Claude
            countermeasures_plan = st.session_state.claude_agent.generate_countermeasures(analysis_data)
            
            # Guardar resultados
            st.session_state.countermeasures_results = {
                **countermeasures_plan,
                'config': config,
                'claude_analysis': True,
                'generation_time': datetime.now().isoformat()
            }
            
            # Agregar al historial
            if 'recent_analyses' not in st.session_state:
                st.session_state.recent_analyses = []
            
            st.session_state.recent_analyses.append({
                'type': 'Countermeasures Plan',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'claude_used': True,
                'summary': {
                    'total_budget': countermeasures_plan.get('budget_breakdown', {}).get('total_investment', '$50K'),
                    'measures_count': len(countermeasures_plan.get('immediate_actions', [])) + 
                                    len(countermeasures_plan.get('short_term_measures', [])),
                    'roi_estimated': countermeasures_plan.get('roi_analysis', {}).get('expected_roi', 'N/A')
                }
            })
            
        except Exception as e:
            st.error(f"Error generando contramedidas: {e}")
            st.session_state.countermeasures_results = {
                'fallback_mode': True,
                'config': config
            }
        
        st.success(" Plan de contramedidas generado exitosamente")
        time.sleep(1)
        st.rerun()

def display_claude_countermeasures_results():
    """Mostrar resultados de contramedidas con Claude"""
    st.markdown("#### 🛡 Plan Integral de Contramedidas")
    
    if 'countermeasures_results' not in st.session_state:
        st.info(" Configura y genera un plan de contramedidas para ver los resultados")
        return
    
    plan = st.session_state.countermeasures_results
    
    # Indicador de Claude
    if plan.get('claude_analysis') and not plan.get('fallback_mode'):
        st.success(" **Plan generado por Claude AI**")
        
        # Resumen ejecutivo del presupuesto
        if 'budget_breakdown' in plan:
            budget = plan['budget_breakdown']
            
            st.markdown("####  Resumen Presupuestario")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Inversión Total", budget.get('total_investment', 'N/A'))
            with col2:
                st.metric("Inmediato", budget.get('immediate', 'N/A'))
            with col3:
                st.metric("Corto Plazo", budget.get('short_term', 'N/A'))
            with col4:
                st.metric("Largo Plazo", budget.get('long_term', 'N/A'))
        
        # ROI Analysis
        if 'roi_analysis' in plan:
            st.markdown("####  Análisis de ROI")
            roi = plan['roi_analysis']
            
            if isinstance(roi, dict):
                for metric, value in roi.items():
                    st.markdown(f"• **{metric.replace('_', ' ').title()}**: {value}")
        
        # Acciones inmediatas
        st.markdown("####  Acciones Inmediatas (0-7 días)")
        for action in plan.get('immediate_actions', []):
            if isinstance(action, dict):
                impact_color = {'CRÍTICO': '#ef4444', 'ALTO': '#f59e0b', 'MEDIO': '#3b82f6'}.get(action.get('impact', 'MEDIO'), '#3b82f6')
                st.markdown(f"""
                <div class="recommendation-item" style="border-left-color: {impact_color};">
                    <strong>{action.get('action', 'Acción')}</strong><br>
                     {action.get('timeline', 'N/A')} |  {action.get('cost', 'N/A')} |  Impacto: {action.get('impact', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="recommendation-item">
                     {action}
                </div>
                """, unsafe_allow_html=True)
        
        # Medidas a corto plazo
        st.markdown("#### ⏱️ Medidas a Corto Plazo (1-4 semanas)")
        for measure in plan.get('short_term_measures', []):
            if isinstance(measure, dict):
                st.markdown(f"""
                <div class="analysis-result">
                    <strong>{measure.get('action', 'Medida')}</strong><br>
                     {measure.get('timeline', 'N/A')} |  {measure.get('cost', 'N/A')} |  Impacto: {measure.get('impact', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"• {measure}")
        
        # Estrategia a largo plazo
        if 'long_term_strategy' in plan:
            st.markdown("####  Estrategia a Largo Plazo")
            strategy = plan['long_term_strategy']
            
            if isinstance(strategy, list):
                for item in strategy:
                    st.markdown(f"• {item}")
            elif isinstance(strategy, dict):
                for phase, description in strategy.items():
                    st.markdown(f"**{phase}**: {description}")
            else:
                st.markdown(strategy)
        
        # Timeline de implementación
        if 'implementation_timeline' in plan:
            st.markdown("####  Cronograma de Implementación")
            
            timeline_data = plan['implementation_timeline']
            
            if isinstance(timeline_data, dict):
                # Crear gráfico de Gantt simple
                phases = list(timeline_data.keys())
                durations = [30, 60, 90, 180]  # Días estimados
                
                fig = go.Figure()
                
                for i, (phase, duration) in enumerate(zip(phases, durations)):
                    fig.add_trace(go.Bar(
                        name=phase,
                        x=[duration],
                        y=[phase],
                        orientation='h',
                        marker_color=px.colors.qualitative.Set3[i % len(px.colors.qualitative.Set3)]
                    ))
                
                fig.update_layout(
                    title="Timeline de Implementación",
                    xaxis_title="Días",
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Métricas de éxito
        if 'success_metrics' in plan:
            st.markdown("####  Métricas de Éxito")
            metrics = plan['success_metrics']
            
            if isinstance(metrics, list):
                for metric in metrics:
                    st.markdown(f"• {metric}")
            elif isinstance(metrics, dict):
                for category, metric_list in metrics.items():
                    st.markdown(f"**{category}**:")
                    if isinstance(metric_list, list):
                        for metric in metric_list:
                            st.markdown(f"  • {metric}")
                    else:
                        st.markdown(f"  • {metric_list}")
        
        # Programas de capacitación
        if 'training_programs' in plan:
            st.markdown("#### 🎓 Programas de Capacitación Recomendados")
            training = plan['training_programs']
            
            if isinstance(training, list):
                for program in training:
                    if isinstance(program, dict):
                        st.markdown(f"""
                        <div class="analysis-result">
                            <strong>{program.get('name', 'Programa')}</strong><br>
                             Audiencia: {program.get('audience', 'N/A')}<br>
                             Duración: {program.get('duration', 'N/A')}<br>
                             Costo: {program.get('cost', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"• {program}")
        
        # Botón para descargar plan completo
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(" Exportar Plan Completo"):
                st.success(" Plan exportado (simulado)")
        
        with col2:
            if st.button(" Enviar a Ejecutivos"):
                st.success(" Enviado por email (simulado)")
        
        with col3:
            if st.button(" Programar Revisión"):
                st.success(" Revisión programada")
    
    else:
        st.warning("⚠ **Plan básico** - Claude no disponible")
        st.info("El plan completo requiere conexión con Claude AI para generar recomendaciones específicas y análisis de ROI.")

# Funciones auxiliares para gráficos (reutilizadas del código anterior)
def create_risk_distribution_chart():
    """Gráfico de distribución de riesgo"""
    risk_data = pd.DataFrame({
        'Nivel': ['Crítico', 'Alto', 'Medio', 'Bajo'],
        'Cantidad': [87, 234, 456, 123]
    })
    
    colors = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981']
    
    fig = px.pie(
        risk_data,
        values='Cantidad',
        names='Nivel',
        title="Distribución de Niveles de Riesgo",
        color_discrete_sequence=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
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
        line=dict(color='#ef4444', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Evolución de Vulnerabilidades en el Tiempo",
        xaxis_title="Período",
        yaxis_title="Número de Vulnerabilidades",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
        
