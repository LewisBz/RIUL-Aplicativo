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
  { icon: 'check_circle', text: 'Aprobación de logros' },
  { icon: 'mail', text: 'Mensaje de Docente Guía' },
];

export const GAMIFICATION = {
  level: 5,
  xp: 148,
  nextLevelXp: 200,
  stars: 4,
  totalStars: 5,
};

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
