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
