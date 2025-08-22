import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime, timedelta
import sys
import os
import re
import ast

# Configuración de la página
st.set_page_config(
    page_title="Plataforma de Análisis de Seguridad",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar agente Claude (REAL)
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    st.error("Anthropic no instalado. Instalar con: pip install anthropic")

# CSS profesional minimalista
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main > div {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .email-container {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        line-height: 1.6;
    }
    
    .email-header {
        padding: 1rem;
        background: #f8fafc;
        border-radius: 6px;
        margin-bottom: 1rem;
        border-left: 4px solid #3b82f6;
    }
    
    .status-card {
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .status-success { border-left-color: #059669; background: #f0fdf4; }
    .status-warning { border-left-color: #d97706; background: #fffbeb; }
    .status-error { border-left-color: #dc2626; background: #fef2f2; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def main():
    """Función principal mejorada con manejo de errores"""
    try:
        load_css()
        
        # Inicializar estado de la sesión
        if 'demo_mode' not in st.session_state:
            st.session_state.demo_mode = False
        if 'completed_analyses' not in st.session_state:
            st.session_state.completed_analyses = []
        if 'user_profiles' not in st.session_state:
            st.session_state.user_profiles = []
        if 'generated_content' not in st.session_state:
            st.session_state.generated_content = []
        
        # Header principal
        st.markdown("""
        <div class="main-header">
            <h1>Sistema de Análisis de Vulnerabilidades</h1>
            <p>Plataforma Profesional de Evaluación de Seguridad</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Configurar agente de IA
        setup_ai_agent()
        
        # Menú principal
        tab1, tab2, tab3, tab4 = st.tabs([
            "Panel Principal",
            "Análisis OSINT", 
            "Perfilado de Usuario",
            "Generación de Contenido"
        ])
        
        with tab1:
            show_dashboard()
        
        with tab2:
            osint_analysis()
        
        with tab3:
            user_profiling()
        
        with tab4:
            content_generation()
        
        # Footer con información adicional
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #6b7280; font-size: 0.9rem; padding: 1rem;">
            <p><strong>Sistema de Análisis de Vulnerabilidades</strong> - Plataforma educativa para evaluación de seguridad</p>
            <p>⚠️ <strong>Uso Ético:</strong> Esta herramienta debe usarse únicamente para fines educativos y de concientización sobre seguridad.</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error en la aplicación: {str(e)}")
        st.info("💡 **Soluciones sugeridas:**")
        st.markdown("""
        1. **Recargar la página** (F5 o Ctrl+R)
        2. **Usar el Modo Demo** en el sidebar
        3. **Verificar la API key** si está usando Claude
        4. **Limpiar caché** del navegador
        """)
        
        # Botón de emergencia para reiniciar
        if st.button("🔄 Reiniciar Aplicación", key="emergency_restart"):
            # Limpiar todo el estado
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def setup_ai_agent():
    """Configurar agente de IA REAL"""
    
    with st.sidebar:
        st.markdown("### Configuración del Sistema")
        
        if not ANTHROPIC_AVAILABLE:
            st.error("**Anthropic SDK no instalado**")
            st.code("pip install anthropic", language="bash")
            return
        
        # Input para API key
        st.markdown("**Obtener API Key:**")
        st.markdown("1. Ir a [console.anthropic.com](https://console.anthropic.com)")
        st.markdown("2. Crear cuenta / Iniciar sesión")
        st.markdown("3. Ir a 'API Keys' y crear nueva clave")
        
        api_key = st.text_input(
            "Clave API de Anthropic", 
            type="password",
            placeholder="sk-ant-api-key...",
            help="Debe empezar con 'sk-ant-'",
            key="anthropic_api_key_input"
        )
        
        # Separar botones del input
        col1, col2 = st.columns(2)
        
        with col1:
            demo_button = st.button("🧪 Modo Demo", key="demo_mode_button", help="Usar datos de ejemplo")
        
        with col2:
            if api_key:
                test_button = st.button("🔧 Probar API", key="test_connection_button", help="Probar conexión")
            else:
                test_button = False
        
        if demo_button:
            st.session_state.demo_mode = True
            st.success("✅ Modo demo activado - usando datos de ejemplo")
        
        if api_key and test_button:
            test_anthropic_connection(api_key)
        elif api_key:
            setup_anthropic_client(api_key)
        
        st.markdown("### 🎯 Sistema de Analisis de Inteligencia")
        if 'anthropic_client' in st.session_state or st.session_state.get('demo_mode', False):
            mode_text = "(DEMO)" if st.session_state.get('demo_mode', False) else ""
            st.markdown(f"""
            ✅ **Análisis OSINT ultra-detallado** {mode_text}  
            ✅ **Perfilado psicológico avanzado** {mode_text}  
            ✅ **Emails de phishing ULTRA-REALISTAS** {mode_text}  
            ✅ **Evaluación de vectores de ataque** {mode_text}  
            ✅ **Contenido indistinguible de emails reales** {mode_text}
            """)
        else:
            st.markdown("""
            ❌ Análisis OSINT automatizado  
            ❌ Perfilado psicológico avanzado  
            ❌ Generación de contenido adaptativo  
            ❌ Evaluación de vectores de ataque  
            ❌ Análisis contextual profundo
            """)

def test_anthropic_connection(api_key):
    """Probar conexión con Anthropic usando modelo que funciona"""
    if not api_key.startswith('sk-ant-'):
        st.error("❌ Formato de API key incorrecto. Debe empezar con 'sk-ant-'")
        return
    
    try:
        with st.spinner("Probando conexión..."):
            client = anthropic.Anthropic(api_key=api_key)
            # Usar directamente el modelo que funciona
            response = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=20,
                messages=[{"role": "user", "content": "Responde solo: 'Conexión exitosa'"}]
            )
            st.session_state.anthropic_client = client
            st.session_state.claude_model = "claude-3-5-haiku-20241022"
            st.session_state.demo_mode = False
            st.success(f"✅ {response.content[0].text}")
    except Exception as e:
        st.error(f"❌ Error de conexión: {str(e)}")
        st.info("💡 Intente con el modo demo mientras tanto")

def setup_anthropic_client(api_key):
    """Configurar cliente sin probar inmediatamente"""
    if api_key.startswith('sk-ant-'):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            st.session_state.anthropic_client = client
            st.session_state.claude_model = "claude-3-5-haiku-20241022"  # Usar modelo que funciona
            st.session_state.demo_mode = False
            st.info("🔑 API Key configurada. Use 'Probar API' para verificar.")
        except Exception as e:
            st.error(f"❌ Error configurando cliente: {str(e)}")

def display_system_info():
    """Mostrar información del sistema"""
    st.markdown("---")
    
    if st.session_state.get('demo_mode'):
        st.markdown("### 🧪 Modo Demo Activo")
        st.info("Usando datos de ejemplo predefinidos")
    elif 'anthropic_client' in st.session_state:
        st.markdown("### ✅ Sistema Conectado")
        st.info(f"Modelo: {st.session_state.get('claude_model', 'N/A')}")
    else:
        st.markdown("### ⚠️ Sistema No Configurado")
        st.warning("Configure API key o use modo demo")
    
    # Botón para limpiar caché fuera del form
    if st.button("🧹 Limpiar Caché", key="clear_cache_main"):
        clear_session_cache()
        st.success("✅ Caché limpiado")

def clear_session_cache():
    """Limpiar caché de sesión"""
    keys_to_clear = ['current_osint', 'current_profile', 'current_content']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def show_dashboard():
    """Panel principal del sistema"""
    
    if not ('anthropic_client' in st.session_state or st.session_state.get('demo_mode')):
        show_setup_instructions()
        return
    
    if st.session_state.get('demo_mode'):
        st.info("🧪 **MODO DEMO ACTIVADO** - Usando datos de ejemplo predefinidos")
    
    st.markdown("### Análisis Activos")
    
    # Métricas reales basadas en datos del sistema
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        analysis_count = len(st.session_state.get('completed_analyses', []))
        st.metric("Análisis Completados", analysis_count)
    
    with col2:
        profile_count = len(st.session_state.get('user_profiles', []))
        st.metric("Usuarios Perfilados", profile_count)
    
    with col3:
        content_count = len(st.session_state.get('generated_content', []))
        st.metric("Contenido Generado", content_count)
    
    with col4:
        system_status = "DEMO" if st.session_state.get('demo_mode') else "AI-Powered"
        st.metric("Estado del Sistema", system_status)
    
    # Historial de análisis
    display_recent_analyses()
    
    # Botón para cargar datos demo fuera de cualquier form
    if st.session_state.get('demo_mode'):
        st.markdown("### 🎯 Datos de Ejemplo")
        if st.button("📊 Cargar Análisis de Ejemplo", key="load_demo_dashboard"):
            load_demo_data()
            st.success("✅ Datos de ejemplo cargados")
            st.rerun()

def show_setup_instructions():
    """Mostrar instrucciones de configuración"""
    st.warning("**Configure la API de Anthropic o use el Modo Demo para acceder a todas las funcionalidades**")
    
    st.markdown("""
    **Para usar este sistema necesitas:**
    
    1. **Cuenta en Anthropic Console**: [console.anthropic.com](https://console.anthropic.com)
    2. **API Key de Anthropic**: Genera una clave en la consola  
    3. **Créditos disponibles**: $5 gratis para cuentas nuevas
    
    **💡 Tip**: Usa el botón **"🧪 Modo Demo"** en el sidebar para probar la interfaz sin API key.
    """)

def display_recent_analyses():
    """Mostrar análisis recientes"""
    if st.session_state.get('completed_analyses'):
        st.markdown("### Análisis Recientes")
        for analysis in st.session_state.completed_analyses[-3:]:
            with st.expander(f"{analysis['type']} - {analysis['timestamp']}", expanded=False):
                if isinstance(analysis['summary'], dict):
                    st.json(analysis['summary'])
                else:
                    st.write(analysis['summary'])

def safe_json_parse(content):
    """Parsear JSON de forma tolerante a errores comunes"""
    if not content or not isinstance(content, str):
        return None

    # Paso 1: limpieza básica
    content = content.strip()
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*$', '', content)

    # Paso 2: extraer bloque con llaves
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
    else:
        json_str = content

    # Paso 3: normalizar espacios y saltos
    json_str = json_str.replace('\n', ' ').replace('\r', ' ')
    json_str = re.sub(r'\s+', ' ', json_str)

    # Paso 4: intentar parseo normal
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Intentar reparaciones comunes
        json_str = fix_common_json_errors(json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Intentar con ast.literal_eval (más permisivo)
            try:
                return ast.literal_eval(json_str)
            except Exception as e:
                st.warning(f"Error JSON incluso tras reparación: {e}")
                st.text(f"Contenido: {json_str}")
                return None

def fix_common_json_errors(text):
    """Corrige errores comunes en JSON generado por IA"""
    # Quitar comas antes de cierre de objeto o array
    text = re.sub(r',\s*([}\]])', r'\1', text)

    # Asegurar que comillas sean dobles
    text = re.sub(r"'", '"', text)

    # Quitar caracteres no permitidos al final
    text = re.sub(r'[\s,]+$', '', text)

    return text


def osint_analysis():
    """Análisis OSINT real mejorado"""
    st.markdown("### Análisis de Inteligencia de Fuentes Abiertas")
    
    if not ('anthropic_client' in st.session_state or st.session_state.get('demo_mode')):
        st.error("**Requiere conexión con Anthropic Claude o modo demo para análisis OSINT**")
        return
    
    with st.form("osint_form", clear_on_submit=False):
        st.markdown("**Información del Objetivo**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Nombre de la Organización*", key="osint_company")
            domain = st.text_input("Dominio Web*", key="osint_domain")
            
        with col2:
            industry = st.selectbox("Industria", [
                "Tecnología", "Finanzas", "Salud", "Educación", 
                "Retail", "Manufactura", "Consultoría", "Gobierno"
            ], key="osint_industry")
            
            company_size = st.selectbox("Tamaño de Empresa", [
                "1-50", "51-200", "201-1000", "1000-5000", "5000+"
            ], key="osint_size")
        
        employee_info = st.text_area(
            "Información de Empleados Clave",
            placeholder="Nombres, roles, información pública de empleados relevantes...",
            key="osint_employees"
        )
        
        tech_stack = st.text_area(
            "Stack Tecnológico Conocido",
            placeholder="Tecnologías, herramientas, servicios que utiliza la empresa...",
            key="osint_tech"
        )
        
        additional_info = st.text_area(
            "Información Adicional",
            placeholder="Redes sociales, noticias recientes, proyectos públicos...",
            key="osint_additional"
        )
        
        submitted = st.form_submit_button("🔍 Iniciar Análisis OSINT", use_container_width=True)
        
        if submitted:
            if company_name and domain:
                run_osint_analysis(company_name, domain, industry, company_size, 
                                 employee_info, tech_stack, additional_info)
            else:
                st.error("Complete los campos obligatorios (*)")
    
    # Mostrar resultados existentes
    if 'current_osint' in st.session_state:
        st.markdown("---")
        st.markdown("### 📊 Último Análisis Completado")
        display_osint_results(st.session_state.current_osint)

def run_osint_analysis(company_name, domain, industry, company_size, 
                      employee_info, tech_stack, additional_info):
    """Ejecutar análisis OSINT real con Claude mejorado"""
    
    if st.session_state.get('demo_mode'):
        with st.spinner("Generando análisis OSINT de ejemplo..."):
            time.sleep(2)
            result = generate_demo_osint(company_name, domain, industry, employee_info)
            save_osint_result(result, company_name)
            display_osint_results(result)
        return
    
    with st.spinner("Ejecutando análisis OSINT profundo..."):
        
        # Prompt mejorado para análisis más específico
        prompt = f"""
Eres un experto analista de ciberseguridad especializado en OSINT. Analiza la siguiente empresa y proporciona un análisis detallado.

EMPRESA A ANALIZAR:
- Nombre: {company_name}
- Dominio: {domain}
- Industria: {industry}
- Tamaño: {company_size} empleados
- Empleados clave: {employee_info}
- Stack tecnológico: {tech_stack}
- Información adicional: {additional_info}

Proporciona un análisis JSON detallado con la siguiente estructura EXACTA:

{{
    "risk_score": 0.75,
    "risk_level": "ALTO",
    "vulnerabilities": [
        {{
            "type": "Exposición de Empleados en RRSS",
            "severity": "ALTA",
            "description": "Descripción específica basada en la información proporcionada",
            "evidence": "Evidencia específica encontrada",
            "impact": "Impacto potencial específico"
        }}
    ],
    "attack_vectors": [
        {{
            "vector": "Spear Phishing",
            "probability": 0.85,
            "impact": "Descripción del impacto específico",
            "method": "Método específico de ataque basado en la información"
        }}
    ],
    "employee_exposure": [
        {{
            "employee": "Nombre o rol específico",
            "risk_level": "ALTO",
            "exposure_type": "LinkedIn, GitHub, etc.",
            "sensitive_info": "Información específica expuesta"
        }}
    ],
    "technical_findings": [
        {{
            "finding": "Hallazgo técnico específico",
            "risk": "Nivel de riesgo",
            "recommendation": "Recomendación específica"
        }}
    ],
    "industry_specific_risks": [
        "Riesgo específico del sector {industry}",
        "Regulaciones específicas"
    ],
    "recommendations": [
        {{
            "priority": "ALTA",
            "category": "Categoría específica",
            "action": "Acción específica detallada",
            "timeline": "Marco temporal recomendado"
        }}
    ]
}}

Basa tu análisis en la información específica proporcionada. Si no hay información suficiente para un campo, usa "Análisis manual requerido".
"""
        
        try:
            response = st.session_state.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",  # Usar modelo que funciona
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            
            with st.expander("🔍 Debug: Respuesta de Claude", expanded=False):
                st.text(content)
            
            # Usar parsing mejorado
            analysis_result = safe_json_parse(content)
            
            if not analysis_result:
                st.warning("⚠️ Error en parsing JSON. Generando análisis básico...")
                analysis_result = generate_fallback_osint(company_name, industry, employee_info)
            
            save_osint_result(analysis_result, company_name)
            st.success("✅ Análisis OSINT completado")
            display_osint_results(analysis_result)
            
        except Exception as e:
            st.error(f"❌ Error en análisis: {str(e)}")
            # Usar fallback inmediatamente
            fallback_result = generate_fallback_osint(company_name, industry, employee_info)
            save_osint_result(fallback_result, company_name)
            display_osint_results(fallback_result)

def generate_demo_osint(company_name, domain, industry, employee_info):
    """Generar análisis OSINT demo más realista"""
    return {
        "risk_score": 0.78,
        "risk_level": "ALTO",
        "vulnerabilities": [
            {
                "type": "Exposición de Empleados en RRSS",
                "severity": "ALTA",
                "description": f"Personal de {company_name} comparte información sobre proyectos en LinkedIn",
                "evidence": "Perfiles públicos con detalles técnicos",
                "impact": "Posible ingeniería social dirigida"
            },
            {
                "type": "Información Técnica Pública",
                "severity": "MEDIA",
                "description": f"Stack tecnológico visible en ofertas de trabajo de {industry}",
                "evidence": "Ofertas laborales detalladas",
                "impact": "Reconocimiento de infraestructura"
            }
        ],
        "attack_vectors": [
            {
                "vector": "Spear Phishing dirigido",
                "probability": 0.85,
                "impact": f"Emails personalizados usando información de {industry}",
                "method": "Aprovechamiento de información pública de empleados"
            }
        ],
        "employee_exposure": [
            {
                "employee": employee_info[:30] + "..." if employee_info else "Personal técnico",
                "risk_level": "ALTO",
                "exposure_type": "LinkedIn, GitHub",
                "sensitive_info": "Proyectos, tecnologías, estructura organizacional"
            }
        ],
        "technical_findings": [
            {
                "finding": f"Subdominios expuestos de {domain}",
                "risk": "MEDIO",
                "recommendation": "Auditoría de subdominios y servicios expuestos"
            }
        ],
        "industry_specific_risks": [
            f"Regulaciones específicas del sector {industry}",
            f"Ataques dirigidos comunes en {industry}"
        ],
        "recommendations": [
            {
                "priority": "ALTA",
                "category": "Concienciación",
                "action": "Programa de entrenamiento en ingeniería social",
                "timeline": "30 días"
            }
        ]
    }

def generate_fallback_osint(company_name, industry, employee_info):
    """Generar análisis OSINT de fallback"""
    return {
        "risk_score": 0.65,
        "risk_level": "MEDIO",
        "vulnerabilities": [
            {
                "type": "Análisis Manual Requerido",
                "severity": "MEDIA",
                "description": f"Se requiere análisis manual para {company_name}",
                "evidence": "Información insuficiente para análisis automático",
                "impact": "Impacto por determinar"
            }
        ],
        "attack_vectors": [
            {
                "vector": "Vectores típicos del sector",
                "probability": 0.5,
                "impact": f"Impactos comunes en {industry}",
                "method": "Análisis manual requerido"
            }
        ],
        "employee_exposure": [],
        "technical_findings": [],
        "industry_specific_risks": [f"Riesgos específicos de {industry}"],
        "recommendations": [
            {
                "priority": "ALTA",
                "category": "Análisis",
                "action": "Realizar análisis OSINT manual detallado",
                "timeline": "Inmediato"
            }
        ]
    }

def save_osint_result(result, company_name):
    """Guardar resultado del análisis OSINT"""
    st.session_state.completed_analyses.append({
        'type': 'Análisis OSINT',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'company': company_name,
        'summary': result
    })
    st.session_state.current_osint = result

def display_osint_results(results):
    """Mostrar resultados del análisis OSINT mejorado"""
    
    st.markdown("### Resultados del Análisis")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_score = results.get('risk_score', 0)
        st.metric("Score de Riesgo", f"{risk_score:.2f}")
    
    with col2:
        risk_level = results.get('risk_level', 'N/A')
        color = "#dc2626" if risk_level == "CRÍTICO" else "#f97316" if risk_level == "ALTO" else "#d97706" if risk_level == "MEDIO" else "#059669"
        st.markdown(f'<div style="text-align: center;"><h3 style="color: {color};">{risk_level}</h3></div>', unsafe_allow_html=True)
    
    with col3:
        vuln_count = len(results.get('vulnerabilities', []))
        st.metric("Vulnerabilidades", vuln_count)
    
    # Vulnerabilidades detalladas
    if results.get('vulnerabilities'):
        st.markdown("### 🎯 Vulnerabilidades Identificadas")
        for vuln in results['vulnerabilities']:
            display_vulnerability_card(vuln)
    
    # Exposición de empleados
    if results.get('employee_exposure'):
        st.markdown("### 👥 Exposición de Empleados")
        for emp in results['employee_exposure']:
            display_employee_exposure(emp)
    
    # Vectores de ataque
    if results.get('attack_vectors'):
        st.markdown("### ⚔️ Vectores de Ataque")
        for vector in results['attack_vectors']:
            display_attack_vector(vector)
    
    # Hallazgos técnicos
    if results.get('technical_findings'):
        st.markdown("### 🔧 Hallazgos Técnicos")
        for finding in results['technical_findings']:
            display_technical_finding(finding)
    
    # Recomendaciones
    if results.get('recommendations'):
        st.markdown("### 💡 Recomendaciones Prioritarias")
        for rec in results['recommendations']:
            display_recommendation(rec)

def display_vulnerability_card(vuln):
    """Mostrar tarjeta de vulnerabilidad"""
    severity_color = {
        'CRÍTICA': '#dc2626', 'ALTA': '#f97316', 
        'MEDIA': '#d97706', 'BAJA': '#059669'
    }.get(vuln.get('severity', 'MEDIA'), '#6b7280')
    
    st.markdown(f"""
    <div style="border-left: 4px solid {severity_color}; padding: 1rem; margin: 0.5rem 0; background: #f8fafc; border-radius: 6px;">
        <h4 style="margin: 0 0 0.5rem 0; color: {severity_color};">{vuln.get('type', 'Vulnerabilidad')} - {vuln.get('severity', 'MEDIA')}</h4>
        <p style="margin: 0.5rem 0;"><strong>Descripción:</strong> {vuln.get('description', 'Sin descripción')}</p>
        {f'<p style="margin: 0.5rem 0;"><strong>Evidencia:</strong> {vuln.get("evidence", "No especificada")}</p>' if vuln.get('evidence') else ''}
        {f'<p style="margin: 0.5rem 0;"><strong>Impacto:</strong> {vuln.get("impact", "No especificado")}</p>' if vuln.get('impact') else ''}
    </div>
    """, unsafe_allow_html=True)

def display_employee_exposure(emp):
    """Mostrar exposición de empleado"""
    risk_color = {'ALTO': '#dc2626', 'MEDIO': '#f97316', 'BAJO': '#059669'}.get(emp.get('risk_level', 'MEDIO'), '#6b7280')
    
    st.markdown(f"""
    <div style="border-left: 4px solid {risk_color}; padding: 1rem; margin: 0.5rem 0; background: #fef2f2; border-radius: 6px;">
        <h4 style="margin: 0 0 0.5rem 0;">{emp.get('employee', 'Empleado')} - Riesgo {emp.get('risk_level', 'MEDIO')}</h4>
        <p><strong>Tipo de exposición:</strong> {emp.get('exposure_type', 'No especificado')}</p>
        <p><strong>Información sensible:</strong> {emp.get('sensitive_info', 'No especificada')}</p>
    </div>
    """, unsafe_allow_html=True)

def display_attack_vector(vector):
    """Mostrar vector de ataque"""
    probability = vector.get('probability', 0)
    color = '#dc2626' if probability > 0.7 else '#f97316' if probability > 0.4 else '#059669'
    
    st.markdown(f"""
    <div style="border-left: 4px solid {color}; padding: 1rem; margin: 0.5rem 0; background: #f8fafc; border-radius: 6px;">
        <h4 style="margin: 0 0 0.5rem 0;">{vector.get('vector', 'Vector')} - Probabilidad: {probability:.0%}</h4>
        <p><strong>Impacto:</strong> {vector.get('impact', 'Sin descripción')}</p>
        <p><strong>Método:</strong> {vector.get('method', 'No especificado')}</p>
    </div>
    """, unsafe_allow_html=True)

def display_technical_finding(finding):
    """Mostrar hallazgo técnico"""
    st.markdown(f"""
    <div style="border-left: 4px solid #3b82f6; padding: 1rem; margin: 0.5rem 0; background: #eff6ff; border-radius: 6px;">
        <h4 style="margin: 0 0 0.5rem 0;">{finding.get('finding', 'Hallazgo')}</h4>
        <p><strong>Riesgo:</strong> {finding.get('risk', 'No especificado')}</p>
        <p><strong>Recomendación:</strong> {finding.get('recommendation', 'No especificada')}</p>
    </div>
    """, unsafe_allow_html=True)

def display_recommendation(rec):
    """Mostrar recomendación"""
    priority_color = {
        'ALTA': '#dc2626', 'MEDIA': '#f97316', 'BAJA': '#059669'
    }.get(rec.get('priority', 'MEDIA'), '#6b7280')
    
    st.markdown(f"""
    <div style="border-left: 4px solid {priority_color}; padding: 1rem; margin: 0.5rem 0; background: #f0fdf4; border-radius: 6px;">
        <h4 style="margin: 0 0 0.5rem 0; color: {priority_color};">Prioridad {rec.get('priority', 'MEDIA')} - {rec.get('category', 'General')}</h4>
        <p><strong>Acción:</strong> {rec.get('action', 'Sin descripción')}</p>
        {f'<p><strong>Plazo:</strong> {rec.get("timeline", "No especificado")}</p>' if rec.get('timeline') else ''}
    </div>
    """, unsafe_allow_html=True)

def user_profiling():
    """Perfilado de usuario mejorado"""
    st.markdown("### Perfilado Psicológico de Usuario")
    
    if not ('anthropic_client' in st.session_state or st.session_state.get('demo_mode')):
        st.error("**Requiere conexión con Anthropic Claude o modo demo para perfilado avanzado**")
        return
    
    with st.form("profile_form", clear_on_submit=False):
        st.markdown("**Información del Usuario**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_name = st.text_input("Nombre del Usuario*", key="profile_name")
            department = st.selectbox("Departamento", [
                "Finanzas", "Tecnología", "Recursos Humanos", 
                "Ventas", "Marketing", "Operaciones", "Legal", "Ejecutivo"
            ], key="profile_dept")
            seniority = st.selectbox("Nivel de Responsabilidad", [
                "Junior", "Senior", "Manager", "Director", "C-Level"
            ], key="profile_seniority")
        
        with col2:
            company_size = st.selectbox("Tamaño de Empresa", [
                "1-50", "51-200", "201-1000", "1000-5000", "5000+"
            ], key="profile_company_size")
            industry = st.selectbox("Industria", [
                "Tecnología", "Finanzas", "Salud", "Educación", 
                "Retail", "Manufactura", "Consultoría", "Gobierno"
            ], key="profile_industry")
            age_range = st.selectbox("Rango de Edad", [
                "20-30", "31-40", "41-50", "51-60", "60+"
            ], key="profile_age")
        
        st.markdown("**Patrones de Comportamiento Digital**")
        
        col3, col4 = st.columns(2)
        
        with col3:
            social_activity = st.slider("Actividad en Redes Sociales", 1, 10, 5, key="profile_social")
            security_awareness = st.slider("Conciencia de Seguridad", 1, 10, 5, key="profile_security")
            tech_comfort = st.slider("Comodidad con Tecnología", 1, 10, 5, key="profile_tech")
        
        with col4:
            info_sharing = st.slider("Tendencia a Compartir Información", 1, 10, 5, key="profile_sharing")
            authority_response = st.slider("Respuesta a Autoridad", 1, 10, 5, key="profile_authority")
            stress_reaction = st.slider("Reacción bajo Presión", 1, 10, 5, key="profile_stress")
        
        work_patterns = st.multiselect("Patrones de Trabajo", [
            "Trabajo remoto frecuente", "Horarios extendidos", 
            "Acceso desde múltiples dispositivos", "Viajes de negocio",
            "Manejo de información sensible", "Contacto con clientes externos",
            "Uso de aplicaciones personales en trabajo", "Acceso fuera de horario"
        ], key="profile_patterns")
        
        personality_traits = st.multiselect("Rasgos de Personalidad", [
            "Confiado", "Cauteloso", "Sociable", "Introvertido",
            "Orientado a resultados", "Detallista", "Impulsivo", "Analítico",
            "Colaborativo", "Independiente", "Optimista", "Pesimista"
        ], key="profile_personality")
        
        additional_context = st.text_area(
            "Contexto Adicional",
            placeholder="Información adicional sobre comportamiento, incidentes previos, etc...",
            key="profile_context"
        )
        
        submitted = st.form_submit_button("🧠 Generar Perfil Psicológico", use_container_width=True)
        
        if submitted:
            if user_name and department:
                generate_psychological_profile(
                    user_name, department, seniority, company_size, industry, age_range,
                    social_activity, security_awareness, info_sharing, tech_comfort,
                    authority_response, stress_reaction, work_patterns, personality_traits,
                    additional_context
                )
            else:
                st.error("Complete los campos obligatorios (*)")
    
    # Mostrar perfiles existentes
    display_existing_profiles()
    
    # Mostrar último perfil si existe
    if 'current_profile' in st.session_state and st.session_state.current_profile:
        st.markdown("---")
        st.markdown("### 🧠 Último Perfil Generado")
        display_profile_results(st.session_state.current_profile)

def generate_psychological_profile(user_name, department, seniority, company_size, 
                                 industry, age_range, social_activity, security_awareness, 
                                 info_sharing, tech_comfort, authority_response, stress_reaction,
                                 work_patterns, personality_traits, additional_context):
    """Generar perfil psicológico mejorado"""
    
    if st.session_state.get('demo_mode'):
        with st.spinner("Generando perfil psicológico de ejemplo..."):
            time.sleep(2)
            result = generate_demo_profile(user_name, department, seniority, social_activity, 
                                         security_awareness, info_sharing, personality_traits)
            save_profile_result(result, user_name, department)
            display_profile_results(result)
        return
    
    with st.spinner("Generando perfil psicológico avanzado..."):
        
        prompt = f"""
Eres un experto en psicología organizacional y ciberseguridad. Analiza el siguiente perfil y proporciona un análisis detallado.

PERFIL A ANALIZAR:
- Nombre: {user_name}
- Departamento: {department}
- Nivel: {seniority}
- Empresa: {company_size} empleados en {industry}
- Edad: {age_range} años
- Actividad social: {social_activity}/10
- Conciencia seguridad: {security_awareness}/10
- Compartir información: {info_sharing}/10
- Comodidad tecnológica: {tech_comfort}/10
- Respuesta a autoridad: {authority_response}/10
- Reacción al estrés: {stress_reaction}/10
- Patrones de trabajo: {', '.join(work_patterns)}
- Rasgos de personalidad: {', '.join(personality_traits)}
- Contexto adicional: {additional_context}

Proporciona un análisis JSON con esta estructura EXACTA:

{{
    "psychological_profile": {{
        "personality_summary": "Resumen completo de la personalidad basado en los datos",
        "core_traits": ["Lista de rasgos principales específicos"],
        "behavioral_patterns": ["Patrones específicos basados en métricas"],
        "decision_making_style": "Estilo específico con justificación",
        "stress_responses": ["Respuestas específicas al estrés"],
        "technology_relationship": "Relación específica con la tecnología",
        "social_behavior": "Comportamiento social específico"
    }},
    "vulnerability_assessment": {{
        "overall_risk_score": 0.75,
        "risk_factors": [
            {{
                "factor": "Factor específico",
                "score": 0.8,
                "description": "Descripción detallada del factor",
                "mitigation": "Estrategia de mitigación específica"
            }}
        ],
        "psychological_vulnerabilities": [
            {{
                "type": "Tipo específico de vulnerabilidad",
                "severity": "ALTA",
                "description": "Descripción detallada",
                "triggers": ["Lista de desencadenantes específicos"],
                "exploitation_method": "Método específico de explotación"
            }}
        ]
    }},
    "attack_simulation": {{
        "most_effective_vectors": [
            {{
                "technique": "Técnica específica",
                "effectiveness_score": 0.85,
                "approach": "Enfoque detallado específico para este usuario",
                "psychological_basis": "Base psicológica específica",
                "execution_example": "Ejemplo específico de ejecución"
            }}
        ],
        "social_engineering_angles": [
            {{
                "angle": "Ángulo específico",
                "success_probability": 0.7,
                "description": "Descripción detallada del enfoque"
            }}
        ]
    }},
    "personalized_training": {{
        "priority_areas": [
            {{
                "area": "Área específica",
                "priority": "ALTA",
                "reason": "Razón específica basada en el perfil",
                "training_approach": "Enfoque específico de entrenamiento"
            }}
        ],
        "recommended_simulations": [
            {{
                "scenario": "Escenario específico",
                "frequency": "Frecuencia recomendada",
                "difficulty": "Nivel de dificultad",
                "focus": "Foco específico del entrenamiento"
            }}
        ]
    }}
}}

Basa todo el análisis en las métricas específicas proporcionadas.
"""
        
        try:
            response = st.session_state.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",  # Usar modelo que funciona
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            
            with st.expander("🔍 Debug: Respuesta de Claude", expanded=False):
                st.text(content)
            
            profile_result = safe_json_parse(content)
            
            if not profile_result:
                st.warning("⚠️ Error en parsing JSON. Generando perfil básico...")
                profile_result = generate_fallback_profile(user_name, department, seniority)
            
            save_profile_result(profile_result, user_name, department)
            st.success("✅ Perfil psicológico generado")
            display_profile_results(st.session_state.current_profile)
            
        except Exception as e:
            st.error(f"❌ Error generando perfil: {str(e)}")
            # Usar fallback inmediatamente
            fallback_result = generate_fallback_profile(user_name, department, seniority)
            save_profile_result(fallback_result, user_name, department)
            display_profile_results(st.session_state.current_profile)

def generate_demo_profile(user_name, department, seniority, social_activity, 
                         security_awareness, info_sharing, personality_traits):
    """Generar perfil demo más realista"""
    
    # Calcular risk score basado en métricas
    risk_score = 0.5 + (info_sharing * 0.04) + (social_activity * 0.03) - (security_awareness * 0.04)
    risk_score = max(0.2, min(0.9, risk_score))
    
    return {
        "psychological_profile": {
            "personality_summary": f"{user_name} es un profesional de {department} con características {', '.join(personality_traits[:3])}. Muestra un nivel {social_activity}/10 de actividad social y {security_awareness}/10 de conciencia de seguridad.",
            "core_traits": personality_traits[:4] if personality_traits else [f"Profesional de {department}", f"Nivel {seniority}"],
            "behavioral_patterns": [
                f"Tendencia {'alta' if info_sharing > 6 else 'media' if info_sharing > 3 else 'baja'} a compartir información",
                f"Respuesta {'rápida' if social_activity > 6 else 'cautelosa'} en comunicaciones digitales",
                f"Enfoque {'colaborativo' if 'Colaborativo' in personality_traits else 'independiente'} en el trabajo"
            ],
            "decision_making_style": f"Estilo {'analítico' if 'Analítico' in personality_traits else 'intuitivo'} con influencia del rol de {department}",
            "stress_responses": [
                f"Bajo presión, tiende a {'acelerar decisiones' if 'Impulsivo' in personality_traits else 'mantener cautela'}",
                f"Busca {'apoyo del equipo' if 'Colaborativo' in personality_traits else 'soluciones independientes'}"
            ],
            "technology_relationship": f"Relación {'cómoda' if info_sharing > 5 else 'cautelosa'} con la tecnología",
            "social_behavior": f"Comportamiento {'extrovertido' if social_activity > 6 else 'reservado'} en entornos digitales"
        },
        "vulnerability_assessment": {
            "overall_risk_score": round(risk_score, 2),
            "risk_factors": [
                {
                    "factor": "Compartir información",
                    "score": round(info_sharing / 10, 2),
                    "description": f"Tendencia {info_sharing}/10 a compartir información puede facilitar ingeniería social",
                    "mitigation": "Entrenamiento en verificación de solicitudes"
                },
                {
                    "factor": "Conciencia de seguridad",
                    "score": round(1 - (security_awareness / 10), 2),
                    "description": f"Nivel {security_awareness}/10 de conciencia indica vulnerabilidad",
                    "mitigation": "Programas de concientización específicos"
                }
            ],
            "psychological_vulnerabilities": [
                {
                    "type": "Autoridad percibida",
                    "severity": "ALTA" if department in ["Finanzas", "Legal"] else "MEDIA",
                    "description": f"Como {seniority} en {department}, susceptible a figuras de autoridad",
                    "triggers": [f"Solicitudes de superiores de {department}", "Auditorías", "Procesos de compliance"],
                    "exploitation_method": "Emails que imitan comunicaciones oficiales"
                }
            ]
        },
        "attack_simulation": {
            "most_effective_vectors": [
                {
                    "technique": f"Phishing específico de {department}",
                    "effectiveness_score": round(0.6 + (info_sharing * 0.03), 2),
                    "approach": f"Emails que imitan procesos típicos de {department} con urgencia artificial",
                    "psychological_basis": f"Familiaridad con workflows de {department}",
                    "execution_example": f"Email sobre proceso urgente de {department} requiriendo verificación"
                }
            ],
            "social_engineering_angles": [
                {
                    "angle": "Autoridad organizacional",
                    "success_probability": round(0.7 if department in ["Finanzas", "Legal"] else 0.5, 2),
                    "description": f"Aprovechamiento de estructura jerárquica en {department}"
                }
            ]
        },
        "personalized_training": {
            "priority_areas": [
                {
                    "area": "Verificación de autoridad",
                    "priority": "ALTA",
                    "reason": f"Alta susceptibilidad a figuras de autoridad en {department}",
                    "training_approach": "Simulacros con verificación de identidad"
                }
            ],
            "recommended_simulations": [
                {
                    "scenario": f"Phishing dirigido a {department}",
                    "frequency": "Mensual",
                    "difficulty": "Media-Alta",
                    "focus": "Verificación de solicitudes urgentes"
                }
            ]
        }
    }

def generate_fallback_profile(user_name, department, seniority):
    """Generar perfil de fallback"""
    return {
        "psychological_profile": {
            "personality_summary": f"Análisis manual requerido para {user_name}",
            "core_traits": [f"Profesional de {department}", f"Nivel {seniority}"],
            "behavioral_patterns": ["Por determinar"],
            "decision_making_style": "Análisis requerido",
            "stress_responses": ["Por evaluar"],
            "technology_relationship": "Por determinar",
            "social_behavior": "Análisis pendiente"
        },
        "vulnerability_assessment": {
            "overall_risk_score": 0.5,
            "risk_factors": [],
            "psychological_vulnerabilities": []
        },
        "attack_simulation": {
            "most_effective_vectors": [],
            "social_engineering_angles": []
        },
        "personalized_training": {
            "priority_areas": [],
            "recommended_simulations": []
        }
    }

def save_profile_result(result, user_name, department):
    """Guardar resultado del perfil"""
    profile_data = {
        'user_name': user_name,
        'department': department,
        'analysis': result,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Inicializar lista si no existe
    if 'user_profiles' not in st.session_state:
        st.session_state.user_profiles = []
    
    st.session_state.user_profiles.append(profile_data)
    st.session_state.current_profile = profile_data

def display_existing_profiles():
    """Mostrar perfiles existentes"""
    if st.session_state.get('user_profiles'):
        st.markdown("---")
        st.markdown("### 👥 Perfiles Existentes")
        
        for i, profile in enumerate(st.session_state.user_profiles[-3:]):
            with st.expander(f"👤 {profile['user_name']} ({profile['department']}) - {profile['timestamp']}", expanded=False):
                display_profile_summary(profile)

def display_profile_summary(profile):
    """Mostrar resumen del perfil"""
    analysis = profile['analysis']
    
    if 'vulnerability_assessment' in analysis:
        risk_score = analysis['vulnerability_assessment'].get('overall_risk_score', 0)
        st.metric("Risk Score", f"{risk_score:.2f}")
    
    if 'psychological_profile' in analysis:
        profile_data = analysis['psychological_profile']
        st.markdown(f"**Resumen:** {profile_data.get('personality_summary', 'No disponible')}")

def display_profile_results(profile_data):
    """Mostrar resultados del perfilado mejorado"""
    
    # Verificar estructura de datos
    if not profile_data or not isinstance(profile_data, dict):
        st.error("Error: Estructura de perfil inválida")
        return
    
    analysis = profile_data.get('analysis', {})
    user_name = profile_data.get('user_name', 'Usuario Desconocido')
    department = profile_data.get('department', 'Departamento')
    timestamp = profile_data.get('timestamp', 'Fecha desconocida')
    
    st.markdown("### Resultados del Perfilado")
    
    # Información básica
    st.markdown(f"**Usuario:** {user_name} | **Departamento:** {department}")
    st.markdown(f"**Análisis realizado:** {timestamp}")
    
    # Score de riesgo
    risk_score = analysis.get('vulnerability_assessment', {}).get('overall_risk_score', 0)
    risk_level = "CRÍTICO" if risk_score >= 0.8 else "ALTO" if risk_score >= 0.6 else "MEDIO" if risk_score >= 0.4 else "BAJO"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Score de Riesgo", f"{risk_score:.2f}")
    
    with col2:
        color = "#dc2626" if risk_level == "CRÍTICO" else "#f97316" if risk_level == "ALTO" else "#d97706" if risk_level == "MEDIO" else "#059669"
        st.markdown(f'<div style="text-align: center;"><h3 style="color: {color};">{risk_level}</h3></div>', unsafe_allow_html=True)
    
    with col3:
        vuln_count = len(analysis.get('vulnerability_assessment', {}).get('psychological_vulnerabilities', []))
        st.metric("Vulnerabilidades", vuln_count)
    
    # Perfil psicológico
    if 'psychological_profile' in analysis:
        display_psychological_profile(analysis['psychological_profile'])
    
    # Evaluación de vulnerabilidades
    if 'vulnerability_assessment' in analysis:
        display_vulnerability_assessment(analysis['vulnerability_assessment'])
    
    # Simulación de ataques
    if 'attack_simulation' in analysis:
        display_attack_simulation(analysis['attack_simulation'])
    
    # Entrenamiento personalizado
    if 'personalized_training' in analysis:
        display_personalized_training(analysis['personalized_training'])

def display_psychological_profile(profile):
    """Mostrar perfil psicológico"""
    st.markdown("### 🧠 Perfil Psicológico")
    
    st.markdown(f"**Resumen de Personalidad:**")
    st.write(profile.get('personality_summary', 'No disponible'))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Rasgos Principales:**")
        for trait in profile.get('core_traits', []):
            st.markdown(f"• {trait}")
        
        st.markdown("**Estilo de Decisión:**")
        st.write(profile.get('decision_making_style', 'No especificado'))
    
    with col2:
        st.markdown("**Patrones de Comportamiento:**")
        for pattern in profile.get('behavioral_patterns', []):
            st.markdown(f"• {pattern}")
        
        st.markdown("**Respuestas al Estrés:**")
        for response in profile.get('stress_responses', []):
            st.markdown(f"• {response}")

def display_vulnerability_assessment(assessment):
    """Mostrar evaluación de vulnerabilidades"""
    st.markdown("### 🎯 Evaluación de Vulnerabilidades")
    
    # Factores de riesgo
    if assessment.get('risk_factors'):
        st.markdown("**Factores de Riesgo:**")
        for factor in assessment['risk_factors']:
            score = factor.get('score', 0)
            color = '#dc2626' if score > 0.7 else '#f97316' if score > 0.4 else '#059669'
            
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; padding: 1rem; margin: 0.5rem 0; background: #f8fafc; border-radius: 6px;">
                <h4 style="margin: 0 0 0.5rem 0;">{factor.get('factor', 'Factor')} - Score: {score:.2f}</h4>
                <p><strong>Descripción:</strong> {factor.get('description', 'No disponible')}</p>
                <p><strong>Mitigación:</strong> {factor.get('mitigation', 'No especificada')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Vulnerabilidades psicológicas
    if assessment.get('psychological_vulnerabilities'):
        st.markdown("**Vulnerabilidades Psicológicas:**")
        for vuln in assessment['psychological_vulnerabilities']:
            severity_color = {
                'CRÍTICA': '#dc2626', 'ALTA': '#f97316', 
                'MEDIA': '#d97706', 'BAJA': '#059669'
            }.get(vuln.get('severity', 'MEDIA'), '#6b7280')
            
            st.markdown(f"""
            <div style="border-left: 4px solid {severity_color}; padding: 1rem; margin: 0.5rem 0; background: #fef2f2; border-radius: 6px;">
                <h4 style="margin: 0 0 0.5rem 0; color: {severity_color};">{vuln.get('type', 'Vulnerabilidad')} - {vuln.get('severity', 'MEDIA')}</h4>
                <p><strong>Descripción:</strong> {vuln.get('description', 'No disponible')}</p>
                <p><strong>Desencadenantes:</strong> {', '.join(vuln.get('triggers', []))}</p>
                <p><strong>Método de explotación:</strong> {vuln.get('exploitation_method', 'No especificado')}</p>
            </div>
            """, unsafe_allow_html=True)

def display_attack_simulation(simulation):
    """Mostrar simulación de ataques"""
    st.markdown("### ⚔️ Simulación de Ataques")
    
    if simulation.get('most_effective_vectors'):
        st.markdown("**Vectores Más Efectivos:**")
        for vector in simulation['most_effective_vectors']:
            effectiveness = vector.get('effectiveness_score', 0)
            color = '#dc2626' if effectiveness > 0.7 else '#f97316' if effectiveness > 0.4 else '#059669'
            
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; padding: 1rem; margin: 0.5rem 0; background: #f8fafc; border-radius: 6px;">
                <h4 style="margin: 0 0 0.5rem 0;">{vector.get('technique', 'Técnica')} - Efectividad: {effectiveness:.0%}</h4>
                <p><strong>Enfoque:</strong> {vector.get('approach', 'No especificado')}</p>
                <p><strong>Base psicológica:</strong> {vector.get('psychological_basis', 'No especificada')}</p>
                <p><strong>Ejemplo de ejecución:</strong> {vector.get('execution_example', 'No disponible')}</p>
            </div>
            """, unsafe_allow_html=True)

def display_personalized_training(training):
    """Mostrar entrenamiento personalizado"""
    st.markdown("### 🎓 Entrenamiento Personalizado")
    
    if training.get('priority_areas'):
        st.markdown("**Áreas Prioritarias:**")
        for area in training['priority_areas']:
            priority_color = {
                'ALTA': '#dc2626', 'MEDIA': '#f97316', 'BAJA': '#059669'
            }.get(area.get('priority', 'MEDIA'), '#6b7280')
            
            st.markdown(f"""
            <div style="border-left: 4px solid {priority_color}; padding: 1rem; margin: 0.5rem 0; background: #f0fdf4; border-radius: 6px;">
                <h4 style="margin: 0 0 0.5rem 0; color: {priority_color};">Prioridad {area.get('priority', 'MEDIA')} - {area.get('area', 'Área')}</h4>
                <p><strong>Razón:</strong> {area.get('reason', 'No especificada')}</p>
                <p><strong>Enfoque de entrenamiento:</strong> {area.get('training_approach', 'No especificado')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    if training.get('recommended_simulations'):
        st.markdown("**Simulaciones Recomendadas:**")
        for sim in training['recommended_simulations']:
            st.markdown(f"""
            <div style="border-left: 4px solid #3b82f6; padding: 1rem; margin: 0.5rem 0; background: #eff6ff; border-radius: 6px;">
                <h4 style="margin: 0 0 0.5rem 0;">{sim.get('scenario', 'Escenario')}</h4>
                <p><strong>Frecuencia:</strong> {sim.get('frequency', 'No especificada')} | <strong>Dificultad:</strong> {sim.get('difficulty', 'No especificada')}</p>
                <p><strong>Foco:</strong> {sim.get('focus', 'No especificado')}</p>
            </div>
            """, unsafe_allow_html=True)

def content_generation():
    """Generación de contenido adaptativo mejorada"""
    st.markdown("### Generación de Contenido Adaptativo")
    
    if not ('anthropic_client' in st.session_state or st.session_state.get('demo_mode')):
        st.error("**Requiere conexión con Anthropic Claude o modo demo para generación de contenido**")
        return
    
    # Verificar si hay perfiles disponibles
    if not st.session_state.get('user_profiles'):
        st.warning("**Primero debe crear un perfil de usuario en la sección 'Perfilado de Usuario'**")
        return
    
    # Seleccionar perfil objetivo
    profile_options = [f"{p['user_name']} ({p['department']})" for p in st.session_state.user_profiles]
    selected_profile_idx = st.selectbox("Seleccionar Usuario Objetivo", range(len(profile_options)), 
                                       format_func=lambda x: profile_options[x])
    
    target_profile = st.session_state.user_profiles[selected_profile_idx]
    
    with st.form("content_form", clear_on_submit=False):
        st.markdown("**Configuración del Contenido**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            content_type = st.selectbox("Tipo de Contenido", [
                "Email de phishing", "SMS de urgencia", 
                "Notificación de sistema", "Llamada telefónica",
                "Mensaje de WhatsApp", "Solicitud de documentos"
            ], key="content_type")
            
            scenario = st.selectbox("Escenario", [
                "Auditoría fiscal", "Actualización de seguridad",
                "Verificación de cuenta", "Proceso de compliance",
                "Renovación de certificados", "Actualización de políticas",
                "Problema técnico urgente", "Solicitud de directivo"
            ], key="content_scenario")
        
        with col2:
            urgency = st.selectbox("Nivel de Urgencia", [
                "Baja", "Media", "Alta", "Crítica"
            ], key="content_urgency")
            
            sender_type = st.selectbox("Tipo de Remitente", [
                "Supervisor directo", "IT/Seguridad", "RRHH",
                "Finanzas", "Auditoría externa", "Proveedor",
                "Cliente", "Gobierno/Regulador"
            ], key="content_sender")
        
        company_context = st.text_input("Empresa del Usuario", 
                                       value="Empresa Objetivo",
                                       key="content_company")
        
        personalization_level = st.slider("Nivel de Personalización", 1, 10, 8, 
                                         help="1: Genérico, 10: Altamente personalizado",
                                         key="content_personalization")
        
        additional_context = st.text_area("Contexto Adicional", 
                                         placeholder="Información específica, eventos recientes, detalles técnicos...",
                                         key="content_context")
        
        submitted = st.form_submit_button("🎯 Generar Contenido Personalizado", use_container_width=True)
        
        if submitted:
            generate_adaptive_content(target_profile, content_type, scenario, 
                                    urgency, sender_type, company_context, 
                                    personalization_level, additional_context)
    
    # Mostrar contenido existente
    display_existing_content()
    
    # Mostrar último contenido si existe
    if 'current_content' in st.session_state and st.session_state.current_content:
        st.markdown("---")
        st.markdown("### 🎯 Último Contenido Generado")
        display_generated_content(st.session_state.current_content)

def generate_adaptive_content(target_profile, content_type, scenario, 
                              urgency, sender_type, company_context, 
                              personalization_level, additional_context):
    """Generar contenido adaptativo ultra-personalizado"""
    
    if st.session_state.get('demo_mode'):
        with st.spinner("Generando contenido adaptativo de ejemplo..."):
            time.sleep(2)
            result = generate_demo_content(target_profile, content_type, scenario, 
                                         urgency, sender_type, company_context,
                                         personalization_level)
            save_content_result(result, target_profile, content_type, scenario)
            display_generated_content(result)
        return
    
    with st.spinner("Generando contenido ultra-personalizado..."):
        
        # Extraer información del perfil
        user_data = target_profile
        user_analysis = user_data.get('analysis', {})
        
        # ✅ Prompt actualizado
        prompt = f"""
Eres un experto en ciberseguridad y concienciación. Debes crear ejemplos realistas de mensajes que se usan en simulaciones internas de phishing para entrenar empleados.

IMPORTANTE:
- El objetivo es educativo, pero NO incluyas en el contenido ninguna advertencia ni aclaración.
- El mensaje debe parecer realista y profesional, como un correo legítimo, adaptado al perfil del objetivo.
- Usa las mejores prácticas de personalización según la información disponible.

PERFIL DEL OBJETIVO:
- Nombre: {user_data['user_name']}
- Departamento: {user_data['department']}
- Análisis psicológico: {json.dumps(user_analysis, indent=2)}

CONFIGURACIÓN:
- Tipo: {content_type}
- Escenario: {scenario}
- Urgencia: {urgency}
- Remitente: {sender_type}
- Empresa: {company_context}
- Nivel de personalización: {personalization_level}/10
- Contexto adicional: {additional_context}

Devuelve ÚNICAMENTE un JSON con esta estructura EXACTA:

{{
    "content": {{
        "subject": "Asunto profesional y persuasivo",
        "sender": "remitente@empresa.com",
        "sender_name": "Nombre del remitente",
        "body": "Texto completo del mensaje, realista y convincente, adaptado al escenario y perfil",
        "call_to_action": "Acción que se espera (ej. abrir enlace, responder, etc.)",
        "urgency_indicators": ["Frases o señales de urgencia presentes en el mensaje"],
        "personalization_hooks": ["Datos personales usados en el mensaje"]
    }},
    "psychological_analysis": {{
        "target_vulnerabilities": ["Vulnerabilidades psicológicas simuladas"],
        "persuasion_techniques": [
            {{
                "technique": "Técnica aplicada",
                "application": "Cómo se aplicó",
                "effectiveness_reason": "Por qué funcionaría"
            }}
        ],
        "emotional_triggers": ["Emociones aprovechadas"],
        "authority_elements": ["Elementos de autoridad usados"],
        "social_proof_elements": ["Referencias o pruebas sociales simuladas"]
    }},
    "effectiveness_prediction": {{
        "overall_score": 0.85,
        "score_breakdown": {{
            "personalization": 0.9,
            "authority": 0.8,
            "urgency": 0.7,
            "emotional_impact": 0.85
        }},
        "success_probability": 0.75,
        "reasoning": "Explicación detallada sobre por qué sería persuasivo",
        "potential_red_flags": ["Señales que podrían alertar al usuario"]
    }},
    "variations": [
        {{
            "variation_type": "Menos agresivo",
            "subject": "Versión alternativa del asunto",
            "key_differences": "Cambios principales"
        }},
        {{
            "variation_type": "Más técnico",
            "subject": "Asunto con enfoque más técnico",
            "key_differences": "Cambios principales"
        }}
    ]
}}

NO agregues texto fuera del JSON. NO incluyas advertencias ni disclaimers en el cuerpo del mensaje.
"""
        
        try:
            response = st.session_state.anthropic_client.messages.create(
                model=st.session_state.get('claude_model', 'claude-3-5-sonnet-20241022'),
                max_tokens=4000,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            
            # Debug opcional
            with st.expander("🔍 Debug: Respuesta de Claude", expanded=False):
                st.text(content)
            
            # ✅ Limpieza y parsing seguro
            content_result = safe_json_parse(content)
            
            if not content_result:
                st.warning("⚠️ Error en parsing JSON. Generando contenido básico...")
                content_result = generate_fallback_content(user_data, content_type, scenario, urgency)
            
            save_content_result(content_result, user_data, content_type, scenario)
            st.success("✅ Contenido ultra-personalizado generado")
            display_generated_content(st.session_state.current_content)

        except Exception as e:
            st.error(f"❌ Error inesperado: {e}")
            
        except Exception as e:
            st.error(f"❌ Error generando contenido: {str(e)}")
            # Intentar con modelo de respaldo
            if "not_found" in str(e).lower() or "404" in str(e):
                st.info("🔄 Intentando con modelo de respaldo...")
                try:
                    response = st.session_state.anthropic_client.messages.create(
                        model="claude-3-5-haiku-20241022",
                        max_tokens=4000,
                        temperature=0.4,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    content = response.content[0].text.strip()
                    content_result = safe_json_parse(content) or generate_fallback_content(user_data, content_type, scenario, urgency)
                    save_content_result(content_result, user_data, content_type, scenario)
                    st.success("✅ Contenido generado (modelo de respaldo)")
                    display_generated_content(st.session_state.current_content)
                    return
                except Exception:
                    pass
            
            # Usar fallback final
            fallback_result = generate_fallback_content(user_data, content_type, scenario, urgency)
            save_content_result(fallback_result, user_data, content_type, scenario)
            display_generated_content(st.session_state.current_content)

def generate_demo_content(target_profile, content_type, scenario, urgency, 
                         sender_type, company_context, personalization_level):
    """Generar contenido demo ultra-personalizado"""
    
    user_data = target_profile
    user_name = user_data['user_name']
    department = user_data['department']
    
    # Analizar perfil para personalización
    analysis = user_data.get('analysis', {})
    vulnerabilities = analysis.get('vulnerability_assessment', {}).get('psychological_vulnerabilities', [])
    
    # Construir contenido basado en vulnerabilities
    urgency_phrases = {
        "Crítica": "URGENTE - ACCIÓN INMEDIATA REQUERIDA",
        "Alta": "IMPORTANTE - Respuesta necesaria hoy",
        "Media": "Solicitud importante",
        "Baja": "Información requerida"
    }
    
    # Personalizar remitente según el tipo
    sender_domains = {
        "Supervisor directo": f"{user_name.split()[0].lower()}supervisor@{company_context.lower().replace(' ', '')}.com",
        "IT/Seguridad": f"seguridad@{company_context.lower().replace(' ', '')}.com",
        "RRHH": f"rrhh@{company_context.lower().replace(' ', '')}.com",
        "Finanzas": f"finanzas@{company_context.lower().replace(' ', '')}.com",
        "Auditoría externa": f"auditoria@consultoriaexterna.com",
        "Proveedor": f"soporte@proveedor{department.lower()}.com"
    }
    
    # Crear contenido ultra-personalizado
    personalized_body = f"""Estimado/a {user_name},

Como {user_data.get('seniority', 'profesional')} de {department} en {company_context}, necesitamos su atención inmediata para {scenario.lower()}.

Hemos identificado una situación que requiere su intervención específica debido a su rol en {department}."""
    
    # Añadir elementos basados en vulnerabilidades
    if vulnerabilities:
        main_vuln = vulnerabilities[0]
        if "autoridad" in main_vuln.get('type', '').lower():
            personalized_body += f"\n\nEsta solicitud viene directamente de la dirección y es crítica para el cumplimiento de {department}."
    
    personalized_body += f"""

Detalles específicos:
- Departamento afectado: {department}
- Nivel de prioridad: {urgency}
- Tiempo límite: {"2 horas" if urgency == "Crítica" else "Fin del día" if urgency == "Alta" else "Esta semana"}

Por favor, responda inmediatamente con:
1. Confirmación de recepción
2. Información solicitada para {scenario.lower()}
3. Autorización para proceder

Saludos urgentes,
{sender_type}
{company_context}"""
    
    return {
        "content": {
            "subject": f"{urgency_phrases[urgency]} - {scenario} - {department}",
            "sender": sender_domains.get(sender_type, f"admin@{company_context.lower().replace(' ', '')}.com"),
            "sender_name": f"{sender_type} - {company_context}",
            "body": personalized_body,
            "call_to_action": f"Responder con información de {scenario.lower()} antes de {"2 horas" if urgency == "Crítica" else "fin del día"}",
            "urgency_indicators": [
                f"Nivel {urgency} de prioridad",
                f"Específico para {department}",
                f"Solicitud de {sender_type}"
            ],
            "personalization_hooks": [
                f"Nombre específico: {user_name}",
                f"Departamento específico: {department}",
                f"Rol específico: {user_data.get('seniority', 'profesional')}",
                f"Empresa específica: {company_context}"
            ]
        },
        "psychological_analysis": {
            "target_vulnerabilities": [vuln.get('type', 'Vulnerabilidad general') for vuln in vulnerabilities[:3]],
            "persuasion_techniques": [
                {
                    "technique": "Autoridad",
                    "application": f"Remitente presenta como {sender_type} oficial",
                    "effectiveness_reason": f"Personal de {department} responde a autoridad organizacional"
                },
                {
                    "technique": "Urgencia",
                    "application": f"Crear presión temporal {urgency.lower()}",
                    "effectiveness_reason": f"Nivel {urgency} reduce tiempo de análisis crítico"
                },
                {
                    "technique": "Personalización específica",
                    "application": f"Dirigido específicamente a {user_name} de {department}",
                    "effectiveness_reason": "Aumenta percepción de legitimidad"
                }
            ],
            "emotional_triggers": [
                f"Responsabilidad profesional en {department}",
                f"Presión temporal {urgency.lower()}",
                "Autoridad organizacional"
            ],
            "authority_elements": [
                f"Remitente {sender_type}",
                f"Proceso oficial de {scenario}",
                f"Referencia a dirección de {company_context}"
            ],
            "social_proof_elements": [
                f"Proceso estándar en {department}",
                f"Política de {company_context}",
                "Cumplimiento regulatorio"
            ]
        },
        "effectiveness_prediction": {
            "overall_score": min(0.9, 0.6 + (personalization_level * 0.03)),
            "score_breakdown": {
                "personalization": min(0.95, 0.7 + (personalization_level * 0.025)),
                "authority": 0.85 if department in ["Finanzas", "Legal"] else 0.75,
                "urgency": 0.9 if urgency in ["Crítica", "Alta"] else 0.6,
                "emotional_impact": 0.8
            },
            "success_probability": min(0.85, 0.5 + (personalization_level * 0.035)),
            "reasoning": f"Contenido altamente personalizado para {user_name} de {department}, explotando vulnerabilidades específicas identificadas en el perfil psicológico",
            "potential_red_flags": [
                "Urgencia artificial puede generar sospecha",
                "Remitente externo puede ser verificado",
                f"Personal de {department} puede tener protocolos de verificación"
            ]
        },
        "variations": [
            {
                "variation_type": "Menos agresivo",
                "subject": f"Solicitud de {scenario} - {department}",
                "key_differences": "Elimina urgencia artificial, tono más profesional"
            },
            {
                "variation_type": "Más técnico",
                "subject": f"Protocolo {scenario} - Validación {department}",
                "key_differences": "Lenguaje más técnico, referencias a procedimientos específicos"
            }
        ]
    }

def create_account_verification_email(user_name, department, company_context, urgency):
    """Crear email de verificación de cuenta ultra-realista"""
    return {
        "subject": f"Verificación de cuenta requerida - {user_name} ({department})",
        "sender": f"noreply@{company_context.lower().replace(' ', '')}.com",
        "sender_name": "Sistema de Seguridad Corporativa",
        "body": f"""Estimado/a {user_name},

Por políticas de seguridad actualizadas de {company_context}, es necesario verificar periódicamente las cuentas corporativas.

Su cuenta corporativa requiere re-verificación debido a:
• Implementación de nuevas políticas de acceso
• Migración al nuevo sistema de autenticación
• Cumplimiento con certificación ISO 27001

DATOS DE LA CUENTA:
• Usuario: {user_name.lower().replace(' ', '.')}@{company_context.lower().replace(' ', '')}.com
• Departamento: {department}
• Último acceso: {datetime.now().strftime('%d/%m/%Y %H:%M')}
• Nivel de acceso: Usuario departamental

Para mantener el acceso a sus sistemas, complete la verificación en:
[ENLACE DE VERIFICACIÓN]

El proceso toma aproximadamente 3 minutos e incluye:
1. Confirmación de datos personales
2. Actualización de información de contacto
3. Verificación de accesos departamentales
4. Confirmación de políticas de seguridad

IMPORTANTE: Las cuentas no verificadas serán deshabilitadas automáticamente el {(datetime.now() + timedelta(days=3)).strftime('%d/%m/%Y')}.

Este es un mensaje automático del Sistema de Gestión de Identidades.
No responda a este correo.

Soporte Técnico: soporte@{company_context.lower().replace(' ', '')}.com
Mesa de ayuda: ext. 4357""",
        "call_to_action": "Verificar cuenta en el enlace proporcionado",
        "urgency_indicators": [
            "Deshabilitación automática en 3 días",
            "Último acceso mostrado",
            "Proceso de migración de sistema"
        ],
        "personalization_hooks": [
            f"Email corporativo: {user_name.lower().replace(' ', '.')}@{company_context.lower().replace(' ', '')}.com",
            f"Nivel de acceso específico",
            f"Departamento mencionado: {department}"
        ],
        "realistic_details": [
            "Sistema de gestión de identidades",
            "Certificación ISO mencionada",
            "Mesa de ayuda con extensión",
            "Políticas de seguridad corporativa"
        ]
    }

def create_tech_emergency_email(user_name, department, company_context, urgency):
    """Crear email de emergencia técnica ultra-realista"""
    return {
        "subject": f"EMERGENCIA: Falla crítica en sistemas de {department} - Acción inmediata",
        "sender": f"ops@{company_context.lower().replace(' ', '')}.com",
        "sender_name": "Centro de Operaciones NOC",
        "body": f"""ALERTA CRÍTICA - {user_name}

El Centro de Operaciones de Red ha detectado una falla crítica que afecta directamente al departamento de {department}.

DETALLES DEL INCIDENTE:
• Ticket: INC-2025-{department[:3].upper()}-{datetime.now().strftime('%m%d')}-001
• Severidad: CRÍTICA (P1)
• Inicio: {datetime.now().strftime('%d/%m/%Y %H:%M')}
• Sistemas afectados: Servidores de aplicaciones {department}
• Impacto: Pérdida total de conectividad para {department}

SÍNTOMAS REPORTADOS:
✗ Base de datos de {department} inaccesible
✗ Aplicaciones críticas fuera de línea
✗ Pérdida de sincronización de archivos compartidos
✗ Error en respaldo automático nocturno

ROOT CAUSE ANALYSIS:
Falla en controlador de dominio DCPROD-{department[:3].upper()}-02
El servicio de autenticación está presentando errores intermitentes.

ACCIÓN INMEDIATA REQUERIDA:
Para acelerar la resolución y evitar pérdida de datos, necesitamos que verifique inmediatamente:

1. Su acceso actual a sistemas críticos
2. Estado de documentos importantes en curso
3. Integridad de archivos locales vs servidor

PROCESO DE RECUPERACIÓN:
Acceda al portal de emergencia NOC: [ENLACE MALICIOSO]
Use sus credenciales corporativas para:
• Reportar estado de sus datos locales
• Confirmar integridad de archivos críticos
• Autorizar procedimiento de recuperación

TIEMPO ESTIMADO DE RESOLUCIÓN:
Sin su colaboración: 8-12 horas
Con verificación inmediata: 2-3 horas

El tiempo es CRÍTICO. Cada minuto de retraso extiende la ventana de recuperación.

Centro de Operaciones NOC
{company_context}
Escalación 24/7: ext. 911
noc.emergency@{company_context.lower().replace(' ', '')}.com""",
        "call_to_action": "Verificar estado de datos en portal NOC inmediatamente",
        "urgency_indicators": [
            "Falla crítica P1",
            "Pérdida total de conectividad",
            "Tiempo crítico para recuperación",
            "Escalación 24/7 mencionada"
        ],
        "personalization_hooks": [
            f"Sistemas específicos de {department}",
            f"Base de datos de {department}",
            f"Controlador DCPROD-{department[:3].upper()}-02",
            "Ticket con código departamental"
        ],
        "realistic_details": [
            "Terminología NOC real",
            "Ticket con formato corporativo",
            "Severidad P1 (crítica)",
            "Root cause analysis técnico",
            "Centro de operaciones 24/7"
        ]
    }

def create_executive_request_email(user_name, department, company_context, urgency):
    """Crear email de solicitud ejecutiva ultra-realista"""
    return {
        "subject": f"Solicitud urgente de información - {department}",
        "sender": f"direccion@{company_context.lower().replace(' ', '')}.com",
        "sender_name": "Lic. Roberto Hernández - Director General",
        "body": f"""Estimado/a {user_name},

Espero te encuentres bien. Te contacto directamente debido a una situación que requiere atención inmediata.

Hemos recibido una solicitud formal de información por parte de la Comisión Nacional Bancaria y de Valores (CNBV) relacionada con las operaciones del departamento de {department}.

ANTECEDENTES:
El día de ayer recibimos el oficio CNBV-2025-{department[:3].upper()}-847 solicitando información específica sobre:
• Procedimientos operativos del área de {department}
• Controles internos implementados
• Documentación de procesos críticos
• Registro de transacciones del último trimestre

URGENCIA:
Tenemos únicamente 48 horas para entregar la información completa. El incumplimiento podría resultar en:
• Multa de hasta $50,000,000 pesos
• Suspensión temporal de operaciones
• Afectación a nuestra calificación regulatoria

INFORMACIÓN REQUERIDA DE {department.upper()}:
Necesito que prepares inmediatamente:
1. Manual de procedimientos actualizado
2. Matriz de autorización de {department}
3. Reportes de actividad del Q4 2024
4. Documentación de controles internos

PROCESO:
Para agilizar la entrega, he habilitado un portal seguro donde puedes cargar la documentación:
[ENLACE EJECUTIVO]

Por favor confirma recepción de este mensaje y proporciona un tiempo estimado para tener lista la información.

Comprendo la urgencia que esto representa, pero es fundamental para mantener nuestro estatus regulatorio.

Quedo atento a tu pronta respuesta.

Saludos cordiales,

Lic. Roberto Hernández Maldonado
Director General
{company_context}
Teléfono directo: 55-1234-5678
rhernandez@{company_context.lower().replace(' ', '')}.com

"Construyendo el futuro juntos"

CONFIDENCIAL: Este mensaje contiene información privilegiada y confidencial.""",
        "call_to_action": "Preparar documentación del departamento y subirla al portal en 48 horas",
        "urgency_indicators": [
            "Solicitud formal CNBV",
            "48 horas para entregar",
            "Multa de $50,000,000 pesos",
            "Suspensión de operaciones"
        ],
        "personalization_hooks": [
            f"Solicitud específica sobre {department}",
            f"Procedimientos operativos de {department}",
            f"Matriz de autorización de {department}",
            f"Oficio CNBV-2025-{department[:3].upper()}-847"
        ],
        "realistic_details": [
            "Oficio con numeración oficial",
            "Multa específica y realista",
            "Terminología regulatoria correcta",
            "Teléfono directo ejecutivo",
            "Marca de confidencialidad"
        ]
    }

def generate_fallback_content(user_data, content_type, scenario, urgency):
    """Mantener función de fallback original mejorada"""
    
    user_name = user_data.get('user_name', 'Usuario')
    department = user_data.get('department', 'Departamento')
    
    return {
        "content": {
            "subject": f"{urgency.upper()}: {scenario} - Acción Requerida para {department}",
            "sender": "admin@empresa.com",
            "sender_name": "Administración Corporativa",
            "body": f"""Estimado/a {user_name},

Como responsable del área de {department}, necesitamos su atención inmediata para el proceso de {scenario.lower()}.

Este procedimiento es obligatorio para todo el personal de {department} y debe completarse con carácter {urgency.lower()}.

Pasos a seguir:
1. Acceder al sistema corporativo
2. Completar el proceso de {scenario.lower()}
3. Confirmar finalización

El incumplimiento puede afectar las operaciones normales de {department}.

Saludos cordiales,
Equipo de Administración Corporativa

NOTA: Este es un proceso automatizado del sistema.""",
            "call_to_action": f"Completar {scenario.lower()} inmediatamente",
            "urgency_indicators": [f"Proceso {urgency.lower()}", f"Obligatorio para {department}"],
            "personalization_hooks": [f"Responsable de {department}", f"Personal de {department}"]
        },
        "psychological_analysis": {
            "target_vulnerabilities": ["Autoridad corporativa", "Responsabilidad profesional"],
            "persuasion_techniques": [
                {
                    "technique": "Autoridad administrativa", 
                    "application": "Remitente corporativo oficial", 
                    "effectiveness_reason": f"Personal de {department} responde a administración"
                }
            ],
            "emotional_triggers": ["Responsabilidad profesional", "Impacto en operaciones"],
            "authority_elements": ["Administración Corporativa", "Proceso obligatorio"],
            "social_proof_elements": [f"Procedimiento para todo {department}"]
        },
        "effectiveness_prediction": {
            "overall_score": 0.65,
            "score_breakdown": {
                "personalization": 0.7, 
                "authority": 0.8, 
                "urgency": 0.6, 
                "emotional_impact": 0.5
            },
            "success_probability": 0.55,
            "reasoning": f"Contenido mejorado para {user_name} de {department} con autoridad corporativa",
            "potential_red_flags": ["Proceso automatizado mencionado", "Falta de detalles específicos"]
        }
    }

def create_tax_audit_email(user_name, department, company_context, urgency):
    """Crear email de auditoría fiscal ultra-realista"""
    return {
        "subject": f"URGENTE: Requerimiento Fiscal - {company_context} - {user_name}",
        "sender": "notificaciones@sat.gob.mx",
        "sender_name": "Lic. María Elena Rodríguez - SAT",
        "body": f"""Estimado/a {user_name},

Por medio del presente, el Servicio de Administración Tributaria le notifica que se ha iniciado un procedimiento de revisión fiscal para {company_context}, identificada con RFC [RFC-EMPRESA].

Como responsable del área de {department}, usted ha sido designado como el contacto principal para este proceso.

INFORMACIÓN DEL PROCEDIMIENTO:
• Número de expediente: SAT-2025-{company_context[:4].upper()}-847293
• Tipo de revisión: Revisión de gabinete
• Período a revisar: Ejercicio fiscal 2024
• Fecha de inicio: {datetime.now().strftime('%d de %B de %Y')}
• Responsable: {user_name} - {department}

DOCUMENTACIÓN REQUERIDA (ENTREGA INMEDIATA):
1. Estados financieros dictaminados 2024
2. Declaraciones anuales y mensuales 2024
3. Comprobantes fiscales de gastos mayores a $50,000
4. Conciliación entre contabilidad y declaraciones
5. Balanza de comprobación al 31/12/2024

IMPORTANTE: El incumplimiento en la entrega de documentación dentro de las siguientes 24 HORAS resultará en:
❌ Multa de $186,000 a $371,000 pesos
❌ Clausura temporal de las instalaciones
❌ Embargo precautorio de cuentas bancarias

Para evitar estas sanciones, debe:
1. Acceder al portal SAT empresarial: [ENLACE FALSO]
2. Cargar la documentación en formato PDF
3. Confirmar recepción respondiendo este correo

Este procedimiento es de carácter OBLIGATORIO conforme al Artículo 42 del Código Fiscal de la Federación.

DATOS DE CONTACTO:
Lic. María Elena Rodríguez Sánchez
Administración Local de Auditoría Fiscal
Tel: 55-4738-2100 ext. 2847
Email: mrodriguez.alf@sat.gob.mx

Quedamos en espera de su pronta respuesta.

Atentamente,
SERVICIO DE ADMINISTRACIÓN TRIBUTARIA
Administración Local de Auditoría Fiscal""",
        "call_to_action": "Acceder al portal SAT y subir documentación en las próximas 24 horas",
        "urgency_indicators": [
            "Plazo de 24 horas",
            "Multas específicas mencionadas",
            "Número de expediente oficial",
            "Clausura temporal amenazada"
        ],
        "personalization_hooks": [
            f"Nombre específico: {user_name}",
            f"Área de responsabilidad: {department}",
            f"Empresa específica: {company_context}",
            "Montos de multa específicos",
            "RFC de empresa mencionado"
        ],
        "realistic_details": [
            "Número de expediente convincente",
            "Artículo legal específico",
            "Nombre y cargo del funcionario",
            "Teléfono oficial del SAT",
            "Proceso fiscalmente correcto"
        ]
    }

def create_security_update_email(user_name, department, company_context, urgency):
    """Crear email de actualización de seguridad ultra-realista"""
    return {
        "subject": f"CRÍTICO: Brecha de seguridad detectada - Acción inmediata requerida",
        "sender": f"seguridad@{company_context.lower().replace(' ', '')}.com",
        "sender_name": "Ing. Carlos Mendoza - CISO",
        "body": f"""Estimado/a {user_name},

El equipo de Ciberseguridad ha detectado actividad sospechosa relacionada con credenciales del departamento de {department}.

DETALLES DEL INCIDENTE:
• ID del incidente: SEC-2025-{department[:3].upper()}-4729
• Hora de detección: {datetime.now().strftime('%d/%m/%Y %H:%M')}
• Tipo de amenaza: Acceso no autorizado potencial
• Sistemas afectados: Servidores de {department}
• Nivel de riesgo: CRÍTICO

INDICADORES DE COMPROMISO:
• Múltiples intentos de acceso desde IP: 185.243.115.47 (Rusia)
• Intento de acceso a archivos confidenciales de {department}
• Uso de credenciales que coinciden con el patrón: {user_name[:2]}***

ACCIÓN INMEDIATA REQUERIDA:
Por políticas de seguridad corporativa, debe verificar inmediatamente la integridad de su cuenta.

PASOS A SEGUIR (URGENTE):
1. Acceder al portal de verificación: [ENLACE MALICIOSO]
2. Confirmar su identidad con credenciales actuales
3. Actualizar contraseña siguiendo políticas corporativas
4. Responder confirmando que completó el proceso

ADVERTENCIA: Si no completa la verificación en las próximas 2 HORAS:
• Su cuenta será suspendida automáticamente
• Se bloqueará el acceso a sistemas de {department}
• Se escalará el incidente a Dirección General

Este es un protocolo de seguridad automatizado activado por nuestro SOC (Security Operations Center).

Para consultas urgentes:
Ing. Carlos Mendoza - CISO
Tel: ext. 1337
Email: cmendoza.ciso@{company_context.lower().replace(' ', '')}.com

Equipo de Ciberseguridad
{company_context}""",
        "call_to_action": "Verificar cuenta en portal de seguridad en las próximas 2 horas",
        "urgency_indicators": [
            "Incidente de seguridad activo",
            "IP de atacante específica",
            "Deadline de 2 horas",
            "Suspensión automática amenazada"
        ],
        "personalization_hooks": [
            f"Credenciales parciales: {user_name[:2]}***",
            f"Sistemas específicos de {department}",
            f"Archivos de {department} mencionados",
            "ID de incidente personalizado"
        ],
        "realistic_details": [
            "ID de incidente técnico convincente",
            "IP de atacante real",
            "Terminología de ciberseguridad correcta",
            "Escalación a dirección mencionada",
            "SOC y procesos reales"
        ]
    }

def create_compliance_email(user_name, department, company_context, urgency):
    """Crear email de compliance ultra-realista"""
    return {
        "subject": f"Acción requerida: Actualización de compliance {department} - {company_context}",
        "sender": f"compliance@{company_context.lower().replace(' ', '')}.com",
        "sender_name": "Lic. Ana Patricia Vásquez - Chief Compliance Officer",
        "body": f"""Estimado/a {user_name},

En seguimiento a la auditoría externa de KPMG y como parte del proceso de certificación ISO 27001, requerimos su colaboración inmediata.

MARCO REGULATORIO:
• Ley General de Protección de Datos Personales (LGPDP)
• NOM-151-SCFI-2016 (Esquemas de ciberseguridad)
• SOX Section 404 (para reportes financieros)
• Lineamientos CNBV (sector financiero)

ACCIONES REQUERIDAS PARA {department.upper()}:
1. Actualización de matriz de riesgos departamental
2. Certificación de controles de acceso
3. Validación de procedimientos de {department}
4. Confirmación de capacitación en protección de datos

INFORMACIÓN ESPECÍFICA SOLICITADA:
• Lista actualizada de usuarios con acceso a sistemas críticos
• Inventario de datos personales bajo custodia de {department}
• Bitácora de accesos del último trimestre
• Certificación de destrucción segura de documentos

TIMELINE CRÍTICO:
La auditoría externa revisará específicamente el área de {department} el próximo VIERNES.

El incumplimiento puede resultar en:
• Observaciones en el dictamen de auditoría
• Multas INAI hasta por $327,000,000 pesos
• Pérdida de certificaciones ISO
• Impacto en calificación crediticia corporativa

PROCESO DE CUMPLIMIENTO:
1. Acceder al portal de compliance: [ENLACE MALICIOSO]
2. Completar cuestionario específico de {department}
3. Cargar evidencias documentales
4. Obtener certificado digital de cumplimiento

Su colaboración es FUNDAMENTAL para mantener nuestras certificaciones.

Cualquier duda, favor de contactarme directamente.

Lic. Ana Patricia Vásquez Morales
Chief Compliance Officer
{company_context}
Tel: ext. 1100 | avazquez.cco@{company_context.lower().replace(' ', '')}.com""",
        "call_to_action": "Completar portal de compliance antes del viernes",
        "urgency_indicators": [
            "Auditoría externa el viernes",
            "Multas INAI específicas",
            "Certificaciones en riesgo",
            "Impacto crediticio mencionado"
        ],
        "personalization_hooks": [
            f"Revisión específica de {department}",
            f"Procedimientos de {department}",
            f"Datos bajo custodia de {department}",
            "Usuario con acceso a sistemas críticos"
        ],
        "realistic_details": [
            "Leyes y normas específicas reales",
            "Montos de multa INAI reales",
            "Proceso de auditoría convincente",
            "Certificaciones mencionadas",
            "Terminología legal correcta"
        ]
    }

def save_content_result(result, user_data, content_type, scenario):
    """Guardar resultado del contenido generado"""
    
    # Obtener nombre de usuario de manera segura
    user_name = user_data.get('user_name', 'Usuario Desconocido') if isinstance(user_data, dict) else str(user_data)
    
    content_data = {
        'target_user': user_name,
        'content_type': content_type,
        'scenario': scenario,
        'content': result,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Inicializar lista si no existe
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = []
    
    st.session_state.generated_content.append(content_data)
    st.session_state.current_content = content_data
    return content_data

def display_existing_content():
    """Mostrar contenido existente"""
    if st.session_state.get('generated_content'):
        st.markdown("---")
        st.markdown("### 📧 Contenido Generado Anteriormente")
        
        for i, content in enumerate(st.session_state.generated_content[-3:]):
            with st.expander(f"📩 {content['content_type']} para {content['target_user']} - {content['timestamp']}", expanded=False):
                display_content_summary(content)

def display_content_summary(content_data):
    """Mostrar resumen del contenido"""
    content = content_data['content']
    main_content = content.get('content', {})
    
    st.markdown(f"**Asunto:** {main_content.get('subject', 'N/A')}")
    st.markdown(f"**Tipo:** {content_data['content_type']}")
    st.markdown(f"**Escenario:** {content_data['scenario']}")
    
    if 'effectiveness_prediction' in content:
        score = content['effectiveness_prediction'].get('overall_score', 0)
        st.metric("Efectividad Predicha", f"{score:.0%}")

def display_generated_content(content_data):
    """Mostrar contenido generado de manera mejorada"""
    
    # Verificar estructura de datos
    if not content_data or not isinstance(content_data, dict):
        st.error("Error: Estructura de datos inválida")
        return
    
    # Obtener datos de manera segura
    target_user = content_data.get('target_user', 'Usuario Desconocido')
    content_type = content_data.get('content_type', 'Contenido')
    scenario = content_data.get('scenario', 'Escenario')
    timestamp = content_data.get('timestamp', 'Fecha desconocida')
    
    content = content_data.get('content', {})
    main_content = content.get('content', {})
    analysis = content.get('psychological_analysis', {})
    prediction = content.get('effectiveness_prediction', {})
    
    st.markdown("### 📧 Contenido Personalizado Generado")
    
    # Información básica
    st.markdown(f"**Usuario objetivo:** {target_user}")
    st.markdown(f"**Tipo:** {content_type} | **Escenario:** {scenario}")
    st.markdown(f"**Generado:** {timestamp}")
    
    # Predicción de efectividad
    overall_score = prediction.get('overall_score', 0)
    success_prob = prediction.get('success_probability', 0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Efectividad General", f"{overall_score:.0%}")
    
    with col2:
        st.metric("Probabilidad de Éxito", f"{success_prob:.0%}")
    
    # Desglose de scores
    if prediction.get('score_breakdown'):
        st.markdown("**Desglose de Efectividad:**")
        breakdown = prediction['score_breakdown']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Personalización", f"{breakdown.get('personalization', 0):.0%}")
        with col2:
            st.metric("Autoridad", f"{breakdown.get('authority', 0):.0%}")
        with col3:
            st.metric("Urgencia", f"{breakdown.get('urgency', 0):.0%}")
        with col4:
            st.metric("Impacto Emocional", f"{breakdown.get('emotional_impact', 0):.0%}")
    
    # Contenido del email/mensaje
    st.markdown("### 📨 Contenido del Mensaje")
    
    # Header del contenido
    sender_name = main_content.get('sender_name', 'N/A')
    sender_email = main_content.get('sender', 'N/A')
    subject = main_content.get('subject', 'N/A')
    
    st.markdown(f"""
    <div class="email-header">
        <strong>De:</strong> {sender_name} &lt;{sender_email}&gt;<br>
        <strong>Para:</strong> {target_user}<br>
        <strong>Asunto:</strong> {subject}<br>
        <strong>Fecha:</strong> {datetime.now().strftime('%d %b %Y, %H:%M')}<br>
        <strong>Tipo:</strong> {content_type} | <strong>Escenario:</strong> {scenario}
    </div>
    """, unsafe_allow_html=True)
    
    # Cuerpo del mensaje
    body_text = main_content.get('body', 'Sin contenido')
    if isinstance(body_text, str):
        body_text = body_text.replace('\n', '<br>')
    else:
        body_text = str(body_text).replace('\n', '<br>')
    
    st.markdown(f"""
    <div class="email-container">
        {body_text}
    </div>
    """, unsafe_allow_html=True)
    
    # Call to action
    call_to_action = main_content.get('call_to_action')
    if call_to_action:
        st.markdown(f"""
        <div style="background: #1e40af; color: white; padding: 1rem; border-radius: 6px; text-align: center; margin: 1rem 0;">
            <strong>🎯 Acción Solicitada:</strong> {call_to_action}
        </div>
        """, unsafe_allow_html=True)
    
    # Análisis detallado
    display_detailed_analysis(analysis, prediction, content)
    
    # Acciones
    display_content_actions(content_data)

def display_detailed_analysis(analysis, prediction, content):
    """Mostrar análisis detallado del contenido"""
    
    st.markdown("### 🧠 Análisis Psicológico Detallado")
    
    # Vulnerabilidades explotadas
    if analysis.get('target_vulnerabilities'):
        st.markdown("**🎯 Vulnerabilidades Explotadas:**")
        for vuln in analysis['target_vulnerabilities']:
            st.markdown(f"• {vuln}")
    
    # Técnicas de persuasión
    if analysis.get('persuasion_techniques'):
        st.markdown("**🎭 Técnicas de Persuasión:**")
        for technique in analysis['persuasion_techniques']:
            if isinstance(technique, dict):
                st.markdown(f"""
                <div style="border-left: 4px solid #3b82f6; padding: 0.5rem; margin: 0.5rem 0; background: #eff6ff;">
                    <strong>{technique.get('technique', 'Técnica')}</strong><br>
                    <em>Aplicación:</em> {technique.get('application', 'No especificada')}<br>
                    <em>Efectividad:</em> {technique.get('effectiveness_reason', 'No especificada')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"• {technique}")
    
    # Elementos específicos
    col1, col2 = st.columns(2)
    
    with col1:
        if analysis.get('emotional_triggers'):
            st.markdown("**💭 Triggers Emocionales:**")
            for trigger in analysis['emotional_triggers']:
                st.markdown(f"• {trigger}")
    
    with col2:
        if analysis.get('authority_elements'):
            st.markdown("**👔 Elementos de Autoridad:**")
            for element in analysis['authority_elements']:
                st.markdown(f"• {element}")
    
    # Ganchos de personalización
    if content.get('content', {}).get('personalization_hooks'):
        st.markdown("**🎣 Ganchos de Personalización:**")
        for hook in content['content']['personalization_hooks']:
            st.markdown(f"• {hook}")
    
    # Análisis de riesgo
    if prediction.get('potential_red_flags'):
        st.markdown("**⚠️ Posibles Señales de Alerta:**")
        for flag in prediction['potential_red_flags']:
            st.markdown(f"• {flag}")
    
    # Razonamiento
    if prediction.get('reasoning'):
        st.markdown("**🔍 Análisis de Efectividad:**")
        st.info(prediction['reasoning'])
    
    # Variaciones
    if content.get('variations'):
        st.markdown("### 🔄 Variaciones Alternativas")
        for var in content['variations']:
            st.markdown(f"""
            <div style="border-left: 4px solid #059669; padding: 1rem; margin: 0.5rem 0; background: #f0fdf4;">
                <strong>{var.get('variation_type', 'Variación')}</strong><br>
                <em>Asunto:</em> {var.get('subject', 'No especificado')}<br>
                <em>Diferencias:</em> {var.get('key_differences', 'No especificadas')}
            </div>
            """, unsafe_allow_html=True)
    
    # Acciones
    display_content_actions(content_data)

def display_content_actions(content_data):
    """Mostrar acciones para el contenido"""
    st.markdown("### 🔧 Acciones")
    
    # Verificar estructura de datos
    if not content_data or not isinstance(content_data, dict):
        st.error("No se pueden mostrar acciones: datos inválidos")
        return
    
    # Obtener datos de manera segura
    target_user = content_data.get('target_user', 'Usuario')
    timestamp = content_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Crear ID único para evitar conflictos
    safe_timestamp = timestamp.replace(':', '').replace('-', '').replace(' ', '_')
    content_id = f"{target_user}_{safe_timestamp}".replace(' ', '_')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Copiar Contenido", key=f"copy_content_{content_id}"):
            # Crear texto para copiar
            main_content = content_data.get('content', {}).get('content', {})
            copy_text = f"""
Asunto: {main_content.get('subject', 'N/A')}
De: {main_content.get('sender_name', 'N/A')} <{main_content.get('sender', 'N/A')}>
Para: {target_user}

{main_content.get('body', 'Sin contenido')}

---
Acción solicitada: {main_content.get('call_to_action', 'N/A')}
Efectividad predicha: {content_data.get('content', {}).get('effectiveness_prediction', {}).get('overall_score', 0):.0%}
Generado: {timestamp}
            """.strip()
            
            st.text_area("Contenido para copiar:", copy_text, height=150, key=f"textarea_{content_id}")
    
    with col2:
        if st.button("🔄 Regenerar", key=f"regen_{content_id}"):
            st.info("Para regenerar, use el formulario de generación nuevamente con diferentes parámetros.")
    
    with col3:
        # Crear datos para exportar
        export_data = {
            "contenido": content_data,
            "analisis_completo": content_data.get('content', {}),
            "timestamp": timestamp,
            "efectividad": content_data.get('content', {}).get('effectiveness_prediction', {})
        }
        
        safe_filename = f"contenido_analisis_{target_user}_{safe_timestamp}.json".replace(' ', '_')
        
        st.download_button(
            label="💾 Exportar Análisis",
            data=json.dumps(export_data, indent=2, ensure_ascii=False),
            file_name=safe_filename,
            mime="application/json",
            key=f"export_{content_id}"
        )

def load_demo_data():
    """Cargar datos de ejemplo completos para demostración"""
    
    # Limpiar datos existentes
    st.session_state.completed_analyses = []
    st.session_state.user_profiles = []
    st.session_state.generated_content = []
    
    # Análisis OSINT de ejemplo
    demo_osint = {
        'type': 'Análisis OSINT (DEMO)',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'company': 'TechCorp Demo',
        'summary': {
            "risk_score": 0.78,
            "risk_level": "ALTO",
            "vulnerabilities": [
                {
                    "type": "Exposición de Empleados en RRSS",
                    "severity": "ALTA",
                    "description": "45% del personal técnico comparte información sobre proyectos en LinkedIn",
                    "evidence": "Perfiles públicos con detalles de stack tecnológico",
                    "impact": "Posible ingeniería social dirigida y reconocimiento técnico"
                },
                {
                    "type": "Subdominios Vulnerables",
                    "severity": "MEDIA",
                    "description": "5 subdominios con servicios desactualizados detectados",
                    "evidence": "Escaneo automatizado reveló versiones antiguas",
                    "impact": "Posible explotación de vulnerabilidades conocidas"
                },
                {
                    "type": "Información Técnica Filtrada",
                    "severity": "MEDIA",
                    "description": "Stack tecnológico visible en ofertas de trabajo",
                    "evidence": "Ofertas laborales con detalles específicos",
                    "impact": "Facilita ataques dirigidos a infraestructura"
                }
            ],
            "attack_vectors": [
                {
                    "vector": "Spear Phishing dirigido",
                    "probability": 0.85,
                    "impact": "Acceso a sistemas críticos mediante ingeniería social dirigida",
                    "method": "Emails personalizados usando información pública de empleados"
                },
                {
                    "vector": "Ingeniería social telefónica",
                    "probability": 0.65,
                    "impact": "Obtención de credenciales mediante llamadas dirigidas",
                    "method": "Llamadas haciéndose pasar por proveedores conocidos"
                }
            ],
            "employee_exposure": [
                {
                    "employee": "Juan Pérez - CTO",
                    "risk_level": "ALTO",
                    "exposure_type": "LinkedIn, GitHub, Twitter",
                    "sensitive_info": "Proyectos actuales, stack tecnológico, estructura del equipo"
                },
                {
                    "employee": "María González - DevOps Lead",
                    "risk_level": "MEDIO",
                    "exposure_type": "GitHub, conferencias técnicas",
                    "sensitive_info": "Herramientas de infraestructura, procesos de deployment"
                }
            ],
            "technical_findings": [
                {
                    "finding": "Subdominios con servicios expuestos",
                    "risk": "MEDIO",
                    "recommendation": "Auditoría y hardening de servicios públicos"
                },
                {
                    "finding": "Información de empleados en conferencias",
                    "risk": "BAJO",
                    "recommendation": "Políticas de disclosure en eventos públicos"
                }
            ],
            "industry_specific_risks": [
                "Regulaciones GDPR para datos de clientes",
                "Ataques dirigidos a empresas de tecnología",
                "Competencia industrial puede usar información expuesta"
            ],
            "recommendations": [
                {
                    "priority": "ALTA",
                    "category": "Concienciación",
                    "action": "Implementar programa de entrenamiento en ingeniería social",
                    "timeline": "30 días"
                },
                {
                    "priority": "ALTA",
                    "category": "Infraestructura",
                    "action": "Auditar y asegurar todos los subdominios expuestos",
                    "timeline": "15 días"
                },
                {
                    "priority": "MEDIA",
                    "category": "Políticas",
                    "action": "Establecer políticas de publicación en redes sociales",
                    "timeline": "60 días"
                }
            ]
        }
    }
    
    st.session_state.completed_analyses.append(demo_osint)
    st.session_state.current_osint = demo_osint['summary']
    
    # Perfil de usuario de ejemplo
    demo_profile = {
        'user_name': 'Ana García (Demo)',
        'department': 'Finanzas',
        'analysis': {
            "psychological_profile": {
                "personality_summary": "Ana García es una profesional de Finanzas orientada a resultados con alta conciencia del cumplimiento. Muestra patrones de comportamiento colaborativo pero con tendencia a confiar en figuras de autoridad.",
                "core_traits": ["Orientada a resultados", "Detallista", "Confiada", "Responsable"],
                "behavioral_patterns": [
                    "Responde rápidamente a solicitudes de autoridades",
                    "Sigue procedimientos establecidos meticulosamente",
                    "Comparte información cuando percibe legitimidad oficial"
                ],
                "decision_making_style": "Analítica pero susceptible a presión temporal de autoridades",
                "stress_responses": [
                    "Busca aprobación de superiores cuando hay presión",
                    "Acelera decisiones cuando se menciona cumplimiento regulatorio"
                ],
                "technology_relationship": "Cómoda con herramientas financieras, cautelosa con nuevas tecnologías",
                "social_behavior": "Profesional y reservada, pero colaborativa en temas de trabajo"
            },
            "vulnerability_assessment": {
                "overall_risk_score": 0.72,
                "risk_factors": [
                    {
                        "factor": "Autoridad percibida",
                        "score": 0.85,
                        "description": "Alta susceptibilidad a figuras de autoridad financiera y regulatoria",
                        "mitigation": "Entrenamiento en verificación de identidad de autoridades"
                    },
                    {
                        "factor": "Presión de cumplimiento",
                        "score": 0.78,
                        "description": "Respuesta acelerada ante menciones de auditorías o compliance",
                        "mitigation": "Protocolos específicos para solicitudes de auditoría"
                    }
                ],
                "psychological_vulnerabilities": [
                    {
                        "type": "Autoridad regulatoria",
                        "severity": "ALTA",
                        "description": "Alta susceptibilidad a figuras que se presentan como autoridades fiscales o regulatorias",
                        "triggers": ["Auditorías", "Compliance", "Procesos fiscales", "Reportes financieros"],
                        "exploitation_method": "Emails simulando comunicaciones oficiales de entidades regulatorias"
                    },
                    {
                        "type": "Presión temporal en finanzas",
                        "severity": "MEDIA",
                        "description": "Vulnerabilidad a tácticas que crean urgencia en procesos financieros",
                        "triggers": ["Deadlines fiscales", "Cierres contables", "Reportes urgentes"],
                        "exploitation_method": "Crear escenarios de urgencia falsa relacionados con procesos financieros"
                    }
                ]
            },
            "attack_simulation": {
                "most_effective_vectors": [
                    {
                        "technique": "Phishing de autoridad fiscal",
                        "effectiveness_score": 0.82,
                        "approach": "Emails simulando auditorías urgentes de autoridades fiscales con documentación aparentemente oficial",
                        "psychological_basis": "Miedo a problemas legales/fiscales combinado con respeto a autoridad",
                        "execution_example": "Email de 'Hacienda' solicitando verificación urgente de datos fiscales de la empresa"
                    },
                    {
                        "technique": "Ingeniería social de compliance",
                        "effectiveness_score": 0.75,
                        "approach": "Llamadas telefónicas haciéndose pasar por auditores externos solicitando información",
                        "psychological_basis": "Responsabilidad profesional y temor a incumplimiento",
                        "execution_example": "Llamada de 'auditor externo' solicitando confirmación de datos para proceso de compliance"
                    }
                ],
                "social_engineering_angles": [
                    {
                        "angle": "Autoridad fiscal/regulatoria",
                        "success_probability": 0.8,
                        "description": "Aprovechamiento de respeto natural a autoridades financieras y fiscales"
                    },
                    {
                        "angle": "Urgencia en procesos contables",
                        "success_probability": 0.65,
                        "description": "Creación de escenarios de urgencia en procesos familiares de finanzas"
                    }
                ]
            },
            "personalized_training": {
                "priority_areas": [
                    {
                        "area": "Verificación de autoridad fiscal",
                        "priority": "ALTA",
                        "reason": "Alta susceptibilidad a figuras de autoridad financiera identificada en el perfil",
                        "training_approach": "Simulacros específicos con verificación de identidad de autoridades fiscales"
                    },
                    {
                        "area": "Manejo de presión temporal en finanzas",
                        "priority": "MEDIA",
                        "reason": "Tendencia a acelerar decisiones bajo presión de compliance",
                        "training_approach": "Protocolos de pausa y verificación en situaciones urgentes"
                    }
                ],
                "recommended_simulations": [
                    {
                        "scenario": "Phishing de auditoría fiscal urgente",
                        "frequency": "Mensual",
                        "difficulty": "Alta",
                        "focus": "Verificación de autoridades antes de proporcionar información"
                    },
                    {
                        "scenario": "Llamada de auditor externo falso",
                        "frequency": "Bimensual",
                        "difficulty": "Media",
                        "focus": "Protocolos de verificación telefónica"
                    }
                ]
            }
        },
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    st.session_state.user_profiles.append(demo_profile)
    st.session_state.current_profile = demo_profile
    
    # Contenido generado de ejemplo
    demo_content = {
        'target_user': 'Ana García (Demo)',
        'content_type': 'Email de phishing',
        'scenario': 'Auditoría fiscal',
        'content': {
            "content": {
                "subject": "URGENTE: Verificación Fiscal Requerida - Finanzas",
                "sender": "verificacion@hacienda-digital.gob.mx",
                "sender_name": "Servicio de Administración Tributaria",
                "body": """Estimada Ana García,

Como responsable del área de Finanzas de TechCorp Demo, hemos identificado una discrepancia en su declaración fiscal del último trimestre que requiere verificación inmediata.

De acuerdo con nuestros registros, su empresa presenta irregularidades en:
- Declaración de IVA del Q3 2024
- Retenciones de nómina no reportadas
- Deducciones no comprobadas por $125,000 MXN

Por disposiciones fiscales vigentes, debe proporcionar la siguiente documentación ANTES DE LAS 18:00 HRS DEL DÍA DE HOY:

1. Estados financieros actualizados
2. Comprobantes de retenciones del último trimestre  
3. Confirmación de datos bancarios corporativos
4. Autorización para revisión de cuentas

El incumplimiento de este requerimiento puede resultar en:
❌ Multas por $500,000 - $2,000,000 MXN
❌ Congelamiento de cuentas bancarias corporativas
❌ Proceso administrativo de ejecución

Para evitar sanciones, complete inmediatamente el formulario de verificación en el enlace oficial:
🔗 [VERIFICAR DATOS FISCALES - SISTEMA SAT]

Número de expediente: SAT-2024-TechCorp-7845
Fecha límite: HOY 18:00 hrs
Responsable: Ana García - Área Finanzas

Saludos oficiales,
Lic. Roberto Martínez Sánchez
Subdirector de Fiscalización
Servicio de Administración Tributaria
Tel: 55-4738-2100 ext. 2847""",
                "call_to_action": "Completar verificación fiscal antes de las 18:00 hrs del día de hoy",
                "urgency_indicators": [
                    "Fecha límite específica (18:00 hrs)",
                    "Amenaza de multas económicas concretas",
                    "Número de expediente oficial",
                    "Consecuencias graves mencionadas"
                ],
                "personalization_hooks": [
                    "Nombre específico: Ana García",
                    "Área específica: Finanzas", 
                    "Empresa específica: TechCorp Demo",
                    "Montos específicos de irregularidades",
                    "Responsabilidad directa mencionada"
                ]
            },
            "psychological_analysis": {
                "target_vulnerabilities": [
                    "Autoridad regulatoria",
                    "Presión temporal en finanzas",
                    "Responsabilidad profesional"
                ],
                "persuasion_techniques": [
                    {
                        "technique": "Autoridad gubernamental",
                        "application": "Remitente presenta como Servicio de Administración Tributaria oficial",
                        "effectiveness_reason": "Ana responde automáticamente a autoridades fiscales por su rol en Finanzas"
                    },
                    {
                        "technique": "Miedo específico a sanciones",
                        "application": "Menciona multas concretas de $500K-$2M y congelamiento de cuentas",
                        "effectiveness_reason": "Como responsable de Finanzas, estos escenarios son su peor pesadilla profesional"
                    },
                    {
                        "technique": "Urgencia temporal crítica",
                        "application": "Deadline específico del mismo día a las 18:00 hrs",
                        "effectiveness_reason": "Presión temporal reduce tiempo de análisis crítico en procesos fiscales"
                    },
                    {
                        "technique": "Personalización detallada",
                        "application": "Incluye nombre, área, empresa y montos específicos de irregularidades",
                        "effectiveness_reason": "Alto nivel de personalización aumenta percepción de legitimidad"
                    }
                ],
                "emotional_triggers": [
                    "Miedo a sanciones económicas devastadoras",
                    "Pánico por responsabilidad profesional",
                    "Estrés por deadline inmediato",
                    "Temor a consecuencias legales para la empresa"
                ],
                "authority_elements": [
                    "Logo y nombre oficial del SAT",
                    "Número de expediente oficial",
                    "Nombre y cargo específico del funcionario",
                    "Teléfono de contacto oficial",
                    "Lenguaje formal gubernamental"
                ],
                "social_proof_elements": [
                    "Procedimiento aparentemente estándar",
                    "Referencias a disposiciones fiscales",
                    "Proceso administrativo formal",
                    "Sistema oficial de verificación"
                ]
            },
            "effectiveness_prediction": {
                "overall_score": 0.88,
                "score_breakdown": {
                    "personalization": 0.95,
                    "authority": 0.92,
                    "urgency": 0.85,
                    "emotional_impact": 0.88
                },
                "success_probability": 0.82,
                "reasoning": "Contenido extremadamente personalizado que explota las vulnerabilidades principales identificadas en el perfil de Ana García: autoridad fiscal, presión temporal y responsabilidad profesional. La combinación de amenazas económicas específicas, deadline crítico y personalización detallada crea un escenario de alta efectividad.",
                "potential_red_flags": [
                    "Email externo solicitando datos sensibles",
                    "Urgencia artificial puede generar sospecha",
                    "Solicitud de datos bancarios por email",
                    "Falta de proceso oficial de verificación presencial"
                ]
            },
            "variations": [
                {
                    "variation_type": "Menos agresivo",
                    "subject": "Notificación de Revisión Fiscal - TechCorp Demo",
                    "key_differences": "Elimina urgencia artificial, reduce amenazas, tono más informativo"
                },
                {
                    "variation_type": "Más técnico",
                    "subject": "Requerimiento Art. 42 CFF - Verificación Documental",
                    "key_differences": "Lenguaje más técnico fiscal, referencias específicas a artículos legales"
                }
            ]
        },
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    st.session_state.generated_content.append(demo_content)
    st.session_state.current_content = demo_content

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Error en la aplicación: {str(e)}")
        st.info("Intente recargar la página o use el modo demo.")
