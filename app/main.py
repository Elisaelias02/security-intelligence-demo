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
                            """)
                            return
                else:
                    st.error(f"❌ Error de conexión: {error_msg}")
                    st.markdown("""
                    **Posibles soluciones:**
                    1. Verificar que la API key sea correcta (debe empezar con 'sk-ant-')
                    2. Verificar que tenga créditos disponibles
                    3. Verificar conexión a internet
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
        
        if 'anthropic_client' in st.session_state:
            st.markdown("""
            ✅ **Análisis OSINT automatizado**  
            ✅ **Perfilado psicológico avanzado**  
            ✅ **Generación de contenido adaptativo**  
            ✅ **Evaluación de vectores de ataque**  
            ✅ **Análisis contextual profundo**
            """)
        else:
            st.markdown("""
            ❌ Análisis OSINT automatizado  
            ❌ Perfilado psicológico avanzado  
            ❌ Generación de contenido adaptativo  
            ❌ Evaluación de vectores de ataque  
            ❌ Análisis contextual profundo
            """)

def show_dashboard():
    """Panel principal del sistema"""
    
    if 'anthropic_client' not in st.session_state:
        st.warning("**Configure la API de Anthropic para acceder a todas las funcionalidades**")
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
        
        **Importante**: Este sistema está optimizado para Claude 3.5 Sonnet.
        Con modelos menores, la calidad del análisis será menor.
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
        st.metric("Precisión del Sistema", "AI-Powered")
    
    # Historial de análisis
    if 'completed_analyses' in st.session_state:
        st.markdown("### Análisis Recientes")
        for analysis in st.session_state.completed_analyses[-5:]:
            with st.expander(f"{analysis['type']} - {analysis['timestamp']}"):
                st.write(analysis['summary'])

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

