"""
Servidor MCP Remoto: Citas Inspiracionales para Dormir
Desplegable en servicios de nube como Google Cloud Run, Railway, etc.
"""

import asyncio
import json
import logging
import random
from datetime import datetime, time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Dependencias para MCP
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Para despliegue web
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SleepQuote:
    """Estructura para citas inspiracionales"""
    id: int
    quote: str
    author: str
    category: str
    time_of_day: str  # morning, evening, night
    mood: str  # calm, motivational, peaceful, reflective

class SleepQuotesDatabase:
    """Base de datos en memoria para citas inspiracionales"""
    
    def __init__(self):
        self.quotes = self._initialize_quotes()
        self.user_preferences = {}
    
    def _initialize_quotes(self) -> List[SleepQuote]:
        """Inicializa la base de datos con citas predefinidas"""
        quotes_data = [
            # Citas para la noche
            {
                "id": 1,
                "quote": "Cada noche es una oportunidad para que tu mente y cuerpo se regeneren completamente.",
                "author": "Dr. Sleep Coach",
                "category": "sleep_hygiene",
                "time_of_day": "night",
                "mood": "peaceful"
            },
            {
                "id": 2,
                "quote": "El sueño es la mejor meditación que existe. Entrégate a él con gratitud.",
                "author": "Dalai Lama",
                "category": "mindfulness",
                "time_of_day": "night",
                "mood": "calm"
            },
            {
                "id": 3,
                "quote": "Tu cerebro trabaja toda la noche organizando los recuerdos del día. Dale el descanso que merece.",
                "author": "Neuroscience Today",
                "category": "science",
                "time_of_day": "night",
                "mood": "educational"
            },
            {
                "id": 4,
                "quote": "Desconecta los dispositivos, conecta con tus sueños.",
                "author": "Sleep Expert",
                "category": "sleep_hygiene",
                "time_of_day": "evening",
                "mood": "motivational"
            },
            {
                "id": 5,
                "quote": "El sueño es el momento en que tu cuerpo repara, tu mente procesa y tu alma descansa.",
                "author": "Wellness Guru",
                "category": "holistic",
                "time_of_day": "night",
                "mood": "peaceful"
            },
            
            # Citas para la mañana
            {
                "id": 6,
                "quote": "Cada amanecer es una nueva página en blanco. ¿Cómo la vas a escribir hoy?",
                "author": "Morning Wisdom",
                "category": "motivation",
                "time_of_day": "morning",
                "mood": "motivational"
            },
            {
                "id": 7,
                "quote": "Un buen día comienza con una noche de sueño reparador. Tu cuerpo te lo agradece.",
                "author": "Health Coach",
                "category": "wellness",
                "time_of_day": "morning",
                "mood": "calm"
            },
            {
                "id": 8,
                "quote": "El sol sale para recordarte que cada día es una nueva oportunidad de brillar.",
                "author": "Sun Wisdom",
                "category": "inspiration",
                "time_of_day": "morning",
                "mood": "motivational"
            },
            
            # Citas para la tarde/noche
            {
                "id": 9,
                "quote": "A medida que el día llega a su fin, permite que tu mente también encuentre paz.",
                "author": "Evening Reflection",
                "category": "mindfulness",
                "time_of_day": "evening",
                "mood": "reflective"
            },
            {
                "id": 10,
                "quote": "Una habitación oscura, fresca y silenciosa es el templo sagrado del sueño reparador.",
                "author": "Sleep Environment Expert",
                "category": "sleep_hygiene",
                "time_of_day": "evening",
                "mood": "educational"
            },
            
            # Consejos de higiene del sueño
            {
                "id": 11,
                "quote": "La cafeína permanece en tu sistema hasta 8 horas. Planifica tu última taza sabiamente.",
                "author": "Sleep Science",
                "category": "sleep_hygiene",
                "time_of_day": "evening",
                "mood": "educational"
            },
            {
                "id": 12,
                "quote": "Tu cama es solo para dormir y relajarte. Mantenla como un santuario de descanso.",
                "author": "Sleep Hygiene Pro",
                "category": "sleep_hygiene",
                "time_of_day": "evening",
                "mood": "motivational"
            },
            {
                "id": 13,
                "quote": "Respirar profundamente por 4 segundos, mantener por 7, exhalar por 8. La técnica 4-7-8 para el sueño.",
                "author": "Dr. Andrew Weil",
                "category": "techniques",
                "time_of_day": "night",
                "mood": "calm"
            },
            {
                "id": 14,
                "quote": "La luz azul de las pantallas confunde a tu cerebro. Dale una hora de descanso antes de dormir.",
                "author": "Circadian Rhythm Expert",
                "category": "sleep_hygiene",
                "time_of_day": "evening",
                "mood": "educational"
            },
            {
                "id": 15,
                "quote": "Dormir no es tiempo perdido, es inversión en tu salud, productividad y felicidad del mañana.",
                "author": "Productivity Coach",
                "category": "motivation",
                "time_of_day": "night",
                "mood": "motivational"
            }
        ]
        
        return [SleepQuote(**quote_data) for quote_data in quotes_data]
    
    def get_random_quote(self, **filters) -> SleepQuote:
        """Obtiene una cita aleatoria con filtros opcionales"""
        filtered_quotes = self.quotes
        
        for key, value in filters.items():
            if key in ['category', 'time_of_day', 'mood']:
                filtered_quotes = [q for q in filtered_quotes if getattr(q, key) == value]
        
        if not filtered_quotes:
            filtered_quotes = self.quotes
        
        return random.choice(filtered_quotes)
    
    def get_quote_by_time(self) -> SleepQuote:
        """Obtiene una cita apropiada para la hora actual"""
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 18:
            time_filter = "morning"  # Usar citas motivacionales
        elif 18 <= current_hour < 22:
            time_filter = "evening"
        else:
            time_filter = "night"
        
        return self.get_random_quote(time_of_day=time_filter)
    
    def get_sleep_tip(self) -> SleepQuote:
        """Obtiene un consejo específico de higiene del sueño"""
        return self.get_random_quote(category="sleep_hygiene")
    
    def search_quotes(self, query: str) -> List[SleepQuote]:
        """Busca citas por palabra clave"""
        query_lower = query.lower()
        matching_quotes = []
        
        for quote in self.quotes:
            if (query_lower in quote.quote.lower() or 
                query_lower in quote.author.lower() or
                query_lower in quote.category.lower()):
                matching_quotes.append(quote)
        
        return matching_quotes[:5]  # Limitar a 5 resultados

