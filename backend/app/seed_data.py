"""Conjunto de datos de demostración de la plataforma RIUL.

Fuente única de verdad del paquete de datos sembrado por `flask seed-demo`.
Documentación completa: docs/tablas-y-datos.md
"""
from datetime import datetime

# --- Facultades y programas ---
SEED_FACULTIES = {
    "Ingeniería": [
        "Ingeniería de Sistemas",
        "Ingeniería Industrial",
        "Ingeniería Estadística",
        "Ingeniería Mecánica",
    ],
    "Ciencias Básicas": ["Biología"],
    "Ciencias Sociales": ["Comunicación Social"],
}

# --- Usuarios ---
# Relaciones expresadas por rol + facultad/programa:
#   - administrator  -> nivel plataforma, sin facultad asignada.
#   - leader         -> docente que guía a investigadores de su misma
#                       facultad/programa (relación de mentoría).
#   - researcher     -> estudiante investigador vinculado a su líder por
#                       facultad/programa.
SEED_DEMO_USERS = [
    # Administradores (2)
    {
        "full_name": "Ana Sofía Restrepo",
        "email": "ana.restrepo@unilibre.edu.co",
        "role": "administrator",
        "status": "active",
        "faculty": None,
        "program": None,
        "motivation": None,
    },
    {
        "full_name": "Leonardo Pardo Roa",
        "email": "leonardo.pardo@unilibre.edu.co",
        "role": "administrator",
        "status": "active",
        "faculty": None,
        "program": None,
        "motivation": None,
    },
    # Líderes / docentes (4)
    {
        "full_name": "Laura Mendoza",
        "email": "laura.mendoza@unilibre.edu.co",
        "role": "leader",
        "status": "active",
        "faculty": "Ingeniería",
        "program": "Ingeniería de Sistemas",
        "motivation": None,
    },
    {
        "full_name": "María Antonieta Pérez",
        "email": "maria.antonieta.perez@unilibre.edu.co",
        "role": "leader",
        "status": "active",
        "faculty": "Ingeniería",
        "program": "Ingeniería de Sistemas",
        "motivation": None,
    },
    {
        "full_name": "Mateo Silva",
        "email": "mateo.silva@unilibre.edu.co",
        "role": "leader",
        "status": "active",
        "faculty": "Ingeniería",
        "program": "Ingeniería Industrial",
        "motivation": None,
    },
    {
        "full_name": "Javier Torres",
        "email": "javier.torres@unilibre.edu.co",
        "role": "leader",
        "status": "active",
        "faculty": "Ciencias Básicas",
        "program": "Biología",
        "motivation": None,
    },
    # Investigadores activos (7), cada uno bajo su líder
    {
        "full_name": "Camila Rojas",
        "email": "camila.rojas@unilibre.edu.co",
        "role": "researcher",
        "status": "active",
        "faculty": "Ingeniería",
        "program": "Ingeniería de Sistemas",
        "motivation": None,
    },
    {
        "full_name": "Andrés Pérez",
        "email": "andres.perez@unilibre.edu.co",
        "role": "researcher",
        "status": "active",
        "faculty": "Ingeniería",
        "program": "Ingeniería de Sistemas",
        "motivation": None,
    },
    {
        "full_name": "Luis Grandett",
        "email": "luis.grandett@unilibre.edu.co",
        "role": "researcher",
        "status": "active",
        "faculty": "Ingeniería",
        "program": "Ingeniería de Sistemas",
        "motivation": None,
    },
    {
        "full_name": "Carolina Martínez",
        "email": "carolina.martinez@unilibre.edu.co",
        "role": "researcher",
        "status": "active",
        "faculty": "Ingeniería",
        "program": "Ingeniería de Sistemas",
        "motivation": None,
    },
    {
        "full_name": "Diego Gutiérrez",
        "email": "diego.gutierrez@unilibre.edu.co",
        "role": "researcher",
        "status": "active",
        "faculty": "Ingeniería",
        "program": "Ingeniería Industrial",
        "motivation": None,
    },
    {
        "full_name": "Paula Fernández",
        "email": "paula.fernandez@unilibre.edu.co",
        "role": "researcher",
        "status": "active",
        "faculty": "Ingeniería",
        "program": "Ingeniería Industrial",
        "motivation": None,
    },
    {
        "full_name": "Sofía Díaz",
        "email": "sofia.diaz@unilibre.edu.co",
        "role": "researcher",
        "status": "active",
        "faculty": "Ciencias Básicas",
        "program": "Biología",
        "motivation": None,
    },
    # Solicitud pendiente (externa) — login bloqueado hasta aprobación
    {
        "full_name": "Isabela Blanco",
        "email": "isabela.blanco@gmail.com",
        "role": "researcher",
        "status": "pending",
        "faculty": "Ciencias Básicas",
        "program": "Biología",
        "motivation": (
            "Quiero integrarme al proyecto de biorremediación de suelos "
            "contaminados en el Atlántico y aportar desde mi experiencia en "
            "microbiología aplicada."
        ),
    },
    # Solicitud rechazada (externa) — login bloqueado
    {
        "full_name": "Tomás Restrepo",
        "email": "tomas.restrepo@hotmail.com",
        "role": "researcher",
        "status": "rejected",
        "faculty": "Ingeniería",
        "program": "Ingeniería de Sistemas",
        "motivation": "Colaboración externa en proyectos de ciberseguridad.",
    },
]

