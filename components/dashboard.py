import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

def create_executive_dashboard():
    st.markdown("###  Dashboard Ejecutivo de Seguridad")
    
    # Métricas principales en tarjetas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card risk-critical">
            <h3>87</h3>
            <p>Vulnerabilidades Críticas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card risk-high">
            <h3>234</h3>
            <p>Empleados Alto Riesgo</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card risk-low">
            <h3>92%</h3>
            <p>Cobertura Análisis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>15min</h3>
            <p>Tiempo Análisis</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de riesgos
        create_risk_distribution_chart()
    
    with col2:
        # Timeline de vulnerabilidades
        create_vulnerability_timeline()
    
    # Tabla de empleados de alto riesgo
    st.markdown("###  Empleados de Mayor Riesgo")
    create_high_risk_employees_table()
    
    # Mapa de calor de departamentos
    st.markdown("###  Mapa de Riesgo por Departamento")
    create_department_risk_heatmap()

def create_risk_distribution_chart():
    risk_data = pd.DataFrame({
        'Nivel': ['Crítico', 'Alto', 'Medio', 'Bajo'],
        'Cantidad': [87, 234, 456, 123],
        'Color': ['#ef4444', '#f59e0b', '#3b82f6', '#10b981']
    })
    
    fig = px.pie(
        risk_data,
        values='Cantidad',
        names='Nivel',
        color='Nivel',
        color_discrete_map={
            'Crítico': '#ef4444',
            'Alto': '#f59e0b', 
            'Medio': '#3b82f6',
            'Bajo': '#10b981'
        },
        title="Distribución de Niveles de Riesgo"
    )
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_vulnerability_timeline():
    # Generar datos de timeline
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    base_vulnerabilities = [45, 52, 48, 61, 58, 67, 74, 69, 73, 81, 87, 92]
    
    # Agregar ruido realista
    vulnerabilities = [v + np.random.randint(-5, 8) for v in base_vulnerabilities]
    
    fig = go.Figure()
    
    # Línea principal
    fig.add_trace(go.Scatter(
        x=dates,
        y=vulnerabilities,
        mode='lines+markers',
        name='Vulnerabilidades Detectadas',
        line=dict(color='#ef4444', width=3),
        marker=dict(size=8, color='#ef4444', symbol='circle'),
        hovertemplate='<b>%{x|%B %Y}</b><br>Vulnerabilidades: %{y}<extra></extra>'
    ))
    
    # Línea de tendencia
    z = np.polyfit(range(len(vulnerabilities)), vulnerabilities, 1)
    p = np.poly1d(z)
    trend_line = [p(i) for i in range(len(vulnerabilities))]
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=trend_line,
        mode='lines',
        name='Tendencia',
        line=dict(color='#f59e0b', width=2, dash='dash'),
        hovertemplate='<b>Tendencia</b><br>%{x|%B %Y}: %{y:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Evolución de Vulnerabilidades en el Tiempo",
        xaxis_title="Período",
        yaxis_title="Número de Vulnerabilidades",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_high_risk_employees_table():
    # Datos realistas de empleados de alto riesgo
    high_risk_data = {
        'Empleado': ['María González', 'Carlos Rodríguez', 'Ana Martínez', 'Luis Hernández', 'Carmen López'],
        'Cargo': ['CFO', 'Director IT', 'Gerente RRHH', 'Coord. Operaciones', 'Analista Senior'],
        'Departamento': ['Finanzas', 'Tecnología', 'Recursos Humanos', 'Operaciones', 'Finanzas'],
        'Score Riesgo': [0.95, 0.87, 0.82, 0.79, 0.74],
        'Vulnerabilidades': [
            'Oversharing en LinkedIn, acceso a cuentas bancarias',
            'Privilegios admin, info técnica en GitHub',
            'Datos personales empleados, redes sociales activas',
            'Contactos proveedores, horarios predecibles',
            'Acceso sistemas financieros, información familiar pública'
        ],
        'Última Actividad': ['2 horas', '1 día', '3 días', '1 semana', '2 días']
    }
    
    df = pd.DataFrame(high_risk_data)
    
    # Aplicar formato condicional
    def format_risk_score(val):
        if val >= 0.9:
            return f'🔴 {val:.2f}'
        elif val >= 0.8:
            return f'🟡 {val:.2f}'
        elif val >= 0.7:
            return f'🟠 {val:.2f}'
        else:
            return f'🟢 {val:.2f}'
    
    # Crear una copia para mostrar con formato
    display_df = df.copy()
    display_df['Score Riesgo'] = display_df['Score Riesgo'].apply(format_risk_score)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=200,
        hide_index=True
    )
    
    # Botón para generar reporte detallado
    if st.button(" Generar Reporte Detallado", key="risk_report"):
        with st.spinner("Generando reporte..."):
            time.sleep(2)
            st.success(" Reporte generado y enviado por email")
            st.download_button(
                label="⬇ Descargar Reporte PDF",
                data=generate_mock_pdf_report(),
                file_name=f"reporte_riesgo_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
def create_department_risk_heatmap():
   # Datos de departamentos y riesgo
   departments = ['Finanzas', 'IT', 'RRHH', 'Ventas', 'Marketing', 'Operaciones', 'Legal', 'Ejecutivos']
   risk_categories = ['Phishing', 'Vishing', 'Pretexting', 'Baiting', 'Tailgating']
   
   # Generar matriz de riesgo realista
   np.random.seed(42)  # Para resultados consistentes
   risk_matrix = np.random.rand(len(departments), len(risk_categories))
   
   # Ajustar algunos valores para que sean más realistas
   risk_adjustments = {
       'Finanzas': {'Phishing': 0.9, 'Pretexting': 0.85},
       'IT': {'Baiting': 0.8, 'Tailgating': 0.7},
       'Ejecutivos': {'Vishing': 0.95, 'Pretexting': 0.9},
       'RRHH': {'Phishing': 0.8, 'Pretexting': 0.75}
   }
   
   for i, dept in enumerate(departments):
       for j, category in enumerate(risk_categories):
           if dept in risk_adjustments and category in risk_adjustments[dept]:
               risk_matrix[i][j] = risk_adjustments[dept][category]
   
   fig = go.Figure(data=go.Heatmap(
       z=risk_matrix,
       x=risk_categories,
       y=departments,
       colorscale='RdYlBu_r',
       colorbar=dict(title="Nivel de Riesgo"),
       hoverimpl='closest',
       hovertemplate='<b>%{y}</b><br>%{x}: %{z:.2f}<extra></extra>'
   ))
   
   fig.update_layout(
       title="Mapa de Calor: Riesgo por Departamento y Tipo de Ataque",
       height=400,
       xaxis_title="Tipo de Ataque",
       yaxis_title="Departamento"
   )
   
   st.plotly_chart(fig, use_container_width=True)

def generate_mock_pdf_report():
   """Generar un PDF mock para demostración"""
   # En un entorno real, aquí usarías reportlab o similar
   mock_pdf_content = b"""Mock PDF Report Content - Security Intelligence Analysis
   
   REPORTE EJECUTIVO DE SEGURIDAD
   Fecha: %s
   
   RESUMEN EJECUTIVO:
   - Vulnerabilidades críticas detectadas: 87
   - Empleados de alto riesgo: 234
   - Score general de riesgo: 0.73/1.0
   
   RECOMENDACIONES PRIORITARIAS:
   1. Implementar capacitación anti-phishing inmediata
   2. Revisar políticas de verificación telefónica
   3. Establecer monitoreo de redes sociales corporativas
   
   """ % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
   
   return mock_pdf_content.encode('utf-8')
