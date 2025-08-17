import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime, timedelta

def create_osint_interface():
    st.markdown("###  Módulo de Inteligencia OSINT")
    st.info("**Open Source Intelligence** - Recopilación y análisis de información públicamente disponible")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        create_osint_input_form()
    
    with col2:
        create_osint_results_panel()

def create_osint_input_form():
    st.markdown("####  Configuración del Análisis OSINT")
    
    with st.form("osint_form"):
        # Datos básicos de la empresa
        st.markdown("** Información Básica de la Empresa**")
        company_name = st.text_input("Nombre de la Empresa", "TechCorp Solutions")
        domain = st.text_input("Dominio Principal", "techcorp.com")
        industry = st.selectbox("Industria", [
            "Tecnología", "Finanzas", "Salud", "Educación", 
            "Retail", "Manufactura", "Consultoría", "Otro"
        ])
        
        col1, col2 = st.columns(2)
        with col1:
            company_size = st.selectbox("Tamaño de Empresa", [
                "1-50 empleados", "51-200 empleados", "201-1000 empleados", 
                "1001-5000 empleados", "5000+ empleados"
            ])
        with col2:
            location = st.text_input("Ubicación Principal", "Madrid, España")
        
        st.markdown("** Fuentes de Información**")
        
        # Fuentes de información con descripciones
        search_sources = {}
        col1, col2 = st.columns(2)
        
        with col1:
            search_sources['linkedin'] = st.checkbox(" LinkedIn", True, help="Perfiles de empleados y estructura organizacional")
            search_sources['website'] = st.checkbox(" Sitio Web Corporativo", True, help="Información pública y estructura de la empresa")
            search_sources['twitter'] = st.checkbox(" Twitter/X", help="Comunicaciones públicas y empleados activos")
            search_sources['facebook'] = st.checkbox(" Facebook", help="Páginas corporativas y empleados")
        
        with col2:
            search_sources['github'] = st.checkbox(" GitHub", help="Repositorios públicos y desarrolladores")
            search_sources['dns'] = st.checkbox(" Registros DNS", help="Subdominios y infraestructura técnica")
            search_sources['news'] = st.checkbox(" Noticias y Prensa", help="Menciones en medios y comunicados")
            search_sources['jobs'] = st.checkbox(" Ofertas de Trabajo", help="Posiciones abiertas y tecnologías utilizadas")
        
        st.markdown("**⚙️ Configuraciones Avanzadas**")
        
        col1, col2 = st.columns(2)
        with col1:
            depth_level = st.select_slider(
                "Profundidad del Análisis",
                options=["Básico", "Intermedio", "Avanzado", "Exhaustivo"],
                value="Intermedio"
            )
        with col2:
            time_range = st.selectbox(
                "Rango Temporal",
                ["Último mes", "Últimos 3 meses", "Último año", "Sin límite"]
            )
        
        # Filtros específicos
        st.markdown("** Filtros Específicos**")
        target_roles = st.multiselect(
            "Roles de Interés",
            ["C-Level", "Directores", "Gerentes", "IT/Seguridad", "Finanzas", "RRHH", "Ventas"],
            default=["C-Level", "IT/Seguridad", "Finanzas"]
        )
        
        # Botón de análisis
        submit_button = st.form_submit_button(" Iniciar Análisis OSINT", type="primary")
        
        if submit_button:
            run_osint_analysis(company_name, domain, search_sources, depth_level, target_roles)