# --- Publicaciones (15, todas las categorías) ---
SEED_DEMO_POSTS = [
    {
        "author": "laura.mendoza@unilibre.edu.co",
        "category": "event",
        "content": (
            "¡Llegó el V Simposio Internacional de Investigación! Del 13 al 14 de "
            "noviembre en el Auditorio A. Inscripciones abiertas en el portal de "
            "eventos. Es el espacio ideal para presentar resultados, metodologías "
            "y formar alianzas de investigación."
        ),
        "link_url": "https://eventos.unilibre.edu.co/simposio-investigacion-2026",
        "created_at": datetime(2026, 9, 12, 10, 30),
    },
    {
        "author": "laura.mendoza@unilibre.edu.co",
        "category": "project_advance",
        "content": (
            "Avance del modelo predictivo de rendimiento académico: superamos el "
            "87% de precisión en las pruebas iniciales. El siguiente hito es la "
            "validación con datos reales de la comunidad estudiantil. Gracias al "
            "equipo por el excelente trabajo."
        ),
        "link_url": None,
        "created_at": datetime(2026, 9, 11, 9, 0),
    },
    {
        "author": "camila.rojas@unilibre.edu.co",
        "category": "event",
        "content": (
            "Taller de datos abiertos para investigadores — 4 de diciembre, 9:00 "
            "a.m., Sala B. Traigan su portátil: trabajaremos con los datasets "
            "institucionales publicados por la Dirección de Investigación. "
            "Cupos: 40."
        ),
        "link_url": None,
        "created_at": datetime(2026, 9, 10, 15, 20),
    },
    {
        "author": "camila.rojas@unilibre.edu.co",
        "category": "article",
        "content": (
            "Comparto con la comunidad nuestra publicación 'Optimización de "
            "Modelos Predictivos', resultado del proyecto liderado por la profe "
            "Laura Mendoza. Disponible para descarga en el enlace."
        ),
        "link_url": "https://doi.org/10.1234/riul.2026.014",
        "created_at": datetime(2026, 9, 9, 11, 45),
    },
    {
        "author": "andres.perez@unilibre.edu.co",
        "category": "community",
        "content": (
            "Convocatoria abierta para la validación del modelo predictivo con la "
            "comunidad estudiantil. Buscamos estudiantes de todos los programas "
            "que quieran participar en las pruebas y aportar datos. Escríbanme "
            "por interno si les interesa."
        ),
        "link_url": None,
        "created_at": datetime(2026, 9, 8, 16, 10),
    },
    {
        "author": "maria.antonieta.perez@unilibre.edu.co",
        "category": "community",
        "content": (
            "El Semillero ITA abre cupos para el segundo semestre. Focos: "
            "Inteligencia Artificial, IoT y Ciberseguridad. Coordinación: Luis "
            "Grandett (ciberseguridad) y Javier Solano (IoT para agricultura de "
            "precisión). ¡Envía tu carta de motivación!"
        ),
        "link_url": None,
        "created_at": datetime(2026, 9, 7, 10, 0),
    },
    {
        "author": "maria.antonieta.perez@unilibre.edu.co",
        "category": "article",
        "content": (
            "Publicado 'Low-cost IoT Sensors for Tomato Crops' en IEEE Latin "
            "America Transactions. Es el resultado del proyecto de sensores de "
            "humedad de bajo costo del semillero ITA."
        ),
        "link_url": "https://doi.org/10.1109/riul.2023.0089",
        "created_at": datetime(2026, 9, 6, 14, 30),
    },
    {
        "author": "luis.grandett@unilibre.edu.co",
        "category": "project_advance",
        "content": (
            "Línea de Ciberseguridad en Redes Académicas: el modelo de detección "
            "de anomalías superó las pruebas de laboratorio con 94% de acierto. "
            "Siguiente paso: implementación piloto en un segmento de la red "
            "universitaria."
        ),
        "link_url": None,
        "created_at": datetime(2026, 9, 5, 9, 15),
    },
    {
        "author": "carolina.martinez@unilibre.edu.co",
        "category": "community",
        "content": (
            "Dejamos la memoria del taller práctico de sensores ESP32: diagramas, "
            "código y fotografías de los prototipos construidos. Cualquier "
            "integrante del semillero puede pedir la carpeta para replicar el "
            "montaje."
        ),
        "link_url": None,
        "created_at": datetime(2026, 9, 4, 17, 5),
    },
    {
        "author": "mateo.silva@unilibre.edu.co",
        "category": "project_advance",
        "content": (
            "Proyecto C (Sensores IoT para campus sostenible): aprobamos la "
            "arquitectura de la red. Empezamos la instalación de los primeros 10 "
            "nodos de medición energética en el campus. Siguen los avances."
        ),
        "link_url": None,
        "created_at": datetime(2026, 9, 3, 8, 50),
    },
    {
        "author": "diego.gutierrez@unilibre.edu.co",
        "category": "presentation",
        "content": (
            "Aceptada nuestra ponencia de avance del Proyecto C en el Encuentro "
            "de Innovación y Transferencia. Presentaremos el prototipo de "
            "sensores y el tablero de consumo energético en tiempo real."
        ),
        "link_url": "https://encuentroinnovacion.unilibre.edu.co/programa",
        "created_at": datetime(2026, 9, 2, 12, 40),
    },
    {
        "author": "paula.fernandez@unilibre.edu.co",
        "category": "community",
        "content": (
            "Bitácora del muestreo energético del campus: recopilamos la primera "
            "semana de datos de iluminación y climatización en tres edificios. "
            "Los datos preliminares se publican la próxima semana."
        ),
        "link_url": None,
        "created_at": datetime(2026, 9, 1, 18, 20),
    },
    {
        "author": "javier.torres@unilibre.edu.co",
        "category": "presentation",
        "content": (
            "Ponencia 'Redes interpretables en educación' aceptada en el "
            "Congreso Colombiano de Computación. El resumen ampliado está "
            "disponible en el enlace."
        ),
        "link_url": "https://ccc2026.co/ponencias/redes-interpretables",
        "created_at": datetime(2026, 8, 31, 9, 30),
    },
    {
        "author": "sofia.diaz@unilibre.edu.co",
        "category": "project_advance",
        "content": (
            "Prototipo inicial del modelo de redes neuronales listo para pruebas. "
            "Se entrenó con datos anonimizados de plataformas educativas. "
            "Pendiente: validación con docentes del programa."
        ),
        "link_url": None,
        "created_at": datetime(2026, 8, 30, 15, 45),
    },
    {
        "author": "ana.restrepo@unilibre.edu.co",
        "category": "community",
        "content": (
            "Recordatorio de lineamientos para la comunidad RIUL: utilicen "
            "categorías descriptivas, incluyan enlace cuando compartan "
            "publicaciones y respeten las fechas de los eventos. Cualquier duda, "
            "escríbenos por el buzón institucional."
        ),
        "link_url": None,
        "created_at": datetime(2026, 8, 29, 10, 0),
    },
]

