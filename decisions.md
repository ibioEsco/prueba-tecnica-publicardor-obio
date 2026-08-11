# Decisiones y supuestos

## Voz de Juan Lucas Barbier

**Supuesto principal:** La voz se inferió a partir de dos publicaciones públicas. Las características definitorias son:

- **Hook de una línea** que funciona como aforismo o contradicción. La primera línea no presenta contexto; aterriza una conclusión.
- **Densidad técnica real** — nombres de productos específicos (JCL, BSDS, GDPS, z15), no "herramientas legacy". Esto es lo que diferencia el contenido de JLB del copy genérico de IA.
- **Párrafos muy cortos**, incluyendo oraciones únicas usadas como pausas dramáticas.
- **Estructura de revelación** — empieza con lo que la gente cree, construye hacia lo que realmente ocurre, termina con un reencuadre (no un resumen ni una pregunta de engagement).
- **Sin signos de exclamación, emojis ni CTAs** — registro técnico adulto.

Los prompts de voz están en `backend/prompts/` y son editables. Agregar más posts de JLB mejora directamente la calidad de generación.

## Scorer de viralidad

**Decisión:** Modelo heurístico explícito, no ML.

No existe historial de datos de JLB. Un modelo ML entrenado en contenido genérico de LinkedIn introduciría ruido disfrazado de ciencia. El scorer heurístico tiene 5 señales con pesos documentados:

| Señal | Peso | Qué mide |
|---|---|---|
| Hook strength | 25 | ¿La primera línea detiene el scroll? |
| Technical specificity | 25 | ¿Tiene nombres de productos reales? |
| Controversy / Position | 20 | ¿El post toma una posición? |
| Pacing | 15 | ¿Hay párrafos cortos y ritmo? |
| Ending quality | 15 | ¿Termina con reencuadre, no pregunta? |

El score influye en la UI: <40 = "Needs work" en rojo, 40–70 = "Publish with edits" en ámbar, >70 = "High potential" en verde. Esto cambia la decisión real del usuario.

## Modo simulado de LinkedIn

**Decisión:** Honestidad explícita sobre el estado.

Sin token OAuth, el producto muestra exactamente qué payload enviaría, qué endpoint usaría y qué permisos requiere. El post queda con status `simulated` con badge naranja "⚠ SIMULATED" — nunca con `published`. Una simulación presentada como publicación real invalida la confianza en el producto.

## Idioma

**Decisión:** Selector EN/ES, posts en inglés por defecto.

Las dos publicaciones de JLB disponibles están en inglés. La audiencia de COBOL/mainframe es internacional. Se mantienen los términos técnicos en inglés en ambos idiomas porque así los conoce la audiencia.

## Stack

- **FastAPI** sobre Flask/Django — async nativo, Pydantic integrado, mínima boilerplate para una API de demostración.
- **SQLite** sobre Postgres — cero infraestructura, demo portable en cualquier máquina.
- **Gemini 1.5 Flash** — API key disponible, suficiente para generación de texto y construcción de prompts de imagen. Imagen 3 requiere acceso separado; el fallback es un SVG placeholder honesto con el prompt visible.
- **React + Vite** sin dependencias de UI — el diseño es custom porque el nicho (mainframe) tiene una estética reconocible (terminal verde, tipografía monoespaciada) que debe reflejarse en la herramienta.

## Qué haría con una semana adicional

1. **Feedback loop** — registrar qué posts aprueba JLB vs descarta para ajustar el scorer con datos reales en lugar de heurísticas.
2. **Fuentes de ideas automáticas** — conectar Hacker News API, LinkedIn trending topics y RSS de blogs de mainframe para sugerir temas sin input manual.
3. **Múltiples variantes** — generar 3 versiones por tema con distintos hooks, presentar las 3 con scores comparativos.
4. **Scheduler** — publicación automática en horario óptimo (martes/miércoles 8-10am hora del autor) con Celery o APScheduler.
5. **Editor de voz** — interfaz para que JLB agregue sus propias publicaciones como ejemplos, refinando el system prompt sin tocar código.
6. **Analytics simulados** — mock de engagement proyectado basado en score, para dar contexto al número sin inventar datos reales.
