export const PROJECTS_SUMMARY = [
  { id: 'proyecto-analisis-datos', title: 'Proyecto A: Análisis de Datos', status: 'En curso' },
  { id: 'proyecto-redes-neuronales', title: 'Proyecto B: Redes Neuronales Aplicadas', status: 'Revisión' },
  { id: 'proyecto-sensores-campus', title: 'Proyecto C: Sensores IoT para Campus', status: 'En curso' },
];

export const PROJECTS = [
  {
    id: 'proyecto-analisis-datos',
    title: 'Análisis predictivo del rendimiento académico',
    type: 'Investigación aplicada',
    status: 'En curso',
    faculty: 'Ingeniería',
    seedbed: 'Semillero Alpha',
    leader: 'Laura Mendoza',
    description: 'Modelo para identificar factores asociados al rendimiento académico y orientar intervenciones tempranas.',
    progress: 68,
    startDate: '2025-02-10',
    endDate: '2026-11-30',
    line: 'Ciencia de datos',
    products: [
      { type: 'Artículo', name: 'Modelo de predicción académica', status: 'En revisión' },
      { type: 'Informe', name: 'Base anonimizada de resultados', status: 'Aprobado' },
    ],
    members: ['Laura Mendoza', 'Andrés Pérez', 'Camila Rojas'],
    milestones: [
      { text: 'Definición de variables', done: true },
      { text: 'Entrenamiento del modelo', done: true },
      { text: 'Validación con la comunidad', done: false },
    ],
  },
  {
    id: 'proyecto-redes-neuronales',
    title: 'Redes neuronales aplicadas a la educación',
    type: 'Desarrollo tecnológico',
    status: 'Revisión',
    faculty: 'Ciencias básicas',
    seedbed: 'Semillero Beta',
    leader: 'Javier Torres',
    description: 'Exploración de modelos interpretables para apoyar la retroalimentación personalizada en cursos universitarios.',
    progress: 42,
    startDate: '2025-08-01',
    endDate: '2027-03-15',
    line: 'Inteligencia artificial',
    products: [{ type: 'Ponencia', name: 'Redes interpretables en educación', status: 'En revisión' }],
    members: ['Javier Torres', 'Sofía Díaz'],
    milestones: [
      { text: 'Revisión bibliográfica', done: true },
      { text: 'Prototipo inicial', done: false },
    ],
  },
  {
    id: 'proyecto-sensores-campus',
    title: 'Sensores IoT para campus sostenible',
    type: 'Innovación',
    status: 'Planeado',
    faculty: 'Ingeniería',
    seedbed: 'Semillero Gamma',
    leader: 'Mateo Silva',
    description: 'Red de sensores para observar consumo energético y condiciones ambientales en espacios universitarios.',
    progress: 12,
    startDate: '2026-09-01',
    endDate: '2027-12-20',
    line: 'Internet de las cosas',
    products: [],
    members: ['Mateo Silva'],
    milestones: [{ text: 'Diseño de arquitectura', done: false }],
  },
];