# --- Reacciones ---
# Lista alineada por índice con SEED_DEMO_POSTS: cada sublista contiene los
# emails de los usuarios relacionados que reaccionan a esa publicación.
SEED_DEMO_REACTIONS = [
    ["camila.rojas@unilibre.edu.co", "andres.perez@unilibre.edu.co", "luis.grandett@unilibre.edu.co", "carolina.martinez@unilibre.edu.co"],
    ["camila.rojas@unilibre.edu.co", "andres.perez@unilibre.edu.co", "javier.torres@unilibre.edu.co"],
    ["laura.mendoza@unilibre.edu.co", "andres.perez@unilibre.edu.co", "sofia.diaz@unilibre.edu.co"],
    ["laura.mendoza@unilibre.edu.co", "andres.perez@unilibre.edu.co", "luis.grandett@unilibre.edu.co", "ana.restrepo@unilibre.edu.co"],
    ["camila.rojas@unilibre.edu.co", "laura.mendoza@unilibre.edu.co", "sofia.diaz@unilibre.edu.co"],
    ["luis.grandett@unilibre.edu.co", "carolina.martinez@unilibre.edu.co", "ana.restrepo@unilibre.edu.co"],
    ["luis.grandett@unilibre.edu.co", "carolina.martinez@unilibre.edu.co", "mateo.silva@unilibre.edu.co"],
    ["carolina.martinez@unilibre.edu.co", "maria.antonieta.perez@unilibre.edu.co", "laura.mendoza@unilibre.edu.co"],
    ["luis.grandett@unilibre.edu.co", "maria.antonieta.perez@unilibre.edu.co", "diego.gutierrez@unilibre.edu.co"],
    ["diego.gutierrez@unilibre.edu.co", "paula.fernandez@unilibre.edu.co", "laura.mendoza@unilibre.edu.co"],
    ["paula.fernandez@unilibre.edu.co", "mateo.silva@unilibre.edu.co", "luis.grandett@unilibre.edu.co"],
    ["diego.gutierrez@unilibre.edu.co", "mateo.silva@unilibre.edu.co", "carolina.martinez@unilibre.edu.co"],
    ["sofia.diaz@unilibre.edu.co", "camila.rojas@unilibre.edu.co", "laura.mendoza@unilibre.edu.co"],
    ["javier.torres@unilibre.edu.co", "camila.rojas@unilibre.edu.co", "andres.perez@unilibre.edu.co"],
    ["laura.mendoza@unilibre.edu.co", "leonardo.pardo@unilibre.edu.co", "maria.antonieta.perez@unilibre.edu.co"],
]

# ---------------------------------------------------------------------------
# Perfiles extendidos (`user_profiles`): prefijo de correo -> (bio, ORCID, foto)
# ---------------------------------------------------------------------------
SEED_USER_PROFILES = {
    "laura.mendoza": (
        "Docente investigadora en estadística aplicada. Lidera DataLab y el Semillero de IA.",
        "0000-0002-0000-0001",
        None,
    ),
    "maria.antonieta.perez": (
        "Ph.D. en Ciencias de la Computación. Dirige el semillero ITA.",
        "0000-0002-0000-0002",
        None,
    ),
    "mateo.silva": (
        "Ingeniero industrial enfocado en eficiencia energética.",
        "0000-0002-0000-0003",
        None,
    ),
    "javier.torres": (
        "Microbiólogo. Biorremediación de suelos del Atlántico.",
        "0000-0002-0000-0004",
        None,
    ),
    "camila.rojas": (
        "Investigadora en analítica educativa y modelos predictivos.",
        "0000-0003-0000-0005",
        None,
    ),
    "luis.grandett": (
        "Estudiante investigador en IoT y ciberseguridad de redes académicas.",
        None,
        None,
    ),
}

