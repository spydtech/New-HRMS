# from datetime import date, datetime
# from decimal import Decimal

# from pydantic import AliasChoices, BaseModel, ConfigDict, Field


# class ProjectClientInfo(BaseModel):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)

#     id: int
#     name: str
#     email: str


# class ProjectTeamInfo(BaseModel):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)

#     id: int
#     teamName: str = Field(validation_alias="team_name")
#     team_name: str = Field(validation_alias="team_name")


# class ProjectTeamLeadInfo(BaseModel):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)

#     id: int
#     name: str
#     email: str
#     designation: str | None = None
#     profileImage: str | None = Field(default=None, validation_alias="profile_image")


# class ProjectBase(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")

#     project_name: str = Field(
#         min_length=2,
#         max_length=200,
#         validation_alias=AliasChoices("projectName", "project_name"),
#     )
#     description: str | None = None
#     client_id: int | None = Field(
#         default=None, validation_alias=AliasChoices("clientId", "client_id")
#     )
#     team_id: int | None = Field(
#         default=None, validation_alias=AliasChoices("teamId", "team_id")
#     )
#     team_lead_id: int | None = Field(
#         default=None, validation_alias=AliasChoices("teamLeadId", "team_lead_id")
#     )
#     start_date: date | None = Field(
#         default=None, validation_alias=AliasChoices("startDate", "start_date")
#     )
#     end_date: date | None = Field(
#         default=None, validation_alias=AliasChoices("endDate", "end_date")
#     )
#     project_priority: str = Field(
#         default="Medium",
#         validation_alias=AliasChoices("projectPriority", "project_priority"),
#     )
#     rate: Decimal | None = None
#     rate_type: str | None = Field(
#         default=None, validation_alias=AliasChoices("rateType", "rate_type")
#     )
#     status: str = "Active"
#     progress: int = 0
#     project_image: str | None = Field(
#         default=None,
#         validation_alias=AliasChoices("projectImage", "project_image"),
#     )


# class ProjectCreate(ProjectBase):
#     pass


# class ProjectUpdate(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")

#     project_name: str | None = Field(
#         default=None, validation_alias=AliasChoices("projectName", "project_name")
#     )
#     description: str | None = None
#     client_id: int | None = Field(
#         default=None, validation_alias=AliasChoices("clientId", "client_id")
#     )
#     team_id: int | None = Field(
#         default=None, validation_alias=AliasChoices("teamId", "team_id")
#     )
#     team_lead_id: int | None = Field(
#         default=None, validation_alias=AliasChoices("teamLeadId", "team_lead_id")
#     )
#     start_date: date | None = Field(
#         default=None, validation_alias=AliasChoices("startDate", "start_date")
#     )
#     end_date: date | None = Field(
#         default=None, validation_alias=AliasChoices("endDate", "end_date")
#     )
#     project_priority: str | None = Field(
#         default=None,
#         validation_alias=AliasChoices("projectPriority", "project_priority"),
#     )
#     rate: Decimal | None = None
#     rate_type: str | None = Field(
#         default=None, validation_alias=AliasChoices("rateType", "rate_type")
#     )
#     status: str | None = None
#     progress: int | None = None
#     project_image: str | None = Field(
#         default=None,
#         validation_alias=AliasChoices("projectImage", "project_image"),
#     )


# class ProjectProgressUpdate(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")

#     progress: int = Field(ge=0, le=100)


# class ProjectRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)

#     id: int
#     projectName: str = Field(validation_alias="project_name")
#     project_name: str = Field(validation_alias="project_name")
#     description: str | None = None

#     clientId: int | None = Field(default=None, validation_alias="client_id")
#     teamId: int | None = Field(default=None, validation_alias="team_id")
#     teamLeadId: int | None = Field(default=None, validation_alias="team_lead_id")

#     startDate: date | None = Field(default=None, validation_alias="start_date")
#     endDate: date | None = Field(default=None, validation_alias="end_date")
#     projectPriority: str = Field(validation_alias="project_priority")
#     rate: Decimal | None = None
#     rateType: str | None = Field(default=None, validation_alias="rate_type")
#     status: str
#     progress: int = 0
#     projectImage: str | None = Field(default=None, validation_alias="project_image")

#     client: ProjectClientInfo | None = None
#     team: ProjectTeamInfo | None = None
#     teamLead: ProjectTeamLeadInfo | None = Field(
#         default=None, validation_alias="team_lead"
#     )

