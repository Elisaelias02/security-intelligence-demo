import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
from datetime import datetime

def create_profiling_interface():
    st.markdown("### 👥 Perfilado Avanzado de Objetivos")
    st.info("**Análisis psicológico y comportamental** de empleados para identificar vulnerabilidades específicas")
    
    # Tabs para diferentes tipos de perfilado
    profile_tab1, profile_tab2, profile_tab3 = st.tabs([
        " Perfilado Individual", 
        " Análisis de Grupo", 
        " Patrones Psicológicos"
    ])
    
    with profile_tab1:
        create_individual_profiling()
    
    with profile_tab2:
        create_group_analysis()
    
    with profile_tab3:
        create_psychological_patterns()

def create_individual_profiling():
    st.markdown("####  Análisis Individual de Empleado")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("** Datos del Objetivo**")
        
        # Selector de empleado (basado en resultados OSINT)
        if 'osint_results' in st.session_state:
            employee_options = generate_employee_list(st.session_state.osint_results['total_employees'])
        else:
            employee_options = [
                "María González - CFO",
                "Carlos Rodríguez - Director IT", 
                "Ana Martínez - Gerente RRHH",
                "Luis Hernández - Coord. Operaciones"
            ]
        
        selected_employee = st.selectbox("Seleccionar Empleado", employee_options)
        
        # Formulario de datos adicionales
        with st.form("individual_profile_form"):
            st.markdown("**🔍 Información Adicional**")
            
            social_media_activity = st.slider("Actividad en RRSS (1-10)", 1, 10, 7)
            public_info_sharing = st.slider("Compartir Info Pública (1-10)", 1, 10, 6)
            security_awareness = st.slider("Conciencia de Seguridad (1-10)", 1, 10, 4)
            
            interests = st.multiselect(
                "Intereses Principales",
                ["Tecnología", "Deportes", "Viajes", "Familia", "Finanzas", "Entretenimiento", "Educación"],
                default=["Tecnología", "Viajes"]
            )
            
            communication_style = st.selectbox(
                "Estilo de Comunicación",
                ["Formal", "Casual", "Técnico", "Emocional", "Directo"]
            )
            
            work_schedule = st.selectbox(
                "Horario de Trabajo",
                ["9-17 Estándar", "Flexible", "Nocturno", "Fines de Semana", "24/7 Disponible"]
            )
            
            analyze_button = st.form_submit_button(" Analizar Perfil", type="primary")
            
            if analyze_button:
                run_individual_analysis(selected_employee, {
                    'social_activity': social_media_activity,
                    'info_sharing': public_info_sharing,
                    'security_awareness': security_awareness,
                    'interests': interests,
                    'communication': communication_style,
                    'schedule': work_schedule
                })
    
    with col2:
        display_individual_results()

def run_individual_analysis(employee, profile_data):
    """Ejecutar análisis individual del empleado"""
    
    with st.spinner(" Analizando perfil psicológico..."):
        progress_bar = st.progress(0)
        
        analysis_steps = [
            "Analizando patrones de comportamiento digital...",
            "Evaluando vulnerabilidades psicológicas...",
            "Identificando vectores de ataque óptimos...",
            "Calculando probabilidades de éxito...",
            "Generando recomendaciones de defensa..."
        ]
        
        for i, step in enumerate(analysis_steps):
            time.sleep(0.8)
            progress_bar.progress((i + 1) / len(analysis_steps))
            st.text(step)
        
        # Calcular métricas de riesgo
        risk_score = calculate_individual_risk_score(profile_data)
        
        # Almacenar resultados
        st.session_state.individual_profile = {
            'employee': employee,
            'data': profile_data,
            'risk_score': risk_score,
            'analysis_time': datetime.now(),
            'vulnerabilities': generate_vulnerabilities(profile_data),
            'attack_vectors': generate_attack_vectors(profile_data),
            'recommendations': generate_individual_recommendations(profile_data)
        }
        
        st.success(" Análisis de perfil completado")
        st.rerun()