# Comentarios: (índice de publicación en SEED_DEMO_POSTS, correo, texto, fecha)
SEED_DEMO_COMMENTS = [
    (0, "camila.rojas@unilibre.edu.co", "¡Excelente! Ya me inscribí en el simposio.", datetime(2026, 9, 12, 12, 5)),
    (0, "andres.perez@unilibre.edu.co", "¿Habrá certificado de asistencia?", datetime(2026, 9, 12, 13, 40)),
    (0, "laura.mendoza@unilibre.edu.co", "Sí, se entregará certificado a todos los asistentes.", datetime(2026, 9, 12, 14, 10)),
    (1, "javier.torres@unilibre.edu.co", "Muy buen resultado, felicitaciones al equipo.", datetime(2026, 9, 11, 11, 0)),
    (3, "ana.restrepo@unilibre.edu.co", "Gran aporte para la visibilidad de RIUL.", datetime(2026, 9, 9, 16, 30)),
    (7, "maria.antonieta.perez@unilibre.edu.co", "Cuéntanos más sobre la metodología en la próxima reunión.", datetime(2026, 9, 5, 10, 15)),
    (12, "sofia.diaz@unilibre.edu.co", "¡Orgullosa de formar parte del semillero!", datetime(2026, 8, 31, 9, 45)),
]

# Compartidos: lista alineada por índice con SEED_DEMO_POSTS (solo algunas).
SEED_DEMO_SHARES = {
    0: ["camila.rojas@unilibre.edu.co", "luis.grandett@unilibre.edu.co"],
    3: ["laura.mendoza@unilibre.edu.co"],
    6: ["carolina.martinez@unilibre.edu.co", "mateo.silva@unilibre.edu.co"],
    12: ["camila.rojas@unilibre.edu.co"],
}

# ---------------------------------------------------------------------------
# Dominio de investigación: semilleros, proyectos, productos, eventos,
# convocatorias, logros y notificaciones. Los usuarios se referencian por el
# prefijo de su correo institucional (ver SEED_DEMO_USERS).
# ---------------------------------------------------------------------------
from datetime import date  # noqa: E402

