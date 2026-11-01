/** Adaptadores API (snake_case) -> modelos de vista que consumen las páginas. */

const PROJECT_STATUS = { planned: 'Planeado', in_progress: 'En curso', review: 'Revisión', completed: 'Completado' };
const PRODUCT_STATUS = { in_review: 'En revisión', approved: 'Aprobado' };
const PUBLICATION_STATUS = { published: 'Publicado', in_review: 'En Revisión' };
const ACHIEVEMENT_STATUS = { validated: 'Validado', in_review: 'En revisión', rejected: 'Rechazado' };
const MEMBER_ROLE = { member: 'Estudiante Investigador', co_leader: 'Co-líder Estudiantil' };
const NOTIFICATION_ICON = {
  achievement: 'check_circle', event: 'event', project: 'folder', semillero: 'account_tree', account: 'verified_user',
};
const ROLE_LABEL = { researcher: 'Investigador', leader: 'Docente Líder', administrator: 'Administrador' };
const TONES = ['teal', 'secondary', 'error', 'primary'];

const MEMBER_TONES = {
  primary: { bg: 'var(--primary-fixed-dim)', fg: 'var(--on-primary-fixed)' },
  secondary: { bg: 'var(--secondary-container)', fg: 'var(--on-secondary-container)' },
  teal: { bg: 'var(--tertiary-fixed)', fg: 'var(--on-tertiary-fixed)' },
  error: { bg: 'var(--error-container)', fg: 'var(--on-error-container)' },
};

export function memberTone(tone) {
  return MEMBER_TONES[tone] ?? MEMBER_TONES.primary;
}

export const roleLabel = (role) => ROLE_LABEL[role] ?? role;
export const projectStatusLabel = (status) => PROJECT_STATUS[status] ?? status;
export const publicationStatusLabel = (status) => PUBLICATION_STATUS[status] ?? status;

const parseDate = (iso) => new Date(`${iso}T00:00:00`);
const dayMonth = (iso) => (iso ? parseDate(iso).toLocaleDateString('es-CO', { day: '2-digit', month: 'long' }) : '');
const monthYear = (iso) => (iso ? parseDate(iso).toLocaleDateString('es-CO', { month: 'short', year: 'numeric' }) : '');
export const isoDate = (iso) => (iso ? parseDate(iso).toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' }) : '—');

export function toSemillero(api) {
  return {
    id: api.slug,
    name: api.name,
    faculty: api.faculty?.name ?? 'Sin facultad',
    program: api.program?.name ?? 'Sin programa',
    area: api.area ?? 'General',
    description: api.description ?? '',
    leader: api.leader?.full_name ?? 'Por asignar',
    memberCount: api.member_count,
    icon: api.icon,
    topBadge: api.top_badge,
    myRole: api.my_role,
  };
}

export function toSemilleroDetail(api) {
  const base = toSemillero(api);
  return {
    ...base,
    detail: {
      affiliation: api.affiliation,
      about: api.about ?? '',
      mission: api.mission ?? '',
      vision: api.vision ?? '',
      interestAreas: api.interest_areas,
      leaderTitle: api.leader?.title ?? '',
      members: api.members.map((member, index) => ({
        initials: member.initials,
        name: member.full_name ?? 'Sin nombre',
        role: MEMBER_ROLE[member.role] ?? member.role,
        tone: TONES[index % TONES.length],
      })),
      lines: api.lines.map((line) => ({ ...line, coordinator: line.coordinator ?? 'Por asignar' })),
      projects: api.projects.map((project) => ({
        title: project.title,
        tag: project.type ?? 'Proyecto',
        description: project.description ?? '',
        role: project.role_required ? `Rol requerido: ${project.role_required}` : '',
        status: PROJECT_STATUS[project.status] ?? project.status,
      })),
      publications: api.publications.map((pub) => ({
        title: pub.title,
        venue: pub.venue ?? '',
        date: monthYear(pub.published_on),
        status: PUBLICATION_STATUS[pub.status] ?? pub.status,
      })),
      activities: api.activities.map((activity) => ({
        date: dayMonth(activity.occurred_on),
        title: activity.title,
        place: activity.place ?? '',
      })),
    },
  };
}

export function toProject(api) {
  return {
    id: api.slug,
    title: api.title,
    type: api.type ?? 'Proyecto',
    status: PROJECT_STATUS[api.status] ?? api.status,
    statusCode: api.status,
    faculty: api.faculty ?? 'Sin facultad',
    seedbed: api.semillero?.name ?? 'Sin semillero',
    leader: api.leader?.full_name ?? '—',
    description: api.description ?? '',
    progress: api.progress,
    startDate: api.start_date ? isoDate(api.start_date) : '—',
    endDate: api.end_date ? isoDate(api.end_date) : '—',
    line: api.line ?? '—',
    myRole: api.my_role,
    products: (api.products ?? []).map((p) => ({ type: p.type, name: p.name, status: PRODUCT_STATUS[p.status] ?? p.status })),
    members: (api.members ?? []).map((m) => m.full_name ?? 'Sin nombre'),
    milestones: (api.milestones ?? []).map((m) => ({ id: m.id, text: m.text, done: m.done })),
  };
}

export function toEvent(api) {
  const isCall = api.kind === 'call';
  const closed = api.status === 'closed';
  const full = api.participation === 'full';
  return {
    id: api.slug,
    kind: api.kind,
    title: api.title,
    description: api.description ?? '',
    type: api.type ?? (isCall ? 'Convocatoria' : 'Evento'),
    status: closed ? 'Cerrado' : full ? 'Sin cupos' : isCall ? 'Abierta' : 'Abierto',
    startDate: api.starts_at,
    endDate: api.ends_at,
    location: api.location ?? 'Por definir',
    capacity: api.capacity,
    registered: api.registered_count,
    organizer: api.organizer ?? '—',
    requirements: api.requirements,
    participation: api.participation,
    participationStatus: api.participation === 'registered' ? 'registered' : closed ? 'closed' : 'available',
    members: [api.organizer ?? '—'],
    timeline: [
      { text: isCall ? 'Convocatoria publicada' : 'Inscripciones abiertas', done: true },
      { text: closed ? 'Actividad finalizada' : isCall ? 'Cierre de postulaciones' : 'Evento presencial', done: closed },
    ],
  };
}

export function toNotification(api) {
  return {
    id: api.id,
    type: api.type,
    icon: NOTIFICATION_ICON[api.type] ?? 'notifications',
    title: api.title,
    text: api.text,
    createdAt: api.created_at,
    read: api.read,
    href: api.href,
  };
}

export function toAchievement(api) {
  return {
    id: api.id,
    icon: api.icon,
    title: api.title,
    description: api.description ?? '',
    status: ACHIEVEMENT_STATUS[api.status] ?? api.status,
    xp: api.xp,
    date: api.achieved_on,
  };
}

export function toGamification(api) {
  return {
    level: api.level,
    xp: api.xp,
    nextLevelXp: api.next_level_xp,
    stars: api.stars,
    totalStars: api.total_stars,
    badges: api.badges,
    achievements: api.achievements.map(toAchievement),
  };
}

export function toRankingEntry(api) {
  return {
    position: api.position,
    name: api.full_name ?? 'Sin nombre',
    role: roleLabel(api.role),
    xp: api.xp,
    isCurrentUser: api.is_current_user,
  };
}
