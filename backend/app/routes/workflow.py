from flask import Blueprint

from app.controllers import workflow_controller

workflow_bp = Blueprint("workflow", __name__, url_prefix="/api")

workflow_bp.get("/posts/<int:post_id>/comments")(workflow_controller.list_comments)
workflow_bp.post("/posts/<int:post_id>/comments")(workflow_controller.create_comment)
workflow_bp.post("/semilleros/<string:identifier>/join")(workflow_controller.join_semillero)
workflow_bp.post("/semilleros/<string:identifier>/follow")(workflow_controller.follow_semillero)
workflow_bp.get("/semilleros/<string:identifier>/pending")(workflow_controller.semillero_pending)
workflow_bp.patch("/semilleros/<string:identifier>/members/<int:user_id>")(
    workflow_controller.review_member
)
workflow_bp.get("/projects")(workflow_controller.list_projects)
workflow_bp.post("/projects")(workflow_controller.create_project)
workflow_bp.get("/projects/<string:slug>")(workflow_controller.get_project)
workflow_bp.get("/activities")(workflow_controller.list_activities)
workflow_bp.get("/activities/<string:slug>")(workflow_controller.get_activity)
workflow_bp.post("/activities/<string:slug>/join")(workflow_controller.join_activity)
workflow_bp.get("/profile")(workflow_controller.get_profile)
workflow_bp.patch("/profile")(workflow_controller.patch_profile)
workflow_bp.get("/gamification")(workflow_controller.gamification)
workflow_bp.post("/achievements")(workflow_controller.create_achievement)
workflow_bp.get("/home")(workflow_controller.home)
workflow_bp.get("/notifications")(workflow_controller.list_notifications)
workflow_bp.post("/notifications/<int:notification_id>/read")(
    workflow_controller.read_notification
)