# Cada semillero: el líder se registra como miembro con rol `leader`. Los
# miembros son (usuario, rol) o (usuario, rol, estado); por defecto `active`.
SEED_SEMILLEROS = [
    {
        "name": "Innovación Tecnológica Aplicada (ITA)",
        "area": "Inteligencia Artificial",
        "icon": "memory",
        "faculty": "Ingeniería",
        "program": "Ingeniería de Sistemas",
        "leader": "maria.antonieta.perez",
        "leader_title": "Ph.D. en Ciencias de la Computación",
        "description": "Desarrollo de soluciones tecnológicas innovadoras aplicadas a problemas reales de la industria y la sociedad.",
        "affiliation": "Facultad de Ingeniería - Unidad Académica de Sistemas",
        "about": "El semillero ITA se enfoca en soluciones tecnológicas aplicadas a problemas reales de la industria y la sociedad, fomentando la investigación activa entre estudiantes de pregrado.",
        "mission": "Formar investigadores con alta capacidad técnica y crítica para liderar proyectos tecnológicos.",
        "vision": "Ser referente nacional en innovación aplicada y patentes universitarias para el 2026.",
        "interest_areas": ["Inteligencia Artificial", "Internet de las Cosas (IoT)", "Ciberseguridad"],
        "members": [
            ("luis.grandett", "member"),
            ("camila.rojas", "member"),
            ("carolina.martinez", "member"),
            ("andres.perez", "member"),
            ("diego.gutierrez", "co_leader"),
            ("paula.fernandez", "member", "pending"),
        ],
        "lines": [
            ("memory", "IoT para Agricultura de Precisión", "Diego Gutiérrez"),
            ("security", "Ciberseguridad en Redes Académicas", "Luis Grandett"),
        ],
        "activities": [
            (date(2026, 6, 1), "Ponencia Validada", "Simposio Nacional de Investigación"),
            (date(2026, 5, 15), "Taller de Redacción Científica", "Evento interno"),
        ],
    },
    {
        "name": "DataLab - RIUL",
        "area": "Ciencia de Datos",
        "icon": "monitoring",
        "top_badge": "Top 5%",
        "faculty": "Ingeniería",
        "program": "Ingeniería Estadística",
        "leader": "laura.mendoza",
        "leader_title": "Ph.D. en Estadística Aplicada",
        "description": "Minería de datos aplicada a la deserción estudiantil universitaria.",
        "affiliation": "Facultad de Ingeniería - Unidad Académica de Estadística",
        "about": "DataLab aplica minería de datos y aprendizaje automático a problemas institucionales, con énfasis en analítica educativa y retención estudiantil.",
        "mission": "Transformar datos institucionales en decisiones académicas basadas en evidencia.",
        "vision": "Consolidarse como laboratorio de analítica referente en la región Caribe.",
        "interest_areas": ["Minería de Datos", "Analítica Educativa", "Machine Learning"],
        "members": [("camila.rojas", "co_leader"), ("andres.perez", "member"), ("paula.fernandez", "member")],
        "lines": [
            ("school", "Analítica de Deserción Estudiantil", "Camila Rojas"),
            ("insights", "Modelos Predictivos Académicos", "Andrés Pérez"),
        ],
        "activities": [
            (date(2026, 6, 10), "Hackathon de Datos Abiertos", "Competencia nacional"),
            (date(2026, 5, 20), "Seminario de Visualización", "Evento interno RIUL"),
        ],
    },
    {
        "name": "Semillero de Inteligencia Artificial (SIA)",
        "area": "Inteligencia Artificial",
        "icon": "psychology",
        "faculty": "Ingeniería",
        "program": "Ingeniería de Sistemas",
        "leader": "laura.mendoza",
        "leader_title": "Ph.D. en Inteligencia Artificial",
        "description": "Investigación aplicada en modelos de aprendizaje profundo para la resolución de problemas regionales.",
        "affiliation": "Facultad de Ingeniería - Unidad Académica de Sistemas",
        "about": "SIA investiga aprendizaje profundo y visión por computadora enfocados en problemáticas del Caribe colombiano.",
        "mission": "Impulsar la adopción responsable de la inteligencia artificial en la región.",
        "vision": "Publicar investigación de impacto internacional con participación estudiantil activa.",
        "interest_areas": ["Deep Learning", "Visión por Computadora", "Procesamiento de Lenguaje Natural"],
        "members": [("andres.perez", "co_leader"), ("sofia.diaz", "member")],
        "lines": [("visibility", "Visión Artificial para Agricultura", "Andrés Pérez")],
        "activities": [(date(2026, 6, 5), "Charla: IA Generativa", "Auditorio Facultad de Ingeniería")],
    },
    {
        "name": "Grupo de Energías Renovables",
        "area": "Sostenibilidad",
        "icon": "wind_power",
        "faculty": "Ingeniería",
        "program": "Ingeniería Mecánica",
        "leader": "mateo.silva",
        "leader_title": "Ph.D. en Ingeniería Energética",
        "description": "Desarrollo de prototipos para la optimización de energía eólica en zonas costeras.",
        "affiliation": "Facultad de Ingeniería - Unidad Académica de Mecánica",
        "about": "El grupo diseña y evalúa prototipos de aprovechamiento eólico y solar adaptados a la región costera.",
        "mission": "Contribuir a la transición energética mediante investigación aplicada.",
        "vision": "Ser el grupo de referencia en energía eólica costera a nivel universitario.",
        "interest_areas": ["Energía Eólica", "Energía Solar", "Eficiencia Energética"],
        "members": [("diego.gutierrez", "co_leader"), ("paula.fernandez", "member")],
        "lines": [("wind_power", "Microgeneración Eólica Costera", "Diego Gutiérrez")],
        "activities": [(date(2026, 5, 18), "Visita Técnica al Parque Eólico", "Guajira")],
    },
    {
        "name": "Biotecnología Aplicada",
        "area": "Sostenibilidad",
        "icon": "biotech",
        "faculty": "Ciencias Básicas",
        "program": "Biología",
        "leader": "javier.torres",
        "leader_title": "MSc. en Microbiología",
        "description": "Estudio de microorganismos para la biorremediación de suelos contaminados en el Atlántico.",
        "affiliation": "Facultad de Ciencias Básicas - Unidad Académica de Biología",
        "about": "El semillero estudia consorcios microbianos nativos capaces de degradar hidrocarburos en suelos agrícolas del Atlántico.",
        "mission": "Generar soluciones biotecnológicas para la recuperación de ecosistemas degradados.",
        "vision": "Transferir tecnología de biorremediación a actores productivos regionales.",
        "interest_areas": ["Biorremediación", "Microbiología", "Química Ambiental"],
        "members": [("sofia.diaz", "co_leader")],
        "lines": [("biotech", "Consorcios Microbianos Nativos", "Sofía Díaz")],
        "activities": [(date(2026, 5, 22), "Muestreo de Suelos", "Campo experimental")],
    },
    {
        "name": "Análisis de Redes Sociales",
        "area": "Ciencias Sociales",
        "icon": "share",
        "faculty": "Ciencias Sociales",
        "program": "Comunicación Social",
        "leader": "mateo.silva",
        "leader_title": "Docente investigador en Comunicación Digital",
        "description": "Investigación sobre el impacto de las redes digitales en el comportamiento político local.",
        "affiliation": "Facultad de Ciencias Sociales - Unidad Académica de Comunicación",
        "about": "Analiza conversaciones digitales y dinámicas de opinión pública en redes sociales durante periodos electorales locales.",
        "mission": "Comprender críticamente el papel de las plataformas digitales en la democracia local.",
        "vision": "Convertirse en observatorio regional de opinión digital.",
        "interest_areas": ["Opinión Pública", "Comunicación Digital", "Análisis de Redes"],
        "members": [("luis.grandett", "member", "rejected")],
        "lines": [("forum", "Observatorio de Opinión Digital", None)],
        "activities": [(date(2026, 6, 2), "Panel: Elecciones y Redes", "Universidad Libre")],
    },
]

