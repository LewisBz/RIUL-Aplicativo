"""Datos de referencia del dominio de logros (catálogos, no datos demo).

`levels`, `badges` y `achievement_types` son tablas de catálogo: la migración
0004 las siembra y `seed_reference_data()` las mantiene idempotentes.
"""

XP_PER_LEVEL = 200
MAX_LEVEL = 20

# (level_number, min_xp, stars)
LEVELS = [
    (number, (number - 1) * XP_PER_LEVEL, min(5, number))
    for number in range(1, MAX_LEVEL + 1)
]

# (name, description, icon)
BADGES = [
    ("Participante de eventos", "Participó en un evento institucional.", "event"),
    ("Voz de la comunidad", "Aportó contenido valioso al feed.", "forum"),
    ("Investigador de proyectos", "Contribuyó a un proyecto de investigación.", "science"),
    ("Publicador académico", "Publicó un artículo académico.", "article"),
    ("Ponente", "Presentó una ponencia o producto.", "slideshow"),
    ("Innovador", "Registró una patente.", "lightbulb"),
    ("Líder de semillero", "Impulsó un semillero de investigación.", "groups"),
]

# (code, name, icon, xp_value, badge_name)
ACHIEVEMENT_TYPES = [
    ("event", "Participación en evento", "event", 20, "Participante de eventos"),
    ("post", "Publicación destacada", "forum", 10, "Voz de la comunidad"),
    ("project", "Proyecto de investigación", "science", 100, "Investigador de proyectos"),
    ("article", "Artículo académico", "article", 150, "Publicador académico"),
    ("presentation", "Ponencia", "slideshow", 80, "Ponente"),
    ("patent", "Patente", "lightbulb", 300, "Innovador"),
    ("semillero", "Aporte a semillero", "groups", 50, "Líder de semillero"),
]