export const EVENTS = [
  {
    id: 'simposio-investigacion-2026',
    kind: 'event',
    title: 'V Simposio Internacional de Investigación',
    description: 'Encuentro para compartir resultados, metodologías y nuevas alianzas de investigación.',
    type: 'Simposio',
    status: 'Abierto',
    startDate: '2026-11-13T18:00:00',
    endDate: '2026-11-14T18:00:00',
    location: 'Auditorio A',
    capacity: 180,
    registered: 124,
    organizer: 'Dirección de Investigación',
    requirements: ['Registro previo', 'Documento de identidad institucional'],
    participationStatus: 'registered',
    members: ['Dirección de Investigación', 'Laura Mendoza'],
    timeline: [{ text: 'Inscripciones abiertas', done: true }, { text: 'Evento presencial', done: false }],
  },
  {
    id: 'taller-datos-abiertos',
    kind: 'event',
    title: 'Taller de datos abiertos para investigadores',
    description: 'Sesión práctica sobre documentación, publicación y reutilización responsable de datos.',
    type: 'Taller',
    status: 'Abierto',
    startDate: '2026-12-04T09:00:00',
    endDate: '2026-12-04T12:00:00',
    location: 'Sala B',
    capacity: 40,
    registered: 19,
    organizer: 'Semillero Alpha',
    requirements: ['Llevar computador portátil'],
    participationStatus: 'available',
    members: ['Camila Rojas'],
    timeline: [{ text: 'Cupos disponibles', done: true }],
  },
  {
    id: 'convocatoria-semilleros-2027',
    kind: 'call',
    title: 'Convocatoria de fortalecimiento a semilleros 2027',
    description: 'Presenta una propuesta para fortalecer las capacidades y productos de tu semillero.',
    type: 'Convocatoria',
    status: 'Abierta',
    startDate: '2026-11-01T00:00:00',
    endDate: '2027-01-30T23:59:00',
    location: 'Virtual',
    capacity: null,
    registered: null,
    organizer: 'Vicerrectoría de Investigación',
    requirements: ['Propuesta de trabajo', 'Presupuesto estimado', 'Aval del semillero'],
    participationStatus: 'pending',
    members: ['Vicerrectoría de Investigación'],
    timeline: [{ text: 'Convocatoria publicada', done: true }, { text: 'Cierre de postulaciones', done: false }],
  },
  {
    id: 'encuentro-innovacion-2025',
    kind: 'event',
    title: 'Encuentro de innovación y transferencia',
    description: 'Jornada de presentación de prototipos y productos de investigación universitaria.',
    type: 'Encuentro',
    status: 'Cerrado',
    startDate: '2025-10-18T08:00:00',
    endDate: '2025-10-18T17:00:00',
    location: 'Auditorio A',
    capacity: 100,
    registered: 100,
    organizer: 'Centro de Innovación',
    requirements: [],
    participationStatus: 'closed',
    members: ['Centro de Innovación'],
    timeline: [{ text: 'Evento finalizado', done: true }],
  },
];

export const PUBLICATIONS = [
  { icon: 'article', title: 'Optimización de Modelos Predictivos', meta: 'Nature • 2025' },
  { icon: 'article', title: 'Redes Neuronales en Educación', meta: 'IEEE • 2024' },
];

export const SEMILLERO = {
  name: 'Semillero Alpha',
  members: '20 Miembros activos',
  activities: '3 Actividades este mes',
};

export const NOTIFICATIONS = [
  { id: 'notification-achievement', type: 'achievement', icon: 'check_circle', title: 'Logro validado', text: 'Tu participación en el V Simposio fue validada.', createdAt: '2026-08-20T10:30:00', read: false, priority: 'high', href: '/gamification' },
  { id: 'notification-event', type: 'event', icon: 'event', title: 'Próximo evento', text: 'El Taller de datos abiertos comienza pronto.', createdAt: '2026-08-18T14:00:00', read: false, priority: 'normal', href: '/event-detail?id=taller-datos-abiertos' },
  { id: 'notification-message', type: 'message', icon: 'mail', title: 'Mensaje de docente guía', text: 'Tienes un nuevo mensaje sobre tu proyecto.', createdAt: '2026-08-15T09:15:00', read: true, priority: 'normal', href: '/profile' },
  { id: 'notification-project', type: 'project', icon: 'folder', title: 'Avance de proyecto', text: 'Se registró una actualización en tu proyecto.', createdAt: '2026-08-12T16:45:00', read: true, priority: 'low', href: '/projects' },
];

export const GAMIFICATION = {
  level: 5,
  xp: 148,
  nextLevelXp: 200,
  stars: 4,
  totalStars: 5,
};

export const RANKING = [
  { position: 1, name: 'Laura Mendoza', role: 'Investigadora', xp: 2140 },
  { position: 2, name: 'Javier Torres', role: 'Investigador', xp: 1890 },
  { position: 3, name: 'Camila Rojas', role: 'Investigadora', xp: 1760, isCurrentUser: true },
  { position: 4, name: 'Mateo Silva', role: 'Investigador', xp: 1520 },
];

export const BADGES = [
  { icon: 'workspace_premium', title: 'Publicador Destacado', highlighted: true },
  { icon: 'military_tech', title: 'Participante Evento' },
  { icon: 'group', title: 'Líder Semillero' },
];

export const MY_SEMILLEROS = [
  { name: 'Semillero Alpha', role: 'Rol: Miembro' },
  { name: 'Semillero Beta', role: 'Rol: Co-líder' },
];