# (usuario, semillero) — seguimiento sin vinculación
SEED_SEMILLERO_FOLLOWS = [
    ("camila.rojas", "Innovación Tecnológica Aplicada (ITA)"),
    ("camila.rojas", "Semillero de Inteligencia Artificial (SIA)"),
    ("sofia.diaz", "DataLab - RIUL"),
    ("paula.fernandez", "Innovación Tecnológica Aplicada (ITA)"),
    ("luis.grandett", "DataLab - RIUL"),
    ("carolina.martinez", "DataLab - RIUL"),
    ("diego.gutierrez", "Biotecnología Aplicada"),
    ("andres.perez", "Grupo de Energías Renovables"),
]

# Proyectos: el líder es el integrante con rol `principal`. Los productos son
# (tipo, título, estado) con tipo en article | presentation | patent | report.
SEED_PROJECTS = [
    {
        "title": "Análisis predictivo del rendimiento académico",
        "type": "Investigación aplicada",
        "status": "in_progress",
        "semillero": "DataLab - RIUL",
        "leader": "laura.mendoza",
        "members": ["andres.perez", "camila.rojas"],
        "description": "Modelo para identificar factores asociados al rendimiento académico y orientar intervenciones tempranas.",
        "progress": 68,
        "line": "Ciencia de datos",
        "role_required": "Científico de Datos (Python/R)",
        "start_date": date(2025, 2, 10),
        "end_date": date(2026, 11, 30),
        "products": [("article", "Modelo de predicción académica", "in_review"), ("report", "Base anonimizada de resultados", "approved")],
        "milestones": [("Definición de variables", True), ("Entrenamiento del modelo", True), ("Validación con la comunidad", False)],
    },
    {
        "title": "Redes neuronales aplicadas a la educación",
        "type": "Desarrollo tecnológico",
        "status": "review",
        "semillero": "Semillero de Inteligencia Artificial (SIA)",
        "leader": "javier.torres",
        "members": ["sofia.diaz"],
        "description": "Exploración de modelos interpretables para apoyar la retroalimentación personalizada en cursos universitarios.",
        "progress": 42,
        "line": "Inteligencia artificial",
        "role_required": "Desarrollador Python / TensorFlow",
        "start_date": date(2025, 8, 1),
        "end_date": date(2027, 3, 15),
        "products": [("presentation", "Redes interpretables en educación", "in_review")],
        "milestones": [("Revisión bibliográfica", True), ("Prototipo inicial", False)],
    },
    {
        "title": "Sensores IoT para campus sostenible",
        "type": "Innovación",
        "status": "planned",
        "semillero": "Innovación Tecnológica Aplicada (ITA)",
        "leader": "mateo.silva",
        "members": [],
        "description": "Red de sensores para observar consumo energético y condiciones ambientales en espacios universitarios.",
        "progress": 12,
        "line": "Internet de las cosas",
        "role_required": "Desarrollador C++ / Hardware",
        "start_date": date(2026, 9, 1),
        "end_date": date(2027, 12, 20),
        "products": [],
        "milestones": [("Diseño de arquitectura", False)],
    },
    {
        "title": "Prototipo de sensores de humedad de bajo costo",
        "type": "Prototipo",
        "status": "in_progress",
        "semillero": "Innovación Tecnológica Aplicada (ITA)",
        "leader": "luis.grandett",
        "members": ["diego.gutierrez", "carolina.martinez"],
        "description": "Diseño e implementación de nodos sensores usando ESP32 para cultivos de tomate en el Atlántico.",
        "progress": 55,
        "line": "IoT para Agricultura de Precisión",
        "role_required": "Desarrollador C++ / Hardware",
        "start_date": date(2026, 1, 15),
        "end_date": date(2026, 12, 15),
        "products": [("report", "Informe técnico del nodo sensor ESP32", "in_review")],
        "milestones": [("Selección de sensores", True), ("Pruebas de campo", False)],
    },
    {
        "title": "Detección de plagas con redes convolucionales",
        "type": "Prototipo",
        "status": "in_progress",
        "semillero": "Semillero de Inteligencia Artificial (SIA)",
        "leader": "andres.perez",
        "members": ["sofia.diaz"],
        "description": "Clasificación de plagas en cultivos de banano usando imágenes de campo.",
        "progress": 35,
        "line": "Visión Artificial para Agricultura",
        "role_required": "Desarrollador Python / TensorFlow",
        "start_date": date(2026, 3, 1),
        "end_date": date(2027, 2, 28),
        "products": [],
        "milestones": [("Recolección de imágenes", True), ("Entrenamiento", False)],
    },
    {
        "title": "Turbina eólica de bajo costo para zonas rurales",
        "type": "Prototipo",
        "status": "in_progress",
        "semillero": "Grupo de Energías Renovables",
        "leader": "diego.gutierrez",
        "members": ["paula.fernandez", "mateo.silva"],
        "description": "Diseño de aerogenerador de eje vertical para comunidades sin acceso eléctrico.",
        "progress": 28,
        "line": "Microgeneración Eólica Costera",
        "role_required": "Diseño CAD / Simulación CFD",
        "start_date": date(2026, 2, 1),
        "end_date": date(2027, 1, 31),
        "products": [],
        "milestones": [("Diseño CAD", True), ("Simulación CFD", False)],
    },
    {
        "title": "Observatorio de calidad del aire universitario",
        "type": "Investigación aplicada",
        "status": "closed",
        "semillero": "Biotecnología Aplicada",
        "leader": "javier.torres",
        "members": ["sofia.diaz"],
        "description": "Monitoreo de material particulado en el campus durante dos años; proyecto finalizado y entregado.",
        "progress": 100,
        "line": "Química Ambiental",
        "role_required": "Química / Estadística",
        "start_date": date(2024, 2, 1),
        "end_date": date(2025, 12, 15),
        "products": [("report", "Informe final del observatorio", "approved")],
        "milestones": [("Instalación de estaciones", True), ("Informe final", True)],
    },
]

