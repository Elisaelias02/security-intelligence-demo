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
    load_css()
    
    # Inicializar estado de la sesión
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = False
    
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

def setup_ai_agent():
    """Configurar agente de IA REAL"""
    
    with st.sidebar:
        st.markdown("### Configuración del Sistema")
        
        if not ANTHROPIC_AVAILABLE:
            st.error("**Anthropic SDK no instalado**")
            st.code("pip install anthropic", language="bash")
            st.markdown("**Instalación completa:**")
            st.code("""
pip install anthropic
pip install streamlit
pip install plotly
pip install pandas
            """, language="bash")
            return
        
        # Input para API key
        st.markdown("**Obtener API Key:**")
        st.markdown("1. Ir a [console.anthropic.com](https://console.anthropic.com)")
        st.markdown("2. Crear cuenta / Iniciar sesión")
        st.markdown("3. Ir a 'API Keys' y crear nueva clave")
        st.markdown("4. Copiar la clave (empieza con 'sk-ant-')")
        
        api_key = st.text_input(
            "Clave API de Anthropic", 
            type="password",
            placeholder="sk-ant-api-key...",
            help="Debe empezar con 'sk-ant-'"
        )
        
        # Botón para usar datos de ejemplo
        if st.button("🧪 Usar Datos de Ejemplo (Sin IA)"):
            st.session_state.demo_mode = True
            st.success("✅ Modo demo activado - usando datos de ejemplo")
            st.info("📝 Este modo muestra la interfaz con datos predefinidos sin usar IA")
        
        if api_key:
            # Validación básica de formato
            if not api_key.startswith('sk-ant-'):
                st.error("❌ Formato de API key incorrecto. Debe empezar con 'sk-ant-'")
                return
                
            try:
                # Inicializar cliente Anthropic REAL
                client = anthropic.Anthropic(api_key=api_key)
                
                # Probar conexión con Claude 3.5 Sonnet (modelo más avanzado disponible)
                test_response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "test"}]
                )
                
                st.session_state.anthropic_client = client
                st.session_state.claude_model = "claude-3-5-sonnet-20241022"
                st.session_state.demo_mode = False
                st.success("✅ Anthropic Claude 3.5 Sonnet conectado")
                st.info("**Modelo**: Claude 3.5 Sonnet (más avanzado)")
                st.info("**Contexto**: 200k tokens | **Límite**: Según plan")
                
                # Botón para probar conexión
                if st.button("🧪 Probar Conexión"):
                    test_prompt = "Responde solo 'Claude 3.5 Sonnet conectado exitosamente' si puedes ver este mensaje."
                    try:
                        test_resp = client.messages.create(
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=30,
                            messages=[{"role": "user", "content": test_prompt}]
                        )
                        st.success(f"✅ {test_resp.content[0].text}")
                    except Exception as test_error:
                        st.error(f"❌ Error en prueba: {test_error}")
                
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg or "not_found" in error_msg:
                    # Intentar con Claude 3.5 Haiku como respaldo
                    try:
                        client = anthropic.Anthropic(api_key=api_key)
                        test_response = client.messages.create(
                            model="claude-3-5-haiku-20241022",
                            max_tokens=10,
                            messages=[{"role": "user", "content": "test"}]
                        )
                        st.session_state.anthropic_client = client
                        st.session_state.claude_model = "claude-3-5-haiku-20241022"
                        st.session_state.demo_mode = False
                        st.success("✅ Anthropic Claude 3.5 Haiku conectado")
                        st.info("**Modelo**: claude-3-5-haiku-20241022 (respaldo)")
                        st.warning("Nota: Usando Claude 3.5 Haiku (modelo económico)")
                        
                    except Exception as e2:
                        # Último recurso: Claude 3 Opus
                        try:
                            test_response = client.messages.create(
                                model="claude-3-opus-20240229",
                                max_tokens=10,
                                messages=[{"role": "user", "content": "test"}]
                            )
                            st.session_state.anthropic_client = client
                            st.session_state.claude_model = "claude-3-opus-20240229"
                            st.session_state.demo_mode = False
                            st.success("✅ Anthropic Claude 3 Opus conectado")
                            st.info("**Modelo**: claude-3-opus-20240229")
                            st.warning("Nota: Usando Claude 3 Opus (modelo premium)")
                            
                        except Exception as e3:
                            st.error(f"❌ Error de conexión con todos los modelos")
                            st.error(f"**Error técnico:** {str(e3)}")
                            st.markdown("""
                            **Posibles soluciones:**
                            1. Verificar que la API key sea correcta
                            2. Verificar que tenga créditos disponibles en su cuenta
                            3. Verificar que la API key tenga permisos
                            4. Intentar en unos minutos (puede ser problema temporal)
                            5. Usar el botón "Usar Datos de Ejemplo" para probar la interfaz
                            """)
                            return
                else:
                    st.error(f"❌ Error de conexión: {error_msg}")
                    st.markdown("""
                    **Posibles soluciones:**
                    1. Verificar que la API key sea correcta (debe empezar con 'sk-ant-')
                    2. Verificar que tenga créditos disponibles
                    3. Verificar conexión a internet
                    4. Usar el botón "Usar Datos de Ejemplo" para probar la interfaz
                    """)
                    return
        else:
            st.warning("⚠️ API key requerida para funcionalidad completa")
            st.info("El sistema intentará usar **Claude 3.5 Sonnet** primero, luego **Claude 3.5 Haiku**, y **Claude 3 Opus** como último recurso")
            if 'anthropic_client' in st.session_state:
                del st.session_state.anthropic_client
        
        st.markdown("---")
        st.markdown("### Información de Costos")
        st.markdown("""
        **Claude 3.5 Sonnet**: ~$3 por millón de tokens (MÁS AVANZADO)  
        **Claude 3.5 Haiku**: ~$1 por millón de tokens  
        **Claude 3 Opus**: ~$15 por millón de tokens  
        
        **Estimado por análisis**: $0.01 - $0.15  
        **Créditos gratuitos**: $5 para nuevas cuentas  
        **Límite por minuto**: Según plan de usuario
        """)
        
        st.markdown("### Capacidades")
        
        if 'anthropic_client' in st.session_state or st.session_state.get('demo_mode', False):
            mode_text = "(DEMO)" if st.session_state.get('demo_mode', False) else ""
            st.markdown(f"""
            ✅ **Análisis OSINT automatizado** {mode_text}  
            ✅ **Perfilado psicológico avanzado** {mode_text}  
            ✅ **Generación de contenido adaptativo** {mode_text}  
            ✅ **Evaluación de vectores de ataque** {mode_text}  
            ✅ **Análisis contextual profundo** {mode_text}
            """)
        else:
            st.markdown("""
            ❌ Análisis OSINT automatizado  
            ❌ Perfilado psicológico avanzado  
            ❌ Generación de contenido adaptativo  
            ❌ Evaluación de vectores de ataque  
            ❌ Análisis contextual profundo
            """)
        
        # Debug info
        if st.session_state.get('demo_mode'):
            st.markdown("---")
            st.markdown("### 🧪 Modo Demo Activo")
            st.info("Usando datos de ejemplo predefinidos")
            
        # Mostrar información de debug si está disponible
        if 'anthropic_client' in st.session_state:
            st.markdown("---")
            st.markdown("### 🔧 Debug Info")
            st.text(f"Modelo: {st.session_state.get('claude_model', 'N/A')}")
            st.text(f"Estado: Conectado")
            
            if st.button("🧹 Limpiar Caché"):
                for key in ['current_osint', 'current_profile', 'current_content']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("✅ Caché limpiado")

