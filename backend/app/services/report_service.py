"""Instantáneas de analítica (`report_snapshots`).

Un reporte congela métricas de un periodo; un ranking congela el top de
usuarios y semilleros por XP. Nacen como borrador (`published_at` nulo) y la
administración los publica. El ranking "en vivo" no se almacena: se calcula
con ``ORDER BY user_progress.xp`` (ver `gamification_service.ranking`).
"""
from datetime import date, datetime, timezone

from app.models import (
    REPORT_KIND_RANKING,
    REPORT_KIND_REPORT,
    REPORT_KINDS,
    ROLE_ADMINISTRATOR,
    ReportSnapshot,
    User,
)
from app.repositories import analytics_repository, report_repository
from app.services import admin_service
from app.utils.errors import ServiceError

RANKING_SIZE = 10


def _require_admin(actor: User) -> None:
    if actor.role != ROLE_ADMINISTRATOR:
        raise ServiceError("Se requieren permisos de administrador.", 403)


def _report_metrics(start: date, end: date) -> dict:
    analytics = admin_service.analytics()
    return {
        "period": analytics_repository.period_counts(start, end),
        "totals": analytics["totals"],
        "semilleros_by_faculty": analytics["semilleros_by_faculty"],
        "top_semilleros": analytics["top_semilleros"],
        "account_status": analytics["account_status"],
    }


def _ranking_metrics() -> dict:
    return {
        "users": [
            {"position": index, "full_name": name, "xp": xp}
            for index, (name, xp) in enumerate(
                analytics_repository.top_users_by_xp(RANKING_SIZE), start=1
            )
        ],
        "semilleros": [
            {"position": index, "name": name, "faculty": faculty, "xp": xp}
            for index, (name, faculty, xp) in enumerate(
                analytics_repository.top_semilleros_by_xp(RANKING_SIZE), start=1
            )
        ],
    }


def generate(actor: User, kind: str, period_start: date, period_end: date) -> ReportSnapshot:
    _require_admin(actor)
    if kind not in REPORT_KINDS:
        raise ServiceError("Tipo de reporte inválido.", 400)
    if period_end < period_start:
        raise ServiceError("El fin del periodo no puede ser anterior al inicio.", 400)
    metrics = (
        _ranking_metrics()
        if kind == REPORT_KIND_RANKING
        else _report_metrics(period_start, period_end)
    )
    report = report_repository.add(
        ReportSnapshot(
            generated_by=actor.id,
            kind=kind,
            period_start=period_start,
            period_end=period_end,
            metrics_json=metrics,
        )
    )
    report_repository.commit()
    return report


def get_or_404(report_id: int) -> ReportSnapshot:
    report = report_repository.get(report_id)
    if report is None:
        raise ServiceError("Reporte no encontrado.", 404)
    return report


def publish(actor: User, report_id: int) -> ReportSnapshot:
    _require_admin(actor)
    report = get_or_404(report_id)
    if report.published_at is not None:
        raise ServiceError("El reporte ya está publicado.", 409)
    report.published_at = datetime.now(timezone.utc).replace(tzinfo=None)
    report_repository.commit()
    return report


def list_reports(actor: User, kind: str | None = None) -> list[ReportSnapshot]:
    _require_admin(actor)
    if kind and kind not in REPORT_KINDS:
        raise ServiceError("Tipo de reporte inválido.", 400)
    return report_repository.list_reports(kind=kind)


def list_published(kind: str | None = None) -> list[ReportSnapshot]:
    if kind and kind not in REPORT_KINDS:
        raise ServiceError("Tipo de reporte inválido.", 400)
    return report_repository.list_reports(kind=kind, published_only=True)


def get_published_or_404(report_id: int) -> ReportSnapshot:
    report = get_or_404(report_id)
    if report.published_at is None:
        raise ServiceError("Reporte no encontrado.", 404)
    return report