# Productos propios sin proyecto (antes `publications`): artículos académicos.
SEED_PRODUCTS = [
    {"author": "camila.rojas", "semillero": "DataLab - RIUL", "type": "article", "title": "Optimización de Modelos Predictivos", "venue": "Nature", "published_on": date(2025, 3, 12), "status": "approved"},
    {"author": "camila.rojas", "semillero": "Innovación Tecnológica Aplicada (ITA)", "type": "article", "title": "Redes Neuronales en Educación", "venue": "IEEE Access", "published_on": date(2024, 11, 2), "status": "approved"},
    {"author": "luis.grandett", "semillero": "Innovación Tecnológica Aplicada (ITA)", "type": "article", "title": "Low-cost IoT Sensors for Tomato Crops", "venue": "IEEE Latin America Transactions", "published_on": date(2023, 10, 1), "status": "approved"},
    {"author": "laura.mendoza", "semillero": "DataLab - RIUL", "type": "article", "title": "Early Dropout Prediction with Ensemble Models", "venue": "Revista Ibérica de Sistemas", "published_on": date(2024, 3, 1), "status": "approved"},
    {"author": "diego.gutierrez", "semillero": "Grupo de Energías Renovables", "type": "article", "title": "Low-cost Vertical Axis Wind Turbines", "venue": "Journal of Renewable Energy", "published_on": date(2024, 2, 1), "status": "in_review"},
    {"author": "javier.torres", "semillero": "Biotecnología Aplicada", "type": "patent", "title": "Consorcio microbiano para degradación de hidrocarburos", "venue": "SIC Colombia", "published_on": date(2025, 6, 20), "status": "in_review"},
]

# Eventos. `registered`: usuario o (usuario, rol) con rol attendee | speaker | organizer.
SEED_EVENTS = [
    {
        "title": "V Simposio Internacional de Investigación",
        "type": "Simposio", "status": "open",
        "description": "Encuentro para compartir resultados, metodologías y nuevas alianzas de investigación.",
        "starts_at": datetime(2026, 11, 13, 18, 0), "ends_at": datetime(2026, 11, 14, 18, 0),
        "location": "Auditorio A", "capacity": 180, "organizer": "Dirección de Investigación",
        "requirements": ["Registro previo", "Documento de identidad institucional"],
        "created_by": "ana.restrepo",
        "registered": [
            ("laura.mendoza", "organizer"), "camila.rojas", "andres.perez", "luis.grandett",
        ],
    },
    {
        "title": "Taller de datos abiertos para investigadores",
        "type": "Taller", "status": "open",
        "description": "Sesión práctica sobre documentación, publicación y reutilización responsable de datos.",
        "starts_at": datetime(2026, 12, 4, 9, 0), "ends_at": datetime(2026, 12, 4, 12, 0),
        "location": "Sala B", "capacity": 40, "organizer": "DataLab - RIUL",
        "requirements": ["Llevar computador portátil"],
        "semillero": "DataLab - RIUL",
        "created_by": "laura.mendoza",
        "registered": ["paula.fernandez"],
    },
    {
        "title": "Encuentro de innovación y transferencia",
        "type": "Encuentro", "status": "closed",
        "description": "Jornada de presentación de prototipos y productos de investigación universitaria.",
        "starts_at": datetime(2025, 10, 18, 8, 0), "ends_at": datetime(2025, 10, 18, 17, 0),
        "location": "Auditorio A", "capacity": 100, "organizer": "Centro de Innovación",
        "requirements": [],
        "created_by": "ana.restrepo",
        "registered": ["laura.mendoza", ("javier.torres", "speaker")],
    },
]

# Convocatorias publicadas por la administración. Cada postulación es
# ("user", usuario, estado) o ("semillero", nombre, estado).
SEED_CALLS = [
    {
        "title": "Convocatoria de fortalecimiento a semilleros 2027",
        "type": "Convocatoria", "status": "open",
        "description": "Presenta una propuesta para fortalecer las capacidades y productos de tu semillero.",
        "starts_at": datetime(2026, 11, 1, 0, 0), "ends_at": datetime(2027, 1, 30, 23, 59),
        "location": "Virtual", "organizer": "Vicerrectoría de Investigación",
        "requirements": ["Propuesta de trabajo", "Presupuesto estimado", "Aval del semillero"],
        "published_by": "ana.restrepo",
        "applications": [
            ("semillero", "DataLab - RIUL", "accepted"),
            ("semillero", "Biotecnología Aplicada", "pending"),
            ("user", "camila.rojas", "pending"),
        ],
    },
]

