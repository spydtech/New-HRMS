# from fastapi import APIRouter

# from app.api.v1.endpoints import (
#     activities,
#     auth,
#     attendance,
#     clients,        # new
#     documents,
#     education,
#     employees,
#     health,
#     leaves,
#     holidays,
#     projects,       # new
#     teams,
#     users,
# )

# api_router = APIRouter()
# api_router.include_router(health.router)
# api_router.include_router(auth.router)
# api_router.include_router(users.router)
# api_router.include_router(employees.router)
# api_router.include_router(clients.router)   # new
# api_router.include_router(projects.router)  # new
# api_router.include_router(activities.router)
# api_router.include_router(education.router)
# api_router.include_router(documents.router)
# api_router.include_router(attendance.router)
# api_router.include_router(leaves.router)
# api_router.include_router(holidays.router)
# api_router.include_router(teams.router)



from fastapi import APIRouter

from app.api.v1.endpoints import (
    activities,
    auth,
    attendance,
    clients,
    documents,
    education,
    employees,
    health,
    holidays,
    leaves,
    payroll,
    projects,
    teams,
    users,
    events,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(employees.router)
api_router.include_router(clients.router)
api_router.include_router(projects.router)
api_router.include_router(activities.router)
api_router.include_router(education.router)
api_router.include_router(documents.router)
api_router.include_router(attendance.router)
api_router.include_router(leaves.router)
api_router.include_router(holidays.router)
api_router.include_router(teams.router)
api_router.include_router(payroll.router)
api_router.include_router(events.router)