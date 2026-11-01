from marshmallow import Schema, ValidationError, fields, validate, validates_schema

from app.models import REPORT_KINDS
from app.schemas.projects import iso


class ReportCreateSchema(Schema):
    kind = fields.Str(
        required=True,
        validate=validate.OneOf(REPORT_KINDS, error="Tipo de reporte inválido."),
    )
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)

    @validates_schema
    def check_period(self, data, **kwargs):
        if data.get("period_start") and data.get("period_end"):
            if data["period_end"] < data["period_start"]:
                raise ValidationError(
                    "El fin del periodo no puede ser anterior al inicio.", "period_end"
                )


class ReportListQuerySchema(Schema):
    kind = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.OneOf(REPORT_KINDS, error="Tipo de reporte inválido."),
    )


def serialize_report(report, with_metrics: bool = True) -> dict:
    payload = {
        "id": report.id,
        "kind": report.kind,
        "period_start": iso(report.period_start),
        "period_end": iso(report.period_end),
        "published": report.is_published,
        "published_at": iso(report.published_at),
        "created_at": iso(report.created_at),
        "generated_by": {"id": report.author.id, "full_name": report.author.full_name},
    }
    if with_metrics:
        payload["metrics"] = report.metrics_json
    return payload
