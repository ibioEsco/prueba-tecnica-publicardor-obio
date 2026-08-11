"""
Viral score heuristic for COBOL/mainframe LinkedIn posts.

Scoring model (0-100) based on 5 signals observed in high-engagement
technical LinkedIn content. Each signal contributes a weighted score.
No ML — this is an explicit hypothesis, not a black box.
"""

import re

COBOL_TERMS = [
    "COBOL", "JCL", "CICS", "VSAM", "IMS", "DB2", "RACF", "ISPF", "SMF",
    "JES2", "JES3", "DASD", "zIIP", "MLC", "GDPS", "z/OS", "z15", "z16",
    "mainframe", "Db2", "BSDS", "PPRC", "HyperSwap", "Sysplex", "LPAR",
    "batch", "abend", "runbook", "SLA", "MSU", "ELA", "SCRT", "TSO",
    "REXX", "PL/I", "Assembler", "load balancer", "middleware"
]

HOOK_PATTERNS = [
    r"^\w.{0,60}\.$",
    r"^\w.{0,40}when\b",
    r"^\w.{0,40}before\b",
    r"costs more than",
    r"never made it",
    r"already left",
    r"false confidence",
    r"hide it",
    r"the gap is",
    r"was never the thing",
]

ENGAGEMENT_TRIGGERS = [
    "nobody", "never", "always", "every", "most", "all",
    "the real", "what they", "what it does not", "the fix is not",
    "they did not", "you are", "your", "IBM", "migration",
]

WEAK_SIGNALS = [
    "in today's", "landscape", "rapidly evolving", "journey",
    "excited to share", "thrilled", "delighted", "honored",
    "let me know your thoughts", "what do you think",
    "drop a comment", "don't forget to like",
    "ecosystems", "synergies", "learnings",
]


def score_post(text: str, language: str = "en") -> tuple[int, list[str]]:
    """
    Returns (score: int 0-100, reasons: list[str])
    Reasons explain both what works and what could improve.
    """
    scores = {}
    reasons = []

    # Signal 1: Hook strength (25 pts)
    first_line = text.strip().split("\n")[0].strip()
    hook_score = 0
    if len(first_line) < 80:
        hook_score += 10
    for pattern in HOOK_PATTERNS:
        if re.search(pattern, first_line, re.IGNORECASE):
            hook_score += 15
            break
    hook_score = min(hook_score, 25)
    scores["hook"] = hook_score

    if hook_score >= 20:
        reasons.append("✓ Strong opening hook — first line works as a standalone statement" if language == "en"
                       else "✓ Gancho de apertura fuerte — la primera línea funciona como declaración autónoma")
    elif hook_score >= 10:
        reasons.append("~ Hook is functional but could be sharper — try starting with a contradiction or a cost figure" if language == "en"
                       else "~ El gancho funciona pero puede ser más directo — intenta con una contradicción o un número concreto")
    else:
        reasons.append("✗ Weak hook — the first line doesn't earn a stop-scroll" if language == "en"
                       else "✗ Gancho débil — la primera línea no detiene el scroll")

    # Signal 2: Technical specificity (25 pts)
    text_upper = text.upper()
    found_terms = [t for t in COBOL_TERMS if t.upper() in text_upper]
    term_count = len(set(found_terms))
    tech_score = min(term_count * 5, 25)
    scores["technical"] = tech_score

    if tech_score >= 20:
        reasons.append(f"✓ Technically specific ({term_count} domain terms) — reads like someone who was there" if language == "en"
                       else f"✓ Específico técnicamente ({term_count} términos de dominio) — se lee como alguien que estuvo ahí")
    elif tech_score >= 10:
        reasons.append(f"~ {term_count} technical terms — add more specific product names or version numbers" if language == "en"
                       else f"~ {term_count} términos técnicos — agrega nombres de productos específicos o números de versión")
    else:
        reasons.append("✗ Low technical density — could be about any industry, not COBOL/mainframe" if language == "en"
                       else "✗ Baja densidad técnica — podría ser de cualquier industria, no COBOL/mainframe")

    # Signal 3: Controversy / Opinion sharpness (20 pts)
    controversy_score = 0
    for trigger in ENGAGEMENT_TRIGGERS:
        if trigger.lower() in text.lower():
            controversy_score += 4
    controversy_score = min(controversy_score, 20)
    scores["controversy"] = controversy_score

    if controversy_score >= 16:
        reasons.append("✓ Post takes a clear position — the audience has something to agree or disagree with" if language == "en"
                       else "✓ El post toma una posición clara — la audiencia tiene algo con qué estar de acuerdo o en desacuerdo")
    elif controversy_score >= 8:
        reasons.append("~ Position exists but could be sharper — make the implicit argument explicit" if language == "en"
                       else "~ La posición existe pero puede ser más directa — haz explícito el argumento implícito")
    else:
        reasons.append("✗ Post doesn't take a position — adds information but not a point of view" if language == "en"
                       else "✗ El post no toma posición — agrega información pero no un punto de vista")

    # Signal 4: Paragraph structure / Pacing (15 pts)
    paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    avg_len = sum(len(p.split()) for p in paragraphs) / max(len(paragraphs), 1)
    has_short_punch = any(len(p.split()) <= 6 for p in paragraphs)

    pacing_score = 0
    if 3 <= len(paragraphs) <= 8:
        pacing_score += 8
    if has_short_punch:
        pacing_score += 7
    scores["pacing"] = pacing_score

    if pacing_score >= 12:
        reasons.append("✓ Good pacing — short punchy paragraphs create rhythm" if language == "en"
                       else "✓ Buen ritmo — párrafos cortos crean cadencia")
    elif pacing_score >= 6:
        reasons.append("~ Pacing is ok — consider adding a 1-sentence paragraph for impact" if language == "en"
                       else "~ El ritmo está bien — considera agregar un párrafo de 1 oración para impacto")
    else:
        reasons.append("✗ Dense block of text — break into shorter paragraphs, including at least one single-sentence paragraph" if language == "en"
                       else "✗ Bloque de texto denso — divide en párrafos más cortos, incluye al menos un párrafo de una sola oración")

    # Signal 5: Clean ending / Reframe (15 pts)
    last_para = paragraphs[-1] if paragraphs else ""
    ending_score = 0
    weak_endings = ["let me know", "what do you think", "comment below",
                    "share your", "don't forget", "qué piensan", "déjame saber"]
    if not any(w in last_para.lower() for w in weak_endings):
        ending_score += 8
    if len(last_para.split()) <= 20:
        ending_score += 7
    scores["ending"] = ending_score

    if ending_score >= 12:
        reasons.append("✓ Strong ending — closes with a reframe, not a question" if language == "en"
                       else "✓ Final sólido — cierra con un reencuadre, no con una pregunta")
    else:
        reasons.append("✗ Ending asks for engagement — replace with a reframe or a hard conclusion" if language == "en"
                       else "✗ El final pide engagement — reemplaza con un reencuadre o una conclusión contundente")

    # Penalty: weak signal words
    weak_count = sum(1 for w in WEAK_SIGNALS if w.lower() in text.lower())
    penalty = min(weak_count * 10, 20)

    total = sum(scores.values()) - penalty
    total = max(0, min(100, total))

    if weak_count > 0:
        reasons.append(f"✗ -{penalty} pts: contains {weak_count} generic AI/LinkedIn phrase(s) — remove them" if language == "en"
                       else f"✗ -{penalty} pts: contiene {weak_count} frase(s) genérica(s) de IA/LinkedIn — elimínalas")

    return total, reasons