# Instancia global de la base de datos
sleep_db = SleepQuotesDatabase()

# Servidor MCP
mcp_server = Server("sleep-quotes")

@mcp_server.list_resources()
async def list_resources() -> List[Resource]:
    """Lista los recursos disponibles"""
    return [
        Resource(
            uri="sleep-quotes://categories",
            name="Categorías de citas",
            description="Lista de todas las categorías de citas disponibles",
            mimeType="application/json"
        ),
        Resource(
            uri="sleep-quotes://statistics", 
            name="Estadísticas de citas",
            description="Estadísticas sobre la base de datos de citas",
            mimeType="application/json"
        )
    ]

@mcp_server.read_resource()
async def read_resource(uri: str) -> str:
    """Lee un recurso específico"""
    if uri == "sleep-quotes://categories":
        categories = list(set(quote.category for quote in sleep_db.quotes))
        return json.dumps({
            "categories": categories,
            "total_categories": len(categories)
        }, indent=2)
    
    elif uri == "sleep-quotes://statistics":
        stats = {
            "total_quotes": len(sleep_db.quotes),
            "categories": {},
            "time_periods": {},
            "moods": {}
        }
        
        for quote in sleep_db.quotes:
            # Conteo por categoría
            stats["categories"][quote.category] = stats["categories"].get(quote.category, 0) + 1
            # Conteo por período del día
            stats["time_periods"][quote.time_of_day] = stats["time_periods"].get(quote.time_of_day, 0) + 1
            # Conteo por estado de ánimo
            stats["moods"][quote.mood] = stats["moods"].get(quote.mood, 0) + 1
        
        return json.dumps(stats, indent=2)
    
    else:
        raise ValueError(f"Recurso no encontrado: {uri}")

@mcp_server.list_tools()
async def list_tools() -> List[Tool]:
    """Lista las herramientas disponibles"""
    return [
        Tool(
            name="get_inspirational_quote",
            description="Obtiene una cita inspiracional para dormir",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Categoría de la cita (sleep_hygiene, mindfulness, motivation, etc.)",
                        "enum": ["sleep_hygiene", "mindfulness", "motivation", "science", "holistic", "wellness", "inspiration", "techniques"]
                    },
                    "mood": {
                        "type": "string", 
                        "description": "Estado de ánimo deseado",
                        "enum": ["calm", "motivational", "peaceful", "reflective", "educational"]
                    },
                    "time_based": {
                        "type": "boolean",
                        "description": "Si usar cita basada en la hora actual",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="get_sleep_hygiene_tip",
            description="Obtiene un consejo específico de higiene del sueño",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="search_sleep_quotes",
            description="Busca citas por palabra clave",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Palabra clave para buscar en las citas"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_bedtime_routine_reminder",
            description="Genera un recordatorio personalizado para la rutina de sueño",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_bedtime": {
                        "type": "string",
                        "description": "Hora de dormir del usuario (HH:MM)",
                        "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
                    },
                    "reminder_type": {
                        "type": "string",
                        "description": "Tipo de recordatorio",
                        "enum": ["preparation", "relaxation", "environment", "mindfulness"]
                    }
                }
            }
        ),
        Tool(
            name="get_daily_sleep_wisdom",
            description="Obtiene sabiduría diaria sobre el sueño con cita y consejo",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_tip": {
                        "type": "boolean",
                        "description": "Incluir consejo práctico además de la cita",
                        "default": True
                    }
                }
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Ejecuta una herramienta específica"""
    
    if name == "get_inspirational_quote":
        try:
            filters = {}
            if "category" in arguments:
                filters["category"] = arguments["category"]
            if "mood" in arguments:
                filters["mood"] = arguments["mood"]
            
            if arguments.get("time_based", False):
                quote = sleep_db.get_quote_by_time()
            else:
                quote = sleep_db.get_random_quote(**filters)
            
            current_time = datetime.now().strftime("%H:%M")
            
            response = f"""🌙 CITA INSPIRACIONAL PARA DORMIR 🌙

