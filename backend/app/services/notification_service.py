from app.models import Notification, PRIORITY_NORMAL
from app.repositories import engagement_repository
from app.utils.errors import ServiceError


def notify(
    user_id: int,
    type: str,
    title: str,
    text: str,
    href: str | None = None,
    priority: str = PRIORITY_NORMAL,
    entity: tuple[str, int] | None = None,
) -> Notification:
    """Registra una notificación. El commit lo realiza el servicio llamador.

    `entity` es la pareja ``(entity_kind, entity_id)`` del recurso al que se refiere.
    """
    entity_kind, entity_id = entity if entity else (None, None)
    return engagement_repository.add_notification(
        Notification(
            user_id=user_id,
            type=type,
            title=title,
            text=text[:500],
            href=href,
            priority=priority,
            entity_kind=entity_kind,
            entity_id=entity_id,
        )
    )


def list_notifications(user_id: int, unread_only: bool = False):
    items = engagement_repository.list_notifications(user_id, unread_only)
    return items, engagement_repository.count_unread(user_id)


def mark_read(user_id: int, notification_id: int, read: bool = True) -> Notification:
    notification = engagement_repository.get_notification(notification_id, user_id)
    if notification is None:
        raise ServiceError("Notificación no encontrada.", 404)
    notification.is_read = read
    engagement_repository.commit()
    return notification


def mark_all_read(user_id: int) -> None:
    engagement_repository.mark_all_read(user_id)
    engagement_repository.commit()
