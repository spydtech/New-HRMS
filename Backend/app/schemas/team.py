from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class TeamMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    email: str
    employeeId: str | None = Field(default=None, validation_alias="employee_id")
    role: str
    designation: str | None = None
    profileImage: str | None = Field(default=None, validation_alias="profile_image")


class TeamBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    team_name: str = Field(
        min_length=2,
        max_length=150,
        validation_alias=AliasChoices("teamName", "team_name"),
    )
    description: str | None = None
    image: str | None = None
    lead_id: int | None = Field(
        default=None, validation_alias=AliasChoices("leadId", "lead_id")
    )
    member_ids: list[int] = Field(
        default_factory=list,
        validation_alias=AliasChoices("memberIds", "member_ids"),
    )


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    team_name: str | None = Field(
        default=None, validation_alias=AliasChoices("teamName", "team_name")
    )
    description: str | None = None
    image: str | None = None
    lead_id: int | None = Field(
        default=None, validation_alias=AliasChoices("leadId", "lead_id")
    )
    member_ids: list[int] | None = Field(
        default=None, validation_alias=AliasChoices("memberIds", "member_ids")
    )


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    teamName: str = Field(validation_alias="team_name")
    team_name: str = Field(validation_alias="team_name")
    description: str | None = None
    image: str | None = None
    leadId: int | None = Field(default=None, validation_alias="lead_id")
    leadName: str | None = None
    lead: TeamMemberRead | None = None
    members: list[TeamMemberRead] = []
    memberCount: int = 0
    createdAt: datetime = Field(validation_alias="created_at")
    updatedAt: datetime = Field(validation_alias="updated_at")


def team_to_response(team) -> dict:
    members = list(team.members or [])
    lead = team.lead

    def _u(u):
        return {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "employeeId": u.employee_id,
            "role": u.role,
            "designation": u.designation,
            "profileImage": u.profile_image,
        }

    return {
        "id": team.id,
        "teamName": team.team_name,
        "team_name": team.team_name,
        "description": team.description,
        "image": team.image,
        "leadId": team.lead_id,
        "leadName": lead.name if lead else None,
        "lead": _u(lead) if lead else None,
        "members": [_u(m) for m in members],
        "memberCount": len(members),
        "createdAt": team.created_at,
        "updatedAt": team.updated_at,
    }