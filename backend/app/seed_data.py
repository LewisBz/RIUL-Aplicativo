"""Conjunto de datos de demostración de la plataforma RIUL.

Fuente única de verdad del paquete de datos sembrado por `flask seed-demo`.
Documentación completa: docs/tablas-y-datos.md
"""
from datetime import datetime

# --- Facultades y programas ---
SEED_FACULTIES = {
    "Ingeniería": ["Ingeniería de Sistemas", "Ingeniería Industrial"],
    "Ciencias Básicas": ["Biología"],
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