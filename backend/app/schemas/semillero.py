from marshmallow import Schema, fields


class SemilleroMemberSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    role_in_semillero = fields.Str(dump_only=True)
    full_name = fields.Method("get_full_name")
    email = fields.Method("get_email")
    initials = fields.Method("get_initials")

    def get_full_name(self, obj):
        if obj.user:
            return obj.user.full_name or obj.user.email
        return "Investigador"

    def get_email(self, obj):
        return obj.user.email if obj.user else ""

    def get_initials(self, obj):
        name = self.get_full_name(obj)
        parts = name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        return name[:2].upper() if name else "IN"


class SemilleroListSchema(Schema):
    id = fields.Int(dump_only=True)
    slug = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True)
    area = fields.Str(dump_only=True)
    faculty = fields.Method("get_faculty")
    program = fields.Method("get_program")
    leader = fields.Method("get_leader")
    member_count = fields.Method("get_member_count")
    memberCount = fields.Method("get_member_count")

    def get_faculty(self, obj):
        return obj.faculty.name if obj.faculty else ""

    def get_program(self, obj):
        return obj.program.name if obj.program else ""

    def get_leader(self, obj):
        if obj.leader:
            return obj.leader.full_name or obj.leader.email
        return "Por asignar"

    def get_member_count(self, obj):
        return len(obj.members) if obj.members else 0


class SemilleroDetailSchema(SemilleroListSchema):
    mission = fields.Str(dump_only=True)
    vision = fields.Str(dump_only=True)
    members = fields.Nested(SemilleroMemberSchema, many=True, dump_only=True)