"{quote.quote}"

— {quote.author}

📅 Hora: {current_time}
🏷️  Categoría: {quote.category.replace('_', ' ').title()}
💭 Estado: {quote.mood.title()}
⏰ Momento: {quote.time_of_day.replace('_', ' ').title()}

✨ Que tengas dulces sueños ✨"""
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error obteniendo cita: {str(e)}")]
    
    elif name == "get_sleep_hygiene_tip":
        try:
            tip = sleep_db.get_sleep_tip()
            
            response = f"""💡 CONSEJO DE HIGIENE DEL SUEÑO 💡

{tip.quote}

— {tip.author}

🎯 Esta es tu recomendación personalizada para mejorar tu calidad de sueño.

💤 Recuerda: Pequeños cambios en tus hábitos pueden generar grandes mejoras en tu descanso."""
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error obteniendo consejo: {str(e)}")]
    
    elif name == "search_sleep_quotes":
        try:
            query = arguments["query"]
            results = sleep_db.search_quotes(query)
            
            if not results:
                response = f"""🔍 BÚSQUEDA: "{query}"

❌ No se encontraron citas que coincidan con tu búsqueda.

💡 Intenta con términos como: sueño, descanso, noche, relajación, paz"""
            else:
                response = f"""🔍 RESULTADOS DE BÚSQUEDA: "{query}"

📚 Encontré {len(results)} cita(s) para ti:

"""
                for i, quote in enumerate(results, 1):
                    response += f"""
{i}. "{quote.quote}"
   — {quote.author} | {quote.category.replace('_', ' ').title()}

"""
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error en búsqueda: {str(e)}")]
    
    elif name == "get_bedtime_routine_reminder":
        try:
            bedtime = arguments.get("user_bedtime", "22:00")
            reminder_type = arguments.get("reminder_type", "preparation")
            
            reminders = {
                "preparation": f"""🛏️ RECORDATORIO DE PREPARACIÓN PARA DORMIR

🕘 Tu hora de dormir: {bedtime}

✅ Lista de preparación (1 hora antes):
• Apaga dispositivos electrónicos
• Prepara tu ropa para mañana
• Ajusta la temperatura del cuarto (18-20°C)
• Toma un baño o ducha tibia

💫 "La preparación adecuada es el primer paso hacia un sueño reparador"
— Sleep Coach Expert""",
                
                "relaxation": f"""🧘 RECORDATORIO DE RELAJACIÓN

🕘 Tu hora de dormir: {bedtime}

🌸 Técnicas de relajación (30 min antes):
• Respiración 4-7-8: Inhala 4, mantén 7, exhala 8
• Lectura de un libro relajante
• Música suave o sonidos de la naturaleza
• Meditación o mindfulness

💤 "La relajación es la llave que abre la puerta al sueño profundo"
— Mindfulness Master""",
                
                "environment": f"""🏡 RECORDATORIO DE AMBIENTE

🕘 Tu hora de dormir: {bedtime}

🌙 Optimiza tu ambiente de sueño:
• Habitación oscura (cortinas opacas)
• Silencio o ruido blanco
• Temperatura fresca (18-20°C)
• Colchón y almohada cómodos

🌟 "Tu dormitorio es el templo sagrado del descanso"
— Environment Expert""",
                
                "mindfulness": f"""🧠 RECORDATORIO MINDFULNESS

🕘 Tu hora de dormir: {bedtime}

💭 Práctica de atención plena:
• Reflexiona sobre 3 cosas positivas del día
• Suelta las preocupaciones del día
• Enfócate en el momento presente
• Practica gratitud