def display_individual_results():
    """Mostrar resultados del análisis individual"""
    
    if 'individual_profile' not in st.session_state:
        st.info(" Selecciona un empleado y ejecuta el análisis para ver los resultados")
        return
    
    profile = st.session_state.individual_profile
    
    st.markdown("####  Resultados del Análisis")
    
    # Score de riesgo principal
    risk_color = get_risk_color(profile['risk_score'])
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {risk_color}, {risk_color}88); 
                padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;">
        <h2 style="color: white; margin: 0;">Score de Riesgo: {profile['risk_score']:.2f}/1.0</h2>
        <p style="color: white; margin: 0.5rem 0 0 0; opacity: 0.9;">
            {get_risk_level(profile['risk_score'])}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas detalladas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(" Vectores de Ataque", len(profile['attack_vectors']))
    with col2:
        st.metric(" Vulnerabilidades", len(profile['vulnerabilities']))
    with col3:
        st.metric(" Contramedidas", len(profile['recommendations']))
    
    # Gráfico de radar con dimensiones de riesgo
    create_risk_radar_chart(profile['data'])
    
    # Vulnerabilidades específicas
    st.markdown("#### ⚠ Vulnerabilidades Identificadas")
    for i, vuln in enumerate(profile['vulnerabilities'], 1):
        st.markdown(f"**{i}.** {vuln}")
    
    # Vectores de ataque
    st.markdown("####  Vectores de Ataque Principales")
    for i, vector in enumerate(profile['attack_vectors'], 1):
        st.markdown(f"**{i}.** {vector}")
    
    # Recomendaciones
    st.markdown("####  Recomendaciones de Protección")
    for i, rec in enumerate(profile['recommendations'], 1):
        st.markdown(f"**{i}.** {rec}")