# Logros. `origin` = (tipo de origen, referencia):
#   ("event", título) · ("semillero", nombre) · ("product", (autor, título))
#   · ("project", título) · ("post", índice en SEED_DEMO_POSTS)
# `xp` es el asiento del libro mayor al aprobar (None = valor del tipo).
SEED_ACHIEVEMENTS = [
    {"user": "camila.rojas", "origin": ("event", "V Simposio Internacional de Investigación"), "title": "Participante destacado", "description": "Participación en el V Simposio Internacional", "status": "approved", "xp": 50, "achieved_on": date(2026, 6, 14)},
    {"user": "camila.rojas", "origin": ("product", ("camila.rojas", "Optimización de Modelos Predictivos")), "title": "Publicador académico", "description": "Artículo publicado en una revista indexada", "status": "pending", "xp": None, "achieved_on": date(2026, 5, 20)},
    {"user": "camila.rojas", "origin": ("semillero", "DataLab - RIUL"), "title": "Líder de semillero", "description": "Acompañamiento a un semillero de investigación", "status": "approved", "xp": 80, "achieved_on": date(2026, 3, 10)},
    {"user": "laura.mendoza", "origin": ("product", ("laura.mendoza", "Early Dropout Prediction with Ensemble Models")), "title": "Publicador Destacado", "description": "Producción científica sobresaliente", "status": "approved", "xp": 600, "achieved_on": date(2026, 4, 2)},
    {"user": "laura.mendoza", "origin": ("semillero", "DataLab - RIUL"), "title": "Líder de semillero", "description": "Dirección de dos semilleros", "status": "approved", "xp": 450, "achieved_on": date(2026, 2, 12)},
    {"user": "javier.torres", "origin": ("event", "Encuentro de innovación y transferencia"), "title": "Participante Evento", "description": "Ponencia en el Encuentro de innovación", "status": "approved", "xp": 380, "achieved_on": date(2025, 10, 18)},
    {"user": "mateo.silva", "origin": ("semillero", "Grupo de Energías Renovables"), "title": "Líder de semillero", "description": "Dirección del Grupo de Energías Renovables", "status": "approved", "xp": 260, "achieved_on": date(2026, 1, 20)},
    {"user": "andres.perez", "origin": ("semillero", "DataLab - RIUL"), "title": "Participante destacado", "description": "Hackathon de Datos Abiertos", "status": "approved", "xp": 140, "achieved_on": date(2026, 6, 10)},
    {"user": "luis.grandett", "origin": ("product", ("luis.grandett", "Low-cost IoT Sensors for Tomato Crops")), "title": "Publicador académico", "description": "Artículo IEEE Latin America", "status": "approved", "xp": 210, "achieved_on": date(2023, 10, 1)},
    {"user": "javier.torres", "origin": ("project", "Observatorio de calidad del aire universitario"), "title": "Proyecto finalizado", "description": "Cierre exitoso del observatorio de calidad del aire", "status": "rejected", "xp": None, "achieved_on": date(2025, 12, 20)},
]

# (usuario, tipo, título, texto, prioridad, enlace, leída, fecha)
SEED_NOTIFICATIONS = [
    ("camila.rojas", "achievement", "Logro aprobado", "Tu participación en el V Simposio fue aprobada.", "high", "/gamification", False, datetime(2026, 8, 20, 10, 30)),
    ("camila.rojas", "event", "Próximo evento", "El Taller de datos abiertos comienza pronto.", "normal", "/event-detail?id=taller-de-datos-abiertos-para-investigadores", False, datetime(2026, 8, 18, 14, 0)),
    ("camila.rojas", "semillero", "Actividad de semillero", "DataLab registró una nueva actividad.", "normal", "/semilleros", True, datetime(2026, 8, 15, 9, 15)),
    ("camila.rojas", "project", "Avance de proyecto", "Se registró una actualización en tu proyecto.", "low", "/projects", True, datetime(2026, 8, 12, 16, 45)),
    ("laura.mendoza", "event", "Inscripción confirmada", "Quedaste inscrito en el V Simposio Internacional de Investigación.", "normal", "/events", False, datetime(2026, 10, 20, 8, 0)),
    ("maria.antonieta.perez", "semillero", "Nueva solicitud de vinculación", "Paula Fernández solicitó unirse a Innovación Tecnológica Aplicada (ITA).", "high", "/semilleros", False, datetime(2026, 10, 25, 9, 0)),
]

# Reportes generados por la administración al sembrar (`report_snapshots`):
# (tipo, inicio, fin, publicado). Los publicados se ven en /api/reports.
SEED_REPORTS = [
    ("ranking", date(2026, 1, 1), date(2026, 6, 30), True),
    ("report", date(2026, 7, 1), date(2026, 9, 30), False),
]