def run_real_osint_analysis(company_name, domain, industry, additional_info):
    """Ejecutar análisis OSINT real con Claude"""
    
    with st.spinner("Ejecutando análisis OSINT..."):
        
        # Prompt profesional para Claude
        prompt = f"""
        Actúa como un experto analista de ciberseguridad realizando un análisis OSINT profesional.

        OBJETIVO DE ANÁLISIS:
        - Empresa: {company_name}
        - Dominio: {domain}  
        - Industria: {industry}
        - Info adicional: {additional_info}

        REQUERIMIENTOS:
        1. Analiza vectores de ataque potenciales específicos para esta industria
        2. Identifica vulnerabilidades comunes en empresas similares
        3. Evalúa superficie de ataque basada en la información proporcionada
        4. Proporciona recomendaciones específicas de mitigación
        5. Calcula un score de riesgo justificado

        FORMATO DE RESPUESTA (JSON):
        {{
            "risk_score": 0.XX,
            "risk_level": "BAJO/MEDIO/ALTO/CRÍTICO",
            "vulnerabilities": [
                {{"type": "tipo", "severity": "nivel", "description": "descripción detallada"}}
            ],
            "attack_vectors": [
                {{"vector": "nombre", "probability": 0.XX, "impact": "descripción"}}
            ],
            "industry_specific_risks": ["riesgo 1", "riesgo 2"],
            "recommendations": [
                {{"priority": "ALTA/MEDIA/BAJA", "action": "acción específica"}}
            ],
            "technical_findings": {{
                "exposed_services": ["servicio1", "servicio2"],
                "common_weaknesses": ["debilidad1", "debilidad2"]
            }}
        }}

        IMPORTANTE: Sé específico y profesional. Basa el análisis en patrones reales de la industria {industry}.
        """
        
        try:
            response = st.session_state.anthropic_client.messages.create(
                model=st.session_state.get('claude_model', 'claude-3-5-haiku-20241022'),
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Procesar respuesta
            content = response.content[0].text
            
            # Extraer JSON de la respuesta
            if "```json" in content:
                json_content = content.split("```json")[1].split("```")[0]
            elif "{" in content:
                json_content = content[content.find("{"):content.rfind("}")+1]
            else:
                raise ValueError("No se encontró JSON válido en la respuesta")
            
            analysis_result = json.loads(json_content)
            
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
            st.rerun()
            
        except Exception as e:
            st.error(f"Error en análisis: {str(e)}")

    # Mostrar resultados si existen
    if 'current_osint' in st.session_state:
        display_osint_results(st.session_state.current_osint)

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

def generate_psychological_profile(user_name, department, seniority, company_size, 
                                 industry, social_activity, security_awareness, 
                                 info_sharing, work_patterns, additional_context):
    """Generar perfil psicológico real con Claude"""
    
    with st.spinner("Generando perfil psicológico..."):
        
        prompt = f"""
        Actúa como un experto en psicología organizacional y análisis de comportamiento para ciberseguridad.

        PERFIL A ANALIZAR:
        - Nombre: {user_name}
        - Departamento: {department}
        - Nivel: {seniority}
        - Empresa: {company_size} empleados, industria {industry}
        - Actividad social: {social_activity}/10
        - Conciencia seguridad: {security_awareness}/10
        - Compartir información: {info_sharing}/10
        - Patrones: {', '.join(work_patterns)}
        - Contexto: {additional_context}

        ANÁLISIS REQUERIDO:
        1. Perfil psicológico detallado basado en los datos
        2. Vulnerabilidades específicas de ingeniería social
        3. Vectores de ataque más efectivos para este perfil
        4. Técnicas de manipulación psicológica aplicables
        5. Recomendaciones de entrenamiento específicas

        FORMATO JSON:
        {{
            "psychological_profile": {{
                "personality_traits": ["rasgo1", "rasgo2"],
                "behavioral_patterns": ["patrón1", "patrón2"],
                "decision_making_style": "descripción",
                "stress_responses": ["respuesta1", "respuesta2"]
            }},
            "vulnerability_assessment": {{
                "risk_score": 0.XX,
                "primary_vulnerabilities": [
                    {{"type": "tipo", "severity": "nivel", "description": "descripción"}}
                ],
                "trigger_scenarios": ["escenario1", "escenario2"]
            }},
            "attack_vectors": [
                {{
                    "technique": "técnica",
                    "effectiveness": 0.XX,
                    "approach": "descripción del enfoque",
                    "psychological_basis": "base psicológica"
                }}
            ],
            "training_recommendations": [
                {{"priority": "ALTA/MEDIA/BAJA", "focus_area": "área", "method": "método"}}
            ]
        }}

        IMPORTANTE: Basa el análisis en principios psicológicos reales. Sé específico para el departamento {department} y nivel {seniority}.
        """
        
        try:
            response = st.session_state.anthropic_client.messages.create(
                model=st.session_state.get('claude_model', 'claude-3-5-haiku-20241022'),
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            
            # Extraer JSON
            if "```json" in content:
                json_content = content.split("```json")[1].split("```")[0]
            elif "{" in content:
                json_content = content[content.find("{"):content.rfind("}")+1]
            else:
                raise ValueError("No se encontró JSON válido")
            
            profile_result = json.loads(json_content)
            
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
            st.rerun()
            
        except Exception as e:
            st.error(f"Error generando perfil: {str(e)}")

    # Mostrar resultados si existen
    if 'current_profile' in st.session_state:
        display_profile_results(st.session_state.current_profile)

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

def generate_adaptive_content(target_profile, content_type, scenario, 
                            urgency, company_context, additional_context):
    """Generar contenido adaptativo real con Claude"""
    
    with st.spinner("Generando contenido adaptativo..."):
        
        # Extraer datos del perfil
        user_data = target_profile
        analysis = user_data['analysis']
        
        prompt = f"""
        Actúa como un experto en ingeniería social creando contenido ALTAMENTE PERSONALIZADO para análisis de vulnerabilidades.

        PERFIL DEL USUARIO OBJETIVO:
        - Nombre: {user_data['user_name']}
        - Departamento: {user_data['department']}
        - Análisis psicológico: {json.dumps(analysis['psychological_profile'], indent=2)}
        - Vulnerabilidades: {json.dumps(analysis['vulnerability_assessment'], indent=2)}
        - Vectores efectivos: {json.dumps(analysis['attack_vectors'][:2], indent=2)}

        REQUERIMIENTOS DEL CONTENIDO:
        - Tipo: {content_type}
        - Escenario: {scenario}
        - Urgencia: {urgency}
        - Empresa: {company_context}
        - Contexto: {additional_context}

        INSTRUCCIONES CRÍTICAS:
        1. PERSONALIZA completamente basándote en el perfil psicológico
        2. Usa las vulnerabilidades identificadas específicamente
        3. Aplica los vectores de ataque más efectivos para este usuario
        4. El contenido debe parecer 100% legítimo y profesional
        5. Adapta el tono y estilo al departamento y nivel del usuario
        6. Incluye detalles específicos que solo alguien de su posición conocería

        FORMATO JSON:
        {{
            "content": {{
                "subject": "asunto específico y personalizado",
                "sender": "remitente creíble para el escenario",
                "body": "contenido completo adaptado al perfil",
                "call_to_action": "acción específica a realizar"
            }},
            "personalization_elements": [
                "elemento 1 del perfil usado",
                "elemento 2 del perfil usado"
            ],
            "psychological_techniques": [
                {{"technique": "técnica", "application": "cómo se aplicó"}}
            ],
            "effectiveness_prediction": {{
                "score": 0.XX,
                "reasoning": "por qué será efectivo con este usuario específico"
            }}
        }}

        IMPORTANTE: Este contenido debe estar ESPECÍFICAMENTE diseñado para {user_data['user_name']} en {user_data['department']}. 
        No uses plantillas genéricas. Cada palabra debe estar justificada por el análisis psicológico.
        """
        
        try:
            response = st.session_state.anthropic_client.messages.create(
                model=st.session_state.get('claude_model', 'claude-3-5-haiku-20241022'),
                max_tokens=3000,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            
            # Extraer JSON
            if "```json" in content:
                json_content = content.split("```json")[1].split("```")[0]
            elif "{" in content:
                json_content = content[content.find("{"):content.rfind("}")+1]
            else:
                raise ValueError("No se encontró JSON válido")
            
            content_result = json.loads(json_content)
            
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
            st.rerun()
            
        except Exception as e:
            st.error(f"Error generando contenido: {str(e)}")

    # Mostrar contenido si existe
    if 'current_content' in st.session_state:
        display_generated_content(st.session_state.current_content)

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
    st.markdown(f"""
    <div class="email-container">
        {content.get('body', 'Sin contenido').replace(chr(10), '<br>')}
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
            st.markdown(f"• **{technique.get('technique', 'N/A')}**: {technique.get('application', 'N/A')}")

if __name__ == "__main__":
    main()