def run_osint_analysis(company_name, domain, sources, depth, roles):
    """Ejecutar análisis OSINT simulado"""
    
    # Crear contenedor para el progreso
    progress_container = st.container()
    results_container = st.container()
    
    with progress_container:
        st.markdown("####  Análisis en Progreso...")
        
        # Barra de progreso principal
        main_progress = st.progress(0)
        status_text = st.empty()
        
        # Contenedor para sub-procesos
        sub_progress_container = st.container()
        
        # Simular análisis paso a paso
        total_steps = len([k for k, v in sources.items() if v]) * 2
        current_step = 0
        
        # Resultados acumulativos
        total_employees = 0
        total_emails = 0
        total_profiles = 0
        total_tech = 0
        
        for source, enabled in sources.items():
            if enabled:
                source_names = {
                    'linkedin': 'LinkedIn',
                    'website': 'Sitio Web',
                    'twitter': 'Twitter/X',
                    'facebook': 'Facebook',
                    'github': 'GitHub',
                    'dns': 'DNS/Subdominios',
                    'news': 'Noticias',
                    'jobs': 'Ofertas de Trabajo'
                }
                
                with sub_progress_container:
                    st.write(f" Analizando {source_names[source]}...")
                    sub_progress = st.progress(0)
                    
                    # Simular sub-pasos
                    for i in range(101):
                        time.sleep(0.01)  # Simular procesamiento
                        sub_progress.progress(i)
                        if i % 25 == 0:
                            status_text.text(f"Procesando {source_names[source]}: {i}%")
                    
                    # Simular resultados específicos por fuente
                    if source == 'linkedin':
                        employees_found = np.random.randint(45, 85)
                        total_employees += employees_found
                        st.success(f" {employees_found} perfiles de empleados encontrados")
                        
                    elif source == 'website':
                        emails_found = np.random.randint(8, 20)
                        total_emails += emails_found
                        st.success(f" {emails_found} direcciones de email extraídas")
                        
                    elif source == 'github':
                        repos_found = np.random.randint(12, 30)
                        total_tech += repos_found
                        st.success(f" {repos_found} repositorios públicos identificados")
                        
                    elif source == 'dns':
                        subdomains_found = np.random.randint(15, 45)
                        st.success(f" {subdomains_found} subdominios descubiertos")
                
                current_step += 1
                main_progress.progress(current_step / total_steps)
        
        # Análisis final
        status_text.text(" Procesando resultados con IA...")
        time.sleep(2)
        
        main_progress.progress(1.0)
        status_text.text(" Análisis completado exitosamente!")
        
        # Almacenar resultados en session state
        st.session_state.osint_results = {
            'company_name': company_name,
            'total_employees': total_employees,
            'total_emails': total_emails,
            'total_profiles': total_profiles + total_employees,
            'total_tech': total_tech,
            'analysis_time': datetime.now(),
            'depth': depth,
            'sources_used': [k for k, v in sources.items() if v]
        }
        
        st.success(" Análisis OSINT completado. Revisa los resultados en el panel derecho.")
        
        # Auto-refresh para mostrar resultados
        time.sleep(1)
        st.rerun()

def create_osint_results_panel():
    st.markdown("####  Resultados del Análisis")
    
    if 'osint_results' not in st.session_state:
        st.info(" Configura y ejecuta un análisis OSINT para ver los resultados aquí.")
        
        # Mostrar resultados de ejemplo
        st.markdown("**📝 Ejemplo de Resultados:**")
        example_metrics = {
            "Empleados Identificados": 67,
            "Perfiles de LinkedIn": 45,
            "Emails Encontrados": 23,
            "Cuentas de Twitter": 12,
            "Repositorios GitHub": 18,
            "Subdominios": 31
        }
        
        for metric, value in example_metrics.items():
            st.metric(metric, value)
        
        return
    
    # Mostrar resultados reales
    results = st.session_state.osint_results
    
    # Métricas principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(" Empleados", results['total_employees'], "↑ En tiempo real")
        st.metric(" Emails", results['total_emails'], "↑ Validados")
    
    with col2:
        st.metric(" Perfiles", results['total_profiles'], "↑ Verificados")
        st.metric(" Repositorios", results['total_tech'], "↑ Analizados")
    
    # Información de análisis
    st.markdown("**ℹ Información del Análisis**")
    st.write(f"**Empresa:** {results['company_name']}")
    st.write(f"**Profundidad:** {results['depth']}")
    st.write(f"**Fuentes:** {len(results['sources_used'])}")
    st.write(f"**Completado:** {results['analysis_time'].strftime('%H:%M:%S')}")
    
    # Distribución por departamento (simulada)
    st.markdown("####  Distribución por Departamento")
    dept_data = generate_department_distribution(results['total_employees'])
    
    fig = px.pie(
        values=list(dept_data.values()),
        names=list(dept_data.keys()),
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Línea de tiempo de actividad
    st.markdown("####  Actividad en Redes Sociales")
    activity_data = generate_activity_timeline()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=activity_data['dates'],
        y=activity_data['posts'],
        mode='lines+markers',
        name='Posts/Día',
        line=dict(color='#3b82f6', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        height=250,
        xaxis_title="Fecha",
        yaxis_title="Posts",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Botones de acción
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" Exportar Resultados", key="export_osint"):
            st.success(" Resultados exportados a Excel")
    
    with col2:
        if st.button(" Nuevo Análisis", key="new_osint"):
            del st.session_state.osint_results
            st.rerun()

def generate_department_distribution(total_employees):
    """Generar distribución realista por departamentos"""
    departments = {
        'Tecnología': int(total_employees * 0.35),
        'Ventas': int(total_employees * 0.20),
        'Marketing': int(total_employees * 0.15),
        'Operaciones': int(total_employees * 0.12),
        'Finanzas': int(total_employees * 0.08),
        'RRHH': int(total_employees * 0.06),
        'Legal': int(total_employees * 0.04)
    }
    
    # Ajustar para que sume el total
    current_sum = sum(departments.values())
    if current_sum != total_employees:
        departments['Tecnología'] += total_employees - current_sum
    
    return departments

def generate_activity_timeline():
    """Generar timeline de actividad en redes sociales"""
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    posts = np.random.poisson(3, len(dates))  # Distribución de Poisson para posts
    
    return {
        'dates': dates,
        'posts': posts
    }