def show_dashboard():
    """Panel principal del sistema"""
    
    if 'anthropic_client' not in st.session_state and not st.session_state.get('demo_mode', False):
        st.warning("**Configure la API de Anthropic o use el Modo Demo para acceder a todas las funcionalidades**")
        st.markdown("""
        **Para usar este sistema necesitas:**
        
        1. **Cuenta en Anthropic Console**: [console.anthropic.com](https://console.anthropic.com)
        2. **API Key de Anthropic**: Genera una clave en la consola  
        3. **Créditos disponibles**: $5 gratis para cuentas nuevas
        
        **Modelos soportados (por prioridad):**
        - **Claude 3.5 Sonnet** (MÁS AVANZADO): Análisis ultra-sofisticado, 200k contexto
        - **Claude 3.5 Haiku** (económico): Análisis eficiente y rápido
        - **Claude 3 Opus** (premium): Análisis más complejo y detallado
        
        **¿Por qué Claude 3.5 Sonnet?**
        - **Razonamiento más avanzado** para análisis complejos de vulnerabilidades
        - **Mayor contexto** (200k tokens) para análisis profundos
        - **Mejor comprensión psicológica** para perfilado de usuarios
        - **Generación más sofisticada** de contenido personalizado
        
        **Casos de uso:**
        - Evaluación avanzada de vulnerabilidades de seguridad
        - Análisis psicológico profundo de susceptibilidad 
        - Generación de contenido híper-personalizado para tests
        - Capacitación avanzada en concientización de seguridad
        
        **💡 Tip**: Usa el botón **"🧪 Usar Datos de Ejemplo"** en el sidebar para probar la interfaz sin API key.
        """)
        
        st.markdown("### Instalación Rápida")
        st.code("""
# 1. Instalar dependencias
pip install anthropic streamlit plotly pandas

# 2. Ejecutar el sistema  
streamlit run security_platform.py

# 3. Configurar API key en el sidebar
# 4. El sistema usará automáticamente Claude 3.5 Sonnet
        """, language="bash")
        return
    
    # Mostrar modo actual
    if st.session_state.get('demo_mode', False):
        st.info("🧪 **MODO DEMO ACTIVADO** - Usando datos de ejemplo predefinidos")
    
    st.markdown("### Análisis Activos")
    
    # Métricas reales basadas en datos del sistema
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        analysis_count = len(st.session_state.get('completed_analyses', []))
        st.metric("Análisis Completados", analysis_count)
    
    with col2:
        if 'user_profiles' in st.session_state:
            profile_count = len(st.session_state.user_profiles)
        else:
            profile_count = 0
        st.metric("Usuarios Perfilados", profile_count)
    
    with col3:
        if 'generated_content' in st.session_state:
            content_count = len(st.session_state.generated_content)
        else:
            content_count = 0
        st.metric("Contenido Generado", content_count)
    
    with col4:
        if st.session_state.get('demo_mode', False):
            st.metric("Precisión del Sistema", "DEMO")
        else:
            st.metric("Precisión del Sistema", "AI-Powered")
    
    # Historial de análisis
    if 'completed_analyses' in st.session_state and st.session_state.completed_analyses:
        st.markdown("### Análisis Recientes")
        for analysis in st.session_state.completed_analyses[-5:]:
            with st.expander(f"{analysis['type']} - {analysis['timestamp']}"):
                if isinstance(analysis['summary'], dict):
                    st.json(analysis['summary'])
                else:
                    st.write(analysis['summary'])
    
    # Consejos útiles
    st.markdown("### 💡 Consejos de Uso")
    st.markdown("""
    **Flujo recomendado:**
    1. **Análisis OSINT**: Evalúa la superficie de ataque de la organización
    2. **Perfilado de Usuario**: Analiza vulnerabilidades psicológicas específicas
    3. **Generación de Contenido**: Crea material personalizado para tests
    
    **Para mejores resultados:**
    - Proporciona información detallada en cada formulario
    - Revisa los análisis de debug para entender el razonamiento de la IA
    - Usa el modo demo para familiarizarte con la interfaz
    """)
    
    if st.session_state.get('demo_mode', False):
        st.markdown("### 🎯 Datos de Ejemplo Disponibles")
        if st.button("📊 Cargar Análisis de Ejemplo"):
            # Cargar datos de ejemplo completos
            load_demo_data()
            st.success("✅ Datos de ejemplo cargados")
            st.rerun()

