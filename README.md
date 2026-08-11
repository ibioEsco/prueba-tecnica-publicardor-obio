# LinkedIn COBOL Engine

Motor de contenido autónomo para generar y publicar posts de LinkedIn dirigidos a desarrolladores COBOL y profesionales de mainframe, con la voz de Juan Lucas Barbier.

## Requisitos

- Python 3.11+
- Node.js 18+
- Gemini API key

## Setup en 4 pasos

```bash
# 1. Backend
cd backend
cp .env.example .env
# Editar .env y poner tu GEMINI_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 2. Frontend (nueva terminal)
cd frontend
npm install
npm run dev
# Abre http://localhost:5173
```

## Flujo completo

1. **Ingresa un tema** en el campo de texto (EN o ES)
2. **El motor genera** — post con voz JLB + prompt de imagen + score de viralidad
3. **Revisa el post** — texto, imagen generada, score con razones
4. **Decide** — Aprobar / Editar inline / Descartar / Regenerar
5. **Publica** — real (con token OAuth) o simulado (honestamente etiquetado)
6. **Historial** — estado visible de cada pieza: draft, approved, discarded, published, simulated

## Variables de entorno

| Variable | Requerida | Descripción |
|---|---|---|
| `GEMINI_API_KEY` | ✓ | API key de Google AI Studio |
| `LINKEDIN_ACCESS_TOKEN` | Opcional | Token OAuth para publicación real |
| `LINKEDIN_AUTHOR_URN` | Opcional | `urn:li:person:<id>` del autor |

Sin `LINKEDIN_ACCESS_TOKEN`, todas las publicaciones se ejecutan en modo simulado — se muestra el payload exacto que se enviaría, y el post queda marcado como `simulated` (nunca como `published`).

## Publicación real en LinkedIn

1. Crear app en https://www.linkedin.com/developers/
2. Solicitar productos: "Share on LinkedIn" + "Sign In with LinkedIn"
3. Generar token OAuth 2.0 con scopes: `r_liteprofile`, `w_member_social`
4. Agregar a `.env`: `LINKEDIN_ACCESS_TOKEN=<token>`

## Estructura

```
linkedin-cobol-engine/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── db.py                # SQLite (posts)
│   ├── services/
│   │   ├── generator.py     # Gemini text + image
│   │   ├── scorer.py        # Viral score heurístico
│   │   └── linkedin.py      # Publisher real/simulado
│   └── prompts/
│       ├── voice_jlb_en.txt # System prompt voz JLB (inglés)
│       └── voice_jlb_es.txt # System prompt voz JLB (español)
└── frontend/
    └── src/
        ├── App.jsx
        ├── components/
        │   ├── PostCard.jsx   # Card de revisión + acciones
        │   ├── ViralScore.jsx # Score visual con razones
        │   ├── StatusBadge.jsx
        │   └── History.jsx    # Tabla de historial
        └── lib/api.js
```
