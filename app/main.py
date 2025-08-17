import streamlit as st
import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.dashboard import create_executive_dashboard
from components.osint_module import create_osint_interface
from components.profiling import create_profiling_interface
from components.security_agent import SecurityIntelligenceAgent
import plotly.express as px
import pandas as pd
import json
from datetime import datetime
import time

# Configuración de la página
st.set_page_config(
    page_title="Security Intelligence Platform - Demo",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://tu-empresa.com/support',
        'Report a bug': "https://tu-empresa.com/bug-report",
        'About': "# Security Intelligence Platform\nDemo profesional para análisis de vulnerabilidades de ingeniería social."
    }
)

# CSS personalizado
def load_css():
    st.markdown("""
    <style>
    /* Importar fuentes de Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS */
    :root {
        --primary-color: #1e3a8a;
        --secondary-color: #3b82f6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --light-bg: #f8fafc;
        --dark-text: #1f2937;
        --border-color: #e5e7eb;
    }
    
    /* Estilos generales */
    .main > div {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(30, 58, 138, 0.15);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Tarjetas de métricas */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--secondary-color);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
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
        color: var(--dark-text);
    }
    
    .metric-card p {
        margin: 0.5rem 0 0 0;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Variaciones de color para riesgo */
    .risk-critical { border-left-color: var(--danger-color) !important; }
    .risk-high { border-left-color: #f97316 !important; }
    .risk-medium { border-left-color: var(--warning-color) !important; }
    .risk-low { border-left-color: var(--success-color) !important; }
    
    .risk-critical h3 { color: var(--danger-color); }
    .risk-high h3 { color: #f97316; }
    .risk-medium h3 { color: var(--warning-color); }
    .risk-low h3 { color: var(--success-color); }
    
    /* Botones personalizados */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.15);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: var(--light-bg);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    /* Progress bars */
    .stProgress .st-bo {
        background-color: var(--secondary-color);
    }
    
    /* Alertas */
    .stAlert {
        border-radius: 8px;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Tablas */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Loading spinner personalizado */
    .stSpinner {
        color: var(--secondary-color);
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Cargar CSS personalizado
    load_css()
    
    # Inicializar session state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = {}
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1> Security Intelligence Platform</h1>
        <p>Demostración Profesional de Análisis de Vulnerabilidades de Ingeniería Social</p>
        <small>Powered by AI • Real-time Analysis • Enterprise Grade</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar de configuración
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1e3a8a/white?text=SecIntel+Pro", use_column_width=True)
        
        st.markdown("### ⚙️ Configuración de Análisis")
        
        # Configuraciones principales
        analysis_mode = st.selectbox(
            " Modo de Análisis",
            [
                " Análisis Completo",
                " OSINT Básico", 
                " Perfilado Social",
                " Simulación de Ataque",
                " Evaluación de Defensas"
            ],
            help="Selecciona el tipo de análisis a realizar"
        )
        
        target_scope = st.radio(
            " Alcance del Objetivo",
            [
                " Empresa Completa",
                "🏛 Departamento Específico", 
                " Empleado Individual"
            ]
        )
        
        risk_threshold = st.slider(
            " Umbral de Riesgo", 
            0.0, 1.0, 0.7, 0.1,
            help="Establece el nivel mínimo de riesgo para alertas"
        )
        
        st.markdown("---")
        
        # Información del demo
        st.markdown("### ℹ Información del Demo")
        st.info("""
        **Demo Mode Activo**
        
        • Datos simulados realistas
        • APIs en modo sandbox
        • Resultados para fines educativos
        • Sin impacto en sistemas reales
        """)
        
        # Botón de reset
        if st.button(" Reiniciar Demo", help="Limpiar todos los datos y comenzar de nuevo"):
            st.session_state.analysis_complete = False
            st.session_state.current_analysis = {}
            st.rerun()
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        " Dashboard Ejecutivo",
        " Inteligencia OSINT", 
        " Perfilado Avanzado",
        " Simulación de Ataques",
        " Contramedidas"
    ])
    
    with tab1:
        create_executive_dashboard()
    
    with tab2:
        create_osint_interface()
    
    with tab3:
        create_profiling_interface()
    
    with tab4:
        create_attack_simulation()
    
    with tab5:
        create_countermeasures_interface()

def create_attack_simulation():
    st.markdown("### Ataques de Ingeniería Social")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("####  Configuración del Escenario")
        
        attack_type = st.selectbox(
            "Tipo de Ataque",
            [
                " Phishing por Email",
                " Vishing (Voice Phishing)",
                " Smishing (SMS Phishing)",
                " Watering Hole",
                " Pretexting Social"
            ]
        )
        
        target_profile = st.text_area(
            "Perfil del Objetivo",
            "María González, CFO de TechCorp\n- 15 años de experiencia\n- Activa en LinkedIn\n- Intereses: Golf, tecnología financiera",
            height=100
        )
        
        company_context = st.text_area(
            "Contexto Empresarial",
            "TechCorp Solutions\n- Empresa de software financiero\n- 500 empleados\n- Reciente expansión internacional\n- Procesos de auditoría en curso",
            height=100
        )
        
        if st.button(" Generar Ataque", type="primary"):
            simulate_attack_scenario(attack_type, target_profile, company_context)
    
    with col2:
        st.markdown("####  Métricas de Simulación")
        
        # Métricas de la simulación
        st.metric("Probabilidad de Éxito", "87%", "↑ 15%")
        st.metric("Tiempo de Preparación", "45 min", "↓ 30 min")
        st.metric("Técnicas Utilizadas", "5", "↑ 2")
        
        st.markdown("#### Vectores de Ataque")
        attack_vectors = {
            'Email': 85,
            'Teléfono': 65,
            'Redes Sociales': 78,
            'Físico': 45
        }
        
        for vector, score in attack_vectors.items():
            st.progress(score/100, text=f"{vector}: {score}%")

def simulate_attack_scenario(attack_type, target_profile, company_context):
    """Simular escenario de ataque educativo"""
    with st.spinner("Generando simulación de ataque..."):
        progress_bar = st.progress(0)
        
        # Simulación de pasos
        steps = [
            "Analizando perfil del objetivo...",
            "Identificando vulnerabilidades psicológicas...",
            "Generando contexto de pretexto...",
            "Diseñando estrategia de aproximación...",
            "Calculando probabilidades de éxito...",
            "Generando contramedidas específicas..."
        ]
        
        for i, step in enumerate(steps):
            time.sleep(0.5)  # Simular procesamiento
            progress_bar.progress((i + 1) / len(steps))
            st.text(step)
        
        st.success(" Analisis completado")
        
        # Mostrar resultados de la simulación
        st.markdown("####  Escenario de Ataque")
        
        # Crear tabs para diferentes aspectos
        sim_tab1, sim_tab2, sim_tab3 = st.tabs([" Estrategia", " Psicología", " Defensas"])
        
        with sim_tab1:
            st.markdown("""
            **Vector de Aproximación**: Email corporativo falso
            
            **Pretexto Utilizado**: Auditoría financiera urgente
            
            **Escalación**: 
            1. Email inicial desde "auditor externo"
            2. Solicitud de documentos financieros
            3. Llamada de seguimiento para crear urgencia
            4. Redirección a portal falso para captura de credenciales
            
            **Timing**: Viernes 4:30 PM (momento de alta presión)
            """)
        
        with sim_tab2:
            st.markdown("""
            **Técnicas Psicológicas Identificadas**:
            
            • **Autoridad**: Uso de logotipos y firma oficial
            • **Urgencia**: Deadline de fin de día
            • **Reciprocidad**: "Ayudar" con proceso de auditoría
            • **Validación Social**: Referencias a otros ejecutivos
            • **Escasez**: "Última oportunidad" para enviar documentos
            """)
        
        with sim_tab3:
            st.markdown("""
            **Contramedidas Específicas**:
            
            ✅ **Verificación Multi-canal**: Confirmar por teléfono interno
            ✅ **Políticas de Urgencia**: No procesar solicitudes urgentes sin validación
            ✅ **Capacitación Específica**: Entrenar al equipo financiero
            ✅ **Filtros de Email**: Implementar detección de dominios similares
            ✅ **Proceso de Escalación**: Protocolo claro para solicitudes inusuales
            """)

def create_countermeasures_interface():
    st.markdown("###  Centro de Contramedidas")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("####  Recomendaciones Personalizadas")
        
        # Tabla de contramedidas
        countermeasures_data = {
            'Prioridad': ['🔴 Crítica', '🟡 Alta', '🟡 Alta', '🟢 Media', '🟢 Media'],
            'Contramedida': [
                'Capacitación anti-phishing para equipo financiero',
                'Implementar autenticación multifactor',
                'Políticas de verificación telefónica',
                'Monitoreo de redes sociales corporativas',
                'Simulacros de phishing mensuales'
            ],
            'Impacto': ['90%', '85%', '75%', '60%', '70%'],
            'Tiempo': ['2 semanas', '1 semana', '3 días', '1 mes', '2 meses'],
            'Costo': ['$15K', '$5K', '$2K', '$8K', '$12K']
        }
        
        df_countermeasures = pd.DataFrame(countermeasures_data)
        st.dataframe(df_countermeasures, use_container_width=True)
        
        st.markdown("#### 📊 ROI de Contramedidas")
        
        # Gráfico de ROI
        roi_data = {
            'Contramedida': ['Capacitación', 'MFA', 'Verificación', 'Monitoreo', 'Simulacros'],
            'Inversión': [15000, 5000, 2000, 8000, 12000],
            'Ahorro Anual': [450000, 380000, 225000, 180000, 280000],
            'ROI': [30, 76, 112.5, 22.5, 23.3]
        }
        
        fig = px.scatter(
            roi_data, 
            x='Inversión', 
            y='Ahorro Anual',
            size='ROI',
            color='ROI',
            hover_name='Contramedida',
            title="ROI de Contramedidas de Seguridad",
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("####  Plan de Implementación")
        
        # Timeline de implementación
        st.markdown("""
        **Semana 1-2**
        -  Auditoría de vulnerabilidades
        -  Implementación MFA
        -  Políticas de verificación
        
        **Semana 3-4**
        -  Capacitación anti-phishing
        -  Configuración de alertas
        -  Primer simulacro
        
        **Mes 2**
        -  Monitoreo RRSS
        -  Evaluación de efectividad
        -  Ajustes del programa
        
        **Mes 3+**
        -  Simulacros regulares
        -  Reportes mensuales
        -  Optimización continua
        """)
        
        st.markdown("####  Resumen Financiero")
        st.success("**Inversión Total**: $42K")
        st.info("**Ahorro Anual**: $1.5M")
        st.warning("**ROI Promedio**: 3,571%")

if __name__ == "__main__":
    main()