export const PROFILE_PROJECTS = [
  { name: 'Sistema de evaluación lúdica', meta: 'Rol: Investigador Principal - Estado: Activo' },
];

export const PROFILE_PUBLICATIONS = [
  { title: 'Optimización de Modelos Predictivos', venue: 'Nature', date: '2025-03-12' },
  { title: 'Redes Neuronales en Educación', venue: 'IEEE Access', date: '2024-11-02' },
];

export const PRODUCTS = [
  { type: 'Patente', name: 'Sistema de evaluación lúdica', status: 'Aprobado' },
  { type: 'Artículo', name: 'Modelo predictivo académico', status: 'En revisión' },
];

export const ACHIEVEMENTS = [
  { text: 'Ponencia Validada – Registrado / Validado', done: true },
  { text: 'Participación en Encuentro de Semilleros', done: false },
];

export const GAMIFICATION_ACHIEVEMENTS = [
  {
    id: 'achievement-simposio',
    icon: 'event',
    title: 'Participante destacado',
    description: 'Participación en el V Simposio Internacional',
    status: 'Validado',
    xp: 50,
    date: '2026-06-14',
  },
  {
    id: 'achievement-publication',
    icon: 'article',
    title: 'Publicador académico',
    description: 'Artículo publicado en una revista indexada',
    status: 'En revisión',
    xp: 120,
    date: '2026-05-20',
  },
  {
    id: 'achievement-seedbed',
    icon: 'groups',
    title: 'Líder de semillero',
    description: 'Acompañamiento a un semillero de investigación',
    status: 'Validado',
    xp: 80,
    date: '2026-03-10',
  },
];

const MEMBER_TONES = {
  primary: { bg: 'var(--primary-fixed-dim)', fg: 'var(--on-primary-fixed)' },
  secondary: { bg: 'var(--secondary-container)', fg: 'var(--on-secondary-container)' },
  teal: { bg: 'var(--tertiary-fixed)', fg: 'var(--on-tertiary-fixed)' },
  error: { bg: 'var(--error-container)', fg: 'var(--on-error-container)' },
};

export function memberTone(tone) {
  return MEMBER_TONES[tone] ?? MEMBER_TONES.primary;
}