☮️ "Una mente tranquila encuentra el camino hacia el sueño reparador"
— Mindfulness Teacher"""
            }
            
            return [TextContent(type="text", text=reminders.get(reminder_type, reminders["preparation"]))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error generando recordatorio: {str(e)}")]
    
    elif name == "get_daily_sleep_wisdom":
        try:
            include_tip = arguments.get("include_tip", True)
            
            # Obtener cita basada en la hora
            quote = sleep_db.get_quote_by_time()
            
            current_date = datetime.now().strftime("%A, %d de %B")
            current_time = datetime.now().strftime("%H:%M")
            
            response = f"""📖 SABIDURÍA DIARIA DEL SUEÑO 📖

📅 {current_date} • {current_time}

🌟 CITA DEL DÍA:
"{quote.quote}"
— {quote.author}

"""
            
            if include_tip:
                tip = sleep_db.get_sleep_tip()
                response += f"""💡 CONSEJO PRÁCTICO:
{tip.quote}

🎯 Aplica este consejo hoy y observa cómo mejora tu descanso nocturno.

"""
            
            response += """🌙 Que tengas un día productivo y una noche de sueño reparador. 🌙"""
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error obteniendo sabiduría diaria: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"❌ Herramienta desconocida: {name}")]

# FastAPI para despliegue web
app = FastAPI(
    title="Sleep Quotes MCP Server",
    description="Servidor MCP remoto para citas inspiracionales y consejos de sueño",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raíz con información del servidor"""
    return {
        "name": "Sleep Quotes MCP Server",
        "version": "1.0.0",
        "description": "Servidor MCP remoto para citas inspiracionales y consejos de sueño",
        "status": "running",
        "total_quotes": len(sleep_db.quotes),
        "categories": list(set(quote.category for quote in sleep_db.quotes)),
        "endpoints": {
            "health": "/health",
            "quote": "/api/quote",
            "tip": "/api/tip", 
            "search": "/api/search/{query}",
            "wisdom": "/api/wisdom",
            "mcp": "/mcp"
        }
    }

@app.get("/health")
async def health_check():
    """Verificación de salud del servidor"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "quotes_loaded": len(sleep_db.quotes)
    }

@app.get("/api/quote")
async def get_quote_api(
    category: Optional[str] = None,
    mood: Optional[str] = None,
    time_based: bool = False
):
    """API REST para obtener citas"""
    try:
        filters = {}
        if category:
            filters["category"] = category
        if mood:
            filters["mood"] = mood
        
        if time_based:
            quote = sleep_db.get_quote_by_time()
        else:
            quote = sleep_db.get_random_quote(**filters)
        
        return {
            "quote": asdict(quote),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tip")
async def get_tip_api():
    """API REST para obtener consejos de higiene del sueño"""
    try:
        tip = sleep_db.get_sleep_tip()
        return {
            "tip": asdict(tip),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search/{query}")
async def search_quotes_api(query: str, limit: int = 5):
    """API REST para buscar citas"""
    try:
        results = sleep_db.search_quotes(query)[:limit]
        return {
            "query": query,
            "results": [asdict(quote) for quote in results],
            "total_found": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wisdom")
async def get_wisdom_api(include_tip: bool = True):
    """API REST para obtener sabiduría diaria"""
    try:
        quote = sleep_db.get_quote_by_time()
        response = {
            "daily_quote": asdict(quote),
            "timestamp": datetime.now().isoformat()
        }
        
        if include_tip:
            tip = sleep_db.get_sleep_tip()
            response["daily_tip"] = asdict(tip)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint MCP para comunicación WebSocket o HTTP
@app.post("/mcp")
async def mcp_endpoint(request: Dict[str, Any]):
    """Endpoint para comunicación MCP"""
    try:
        # Simular llamada MCP
        method = request.get("method", "get_inspirational_quote")
        params = request.get("params", {})
        
        # Procesar según el método
        if method == "get_inspirational_quote":
            quote = sleep_db.get_random_quote()
            return {"result": asdict(quote)}
        elif method == "get_sleep_hygiene_tip":
            tip = sleep_db.get_sleep_tip()
            return {"result": asdict(tip)}
        else:
            return {"error": f"Método desconocido: {method}"}
            
    except Exception as e:
        return {"error": str(e)}

async def main():
    """Función principal para ejecutar el servidor MCP"""
    # Ejecutar servidor MCP via stdio
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sleep-quotes",
                server_version="1.0.0",
                capabilities=mcp_server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    # Determinar modo de ejecución
    mode = os.getenv("RUN_MODE", "mcp")
    
    if mode == "web":
        # Modo web para despliegue
        port = int(os.getenv("PORT", 8000))
        uvicorn.run(
            "sleep_quotes_mcp_server:app",
            host="0.0.0.0",
            port=port,
            reload=False
        )
    else:
        # Modo MCP estándar
        asyncio.run(main())