#     createdAt: datetime = Field(validation_alias="created_at")
#     updatedAt: datetime = Field(validation_alias="updated_at")







from datetime import date, datetime
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ProjectClientInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    email: str


class ProjectTeamMemberInfo(BaseModel):
    """A single member inside a project's assigned team."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    email: str
    profileImage: str | None = Field(default=None, validation_alias="profile_image")
    designation: str | None = None


class ProjectTeamInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    teamName: str = Field(validation_alias="team_name")
    team_name: str = Field(validation_alias="team_name")
    
    # ✅ Included so the frontend can show avatars
    members: list[ProjectTeamMemberInfo] = []


class ProjectTeamLeadInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    email: str
    designation: str | None = None
    profileImage: str | None = Field(default=None, validation_alias="profile_image")


class ProjectBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    project_name: str = Field(
        min_length=2,
        max_length=200,
        validation_alias=AliasChoices("projectName", "project_name"),
    )
    description: str | None = None
    client_id: int | None = Field(
        default=None, validation_alias=AliasChoices("clientId", "client_id")
    )
    team_id: int | None = Field(
        default=None, validation_alias=AliasChoices("teamId", "team_id")
    )
    team_lead_id: int | None = Field(
        default=None, validation_alias=AliasChoices("teamLeadId", "team_lead_id")
    )
    start_date: date | None = Field(
        default=None, validation_alias=AliasChoices("startDate", "start_date")
    )
    end_date: date | None = Field(
        default=None, validation_alias=AliasChoices("endDate", "end_date")
    )
    project_priority: str = Field(
        default="Medium",
        validation_alias=AliasChoices("projectPriority", "project_priority"),
    )
    rate: Decimal | None = None
    rate_type: str | None = Field(
        default=None, validation_alias=AliasChoices("rateType", "rate_type")
    )
    status: str = "Active"
    progress: int = 0
    project_image: str | None = Field(
        default=None,
        validation_alias=AliasChoices("projectImage", "project_image"),
    )


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    project_name: str | None = Field(
        default=None, validation_alias=AliasChoices("projectName", "project_name")
    )
    description: str | None = None
    client_id: int | None = Field(
        default=None, validation_alias=AliasChoices("clientId", "client_id")
    )
    team_id: int | None = Field(
        default=None, validation_alias=AliasChoices("teamId", "team_id")
    )
    team_lead_id: int | None = Field(
        default=None, validation_alias=AliasChoices("teamLeadId", "team_lead_id")
    )
    start_date: date | None = Field(
        default=None, validation_alias=AliasChoices("startDate", "start_date")
    )
    end_date: date | None = Field(
        default=None, validation_alias=AliasChoices("endDate", "end_date")
    )
    project_priority: str | None = Field(
        default=None,
        validation_alias=AliasChoices("projectPriority", "project_priority"),
    )
    rate: Decimal | None = None
    rate_type: str | None = Field(
        default=None, validation_alias=AliasChoices("rateType", "rate_type")
    )
    status: str | None = None
    progress: int | None = None
    project_image: str | None = Field(
        default=None,
        validation_alias=AliasChoices("projectImage", "project_image"),
    )


class ProjectProgressUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    progress: int = Field(ge=0, le=100)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    projectName: str = Field(validation_alias="project_name")
    project_name: str = Field(validation_alias="project_name")
    description: str | None = None

    clientId: int | None = Field(default=None, validation_alias="client_id")
    teamId: int | None = Field(default=None, validation_alias="team_id")
    teamLeadId: int | None = Field(default=None, validation_alias="team_lead_id")

    startDate: date | None = Field(default=None, validation_alias="start_date")
    endDate: date | None = Field(default=None, validation_alias="end_date")
    projectPriority: str = Field(validation_alias="project_priority")
    rate: Decimal | None = None
    rateType: str | None = Field(default=None, validation_alias="rate_type")
    status: str
    progress: int = 0
    projectImage: str | None = Field(default=None, validation_alias="project_image")

    client: ProjectClientInfo | None = None
    team: ProjectTeamInfo | None = None
    teamLead: ProjectTeamLeadInfo | None = Field(
        default=None, validation_alias="team_lead"
    )

    createdAt: datetime = Field(validation_alias="created_at")
    updatedAt: datetime = Field(validation_alias="updated_at")