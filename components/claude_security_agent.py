import anthropic
import json
import os
from datetime import datetime
import streamlit as st
from typing import Dict, List, Optional
import time

class ClaudeSecurityAgent:
    """
    Agente de seguridad profesional usando Claude API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Inicializar el agente con API key"""
        
        # Obtener API key de diferentes fuentes
        self.api_key = (
            api_key or 
            st.secrets.get("ANTHROPIC_API_KEY") or 
            os.getenv("ANTHROPIC_API_KEY")
        )
        
        if not self.api_key:
            st.error(" API Key de Anthropic no encontrada. Usando modo simulación.")
            self.use_simulation = True
            from .simulated_ai_agent import SimulatedSecurityAgent
            self.fallback_agent = SimulatedSecurityAgent()
        else:
            self.use_simulation = False
            self.client = anthropic.Anthropic(api_key=self.api_key)
            
        # Configuración del modelo
        self.model = "claude-3-haiku-20240307"  # Más económico
        self.max_tokens = 1500
        
    def analyze_company_osint(self, company_data: Dict) -> Dict:
        """Análisis OSINT de empresa con Claude"""
        
        if self.use_simulation:
            return self.fallback_agent.analyze_company_profile(company_data)
        
        prompt = f"""
        Como experto en inteligencia de amenazas y OSINT, analiza la siguiente empresa:
        
        DATOS DE LA EMPRESA:
        - Nombre: {company_data.get('name', 'N/A')}
        - Dominio: {company_data.get('domain', 'N/A')}
        - Industria: {company_data.get('industry', 'N/A')}
        - Tamaño: {company_data.get('size', 'N/A')}
        - Ubicación: {company_data.get('location', 'N/A')}
        
        FUENTES ANALIZADAS:
        {', '.join(company_data.get('sources', ['LinkedIn', 'Website', 'Public Records']))}
        
        Proporciona un análisis estructurado en formato JSON con:
        
        1. risk_score: Puntuación de riesgo (0.0-1.0)
        2. vulnerabilities_found: Lista de vulnerabilidades específicas
        3. employees_at_risk: Número estimado de empleados de alto riesgo
        4. attack_surface: Descripción de la superficie de ataque
        5. critical_findings: Lista de hallazgos críticos
        6. department_risks: Riesgos por departamento
        7. recommendations: Recomendaciones prioritarias
        8. timeline_analysis: Análisis de patrones temporales
        
        IMPORTANTE: 
        - Sé específico y realista
        - Enfócate en vulnerabilidades de ingeniería social
        - Incluye métricas cuantificables
        - Proporciona recomendaciones accionables
        
        Responde SOLO con JSON válido.
        """
        
        try:
            with st.spinner(" Claude analizando inteligencia empresarial..."):
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Extraer y parsear JSON
                content = response.content[0].text
                
                # Limpiar el contenido si viene con markdown
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                analysis_result = json.loads(content.strip())
                
                # Añadir metadatos
                analysis_result.update({
                    'analysis_timestamp': datetime.now().isoformat(),
                    'ai_model': self.model,
                    'company_analyzed': company_data.get('name', 'Unknown'),
                    'confidence_level': 0.87
                })
                
                return analysis_result
                
        except json.JSONDecodeError as e:
            st.error(f"Error parseando respuesta de Claude: {e}")
            return self._generate_fallback_analysis(company_data)
        except Exception as e:
            st.error(f"Error con Claude API: {e}")
            return self._generate_fallback_analysis(company_data)
    
    def analyze_employee_profile(self, employee_data: Dict) -> Dict:
        """Análisis psicológico de empleado con Claude"""
        
        if self.use_simulation:
            return self.fallback_agent.analyze_employee_profile(employee_data)
        
        prompt = f"""
        Como especialista en psicología de la ingeniería social, analiza este perfil de empleado:
        
        DATOS DEL EMPLEADO:
        - Nombre/Rol: {employee_data.get('name', 'N/A')}
        - Departamento: {employee_data.get('department', 'N/A')}
        - Actividad en RRSS: {employee_data.get('social_activity', 5)}/10
        - Compartir información: {employee_data.get('info_sharing', 5)}/10
        - Conciencia de seguridad: {employee_data.get('security_awareness', 5)}/10
        - Intereses: {', '.join(employee_data.get('interests', []))}
        - Estilo comunicación: {employee_data.get('communication', 'N/A')}
        - Horario de trabajo: {employee_data.get('schedule', 'N/A')}
        
        Proporciona análisis en JSON con:
        
        1. risk_score: Puntuación de riesgo individual (0.0-1.0)
        2. vulnerability_profile: Lista detallada de vulnerabilidades
        3. psychological_factors: Factores psicológicos explotables
        4. optimal_attack_vectors: Vectores de ataque más efectivos
        5. susceptibility_analysis: Análisis de susceptibilidad por técnica
        6. behavioral_patterns: Patrones de comportamiento identificados
        7. timing_vulnerabilities: Momentos de mayor vulnerabilidad
        8. personalized_recommendations: Recomendaciones específicas
        9. training_priorities: Prioridades de capacitación
        10. monitoring_suggestions: Sugerencias de monitoreo
        
        ENFOQUE EN:
        - Factores psicológicos específicos
        - Vulnerabilidades comportamentales
        - Técnicas de manipulación más efectivas
        - Contramedidas personalizadas
        
        Responde SOLO con JSON válido.
        """
        
        try:
            with st.spinner(" Claude analizando perfil psicológico..."):
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.content[0].text
                
                # Limpiar JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                profile_analysis = json.loads(content.strip())
                
                # Añadir metadatos
                profile_analysis.update({
                    'analysis_timestamp': datetime.now().isoformat(),
                    'employee_analyzed': employee_data.get('name', 'Unknown'),
                    'ai_model': self.model,
                    'confidence_level': 0.91
                })
                
                return profile_analysis
                
        except Exception as e:
            st.error(f"Error en análisis de empleado: {e}")
            return self._generate_fallback_employee_analysis(employee_data)
    
    def generate_attack_simulation(self, target_profile: Dict, company_context: Dict) -> Dict:
        """Generar simulación educativa de ataque con Claude"""
        
        prompt = f"""
        TAREA: Crear simulación EDUCATIVA de ataque de ingeniería social.
        
        IMPORTANTE: Esto es para CAPACITACIÓN Y CONCIENCIACIÓN, no para uso malicioso.
        
        PERFIL DEL OBJETIVO:
        {json.dumps(target_profile, indent=2)}
        
        CONTEXTO EMPRESARIAL:
        {json.dumps(company_context, indent=2)}
        
        Como experto en seguridad cibernética, diseña una simulación educativa que muestre:
        
        1. attack_scenario: Escenario de ataque detallado pero educativo
        2. psychological_techniques: Técnicas psicológicas que se utilizarían
        3. social_engineering_methods: Métodos específicos de ingeniería social
        4. success_probability: Probabilidad de éxito estimada
        5. timeline_execution: Cronología del ataque simulado
        6. red_flags_ignored: Señales de alerta que se pasarían por alto
        7. defensive_measures: Medidas defensivas específicas
        8. educational_insights: Insights educativos clave
        9. training_recommendations: Recomendaciones de entrenamiento
        10. detection_strategies: Estrategias de detección
        
        CARACTERÍSTICAS DEL ANÁLISIS:
        - Enfoque educativo y preventivo
        - Explicación de técnicas sin contenido malicioso
        - Énfasis en contramedidas y detección
        - Casos de estudio para capacitación
        
        DISCLAIMER: Incluir claramente que es solo para educación y prevención.
        
        Responde SOLO con JSON válido.
        """
        
        try:
            with st.spinner(" Claude generando simulación educativa..."):
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,  # Más tokens para análisis completo
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.content[0].text
                
                # Limpiar JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                simulation = json.loads(content.strip())
                
                # Añadir disclaimer de seguridad
                simulation.update({
                    'disclaimer': 'SIMULACIÓN EDUCATIVA - Solo para capacitación y concienciación',
                    'purpose': 'Educación en seguridad cibernética',
                    'generated_by': 'Claude AI Security Agent',
                    'timestamp': datetime.now().isoformat(),
                    'ethical_use_only': True
                })
                
                return simulation
                
        except Exception as e:
            st.error(f"Error generando simulación: {e}")
            return self._generate_fallback_simulation()
    
    def generate_countermeasures(self, analysis_results: Dict) -> Dict:
        """Generar contramedidas inteligentes con Claude"""
        
        prompt = f"""
        Como consultor senior en seguridad cibernética, basándote en este análisis:
        
        {json.dumps(analysis_results, indent=2)}
        
        Genera un plan integral de contramedidas en JSON con:
        
        1. immediate_actions: Acciones inmediatas (0-7 días)
        2. short_term_measures: Medidas a corto plazo (1-4 semanas)
        3. long_term_strategy: Estrategia a largo plazo (1-6 meses)
        4. budget_breakdown: Desglose presupuestario detallado
        5. roi_analysis: Análisis de retorno de inversión
        6. implementation_timeline: Cronograma de implementación
        7. success_metrics: Métricas de éxito medibles
        8. risk_reduction_estimates: Estimaciones de reducción de riesgo
        9. training_programs: Programas de capacitación específicos
        10. monitoring_framework: Marco de monitoreo continuo
        
        PARA CADA CONTRAMEDIDA INCLUIR:
        - Descripción detallada
        - Costo estimado
        - Tiempo de implementación
        - Impacto esperado
        - Métricas de seguimiento
        - Responsables sugeridos
        
        PRIORIZAR POR:
        - Impacto en reducción de riesgo
        - Facilidad de implementación
        - Costo-beneficio
        - Urgencia basada en vulnerabilidades críticas
        
        Responde SOLO con JSON válido.
        """
        
        try:
            with st.spinner(" Claude generando contramedidas inteligentes..."):
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.content[0].text
                
                # Limpiar JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                countermeasures = json.loads(content.strip())
                
                # Añadir metadatos
                countermeasures.update({
                    'generated_timestamp': datetime.now().isoformat(),
                    'ai_model': self.model,
                    'analysis_basis': 'Claude AI Security Analysis',
                    'confidence_level': 0.89
                })
                
                return countermeasures
                
        except Exception as e:
            st.error(f"Error generando contramedidas: {e}")
            return self._generate_fallback_countermeasures()
    
    def _generate_fallback_analysis(self, company_data: Dict) -> Dict:
        """Análisis de fallback si Claude falla"""
        return {
            'risk_score': 0.75,
            'vulnerabilities_found': [
                'Alta exposición en redes sociales corporativas',
                'Información organizacional públicamente disponible',
                'Empleados con perfiles de alto riesgo identificados'
            ],
            'employees_at_risk': 45,
            'attack_surface': 'Superficie de ataque extensa con múltiples vectores',
            'critical_findings': [
                'Ejecutivos con información personal expuesta',
                'Patrones de comunicación corporativa predecibles',
                'Falta de políticas de redes sociales'
            ],
            'recommendations': [
                'Capacitación anti-phishing inmediata',
                'Implementar autenticación multifactor',
                'Revisar políticas de redes sociales'
            ],
            'fallback_mode': True,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _generate_fallback_employee_analysis(self, employee_data: Dict) -> Dict:
        """Análisis de empleado de fallback"""
        return {
            'risk_score': 0.68,
            'vulnerability_profile': [
                'Actividad alta en redes sociales',
                'Tendencia a compartir información profesional',
                'Posible susceptibilidad a técnicas de autoridad'
            ],
            'optimal_attack_vectors': [
                'Phishing dirigido por email',
                'Ingeniería social vía LinkedIn',
                'Vishing con pretexto corporativo'
            ],
            'personalized_recommendations': [
                'Capacitación específica en reconocimiento de phishing',
                'Protocolo de verificación para solicitudes urgentes',
                'Revisión de configuraciones de privacidad'
            ],
            'fallback_mode': True,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _generate_fallback_simulation(self) -> Dict:
        """Simulación de fallback"""
        return {
            'attack_scenario': 'Simulación educativa básica de phishing dirigido',
            'success_probability': 0.67,
            'educational_insights': [
                'Los ataques personalizados tienen mayor éxito',
                'La urgencia reduce la capacidad de verificación',
                'La autoridad percibida aumenta la compliance'
            ],
            'defensive_measures': [
                'Verificación multi-canal obligatoria',
                'Capacitación en reconocimiento de señales',
                'Protocolos de escalación claros'
            ],
            'disclaimer': 'Simulación educativa generada en modo fallback',
            'fallback_mode': True
        }
    
    def _generate_fallback_countermeasures(self) -> Dict:
        """Contramedidas de fallback"""
        return {
            'immediate_actions': [
                {
                    'action': 'Capacitación anti-phishing de emergencia',
                    'timeline': '7 días',
                    'cost': '$10,000',
                    'impact': 'Alto'
                }
            ],
            'short_term_measures': [
                {
                    'action': 'Implementar MFA obligatorio',
                    'timeline': '2 semanas',
                    'cost': '$5,000',
                    'impact': 'Crítico'
                }
            ],
            'budget_breakdown': {
                'total_investment': '$50,000',
                'immediate': '$15,000',
                'short_term': '$20,000',
                'long_term': '$15,000'
            },
            'fallback_mode': True
        }
    
    def check_api_status(self) -> Dict:
        """Verificar estado de la API"""
        if self.use_simulation:
            return {
                'status': 'simulation_mode',
                'message': 'Usando modo simulación - No se requiere API',
                'api_available': False
            }
        
        try:
            # Test simple con Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Test"}]
            )
            
            return {
                'status': 'active',
                'message': 'Claude API funcionando correctamente',
                'api_available': True,
                'model': self.model
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error con Claude API: {str(e)}',
                'api_available': False
            }

# Función de utilidad para crear el agente
def create_claude_agent(api_key: Optional[str] = None) -> ClaudeSecurityAgent:
    """Crear instancia del agente Claude"""
    return ClaudeSecurityAgent(api_key=api_key)