export const SEMILLEROS = [
  {
    id: 'ita',
    name: 'Innovación Tecnológica Aplicada (ITA)',
    faculty: 'Ingeniería',
    program: 'Ingeniería de Sistemas',
    area: 'Inteligencia Artificial',
    description:
      'Desarrollo de soluciones tecnológicas innovadoras aplicadas a problemas reales de la industria y la sociedad.',
    leader: 'Dra. María Antonieta Pérez',
    memberCount: 12,
    icon: 'memory',
    topBadge: null,
    detail: {
      affiliation: 'Facultad de Ingeniería - Unidad Académica de Sistemas',
      about:
        'El semillero ITA se enfoca en el desarrollo de soluciones tecnológicas innovadoras aplicadas a problemas reales de la industria y la sociedad, fomentando la investigación activa entre los estudiantes de pregrado.',
      mission: 'Formar investigadores con alta capacidad técnica y crítica para liderar proyectos tecnológicos.',
      vision: 'Ser referente nacional en innovación aplicada y patentes universitarias para el 2026.',
      interestAreas: ['Inteligencia Artificial', 'Internet de las Cosas (IoT)', 'Ciberseguridad'],
      leaderTitle: 'Ph.D. en Ciencias de la Computación',
      members: [
        { initials: 'LG', name: 'Luis Grandett', role: 'Estudiante Investigador', tone: 'teal' },
        { initials: 'HL', name: 'Hector Leon', role: 'Estudiante Investigador', tone: 'secondary' },
        { initials: 'JS', name: 'Javier Solano', role: 'Co-líder Estudiantil', tone: 'error' },
        { initials: 'CM', name: 'Carolina Martínez', role: 'Estudiante Investigador', tone: 'primary' },
        { initials: 'DP', name: 'David Pérez', role: 'Estudiante Investigador', tone: 'teal' },
        { initials: 'SR', name: 'Sara Rodríguez', role: 'Estudiante Investigador', tone: 'secondary' },
      ],
      lines: [
        { icon: 'memory', name: 'IoT para Agricultura de Precisión', coordinator: 'Javier Solano' },
        { icon: 'security', name: 'Ciberseguridad en Redes Académicas', coordinator: 'Luis Grandett' },
      ],
      projects: [
        {
          title: 'Prototipo de Sensores de Humedad de Bajo Costo',
          tag: 'Prototipo',
          description: 'Diseño e implementación de nodos sensores usando ESP32 para cultivos de tomate en el Atlántico.',
          role: 'Rol requerido: Desarrollador C++ / Hardware',
          status: 'En Desarrollo',
        },
        {
          title: 'Algoritmo de Detección de Anomalías de Red',
          tag: 'Artículo',
          description: 'Estudio de modelos de Machine Learning aplicados al tráfico de red universitario.',
          role: 'Rol requerido: Data Scientist (Python)',
          status: 'Fase de Pruebas',
        },
      ],
      publications: [
        { title: 'Low-cost IoT Sensors for Tomato Crops', venue: 'IEEE Latin America Transactions', date: 'Oct 2023', status: 'Publicado' },
        { title: 'ML-based Intrusion Detection in SDN', venue: 'Congreso Colombiano de Computación', date: 'Nov 2023', status: 'En Revisión' },
      ],
      activities: [
        { date: '01 Junio', title: 'Ponencia Validada', place: 'Simposio Nacional de Investigación' },
        { date: '15 Mayo', title: 'Taller de Redacción Científica', place: 'Participación en Evento Interno' },
        { date: '28 Abril', title: 'Reunión de Seguimiento', place: 'Sesión interna del semillero' },
      ],
    },
  },
  {
    id: 'datalab',
    name: 'DataLab - RIUL',
    faculty: 'Ingeniería',
    program: 'Ingeniería Estadística',
    area: 'Ciencia de Datos',
    description: 'Minería de datos aplicada a la deserción estudiantil universitaria.',
    leader: 'Dr. Javier Solano',
    memberCount: 22,
    icon: 'monitoring',
    topBadge: 'Top 5%',
    detail: {
      affiliation: 'Facultad de Ingeniería - Unidad Académica de Estadística',
      about:
        'DataLab aplica técnicas de minería de datos y aprendizaje automático a problemas institucionales, con énfasis en analítica educativa y retención estudiantil.',
      mission: 'Transformar datos institucionales en decisiones académicas basadas en evidencia.',
      vision: 'Consolidarse como laboratorio de analítica referente en la región Caribe.',
      interestAreas: ['Minería de Datos', 'Analítica Educativa', 'Machine Learning'],
      leaderTitle: 'Ph.D. en Estadística Aplicada',
      members: [
        { initials: 'AG', name: 'Ana Gómez', role: 'Estudiante Investigador', tone: 'teal' },
        { initials: 'RM', name: 'Ricardo Mejía', role: 'Co-líder Estudiantil', tone: 'secondary' },
        { initials: 'LT', name: 'Laura Torres', role: 'Estudiante Investigador', tone: 'primary' },
        { initials: 'JN', name: 'Julio Navarro', role: 'Estudiante Investigador', tone: 'error' },
      ],
      lines: [
        { icon: 'school', name: 'Analítica de Deserción Estudiantil', coordinator: 'Ricardo Mejía' },
        { icon: 'insights', name: 'Modelos Predictivos Académicos', coordinator: 'Laura Torres' },
      ],
      projects: [
        {
          title: 'Modelo de Alerta Temprana de Deserción',
          tag: 'Artículo',
          description: 'Clasificación de estudiantes en riesgo usando históricos académicos de la Universidad.',
          role: 'Rol requerido: Científico de Datos (Python/R)',
          status: 'Fase de Pruebas',
        },
      ],
      publications: [
        { title: 'Early Dropout Prediction with Ensemble Models', venue: 'Revista Ibérica de Sistemas', date: 'Mar 2024', status: 'Publicado' },
      ],
      activities: [
        { date: '10 Junio', title: 'Hackathon de Datos Abiertos', place: 'Competencia nacional' },
        { date: '20 Mayo', title: 'Seminario de Visualización', place: 'Evento interno RIUL' },
      ],
    },
  },
  {
    id: 'sia',
    name: 'Semillero de Inteligencia Artificial (SIA)',
    faculty: 'Ingeniería',
    program: 'Ingeniería de Sistemas',
    area: 'Inteligencia Artificial',
    description: 'Investigación aplicada en modelos de aprendizaje profundo para la resolución de problemas regionales.',
    leader: 'Dra. Elena Ríos',
    memberCount: 12,
    icon: 'psychology',
    topBadge: null,
    detail: {
      affiliation: 'Facultad de Ingeniería - Unidad Académica de Sistemas',
      about:
        'SIA investiga modelos de aprendizaje profundo y visión por computadora enfocados en problemáticas del Caribe colombiano.',
      mission: 'Impulsar la adopción responsable de la inteligencia artificial en la región.',
      vision: 'Publicar investigación de impacto internacional con participación estudiantil activa.',
      interestAreas: ['Deep Learning', 'Visión por Computadora', 'Procesamiento de Lenguaje Natural'],
      leaderTitle: 'Ph.D. en Inteligencia Artificial',
      members: [
        { initials: 'MV', name: 'Mateo Vargas', role: 'Estudiante Investigador', tone: 'teal' },
        { initials: 'CL', name: 'Camila López', role: 'Co-líder Estudiantil', tone: 'secondary' },
        { initials: 'AO', name: 'Andrés Ospina', role: 'Estudiante Investigador', tone: 'primary' },
      ],
      lines: [
        { icon: 'visibility', name: 'Visión Artificial para Agricultura', coordinator: 'Mateo Vargas' },
      ],
      projects: [
        {
          title: 'Detección de Plagas con Redes Convolucionales',
          tag: 'Prototipo',
          description: 'Clasificación de plagas en cultivos de banana usando imágenes de campo.',
          role: 'Rol requerido: Desarrollador Python / TensorFlow',
          status: 'En Desarrollo',
        },
      ],
      publications: [
        { title: 'CNN-based Pest Detection for Banana Crops', venue: 'Symposium on AI Applications', date: 'Ago 2023', status: 'Publicado' },
      ],
      activities: [
        { date: '05 Junio', title: 'Charla: IA Generativa', place: 'Auditorio Facultad de Ingeniería' },
      ],
    },
  },
  {
    id: 'energias',
    name: 'Grupo de Energías Renovables',
    faculty: 'Ingeniería',
    program: 'Ingeniería Mecánica',
    area: 'Sostenibilidad',
    description: 'Desarrollo de prototipos para la optimización de energía eólica en zonas costeras.',
    leader: 'Dr. Carlos Mendoza',
    memberCount: 8,
    icon: 'wind_power',
    topBadge: null,
    detail: {
      affiliation: 'Facultad de Ingeniería - Unidad Académica de Mecánica',
      about:
        'El grupo diseña y evalúa prototipos de aprovechamiento eólico y solar adaptados a las condiciones climáticas de la región costera.',
      mission: 'Contribuir a la transición energética mediante investigación aplicada.',
      vision: 'Ser el grupo de referencia en energía eólica costera a nivel universitario.',
      interestAreas: ['Energía Eólica', 'Energía Solar', 'Eficiencia Energética'],
      leaderTitle: 'Ph.D. en Ingeniería Energética',
      members: [
        { initials: 'PF', name: 'Paula Fernández', role: 'Estudiante Investigador', tone: 'teal' },
        { initials: 'DG', name: 'Diego Gutiérrez', role: 'Co-líder Estudiantil', tone: 'secondary' },
      ],
      lines: [
        { icon: 'wind_power', name: 'Microgeneración Eólica Costera', coordinator: 'Diego Gutiérrez' },
      ],
      projects: [
        {
          title: 'Turbina Eólica de Bajo Costo para Zonas Rurales',
          tag: 'Prototipo',
          description: 'Diseño de aerogenerador de eje vertical para comunidades sin acceso eléctrico.',
          role: 'Rol requerido: Diseño CAD / Simulación CFD',
          status: 'En Desarrollo',
        },
      ],
      publications: [
        { title: 'Low-cost Vertical Axis Wind Turbines', venue: 'Journal of Renewable Energy', date: 'Feb 2024', status: 'En Revisión' },
      ],
      activities: [
        { date: '18 Mayo', title: 'Visita Técnica al Parque Eólico', place: 'Guajira' },
      ],
    },
  },
  {
    id: 'biotec',
    name: 'Biotecnología Aplicada',
    faculty: 'Ciencias Básicas',
    program: 'Biología',
    area: 'Sostenibilidad',
    description: 'Estudio de microorganismos para la biorremediación de suelos contaminados en el Atlántico.',
    leader: 'MSc. Ana Valle',
    memberCount: 15,
    icon: 'biotech',
    topBadge: null,
    detail: {
      affiliation: 'Facultad de Ciencias Básicas - Unidad Académica de Biología',
      about:
        'El semillero estudia consorcios microbianos nativos capaces de degradar hidrocarburos en suelos agrícolas del departamento del Atlántico.',
      mission: 'Generar soluciones biotecnológicas para la recuperación de ecosistemas degradados.',
      vision: 'Transferir tecnología de biorremediación a actores productivos regionales.',
      interestAreas: ['Biorremediación', 'Microbiología', 'Química Ambiental'],
      leaderTitle: 'MSc. en Microbiología',
      members: [
        { initials: 'VC', name: 'Valeria Cruz', role: 'Estudiante Investigador', tone: 'teal' },
        { initials: 'SM', name: 'Sebastián Molina', role: 'Co-líder Estudiantil', tone: 'secondary' },
        { initials: 'NA', name: 'Natalia Ariza', role: 'Estudiante Investigador', tone: 'primary' },
      ],
      lines: [
        { icon: 'biotech', name: 'Consorcios Microbianos Nativos', coordinator: 'Valeria Cruz' },
      ],
      projects: [
        {
          title: 'Cepario de Bacillus para Suelos Degradados',
          tag: 'Artículo',
          description: 'Caracterización de cepas bacterianas con potencial degradador de hidrocarburos.',
          role: 'Rol requerido: Biólogo / Químico',
          status: 'En Desarrollo',
        },
      ],
      publications: [
        { title: 'Native Bacterial Consortia for Hydrocarbon Remediation', venue: 'Revista de Biología Tropical', date: 'Dic 2023', status: 'Publicado' },
      ],
      activities: [
        { date: '22 Mayo', title: 'Muestreo de Suelos', place: 'Campo experimental' },
      ],
    },
  },
  {
    id: 'redes',
    name: 'Análisis de Redes Sociales',
    faculty: 'Ciencias Sociales',
    program: 'Comunicación Social',
    area: 'Ciencias Sociales',
    description: 'Investigación sobre el impacto de las redes digitales en el comportamiento político local.',
    leader: 'Dr. Luis Grandett',
    memberCount: 6,
    icon: 'share',
    topBadge: null,
    detail: {
      affiliation: 'Facultad de Ciencias Sociales - Unidad Académica de Comunicación',
      about:
        'El semillero analiza conversaciones digitales y dinámicas de opinión pública en redes sociales durante periodos electorales locales.',
      mission: 'Comprender críticamente el papel de las plataformas digitales en la democracia local.',
      vision: 'Convertirse en observatorio regional de opinión digital.',
      interestAreas: ['Opinión Pública', 'Comunicación Digital', 'Análisis de Redes'],
      leaderTitle: 'Ph.D. en Comunicación Política',
      members: [
        { initials: 'IB', name: 'Isabela Blanco', role: 'Estudiante Investigador', tone: 'teal' },
        { initials: 'TR', name: 'Tomás Restrepo', role: 'Co-líder Estudiantil', tone: 'secondary' },
      ],
      lines: [
        { icon: 'forum', name: 'Observatorio de Opinión Digital', coordinator: 'Isabela Blanco' },
      ],
      projects: [
        {
          title: 'Monitoreo de Tendencias Electorales 2026',
          tag: 'Artículo',
          description: 'Análisis de sentimiento sobre candidaturas locales en X e Instagram.',
          role: 'Rol requerido: Analista de Datos / Comunicador',
          status: 'Fase de Pruebas',
        },
      ],
      publications: [
        { title: 'Digital Networks and Local Politics in Colombia', venue: 'Palabra Clave', date: 'Sep 2023', status: 'En Revisión' },
      ],
      activities: [
        { date: '02 Junio', title: 'Panel: Elecciones y Redes', place: 'Universidad Libre' },
      ],
    },
  },
];