def create_risk_radar_chart(profile_data):
    """Crear gráfico de radar con dimensiones de riesgo"""
    
    categories = [
        'Actividad RRSS',
        'Compartir Info',
        'Conciencia Seguridad',
        'Exposición Pública',
        'Predictibilidad',
        'Vulnerabilidad Social'
    ]
    
    # Convertir datos a scores de riesgo (invertir algunos)
    values = [
        profile_data['social_activity'] / 10,
        profile_data['info_sharing'] / 10,
        1 - (profile_data['security_awareness'] / 10),  # Invertir
        profile_data['social_activity'] / 10,
        0.7,  # Valor calculado
        (profile_data['social_activity'] + profile_data['info_sharing']) / 20
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Nivel de Riesgo',
        line=dict(color='#ef4444'),
        fillcolor='rgba(239, 68, 68, 0.1)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=False,
        title="Perfil de Riesgo Multi-dimensional",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_group_analysis():
    st.markdown("####  Análisis de Grupo y Departamental")
    
    # Selector de departamento
    department = st.selectbox(
        "Seleccionar Departamento",
        ["Todos los Departamentos", "Finanzas", "IT", "RRHH", "Ventas", "Marketing", "Operaciones"]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de riesgo por departamento
        st.markdown("####  Distribución de Riesgo")
        create_department_risk_distribution()
    
    with col2:
        # Top empleados de riesgo
        st.markdown("####  Top 10 Empleados de Riesgo")
        create_top_risk_employees_chart()
    
    # Correlaciones entre factores
    st.markdown("####  Correlaciones de Factores de Riesgo")
    create_risk_correlation_matrix()

def create_department_risk_distribution():
    """Gráfico de distribución de riesgo por departamento"""
    
    departments = ['Finanzas', 'IT', 'RRHH', 'Ventas', 'Marketing', 'Operaciones']
    risk_levels = ['Bajo', 'Medio', 'Alto', 'Crítico']
    
    # Generar datos simulados
    data = []
    for dept in departments:
        for level in risk_levels:
            count = np.random.randint(5, 25)
            data.append({'Departamento': dept, 'Nivel': level, 'Cantidad': count})
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x='Departamento', 
        y='Cantidad',
        color='Nivel',
        color_discrete_map={
            'Bajo': '#10b981',
            'Medio': '#3b82f6', 
            'Alto': '#f59e0b',
            'Crítico': '#ef4444'
        },
        title="Empleados por Nivel de Riesgo y Departamento"
    )
    
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

def create_top_risk_employees_chart():
    """Gráfico de top empleados de riesgo"""
    
    employees = [f"Empleado {i}" for i in range(1, 11)]
    risk_scores = sorted(np.random.uniform(0.6, 0.95, 10), reverse=True)
    
    colors = ['#ef4444' if score >= 0.9 else '#f59e0b' if score >= 0.8 else '#3b82f6' for score in risk_scores]
    
    fig = go.Figure(data=[
        go.Bar(
            x=employees,
            y=risk_scores,
            marker_color=colors,
            text=[f'{score:.2f}' for score in risk_scores],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Top 10 Empleados por Score de Riesgo",
        height=350,
        xaxis_title="Empleado",
        yaxis_title="Score de Riesgo"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_risk_correlation_matrix():
    """Matriz de correlación entre factores de riesgo"""
    
    factors = [
        'Actividad RRSS',
        'Info Compartida',
        'Conciencia Seguridad',
        'Exposición Pública',
        'Acceso Privilegiado',
        'Contactos Externos'
    ]
    
    # Generar matriz de correlación simulada
    np.random.seed(42)
    correlation_matrix = np.random.rand(len(factors), len(factors))
    
    # Hacer simétrica
    correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
    np.fill_diagonal(correlation_matrix, 1)
    
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix,
        x=factors,
        y=factors,
        colorscale='RdBu',
        zmid=0,
        colorbar=dict(title="Correlación")
    ))
    
    fig.update_layout(
        title="Matriz de Correlación: Factores de Riesgo",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_psychological_patterns():
    st.markdown("####  Análisis de Patrones Psicológicos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de personalidades
        st.markdown("####  Tipos de Personalidad (DISC)")
        create_personality_distribution()

  with col2:
       # Vulnerabilidades por tipo de personalidad
       st.markdown("#### ⚠ Vulnerabilidades por Personalidad")
       create_personality_vulnerability_chart()
   
   # Análisis de triggers emocionales
   st.markdown("####  Triggers Emocionales Más Efectivos")
   create_emotional_triggers_analysis()
   
   # Patrones temporales
   st.markdown("####  Patrones Temporales de Vulnerabilidad")
   create_temporal_vulnerability_chart()

def create_personality_distribution():
   """Distribución de tipos de personalidad DISC"""
   
   personality_types = ['Dominante', 'Influyente', 'Estable', 'Concienzudo']
   values = [28, 35, 22, 15]  # Porcentajes
   colors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6']
   
   fig = go.Figure(data=[go.Pie(
       labels=personality_types,
       values=values,
       marker_colors=colors,
       hole=.3
   )])
   
   fig.update_traces(
       textposition='inside',
       textinfo='percent+label',
       hovertemplate='<b>%{label}</b><br>%{percent}<br>%{value} empleados<extra></extra>'
   )
   
   fig.update_layout(
       height=350,
       annotations=[dict(text='DISC', x=0.5, y=0.5, font_size=20, showarrow=False)]
   )
   
   st.plotly_chart(fig, use_container_width=True)

def create_personality_vulnerability_chart():
   """Vulnerabilidades específicas por tipo de personalidad"""
   
   data = {
       'Personalidad': ['Dominante', 'Influyente', 'Estable', 'Concienzudo'],
       'Autoridad': [0.9, 0.6, 0.7, 0.8],
       'Urgencia': [0.8, 0.7, 0.5, 0.6],
       'Social': [0.4, 0.9, 0.8, 0.3],
       'Técnico': [0.6, 0.4, 0.6, 0.9]
   }
   
   df = pd.DataFrame(data)
   
   fig = go.Figure()
   
   techniques = ['Autoridad', 'Urgencia', 'Social', 'Técnico']
   colors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6']
   
   for i, technique in enumerate(techniques):
       fig.add_trace(go.Bar(
           name=technique,
           x=df['Personalidad'],
           y=df[technique],
           marker_color=colors[i]
       ))
   
   fig.update_layout(
       title="Susceptibilidad a Técnicas por Personalidad",
       height=350,
       barmode='group',
       yaxis_title="Nivel de Susceptibilidad"
   )
   
   st.plotly_chart(fig, use_container_width=True)

def create_emotional_triggers_analysis():
   """Análisis de triggers emocionales más efectivos"""
   
   triggers_data = {
       'Trigger': [
           'Urgencia Financiera',
           'Amenaza de Seguridad',
           'Oportunidad de Promoción',
           'Problema Técnico Crítico',
           'Solicitud de Autoridad',
           'Beneficio Personal',
           'Presión de Tiempo',
           'Miedo a Consecuencias'
       ],
       'Efectividad': [0.87, 0.82, 0.78, 0.75, 0.73, 0.69, 0.67, 0.84],
       'Frecuencia de Uso': [45, 38, 22, 52, 67, 31, 58, 41],
       'Departamento Principal': [
           'Finanzas', 'IT', 'RRHH', 'IT', 'Todos', 'Ventas', 'Operaciones', 'Ejecutivos'
       ]
   }
   
   df = pd.DataFrame(triggers_data)
   
   # Gráfico de burbujas
   fig = px.scatter(
       df,
       x='Efectividad',
       y='Frecuencia de Uso',
       size='Efectividad',
       color='Departamento Principal',
       hover_name='Trigger',
       size_max=60,
       title="Efectividad vs Frecuencia de Triggers Emocionales"
   )
   
   fig.update_layout(
       height=400,
       xaxis_title="Efectividad (0-1)",
       yaxis_title="Frecuencia de Uso (%)"
   )
   
   st.plotly_chart(fig, use_container_width=True)
   
   # Tabla detallada
   st.markdown("####  Detalle de Triggers por Efectividad")
   df_display = df.sort_values('Efectividad', ascending=False)
   df_display['Efectividad'] = df_display['Efectividad'].apply(lambda x: f"{x:.1%}")
   df_display['Frecuencia de Uso'] = df_display['Frecuencia de Uso'].apply(lambda x: f"{x}%")
   
   st.dataframe(df_display, use_container_width=True, hide_index=True)

def create_temporal_vulnerability_chart():
   """Patrones temporales de vulnerabilidad"""
   
   col1, col2 = st.columns(2)
   
   with col1:
       # Vulnerabilidad por hora del día
       hours = list(range(0, 24))
       vulnerability_by_hour = [
           0.2, 0.1, 0.1, 0.1, 0.1, 0.2, 0.3, 0.4,  # 0-7
           0.6, 0.8, 0.9, 0.9, 0.7, 0.6, 0.8, 0.9,  # 8-15
           0.9, 0.8, 0.6, 0.4, 0.3, 0.3, 0.2, 0.2   # 16-23
       ]
       
       fig = go.Figure()
       fig.add_trace(go.Scatter(
           x=hours,
           y=vulnerability_by_hour,
           mode='lines+markers',
           fill='tonexty',
           name='Vulnerabilidad',
           line=dict(color='#ef4444', width=3),
           marker=dict(size=6)
       ))
       
       fig.update_layout(
           title="Vulnerabilidad por Hora del Día",
           height=300,
           xaxis_title="Hora",
           yaxis_title="Nivel de Vulnerabilidad",
           xaxis=dict(tickmode='linear', tick0=0, dtick=2)
       )
       
       st.plotly_chart(fig, use_container_width=True)
   
   with col2:
       # Vulnerabilidad por día de la semana
       days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
       vulnerability_by_day = [0.7, 0.8, 0.8, 0.9, 0.95, 0.3, 0.2]
       
       colors = ['#10b981' if v < 0.5 else '#f59e0b' if v < 0.8 else '#ef4444' for v in vulnerability_by_day]
       
       fig = go.Figure(data=[
           go.Bar(
               x=days,
               y=vulnerability_by_day,
               marker_color=colors,
               text=[f'{v:.1%}' for v in vulnerability_by_day],
               textposition='auto'
           )
       ])
       
       fig.update_layout(
           title="Vulnerabilidad por Día de la Semana",
           height=300,
           yaxis_title="Nivel de Vulnerabilidad"
       )
       
       st.plotly_chart(fig, use_container_width=True)

# Funciones de utilidad
def generate_employee_list(total_employees):
   """Generar lista de empleados basada en resultados OSINT"""
   roles = ['CEO', 'CFO', 'CTO', 'Director IT', 'Gerente RRHH', 'Coord. Operaciones', 'Analista Senior']
   names = ['María González', 'Carlos Rodríguez', 'Ana Martínez', 'Luis Hernández', 'Carmen López', 'David Pérez', 'Laura Sánchez']
   
   employees = []
   for i in range(min(total_employees, 20)):  # Limitar a 20 para la demo
       if i < len(names):
           name = names[i]
           role = roles[i % len(roles)]
       else:
           name = f"Empleado {i+1}"
           role = roles[i % len(roles)]
       
       employees.append(f"{name} - {role}")
   
   return employees

def calculate_individual_risk_score(profile_data):
   """Calcular score de riesgo individual"""
   
   # Pesos para diferentes factores
   weights = {
       'social_activity': 0.25,
       'info_sharing': 0.30,
       'security_awareness': -0.20,  # Negativo porque mayor conciencia = menor riesgo
       'interests_count': 0.10,
       'communication_risk': 0.15
   }
   
   # Calcular componentes
   social_risk = profile_data['social_activity'] / 10
   sharing_risk = profile_data['info_sharing'] / 10
   awareness_protection = profile_data['security_awareness'] / 10
   interests_risk = len(profile_data['interests']) / 7  # Máximo 7 intereses
   
   # Riesgo por estilo de comunicación
   comm_risks = {
       'Formal': 0.3,
       'Casual': 0.7,
       'Técnico': 0.4,
       'Emocional': 0.8,
       'Directo': 0.5
   }
   communication_risk = comm_risks.get(profile_data['communication'], 0.5)
   
   # Calcular score final
   risk_score = (
       social_risk * weights['social_activity'] +
       sharing_risk * weights['info_sharing'] +
       awareness_protection * weights['security_awareness'] +
       interests_risk * weights['interests_count'] +
       communication_risk * weights['communication_risk']
   )
   
   # Normalizar entre 0 y 1
   risk_score = max(0, min(1, risk_score + 0.3))  # Base mínima de 0.3
   
   return risk_score

def generate_vulnerabilities(profile_data):
   """Generar lista de vulnerabilidades específicas"""
   
   vulnerabilities = []
   
   if profile_data['social_activity'] >= 7:
       vulnerabilities.append("Alta exposición en redes sociales - información personal fácilmente accesible")
   
   if profile_data['info_sharing'] >= 7:
       vulnerabilities.append("Tendencia a compartir información corporativa en canales públicos")
   
   if profile_data['security_awareness'] <= 4:
       vulnerabilities.append("Baja conciencia de seguridad - susceptible a técnicas básicas de ingeniería social")
   
   if 'Familia' in profile_data['interests']:
       vulnerabilities.append("Información familiar pública - posible vector de manipulación emocional")
   
   if 'Tecnología' in profile_data['interests']:
       vulnerabilities.append("Interés en tecnología - susceptible a ataques técnicos sofisticados")
   
   if profile_data['communication'] == 'Emocional':
       vulnerabilities.append("Estilo comunicativo emocional - vulnerable a técnicas de manipulación psicológica")
   
   if profile_data['schedule'] == '24/7 Disponible':
       vulnerabilities.append("Disponibilidad constante - mayor superficie de ataque temporal")
   
   return vulnerabilities

def generate_attack_vectors(profile_data):
   """Generar vectores de ataque específicos"""
   
   vectors = []
   
   # Vectores basados en actividad social
   if profile_data['social_activity'] >= 6:
       vectors.append("Phishing dirigido basado en posts recientes en redes sociales")
       vectors.append("Ingeniería social vía LinkedIn con conexiones falsas")
   
   # Vectores basados en intereses
   if 'Tecnología' in profile_data['interests']:
       vectors.append("Emails de alerta de seguridad falsos con enlaces maliciosos")
   
   if 'Viajes' in profile_data['interests']:
       vectors.append("Ofertas de viajes corporativos falsas para captura de datos")
   
   if 'Familia' in profile_data['interests']:
       vectors.append("Emergencias familiares falsas para generar urgencia")
   
   # Vectores basados en comunicación
   if profile_data['communication'] in ['Casual', 'Emocional']:
       vectors.append("Vishing (phone phishing) con pretexto emocional")
   
   # Vector de timing
   if profile_data['schedule'] != '9-17 Estándar':
       vectors.append("Ataques fuera de horario laboral cuando las defensas están bajas")
   
   return vectors

def generate_individual_recommendations(profile_data):
   """Generar recomendaciones personalizadas"""
   
   recommendations = []
   
   if profile_data['social_activity'] >= 7:
       recommendations.append("Capacitación específica sobre configuración de privacidad en redes sociales")
       recommendations.append("Política de redes sociales corporativas personalizada")
   
   if profile_data['security_awareness'] <= 4:
       recommendations.append("Programa intensivo de concienciación en seguridad")
       recommendations.append("Simulacros de phishing semanales hasta mejora demostrable")
   
   if profile_data['info_sharing'] >= 6:
       recommendations.append("Protocolo de verificación antes de compartir información corporativa")
       recommendations.append("Capacitación sobre clasificación de información sensible")
   
   if profile_data['communication'] == 'Emocional':
       recommendations.append("Entrenamiento específico sobre técnicas de manipulación emocional")
       recommendations.append("Protocolo de 'pausa y verificación' para solicitudes urgentes")
   
   # Recomendación técnica
   recommendations.append("Implementación de autenticación multifactor obligatoria")
   recommendations.append("Monitoreo personalizado de actividades inusuales")
   
   return recommendations

def get_risk_color(risk_score):
   """Obtener color basado en el score de riesgo"""
   if risk_score >= 0.8:
       return '#ef4444'  # Rojo
   elif risk_score >= 0.6:
       return '#f59e0b'  # Naranja
   elif risk_score >= 0.4:
       return '#3b82f6'  # Azul
   else:
       return '#10b981'  # Verde

def get_risk_level(risk_score):
   """Obtener nivel de riesgo textual"""
   if risk_score >= 0.8:
       return 'CRÍTICO - Acción inmediata requerida'
   elif risk_score >= 0.6:
       return 'ALTO - Requiere atención prioritaria'
   elif risk_score >= 0.4:
       return 'MEDIO - Monitoreo continuo recomendado'
   else:
       return 'BAJO - Mantener vigilancia estándar'