def load_demo_data():
    """Cargar datos de ejemplo completos"""
    
    # Análisis OSINT de ejemplo
    if 'completed_analyses' not in st.session_state:
        st.session_state.completed_analyses = []
    
    demo_osint = {
        'type': 'Análisis OSINT (DEMO)',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'company': 'TechCorp Demo',
        'summary': {
            "risk_score": 0.78,
            "risk_level": "ALTO",
            "vulnerabilities": [
                {
                    "type": "Exposición de Empleados",
                    "severity": "ALTA",
                    "description": "45% del personal técnico comparte información sobre proyectos en LinkedIn"
                },
                {
                    "type": "Subdominios Vulnerables",
                    "severity": "MEDIA",
                    "description": "5 subdominios con servicios desactualizados detectados"
                }
            ],
            "attack_vectors": [
                {
                    "vector": "Spear Phishing",
                    "probability": 0.85,
                    "impact": "Acceso a sistemas críticos mediante ingeniería social dirigida"
                }
            ],
            "recommendations": [
                {
                    "priority": "ALTA",
                    "action": "Implementar política de publicación en redes sociales"
                }
            ]
        }
    }
    
    st.session_state.completed_analyses.append(demo_osint)
    st.session_state.current_osint = demo_osint['summary']
    
    # Perfil de usuario de ejemplo
    if 'user_profiles' not in st.session_state:
        st.session_state.user_profiles = []
    
    demo_profile = {
        'user_name': 'Ana García (Demo)',
        'department': 'Finanzas',
        'analysis': {
            "psychological_profile": {
                "personality_traits": ["Orientada a resultados", "Confiada", "Detallista"],
                "behavioral_patterns": ["Responde rápido a autoridades", "Sigue procedimientos"],
                "decision_making_style": "Analítica pero susceptible a presión temporal",
                "stress_responses": ["Busca aprobación", "Acelera decisiones bajo presión"]
            },
            "vulnerability_assessment": {
                "risk_score": 0.72,
                "primary_vulnerabilities": [
                    {
                        "type": "Autoridad percibida",
                        "severity": "ALTA",
                        "description": "Alta susceptibilidad a figuras de autoridad financiera"
                    }
                ]
            },
            "attack_vectors": [
                {
                    "technique": "Phishing de autoridad fiscal",
                    "effectiveness": 0.82,
                    "approach": "Emails simulando auditorías urgentes",
                    "psychological_basis": "Miedo a problemas legales/fiscales"
                }
            ]
        },
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    st.session_state.user_profiles.append(demo_profile)
    st.session_state.current_profile = demo_profile

def osint_analysis():
    """Análisis OSINT real"""
    
    st.markdown("### Análisis de Inteligencia de Fuentes Abiertas")
    
    if 'anthropic_client' not in st.session_state:
        st.error("**Requiere conexión con Anthropic Claude para análisis OSINT**")
        return
    
    with st.form("osint_form"):
        st.markdown("**Información del Objetivo**")
        
        company_name = st.text_input("Nombre de la Organización")
        domain = st.text_input("Dominio Web")
        industry = st.selectbox("Industria", [
            "Tecnología", "Finanzas", "Salud", "Educación", 
            "Retail", "Manufactura", "Consultoría", "Gobierno"
        ])
        
        additional_info = st.text_area(
            "Información Adicional",
            placeholder="Cualquier información adicional sobre la organización..."
        )
        
        if st.form_submit_button("Iniciar Análisis OSINT"):
            if company_name and domain:
                run_real_osint_analysis(company_name, domain, industry, additional_info)
            else:
                st.error("Complete los campos obligatorios")
    
    # Mostrar resultados existentes si los hay
    if 'current_osint' in st.session_state:
        st.markdown("---")
        st.markdown("### 📊 Último Análisis Completado")
        display_osint_results(st.session_state.current_osint)

def run_real_osint_analysis(company_name, domain, industry, additional_info):
    """Ejecutar análisis OSINT real con Claude"""
    
    # Modo demo - usar datos predefinidos
    if st.session_state.get('demo_mode', False):
        with st.spinner("Generando análisis de ejemplo..."):
            time.sleep(2)  # Simular procesamiento
            
            demo_result = {
                "risk_score": 0.75,
                "risk_level": "ALTO",
                "vulnerabilities": [
                    {
                        "type": "Exposición de Empleados en RRSS",
                        "severity": "ALTA",
                        "description": f"Personal de {company_name} comparte información corporativa en LinkedIn y Twitter"
                    },
                    {
                        "type": "Subdominios Expuestos",
                        "severity": "MEDIA",
                        "description": f"Se identificaron 3 subdominios de {domain} con servicios no actualizados"
                    },
                    {
                        "type": "Información Técnica Filtrada",
                        "severity": "MEDIA",
                        "description": f"Stack tecnológico de {industry} visible en ofertas de trabajo"
                    }
                ],
                "attack_vectors": [
                    {
                        "vector": "Phishing dirigido",
                        "probability": 0.85,
                        "impact": f"Emails personalizados usando información pública de empleados de {department if 'department' in locals() else industry}"
                    },
                    {
                        "vector": "Ingeniería social telefónica",
                        "probability": 0.65,
                        "impact": "Llamadas haciéndose pasar por proveedores conocidos del sector"
                    },
                    {
                        "vector": "Ataques a subdominios",
                        "probability": 0.55,
                        "impact": "Explotación de servicios desactualizados en subdominios"
                    }
                ],
                "industry_specific_risks": [
                    f"Regulaciones específicas del sector {industry}",
                    f"Ataques dirigidos comunes en {industry}",
                    "Filtración de datos de clientes"
                ],
                "recommendations": [
                    {
                        "priority": "ALTA",
                        "action": "Implementar programa de concienciación sobre ingeniería social"
                    },
                    {
                        "priority": "ALTA",
                        "action": "Auditar y asegurar todos los subdominios expuestos"
                    },
                    {
                        "priority": "MEDIA",
                        "action": "Establecer políticas de publicación en redes sociales"
                    }
                ]
            }
            
            # Guardar resultado demo
            if 'completed_analyses' not in st.session_state:
                st.session_state.completed_analyses = []
            
            st.session_state.completed_analyses.append({
                'type': 'Análisis OSINT (DEMO)',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'company': company_name,
                'summary': demo_result
            })
            
            st.session_state.current_osint = demo_result
            st.success("✅ Análisis OSINT completado (Modo Demo)")
            
            # Mostrar resultados inmediatamente
            display_osint_results(demo_result)
            return
    
    with st.spinner("Ejecutando análisis OSINT..."):
        
        # Prompt mejorado para Claude
        prompt = f"""
        Eres un experto analista de ciberseguridad. Analiza la siguiente empresa y proporciona un análisis OSINT detallado.

        EMPRESA A ANALIZAR:
        - Nombre: {company_name}
        - Dominio: {domain}  
        - Industria: {industry}
        - Información adicional: {additional_info}

        Proporciona tu respuesta EXCLUSIVAMENTE en formato JSON válido, sin texto adicional antes o después:

        {{
            "risk_score": 0.75,
            "risk_level": "ALTO",
            "vulnerabilities": [
                {{
                    "type": "Ingeniería Social",
                    "severity": "ALTA",
                    "description": "Personal expuesto en redes sociales con información corporativa"
                }},
                {{
                    "type": "Superficie de Ataque Web",
                    "severity": "MEDIA",
                    "description": "Subdominios expuestos con servicios no actualizados"
                }}
            ],
            "attack_vectors": [
                {{
                    "vector": "Phishing dirigido",
                    "probability": 0.8,
                    "impact": "Acceso a credenciales corporativas mediante emails personalizados"
                }},
                {{
                    "vector": "Reconocimiento técnico",
                    "probability": 0.6,
                    "impact": "Identificación de tecnologías y versiones vulnerables"
                }}
            ],
            "industry_specific_risks": [
                "Regulaciones de cumplimiento específicas de {industry}",
                "Ataques dirigidos comunes en sector {industry}"
            ],
            "recommendations": [
                {{
                    "priority": "ALTA",
                    "action": "Implementar programa de concienciación sobre ingeniería social"
                }},
                {{
                    "priority": "MEDIA",
                    "action": "Auditar y asegurar subdominios expuestos"
                }}
            ]
        }}
        """
        
        try:
            response = st.session_state.anthropic_client.messages.create(
                model=st.session_state.get('claude_model', 'claude-3-5-haiku-20241022'),
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Procesar respuesta de manera más robusta
            content = response.content[0].text.strip()
            
            # Debug: mostrar respuesta cruda
            with st.expander("🔍 Debug: Respuesta de Claude"):
                st.text(content)
            
            # Intentar parsear JSON de múltiples formas
            analysis_result = None
            
            # Método 1: JSON entre bloques de código
            if "```json" in content and "```" in content:
                try:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_content = content[json_start:json_end].strip()
                    analysis_result = json.loads(json_content)
                except:
                    pass
            
            # Método 2: Buscar primer { hasta último }
            if not analysis_result and "{" in content and "}" in content:
                try:
                    json_start = content.find("{")
                    json_end = content.rfind("}") + 1
                    json_content = content[json_start:json_end]
                    analysis_result = json.loads(json_content)
                except:
                    pass
            
            # Método 3: Crear resultado de fallback si no se puede parsear
            if not analysis_result:
                st.warning("⚠️ No se pudo parsear JSON. Generando análisis básico...")
                analysis_result = {
                    "risk_score": 0.65,
                    "risk_level": "MEDIO",
                    "vulnerabilities": [
                        {
                            "type": "Análisis Manual Requerido",
                            "severity": "MEDIA",
                            "description": f"Se requiere análisis manual para {company_name} en sector {industry}"
                        }
                    ],
                    "attack_vectors": [
                        {
                            "vector": "Vectores típicos del sector",
                            "probability": 0.5,
                            "impact": f"Impactos comunes en industria {industry}"
                        }
                    ],
                    "industry_specific_risks": [f"Riesgos específicos de {industry}"],
                    "recommendations": [
                        {
                            "priority": "ALTA",
                            "action": "Realizar análisis OSINT manual detallado"
                        }
                    ]
                }
            
            # Guardar resultado
            if 'completed_analyses' not in st.session_state:
                st.session_state.completed_analyses = []
            
            st.session_state.completed_analyses.append({
                'type': 'Análisis OSINT',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'company': company_name,
                'summary': analysis_result
            })
            
            st.session_state.current_osint = analysis_result
            st.success("✅ Análisis OSINT completado")
            
            # Mostrar resultados inmediatamente
            display_osint_results(analysis_result)
            
        except Exception as e:
            st.error(f"❌ Error en análisis: {str(e)}")
            
            # Mostrar análisis de fallback en caso de error total
            fallback_result = {
                "risk_score": 0.5,
                "risk_level": "MEDIO",
                "vulnerabilities": [
                    {
                        "type": "Error de Análisis",
                        "severity": "MEDIA",
                        "description": "No se pudo completar el análisis automático"
                    }
                ],
                "attack_vectors": [
                    {
                        "vector": "Análisis manual requerido",
                        "probability": 0.5,
                        "impact": "Se requiere evaluación manual"
                    }
                ],
                "industry_specific_risks": ["Análisis pendiente"],
                "recommendations": [
                    {
                        "priority": "ALTA",
                        "action": "Contactar especialista en seguridad"
                    }
                ]
            }
            
            st.session_state.current_osint = fallback_result
            display_osint_results(fallback_result)

def display_osint_results(results):
    """Mostrar resultados del análisis OSINT"""
    
    st.markdown("### Resultados del Análisis")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_score = results.get('risk_score', 0)
        st.metric("Score de Riesgo", f"{risk_score:.2f}")
    
    with col2:
        risk_level = results.get('risk_level', 'N/A')
        st.metric("Nivel de Riesgo", risk_level)
    
    with col3:
        vuln_count = len(results.get('vulnerabilities', []))
        st.metric("Vulnerabilidades", vuln_count)
    
    # Vulnerabilidades
    if results.get('vulnerabilities'):
        st.markdown("### Vulnerabilidades Identificadas")
        for vuln in results['vulnerabilities']:
            severity_color = {
                'CRÍTICA': '#dc2626', 'ALTA': '#f97316', 
                'MEDIA': '#d97706', 'BAJA': '#059669'
            }.get(vuln.get('severity', 'MEDIA'), '#6b7280')
            
            st.markdown(f"""
            <div style="border-left: 4px solid {severity_color}; padding: 1rem; margin: 0.5rem 0; background: #f8fafc;">
                <strong>{vuln.get('type', 'Vulnerabilidad')}</strong> - {vuln.get('severity', 'MEDIA')}
                <br>{vuln.get('description', 'Sin descripción')}
            </div>
            """, unsafe_allow_html=True)
    
    # Vectores de ataque
    if results.get('attack_vectors'):
        st.markdown("### Vectores de Ataque")
        for vector in results['attack_vectors']:
            probability = vector.get('probability', 0)
            color = '#dc2626' if probability > 0.7 else '#f97316' if probability > 0.4 else '#059669'
            
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; padding: 1rem; margin: 0.5rem 0; background: #f8fafc;">
                <strong>{vector.get('vector', 'Vector')}</strong> - Probabilidad: {probability:.0%}
                <br>{vector.get('impact', 'Sin descripción')}
            </div>
            """, unsafe_allow_html=True)
    
    # Recomendaciones
    if results.get('recommendations'):
        st.markdown("### Recomendaciones")
        for rec in results['recommendations']:
            priority_color = {
                'ALTA': '#dc2626', 'MEDIA': '#f97316', 'BAJA': '#059669'
            }.get(rec.get('priority', 'MEDIA'), '#6b7280')
            
            st.markdown(f"""
            <div style="border-left: 4px solid {priority_color}; padding: 1rem; margin: 0.5rem 0; background: #f0fdf4;">
                <strong>Prioridad {rec.get('priority', 'MEDIA')}</strong>
                <br>{rec.get('action', 'Sin descripción')}
            </div>
            """, unsafe_allow_html=True)

def user_profiling():
    """Perfilado de usuario real"""
    
    st.markdown("### Perfilado Psicológico de Usuario")
    
    if 'anthropic_client' not in st.session_state:
        st.error("**Requiere conexión con Anthropic Claude para perfilado avanzado**")
        return
    
    with st.form("profile_form"):
        st.markdown("**Información del Usuario**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_name = st.text_input("Nombre del Usuario")
            department = st.selectbox("Departamento", [
                "Finanzas", "Tecnología", "Recursos Humanos", 
                "Ventas", "Marketing", "Operaciones", "Legal", "Ejecutivo"
            ])
            seniority = st.selectbox("Nivel de Responsabilidad", [
                "Junior", "Senior", "Manager", "Director", "C-Level"
            ])
        
        with col2:
            company_size = st.selectbox("Tamaño de Empresa", [
                "1-50", "51-200", "201-1000", "1000-5000", "5000+"
            ])
            industry = st.selectbox("Industria", [
                "Tecnología", "Finanzas", "Salud", "Educación", 
                "Retail", "Manufactura", "Consultoría", "Gobierno"
            ])
        
        # Información de comportamiento
        st.markdown("**Patrones de Comportamiento**")
        
        social_activity = st.slider("Actividad en Redes Sociales", 1, 10, 5)
        security_awareness = st.slider("Conciencia de Seguridad", 1, 10, 5)
        info_sharing = st.slider("Tendencia a Compartir Información", 1, 10, 5)
        
        work_patterns = st.multiselect("Patrones de Trabajo", [
            "Trabajo remoto frecuente", "Horarios extendidos", 
            "Acceso desde múltiples dispositivos", "Viajes de negocio",
            "Manejo de información sensible", "Contacto con clientes externos"
        ])
        
        additional_context = st.text_area(
            "Contexto Adicional",
            placeholder="Información adicional relevante para el análisis..."
        )
        
        if st.form_submit_button("Generar Perfil Psicológico"):
            if user_name and department:
                generate_psychological_profile(
                    user_name, department, seniority, company_size, industry,
                    social_activity, security_awareness, info_sharing,
                    work_patterns, additional_context
                )
            else:
                st.error("Complete los campos obligatorios")
    
    # Mostrar perfiles existentes
    if 'user_profiles' in st.session_state and st.session_state.user_profiles:
        st.markdown("---")
        st.markdown("### 👥 Perfiles Existentes")
        
        for i, profile in enumerate(st.session_state.user_profiles):
            with st.expander(f"👤 {profile['user_name']} ({profile['department']}) - {profile['timestamp']}"):
                display_profile_results(profile)
    
    # Mostrar último perfil si existe
    if 'current_profile' in st.session_state:
        st.markdown("---")
        st.markdown("### 🧠 Último Perfil Generado")
        display_profile_results(st.session_state.current_profile)

def generate_psychological_profile(user_name, department, seniority, company_size, 
                                 industry, social_activity, security_awareness, 
                                 info_sharing, work_patterns, additional_context):
    """Generar perfil psicológico real con Claude"""
    
    # Modo demo - usar datos predefinidos
    if st.session_state.get('demo_mode', False):
        with st.spinner("Generando perfil psicológico de ejemplo..."):
            time.sleep(2)  # Simular procesamiento
            
            # Generar perfil basado en inputs del usuario
            risk_score = 0.5 + (info_sharing * 0.05) + (social_activity * 0.03) - (security_awareness * 0.04)
            risk_score = max(0.2, min(0.9, risk_score))  # Mantener entre 0.2 y 0.9
            
            demo_profile = {
                "psychological_profile": {
                    "personality_traits": [
                        f"Profesional de {department}",
                        f"Nivel {seniority}" if seniority != "Junior" else "Orientado al aprendizaje",
                        "Sociable" if social_activity > 6 else "Reservado" if social_activity < 4 else "Equilibrado socialmente"
                    ],
                    "behavioral_patterns": [
                        "Responde rápido a solicitudes de autoridad" if department in ["Finanzas", "Legal"] else "Evalúa técnicamente las solicitudes",
                        "Comparte información cuando percibe legitimidad" if info_sharing > 6 else "Cauteloso con la información",
                        "Trabajo colaborativo" if "Contacto con clientes externos" in work_patterns else "Trabajo interno"
                    ],
                    "decision_making_style": f"Estilo típico de {department} - analítico" if department in ["Finanzas", "Legal", "Tecnología"] else "Orientado a resultados",
                    "stress_responses": [
                        "Busca soluciones rápidas bajo presión" if security_awareness < 5 else "Mantiene protocolos de seguridad",
                        "Puede omitir verificaciones en situaciones urgentes" if seniority in ["Junior", "Senior"] else "Delega verificaciones"
                    ]
                },
                "vulnerability_assessment": {
                    "risk_score": round(risk_score, 2),
                    "primary_vulnerabilities": [
                        {
                            "type": "Autoridad percibida",
                            "severity": "ALTA" if department in ["Finanzas", "Legal"] else "MEDIA",
                            "description": f"Como {seniority} en {department}, susceptible a figuras de autoridad del sector"
                        },
                        {
                            "type": "Presión temporal",
                            "severity": "ALTA" if security_awareness < 5 else "MEDIA",
                            "description": f"Nivel de conciencia de seguridad {security_awareness}/10 indica vulnerabilidad a tácticas de urgencia"
                        }
                    ],
                    "trigger_scenarios": [
                        f"Solicitudes urgentes relacionadas con {department}",
                        "Problemas técnicos que afectan productividad" if "Acceso desde múltiples dispositivos" in work_patterns else "Comunicaciones de supervisores",
                        "Auditorías o procesos de compliance" if department in ["Finanzas", "Legal"] else "Actualizaciones de sistemas"
                    ]
                },
                "attack_vectors": [
                    {
                        "technique": f"Phishing específico de {department}",
                        "effectiveness": round(0.6 + (info_sharing * 0.03), 2),
                        "approach": f"Emails que imitan comunicaciones típicas de {department}",
                        "psychological_basis": f"Familiaridad con procesos de {department}"
                    },
                    {
                        "technique": "Ingeniería social de urgencia",
                        "effectiveness": round(0.7 - (security_awareness * 0.05), 2),
                        "approach": "Crear sensación de crisis que requiere acción inmediata",
                        "psychological_basis": "Estrés reduce capacidad de análisis crítico"
                    }
                ],
                "training_recommendations": [
                    {
                        "priority": "ALTA",
                        "focus_area": f"Verificación específica para {department}",
                        "method": f"Simulacros adaptados a procesos de {department}"
                    },
                    {
                        "priority": "MEDIA" if security_awareness > 6 else "ALTA",
                        "focus_area": "Conciencia de seguridad general",
                        "method": "Entrenamiento regular en identificación de amenazas"
                    }
                ]
            }
            
            # Guardar perfil demo
            if 'user_profiles' not in st.session_state:
                st.session_state.user_profiles = []
            
            profile_data = {
                'user_name': user_name,
                'department': department,
                'analysis': demo_profile,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            st.session_state.user_profiles.append(profile_data)
            st.session_state.current_profile = profile_data
            
            st.success("✅ Perfil psicológico generado (Modo Demo)")
            
            # Mostrar resultados inmediatamente
            display_profile_results(profile_data)
            return
    
    with st.spinner("Generando perfil psicológico..."):
        
        prompt = f"""
        Eres un experto en psicología organizacional. Analiza el siguiente perfil de usuario y proporciona un análisis detallado de vulnerabilidades psicológicas.

        USUARIO A ANALIZAR:
        - Nombre: {user_name}
        - Departamento: {department}
        - Nivel: {seniority}
        - Empresa: {company_size} empleados en {industry}
        - Actividad social: {social_activity}/10
        - Conciencia seguridad: {security_awareness}/10
        - Compartir información: {info_sharing}/10
        - Patrones de trabajo: {', '.join(work_patterns) if work_patterns else 'No especificados'}
        - Contexto adicional: {additional_context}

        Responde EXCLUSIVAMENTE en formato JSON válido:

        {{
            "psychological_profile": {{
                "personality_traits": [
                    "Orientado a resultados",
                    "Confiado en tecnología",
                    "Sociable"
                ],
                "behavioral_patterns": [
                    "Responde rápido a solicitudes urgentes",
                    "Comparte información cuando percibe autoridad"
                ],
                "decision_making_style": "Toma decisiones rápidas bajo presión",
                "stress_responses": [
                    "Busca soluciones inmediatas",
                    "Puede pasar por alto verificaciones de seguridad"
                ]
            }},
            "vulnerability_assessment": {{
                "risk_score": 0.7,
                "primary_vulnerabilities": [
                    {{
                        "type": "Autoridad percibida",
                        "severity": "ALTA",
                        "description": "Tiende a obedecer figuras de autoridad sin verificación"
                    }},
                    {{
                        "type": "Presión temporal",
                        "severity": "MEDIA",
                        "description": "Vulnerable a tácticas que crean urgencia artificial"
                    }}
                ],
                "trigger_scenarios": [
                    "Solicitudes urgentes de superiores",
                    "Problemas técnicos que requieren acción inmediata"
                ]
            }},
            "attack_vectors": [
                {{
                    "technique": "Phishing de autoridad",
                    "effectiveness": 0.8,
                    "approach": "Emails que imitan comunicaciones de directivos",
                    "psychological_basis": "Respeto a jerarquía organizacional"
                }},
                {{
                    "technique": "Ingeniería social de urgencia",
                    "effectiveness": 0.65,
                    "approach": "Crear sensación de crisis que requiere acción inmediata",
                    "psychological_basis": "Estrés reduce capacidad de análisis crítico"
                }}
            ],
            "training_recommendations": [
                {{
                    "priority": "ALTA",
                    "focus_area": "Verificación de autoridad",
                    "method": "Simulacros de phishing con figuras de autoridad falsas"
                }},
                {{
                    "priority": "MEDIA",
                    "focus_area": "Manejo de presión temporal",
                    "method": "Entrenamiento en protocolos de verificación bajo presión"
                }}
            ]
        }}
        """
        
        try:
            response = st.session_state.anthropic_client.messages.create(
                model=st.session_state.get('claude_model', 'claude-3-5-haiku-20241022'),
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            
            # Debug: mostrar respuesta
            with st.expander("🔍 Debug: Respuesta de Claude"):
                st.text(content)
            
            # Parsing robusto de JSON
            profile_result = None
            
            # Método 1: JSON entre bloques de código
            if "```json" in content and "```" in content:
                try:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_content = content[json_start:json_end].strip()
                    profile_result = json.loads(json_content)
                except:
                    pass
            
            # Método 2: Buscar primer { hasta último }
            if not profile_result and "{" in content and "}" in content:
                try:
                    json_start = content.find("{")
                    json_end = content.rfind("}") + 1
                    json_content = content[json_start:json_end]
                    profile_result = json.loads(json_content)
                except:
                    pass
            
            # Método 3: Resultado de fallback
            if not profile_result:
                st.warning("⚠️ No se pudo parsear JSON. Generando perfil básico...")
                profile_result = {
                    "psychological_profile": {
                        "personality_traits": [f"Profesional de {department}", f"Nivel {seniority}"],
                        "behavioral_patterns": ["Patrones típicos del departamento"],
                        "decision_making_style": f"Estilo típico de {department}",
                        "stress_responses": ["Respuestas estándar al estrés"]
                    },
                    "vulnerability_assessment": {
                        "risk_score": 0.5,
                        "primary_vulnerabilities": [
                            {
                                "type": "Vulnerabilidades del departamento",
                                "severity": "MEDIA",
                                "description": f"Vulnerabilidades típicas de {department}"
                            }
                        ],
                        "trigger_scenarios": ["Escenarios típicos del rol"]
                    },
                    "attack_vectors": [
                        {
                            "technique": "Ataques dirigidos al rol",
                            "effectiveness": 0.5,
                            "approach": f"Técnicas específicas para {department}",
                            "psychological_basis": "Características del rol"
                        }
                    ],
                    "training_recommendations": [
                        {
                            "priority": "ALTA",
                            "focus_area": "Concienciación general",
                            "method": "Entrenamiento estándar de seguridad"
                        }
                    ]
                }
            
            # Guardar perfil
            if 'user_profiles' not in st.session_state:
                st.session_state.user_profiles = []
            
            profile_data = {
                'user_name': user_name,
                'department': department,
                'analysis': profile_result,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            st.session_state.user_profiles.append(profile_data)
            st.session_state.current_profile = profile_data
            
            st.success("✅ Perfil psicológico generado")
            
            # Mostrar resultados inmediatamente
            display_profile_results(profile_data)
            
        except Exception as e:
            st.error(f"❌ Error generando perfil: {str(e)}")
            
            # Perfil de fallback en caso de error total
            fallback_profile = {
                'user_name': user_name,
                'department': department,
                'analysis': {
                    "psychological_profile": {
                        "personality_traits": ["Análisis pendiente"],
                        "behavioral_patterns": ["Requiere análisis manual"],
                        "decision_making_style": "Por determinar",
                        "stress_responses": ["Análisis requerido"]
                    },
                    "vulnerability_assessment": {
                        "risk_score": 0.5,
                        "primary_vulnerabilities": [
                            {
                                "type": "Error de análisis",
                                "severity": "MEDIA",
                                "description": "No se pudo completar el análisis automático"
                            }
                        ],
                        "trigger_scenarios": ["Análisis manual requerido"]
                    },
                    "attack_vectors": [
                        {
                            "technique": "Análisis pendiente",
                            "effectiveness": 0.5,
                            "approach": "Evaluación manual requerida",
                            "psychological_basis": "Por determinar"
                        }
                    ],
                    "training_recommendations": [
                        {
                            "priority": "ALTA",
                            "focus_area": "Evaluación manual",
                            "method": "Contactar especialista"
                        }
                    ]
                },
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            st.session_state.current_profile = fallback_profile
            display_profile_results(fallback_profile)

def display_profile_results(profile_data):
    """Mostrar resultados del perfilado"""
    
    analysis = profile_data['analysis']
    
    st.markdown("### Resultados del Perfilado")
    
    # Score de riesgo
    risk_score = analysis.get('vulnerability_assessment', {}).get('risk_score', 0)
    risk_level = "CRÍTICO" if risk_score >= 0.8 else "ALTO" if risk_score >= 0.6 else "MEDIO" if risk_score >= 0.4 else "BAJO"
    
    st.markdown(f"""
    <div style="padding: 1.5rem; text-align: center; background: linear-gradient(135deg, #1e40af, #3b82f6); 
                color: white; border-radius: 8px; margin: 1rem 0;">
        <h3 style="margin: 0;">Score de Riesgo: {risk_score:.2f}</h3>
        <p style="margin: 0.5rem 0 0 0;">Nivel: {risk_level}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Perfil psicológico
    if 'psychological_profile' in analysis:
        profile = analysis['psychological_profile']
        
        st.markdown("### Perfil Psicológico")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Rasgos de Personalidad:**")
            for trait in profile.get('personality_traits', []):
                st.markdown(f"• {trait}")
        
        with col2:
            st.markdown("**Patrones de Comportamiento:**")
            for pattern in profile.get('behavioral_patterns', []):
                st.markdown(f"• {pattern}")
    
    # Vulnerabilidades
    if 'vulnerability_assessment' in analysis:
        vuln_data = analysis['vulnerability_assessment']
        
        st.markdown("### Vulnerabilidades Identificadas")
        for vuln in vuln_data.get('primary_vulnerabilities', []):
            severity_color = {
                'CRÍTICA': '#dc2626', 'ALTA': '#f97316', 
                'MEDIA': '#d97706', 'BAJA': '#059669'
            }.get(vuln.get('severity', 'MEDIA'), '#6b7280')
            
            st.markdown(f"""
            <div style="border-left: 4px solid {severity_color}; padding: 1rem; margin: 0.5rem 0; background: #fef2f2;">
                <strong>{vuln.get('type', 'Vulnerabilidad')}</strong> - {vuln.get('severity', 'MEDIA')}
                <br>{vuln.get('description', 'Sin descripción')}
            </div>
            """, unsafe_allow_html=True)
    
    # Vectores de ataque
    if 'attack_vectors' in analysis:
        st.markdown("### Vectores de Ataque Efectivos")
        for vector in analysis['attack_vectors']:
            effectiveness = vector.get('effectiveness', 0)
            color = '#dc2626' if effectiveness > 0.7 else '#f97316' if effectiveness > 0.4 else '#059669'
            
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; padding: 1rem; margin: 0.5rem 0; background: #f8fafc;">
                <strong>{vector.get('technique', 'Técnica')}</strong> - Efectividad: {effectiveness:.0%}
                <br><strong>Enfoque:</strong> {vector.get('approach', 'Sin descripción')}
                <br><strong>Base psicológica:</strong> {vector.get('psychological_basis', 'Sin descripción')}
            </div>
            """, unsafe_allow_html=True)

def content_generation():
    """Generación de contenido adaptativo real"""
    
    st.markdown("### Generación de Contenido Adaptativo")
    
    if 'anthropic_client' not in st.session_state:
        st.error("**Requiere conexión con Anthropic Claude para generación de contenido**")
        return
    
    # Verificar si hay perfiles disponibles
    if 'user_profiles' not in st.session_state or not st.session_state.user_profiles:
        st.warning("**Primero debe crear un perfil de usuario en la sección 'Perfilado de Usuario'**")
        return
    
    # Seleccionar perfil objetivo
    profile_options = [f"{p['user_name']} ({p['department']})" for p in st.session_state.user_profiles]
    selected_profile_idx = st.selectbox("Seleccionar Usuario Objetivo", range(len(profile_options)), 
                                       format_func=lambda x: profile_options[x])
    
    target_profile = st.session_state.user_profiles[selected_profile_idx]
    
    with st.form("content_form"):
        st.markdown("**Configuración del Contenido**")
        
        content_type = st.selectbox("Tipo de Contenido", [
            "Email de verificación", "SMS de alerta", 
            "Notificación de sistema", "Solicitud de documentos"
        ])
        
        scenario = st.selectbox("Escenario", [
            "Auditoría fiscal", "Actualización de seguridad",
            "Verificación de cuenta", "Proceso de compliance",
            "Renovación de certificados", "Actualización de políticas"
        ])
        
        urgency = st.selectbox("Nivel de Urgencia", [
            "Baja", "Media", "Alta", "Crítica"
        ])
        
        company_context = st.text_input("Empresa del Usuario", 
                                       value=st.session_state.get('current_osint', {}).get('company_name', 'Empresa Objetivo'))
        
        additional_context = st.text_area("Contexto Adicional", 
                                         placeholder="Información específica para personalizar el contenido...")
        
        if st.form_submit_button("Generar Contenido"):
            generate_adaptive_content(target_profile, content_type, scenario, 
                                    urgency, company_context, additional_context)
    
    # Mostrar contenido existente
    if 'generated_content' in st.session_state and st.session_state.generated_content:
        st.markdown("---")
        st.markdown("### 📧 Contenido Generado Anteriormente")
        
        for i, content in enumerate(st.session_state.generated_content[-3:]):  # Mostrar últimos 3
            with st.expander(f"📩 {content['content_type']} para {content['target_user']} - {content['timestamp']}"):
                display_generated_content(content)
    
    # Mostrar último contenido si existe
    if 'current_content' in st.session_state:
        st.markdown("---")
        st.markdown("### 🎯 Último Contenido Generado")
        display_generated_content(st.session_state.current_content)

def generate_adaptive_content(target_profile, content_type, scenario, 
                            urgency, company_context, additional_context):
    """Generar contenido adaptativo real con Claude"""
    
    # Modo demo - usar datos predefinidos
    if st.session_state.get('demo_mode', False):
        with st.spinner("Generando contenido adaptativo de ejemplo..."):
            time.sleep(2)  # Simular procesamiento
            
            # Extraer datos del perfil
            user_data = target_profile
            department = user_data['department']
            user_name = user_data['user_name']
            
            # Generar contenido basado en configuración
            urgency_phrases = {
                "Crítica": "URGENTE - ACCIÓN INMEDIATA REQUERIDA",
                "Alta": "IMPORTANTE - Respuesta necesaria hoy",
                "Media": "Solicitud importante",
                "Baja": "Información requerida"
            }
            
            scenario_content = {
                "Auditoría fiscal": {
                    "sender": f"auditoria@{company_context.lower().replace(' ', '')}.com",
                    "body": f"Estimado/a {user_name},\n\nSe ha programado una auditoría fiscal para {company_context}. Necesitamos verificar sus datos fiscales inmediatamente.\n\nComo responsable en {department}, debe proporcionar:\n- Documentos fiscales del último trimestre\n- Verificación de cuenta bancaria\n- Confirmación de datos personales\n\nPor favor, complete el formulario adjunto antes de las 17:00 hoy.\n\nSaludos,\nEquipo de Auditoría Externa"
                },
                "Actualización de seguridad": {
                    "sender": f"seguridad@{company_context.lower().replace(' ', '')}.com",
                    "body": f"Hola {user_name},\n\nHemos detectado actividad sospechosa en sistemas de {department}. Por seguridad, debe actualizar sus credenciales AHORA.\n\nPasos a seguir:\n1. Haga clic en el enlace de verificación\n2. Confirme su identidad\n3. Actualice su contraseña\n\nSi no completa este proceso en 2 horas, su cuenta será suspendida temporalmente.\n\nEquipo de Seguridad IT\n{company_context}"
                },
                "Verificación de cuenta": {
                    "sender": f"cuentas@{company_context.lower().replace(' ', '')}.com",
                    "body": f"Estimado/a {user_name},\n\nPor políticas de seguridad de {company_context}, necesitamos verificar su cuenta de {department}.\n\nInformación requerida:\n- Número de empleado\n- Último acceso al sistema\n- Confirmación de email corporativo\n\nEste proceso es obligatorio para todo el personal de {department}.\n\nDepartamento de Recursos Humanos"
                }
            }
            
            selected_scenario = scenario_content.get(scenario, scenario_content["Verificación de cuenta"])
            
            demo_content = {
                "content": {
                    "subject": f"{urgency_phrases[urgency]} - {scenario} para {department}",
                    "sender": selected_scenario["sender"],
                    "body": selected_scenario["body"],
                    "call_to_action": f"Completar {scenario.lower()} inmediatamente" if urgency in ["Crítica", "Alta"] else f"Procesar {scenario.lower()}"
                },
                "personalization_elements": [
                    f"Nombre específico del usuario: {user_name}",
                    f"Departamento específico: {department}",
                    f"Empresa específica: {company_context}",
                    f"Tono adaptado al nivel de {urgency.lower()} urgencia"
                ],
                "psychological_techniques": [
                    {
                        "technique": "Autoridad",
                        "application": f"Remitente que parece oficial de {company_context}"
                    },
                    {
                        "technique": "Urgencia" if urgency in ["Crítica", "Alta"] else "Legitimidad",
                        "application": f"Crear presión temporal apropiada para nivel {urgency.lower()}" if urgency in ["Crítica", "Alta"] else "Parecer proceso rutinario legítimo"
                    },
                    {
                        "technique": "Personalización",
                        "application": f"Dirigido específicamente a rol en {department}"
                    }
                ],
                "effectiveness_prediction": {
                    "score": 0.75 if urgency in ["Crítica", "Alta"] else 0.65,
                    "reasoning": f"Contenido personalizado para {user_name} de {department}, usando técnicas de {urgency.lower()} presión y autoridad aparente"
                }
            }
            
            # Guardar contenido demo
            if 'generated_content' not in st.session_state:
                st.session_state.generated_content = []
            
            content_data = {
                'target_user': user_data['user_name'],
                'content_type': content_type,
                'scenario': scenario,
                'content': demo_content,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            st.session_state.generated_content.append(content_data)
            st.session_state.current_content = content_data
            
            st.success("✅ Contenido adaptativo generado (Modo Demo)")
            
            # Mostrar contenido inmediatamente
            display_generated_content(content_data)
            return
    
    with st.spinner("Generando contenido adaptativo..."):
        
        # Extraer datos del perfil
        user_data = target_profile
        analysis = user_data['analysis']
        
        # Prompt simplificado para obtener JSON más confiable
        prompt = f"""
        Eres un experto en creación de contenido para pruebas de seguridad. Crea un email de phishing educativo personalizado.

        USUARIO OBJETIVO:
        - Nombre: {user_data['user_name']}
        - Departamento: {user_data['department']}
        
        CONFIGURACIÓN:
        - Tipo: {content_type}
        - Escenario: {scenario}
        - Urgencia: {urgency}
        - Empresa: {company_context}
        - Contexto: {additional_context}

        Responde EXCLUSIVAMENTE en formato JSON válido:

        {{
            "content": {{
                "subject": "URGENTE: Actualización de seguridad requerida - Acción inmediata",
                "sender": "seguridad@{company_context.lower().replace(' ', '')}.com",
                "body": "Estimado/a {user_data['user_name']},\\n\\nHemos detectado actividad sospechosa en su cuenta corporativa. Por seguridad, debe actualizar sus credenciales inmediatamente.\\n\\nPor favor, haga clic en el siguiente enlace para verificar su identidad: [LINK]\\n\\nEste proceso debe completarse en las próximas 2 horas para evitar la suspensión de su cuenta.\\n\\nGracias por su cooperación.\\n\\nEquipo de Seguridad IT",
                "call_to_action": "Hacer clic en enlace de verificación y proporcionar credenciales"
            }},
            "personalization_elements": [
                "Nombre específico del usuario",
                "Referencia al departamento de {user_data['department']}",
                "Tono apropiado para el nivel profesional"
            ],
            "psychological_techniques": [
                {{
                    "technique": "Autoridad",
                    "application": "Usar remitente que parece oficial del departamento IT"
                }},
                {{
                    "technique": "Urgencia",
                    "application": "Crear presión temporal con límite de 2 horas"
                }},
                {{
                    "technique": "Miedo",
                    "application": "Amenaza de suspensión de cuenta"
                }}
            ],
            "effectiveness_prediction": {{
                "score": 0.75,
                "reasoning": "Combina autoridad técnica con urgencia, dirigido específicamente a usuario de {user_data['department']}"
            }}
        }}
        """
        
        try:
            response = st.session_state.anthropic_client.messages.create(
                model=st.session_state.get('claude_model', 'claude-3-5-haiku-20241022'),
                max_tokens=3000,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            
            # Debug: mostrar respuesta
            with st.expander("🔍 Debug: Respuesta de Claude"):
                st.text(content)
            
            # Parsing robusto de JSON
            content_result = None
            
            # Método 1: JSON entre bloques de código
            if "```json" in content and "```" in content:
                try:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_content = content[json_start:json_end].strip()
                    content_result = json.loads(json_content)
                except Exception as e:
                    st.warning(f"Error parsing método 1: {e}")
            
            # Método 2: Buscar primer { hasta último }
            if not content_result and "{" in content and "}" in content:
                try:
                    json_start = content.find("{")
                    json_end = content.rfind("}") + 1
                    json_content = content[json_start:json_end]
                    content_result = json.loads(json_content)
                except Exception as e:
                    st.warning(f"Error parsing método 2: {e}")
            
            # Método 3: Resultado de fallback
            if not content_result:
                st.warning("⚠️ No se pudo parsear JSON. Generando contenido básico...")
                content_result = {
                    "content": {
                        "subject": f"{urgency.upper()}: {scenario} - {user_data['user_name']}",
                        "sender": f"admin@{company_context.lower().replace(' ', '')}.com",
                        "body": f"Estimado/a {user_data['user_name']},\n\nNecesitamos que complete una {scenario.lower()} de manera {urgency.lower()}.\n\nPor favor, responda a este email con la información solicitada.\n\nGracias,\nEquipo de Administración",
                        "call_to_action": "Responder con información solicitada"
                    },
                    "personalization_elements": [
                        f"Nombre específico: {user_data['user_name']}",
                        f"Departamento: {user_data['department']}",
                        f"Contexto: {scenario}"
                    ],
                    "psychological_techniques": [
                        {
                            "technique": "Personalización",
                            "application": "Uso del nombre real del usuario"
                        },
                        {
                            "technique": "Autoridad",
                            "application": "Remitente que parece oficial"
                        }
                    ],
                    "effectiveness_prediction": {
                        "score": 0.6,
                        "reasoning": f"Contenido básico personalizado para {user_data['user_name']} de {user_data['department']}"
                    }
                }
            
            # Guardar contenido generado
            if 'generated_content' not in st.session_state:
                st.session_state.generated_content = []
            
            content_data = {
                'target_user': user_data['user_name'],
                'content_type': content_type,
                'scenario': scenario,
                'content': content_result,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            st.session_state.generated_content.append(content_data)
            st.session_state.current_content = content_data
            
            st.success("✅ Contenido adaptativo generado")
            
            # Mostrar contenido inmediatamente
            display_generated_content(content_data)
            
        except Exception as e:
            st.error(f"❌ Error generando contenido: {str(e)}")
            
            # Contenido de fallback en caso de error total
            fallback_content = {
                'target_user': user_data['user_name'],
                'content_type': content_type,
                'scenario': scenario,
                'content': {
                    "content": {
                        "subject": f"Error: Generación fallida para {user_data['user_name']}",
                        "sender": "sistema@empresa.com",
                        "body": "No se pudo generar contenido automáticamente. Se requiere generación manual.",
                        "call_to_action": "Contactar administrador"
                    },
                    "personalization_elements": ["Error en generación"],
                    "psychological_techniques": [{"technique": "Error", "application": "No aplicable"}],
                    "effectiveness_prediction": {"score": 0.0, "reasoning": "Error en generación"}
                },
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            st.session_state.current_content = fallback_content
            display_generated_content(fallback_content)

def display_generated_content(content_data):
    """Mostrar contenido generado"""
    
    content = content_data['content']['content']
    analysis = content_data['content']
    
    st.markdown("### Contenido Generado")
    
    # Predicción de efectividad
    effectiveness = analysis.get('effectiveness_prediction', {})
    score = effectiveness.get('score', 0)
    
    st.markdown(f"""
    <div style="padding: 1rem; background: linear-gradient(135deg, #059669, #10b981); 
                color: white; border-radius: 8px; margin: 1rem 0; text-align: center;">
        <h4 style="margin: 0;">Efectividad Predicha: {score:.0%}</h4>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{effectiveness.get('reasoning', 'Análisis basado en perfil psicológico')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Contenido del email/mensaje
    st.markdown("### Contenido Personalizado")
    
    # Header del contenido
    st.markdown(f"""
    <div class="email-header">
        <strong>De:</strong> {content.get('sender', 'N/A')}<br>
        <strong>Para:</strong> {content_data['target_user']}<br>
        <strong>Asunto:</strong> {content.get('subject', 'N/A')}<br>
        <strong>Fecha:</strong> {datetime.now().strftime('%d %b %Y, %H:%M')}
    </div>
    """, unsafe_allow_html=True)
    
    # Cuerpo del mensaje
    st.markdown("**Contenido:**")
    body_text = content.get('body', 'Sin contenido')
    # Convertir saltos de línea
    if '\\n' in body_text:
        body_text = body_text.replace('\\n', '<br>')
    else:
        body_text = body_text.replace('\n', '<br>')
    
    st.markdown(f"""
    <div class="email-container">
        {body_text}
    </div>
    """, unsafe_allow_html=True)
    
    # Call to action
    if content.get('call_to_action'):
        st.markdown(f"""
        <div style="background: #1e40af; color: white; padding: 1rem; border-radius: 6px; text-align: center; margin: 1rem 0;">
            <strong>Acción Solicitada:</strong> {content['call_to_action']}
        </div>
        """, unsafe_allow_html=True)
    
    # Análisis de personalización
    st.markdown("### Análisis de Personalización")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Elementos de Personalización:**")
        for element in analysis.get('personalization_elements', []):
            st.markdown(f"• {element}")
    
    with col2:
        st.markdown("**Técnicas Psicológicas:**")
        for technique in analysis.get('psychological_techniques', []):
            technique_name = technique.get('technique', 'N/A') if isinstance(technique, dict) else str(technique)
            application = technique.get('application', 'N/A') if isinstance(technique, dict) else 'Aplicación estándar'
            st.markdown(f"• **{technique_name}**: {application}")
    
    # Botones de acción
    st.markdown("### Acciones")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Copiar Contenido"):
            # Crear texto para copiar
            copy_text = f"""
Asunto: {content.get('subject', 'N/A')}
De: {content.get('sender', 'N/A')}
Para: {content_data['target_user']}

{content.get('body', 'Sin contenido').replace('\\n', '\n')}

---
Efectividad Predicha: {score:.0%}
Generado: {content_data['timestamp']}
            """.strip()
            
            # En un entorno real, aquí podrías usar pyperclip o similar
            st.text_area("Contenido para copiar:", copy_text, height=150)
    
    with col2:
        if st.button("🔄 Regenerar"):
            if 'current_profile' in st.session_state and st.session_state.current_profile:
                # Buscar el perfil original
                target_profile = None
                for profile in st.session_state.get('user_profiles', []):
                    if profile['user_name'] == content_data['target_user']:
                        target_profile = profile
                        break
                
                if target_profile:
                    st.info("Regenerando contenido...")
                    st.rerun()
                else:
                    st.error("No se encontró el perfil del usuario original")
            else:
                st.error("No hay perfil disponible para regenerar")
    
    with col3:
        if st.button("💾 Exportar"):
            # Crear datos para exportar
            export_data = {
                "contenido": content_data,
                "analisis": analysis,
                "timestamp": content_data['timestamp']
            }
            
            st.download_button(
                label="Descargar JSON",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name=f"contenido_{content_data['target_user']}_{content_data['timestamp'].replace(':', '-')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
