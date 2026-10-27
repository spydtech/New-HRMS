from datetime import date, datetime

from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.payroll import (
    Allowance, Deduction, PayrollActivity, PayrollBatch, PayrollBatchMember,
    PayrollForm, PayrollRun, PayrollSettings, PaySlipSetting, Payslip, Settlement,
)
from app.models.user import User, UserRole
from app.schemas.payroll import (
    AllowanceCreate, AllowanceRead, AllowanceUpdate,
    BatchCreate, BatchRead, BatchUpdate,
    DeductionCreate, DeductionRead, DeductionUpdate,
    PayrollFormCreate, PayrollFormRead,
    PayrollRunCreate, PayrollRunRead, PayslipRead,
    PayrollSettingsRead, PayrollSettingsUpdate,
    PaySlipSettingRead, PaySlipSettingUpdate,
    SettlementCreate, SettlementRead,
)
from app.services.payroll_service import (
    compute_payslip_for_member, compute_run_totals,
)

router = APIRouter(prefix="/payroll", tags=["payroll"])
HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


def _is_hr(u) -> bool:
    return u.role in HR_ROLES


def _log(session, user, action, description, entity_type=None, entity_id=None):
    session.add(PayrollActivity(
        user_id=getattr(user, "id", None), action=action,
        description=description, entity_type=entity_type, entity_id=entity_id,
    ))


# ---------- Batches ----------
@router.get("/batches", response_model=list[BatchRead])
async def list_batches(session: DbSession, _: CurrentUser):
    result = await session.execute(select(PayrollBatch).order_by(PayrollBatch.name))
    out = []
    for b in result.scalars().all():
        out.append({
            "id": b.id, "name": b.name, "description": b.description,
            "status": b.status, "created_by_id": b.created_by_id,
            "last_payroll_run_at": b.last_payroll_run_at,
            "created_at": b.created_at,
            "member_count": len(b.members or []),
            "members": [
                {
                    "id": m.id, "user_id": m.user_id,
                    "name": m.user.name if m.user else None,
                    "email": m.user.email if m.user else None,
                    "monthly_basic": float(m.monthly_basic or 0),
                    "monthly_hra": float(m.monthly_hra or 0),
                    "monthly_allowances": float(m.monthly_allowances or 0),
                    "joined_on": m.joined_on,
                } for m in (b.members or [])
            ],
        })
    return out


@router.get("/batches/{batch_id}", response_model=BatchRead)
async def get_batch(batch_id: int, session: DbSession, _: CurrentUser):
    b = await session.get(PayrollBatch, batch_id)
    if not b:
        raise NotFoundError("Batch not found")
    return {
        "id": b.id, "name": b.name, "description": b.description, "status": b.status,
        "created_by_id": b.created_by_id, "last_payroll_run_at": b.last_payroll_run_at,
        "created_at": b.created_at, "member_count": len(b.members or []),
        "members": [
            {
                "id": m.id, "user_id": m.user_id,
                "name": m.user.name if m.user else None,
                "email": m.user.email if m.user else None,
                "monthly_basic": float(m.monthly_basic or 0),
                "monthly_hra": float(m.monthly_hra or 0),
                "monthly_allowances": float(m.monthly_allowances or 0),
                "joined_on": m.joined_on,
            } for m in (b.members or [])
        ],
    }


@router.post("/batches", response_model=BatchRead, status_code=status.HTTP_201_CREATED)
async def create_batch(payload: BatchCreate, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can create batches")
    existing = await session.execute(select(PayrollBatch).where(PayrollBatch.name == payload.name))
    if existing.scalar_one_or_none():
        raise ConflictError("Batch name already exists")

    batch = PayrollBatch(
        name=payload.name.strip(), description=payload.description,
        status=payload.status or "Active", created_by_id=current_user.id,
    )
    session.add(batch)
    await session.flush()

    for m in payload.members:
        session.add(PayrollBatchMember(
            batch_id=batch.id, user_id=m.user_id,
            monthly_basic=m.monthly_basic, monthly_hra=m.monthly_hra,
            monthly_allowances=m.monthly_allowances, joined_on=m.joined_on,
        ))

    _log(session, current_user, "batch.create", f"Created batch {batch.name}", "PayrollBatch", batch.id)
    await session.commit()
    await session.refresh(batch)
    return await get_batch(batch.id, session, current_user)


@router.put("/batches/{batch_id}", response_model=BatchRead)
async def update_batch(batch_id: int, payload: BatchUpdate, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can update batches")
    b = await session.get(PayrollBatch, batch_id)
    if not b:
        raise NotFoundError("Batch not found")
    data = payload.model_dump(exclude_unset=True, by_alias=False)
    for f in ("name", "description", "status"):
        if f in data:
            setattr(b, f, data[f])
    if payload.members is not None:
        for m in list(b.members or []):
            await session.delete(m)
        await session.flush()
        for m in payload.members:
            session.add(PayrollBatchMember(
                batch_id=b.id, user_id=m.user_id,
                monthly_basic=m.monthly_basic, monthly_hra=m.monthly_hra,
                monthly_allowances=m.monthly_allowances, joined_on=m.joined_on,
            ))
    _log(session, current_user, "batch.update", f"Updated batch {b.name}", "PayrollBatch", b.id)
    await session.commit()
    await session.refresh(b)
    return await get_batch(b.id, session, current_user)


@router.delete("/batches/{batch_id}")
async def delete_batch(batch_id: int, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can delete batches")
    b = await session.get(PayrollBatch, batch_id)
    if not b:
        raise NotFoundError("Batch not found")
    await session.delete(b)
    await session.commit()
    return {"success": True}


# ---------- Allowances ----------
@router.get("/allowances", response_model=list[AllowanceRead])
async def list_allowances(session: DbSession, _: CurrentUser):
    result = await session.execute(select(Allowance).order_by(Allowance.display_name))
    return list(result.scalars().all())


@router.post("/allowances", response_model=AllowanceRead, status_code=status.HTTP_201_CREATED)
async def create_allowance(payload: AllowanceCreate, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can manage allowances")
    a = Allowance(**payload.model_dump())
    session.add(a)
    _log(session, current_user, "allowance.create", f"Added allowance {a.display_name}", "Allowance", None)
    await session.commit()
    await session.refresh(a)
    return a


@router.put("/allowances/{allowance_id}", response_model=AllowanceRead)
async def update_allowance(allowance_id: int, payload: AllowanceUpdate, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can manage allowances")
    a = await session.get(Allowance, allowance_id)
    if not a:
        raise NotFoundError("Allowance not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    await session.commit()
    await session.refresh(a)
    return a


@router.delete("/allowances/{allowance_id}")
async def delete_allowance(allowance_id: int, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can manage allowances")
    a = await session.get(Allowance, allowance_id)
    if not a:
        raise NotFoundError("Allowance not found")
    await session.delete(a)
    await session.commit()
    return {"success": True}


# ---------- Deductions ----------
@router.get("/deductions", response_model=list[DeductionRead])
async def list_deductions(session: DbSession, _: CurrentUser):
    result = await session.execute(select(Deduction).order_by(Deduction.display_name))
    return list(result.scalars().all())


@router.post("/deductions", response_model=DeductionRead, status_code=status.HTTP_201_CREATED)
async def create_deduction(payload: DeductionCreate, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can manage deductions")
    d = Deduction(**payload.model_dump())
    session.add(d)
    _log(session, current_user, "deduction.create", f"Added deduction {d.display_name}", "Deduction", None)
    await session.commit()
    await session.refresh(d)
    return d


@router.put("/deductions/{deduction_id}", response_model=DeductionRead)
async def update_deduction(deduction_id: int, payload: DeductionUpdate, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can manage deductions")
    d = await session.get(Deduction, deduction_id)
    if not d:
        raise NotFoundError("Deduction not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(d, k, v)
    await session.commit()
    await session.refresh(d)
    return d


@router.delete("/deductions/{deduction_id}")
async def delete_deduction(deduction_id: int, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can manage deductions")
    d = await session.get(Deduction, deduction_id)
    if not d:
        raise NotFoundError("Deduction not found")
    await session.delete(d)
    await session.commit()
    return {"success": True}


# ---------- Settings ----------
async def _get_or_create_settings(session) -> PayrollSettings:
    result = await session.execute(select(PayrollSettings).limit(1))
    s = result.scalar_one_or_none()
    if not s:
        s = PayrollSettings()
        session.add(s)
        await session.commit()
        await session.refresh(s)
    return s


@router.get("/settings", response_model=PayrollSettingsRead)
async def get_settings(session: DbSession, _: CurrentUser):
    return await _get_or_create_settings(session)


@router.put("/settings", response_model=PayrollSettingsRead)
async def update_settings(payload: PayrollSettingsUpdate, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can change payroll settings")
    s = await _get_or_create_settings(session)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    _log(session, current_user, "settings.update", "Updated payroll settings", "PayrollSettings", s.id)
    await session.commit()
    await session.refresh(s)
    return s


@router.get("/payslip-settings", response_model=PaySlipSettingRead)
async def get_payslip_settings(session: DbSession, _: CurrentUser):
    result = await session.execute(select(PaySlipSetting).limit(1))
    s = result.scalar_one_or_none()
    if not s:
        s = PaySlipSetting()
        session.add(s)
        await session.commit()
        await session.refresh(s)
    return s


@router.put("/payslip-settings", response_model=PaySlipSettingRead)
async def update_payslip_settings(payload: PaySlipSettingUpdate, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can change payslip settings")
    result = await session.execute(select(PaySlipSetting).limit(1))
    s = result.scalar_one_or_none()
    if not s:
        s = PaySlipSetting()
        session.add(s)
        await session.flush()
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    await session.commit()
    await session.refresh(s)
    return s


# ---------- Runs ----------
@router.get("/runs", response_model=list[PayrollRunRead])
async def list_runs(session: DbSession, _: CurrentUser):
    result = await session.execute(select(PayrollRun).order_by(PayrollRun.started_at.desc()))
    return list(result.scalars().all())


@router.get("/runs/{run_id}", response_model=PayrollRunRead)
async def get_run(run_id: int, session: DbSession, _: CurrentUser):
    r = await session.get(PayrollRun, run_id)
    if not r:
        raise NotFoundError("Payroll run not found")
    return r


@router.post("/runs", response_model=PayrollRunRead, status_code=status.HTTP_201_CREATED)
async def create_run(payload: PayrollRunCreate, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can start payroll")

    batch = await session.get(PayrollBatch, payload.batch_id)
    if not batch:
        raise NotFoundError("Batch not found")

    settings = await _get_or_create_settings(session)

    run = PayrollRun(
        batch_id=batch.id,
        pay_period_start=payload.pay_period_start,
        pay_period_end=payload.pay_period_end,
        payroll_type=payload.payroll_type or "Monthly",
        status="Processing",
        started_by_id=current_user.id,
        notes=payload.notes,
    )
    session.add(run)
    await session.flush()

    for member in batch.members or []:
        session.add(compute_payslip_for_member(member, run, settings))

    await session.flush()
    await session.refresh(run, ["payslips"])
    compute_run_totals(run)
    batch.last_payroll_run_at = datetime.utcnow()

    _log(session, current_user, "run.create", f"Started payroll for {batch.name}", "PayrollRun", run.id)
    await session.commit()
    await session.refresh(run)
    return run


@router.post("/runs/{run_id}/complete", response_model=PayrollRunRead)
async def complete_run(run_id: int, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can complete payroll")
    r = await session.get(PayrollRun, run_id)
    if not r:
        raise NotFoundError("Payroll run not found")
    r.status = "Completed"
    r.completed_at = datetime.utcnow()
    _log(session, current_user, "run.complete", f"Completed payroll run #{r.id}", "PayrollRun", r.id)
    await session.commit()
    await session.refresh(r)
    return r


@router.post("/runs/{run_id}/void", response_model=PayrollRunRead)
async def void_run(run_id: int, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can void payroll")
    r = await session.get(PayrollRun, run_id)
    if not r:
        raise NotFoundError("Payroll run not found")
    r.status = "Voided"
    _log(session, current_user, "run.void", f"Voided payroll run #{r.id}", "PayrollRun", r.id)
    await session.commit()
    await session.refresh(r)
    return r


@router.get("/runs/{run_id}/payslips", response_model=list[PayslipRead])
async def list_run_payslips(run_id: int, session: DbSession, _: CurrentUser):
    result = await session.execute(select(Payslip).where(Payslip.payroll_run_id == run_id))
    return list(result.scalars().all())


# ---------- Payslips ----------
@router.get("/payslips", response_model=list[PayslipRead])
async def list_payslips(
    session: DbSession, current_user: CurrentUser,
    user_id: int | None = None, year: int | None = None,
):
    stmt = select(Payslip).order_by(Payslip.created_at.desc())
    if not _is_hr(current_user):
        stmt = stmt.where(Payslip.user_id == current_user.id)
    elif user_id:
        stmt = stmt.where(Payslip.user_id == user_id)
    if year:
        stmt = stmt.where(
            Payslip.created_at >= date(year, 1, 1),
            Payslip.created_at < date(year + 1, 1, 1),
        )
    result = await session.execute(stmt)
    return list(result.scalars().all())


# ---------- Forms ----------
@router.get("/forms", response_model=list[PayrollFormRead])
async def list_forms(session: DbSession, _: CurrentUser):
    result = await session.execute(select(PayrollForm).order_by(PayrollForm.created_on.desc()))
    return list(result.scalars().all())


@router.post("/forms", response_model=PayrollFormRead, status_code=status.HTTP_201_CREATED)
async def create_form(payload: PayrollFormCreate, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can generate forms")
    f = PayrollForm(
        form_type=payload.form_type, financial_year=payload.financial_year,
        created_by_id=current_user.id, created_for_id=payload.created_for_id,
    )
    session.add(f)
    _log(session, current_user, "form.create", f"Generated {f.form_type}", "PayrollForm", None)
    await session.commit()
    await session.refresh(f)
    return f


# ---------- Settlements ----------
@router.get("/settlements", response_model=list[SettlementRead])
async def list_settlements(session: DbSession, _: CurrentUser):
    result = await session.execute(select(Settlement).order_by(Settlement.run_date.desc()))
    return list(result.scalars().all())


@router.post("/settlements", response_model=SettlementRead, status_code=status.HTTP_201_CREATED)
async def create_settlement(payload: SettlementCreate, session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can create settlements")
    s = Settlement(**payload.model_dump())
    session.add(s)
    _log(session, current_user, "settlement.create", f"Added settlement for user {s.user_id}", "Settlement", None)
    await session.commit()
    await session.refresh(s)
    return s


# ---------- Dashboard ----------
@router.get("/dashboard")
async def get_dashboard(session: DbSession, _: CurrentUser):
    result = await session.execute(select(Payslip).order_by(Payslip.created_at.desc()).limit(500))
    slips = list(result.scalars().all())

    total_gross = sum((s.gross for s in slips), start=0)
    total_net = sum((s.net_amount for s in slips), start=0)
    total_tds = sum((s.income_tax + s.surcharge + s.cess for s in slips), start=0)
    total_pt = sum((s.professional_tax for s in slips), start=0)
    total_epf = sum((s.pf_employee for s in slips), start=0)
    total_er_pf = sum((s.pf_employer for s in slips), start=0)
    total_esi_emp = sum((s.esi_employee for s in slips), start=0)
    total_esi_er = sum((s.esi_employer for s in slips), start=0)

    return {
        "payDetails": {
            "gross": float(total_gross), "netPay": float(total_net),
            "tds": float(total_tds), "pt": float(total_pt),
        },
        "pfEsi": {
            "epf": float(total_epf), "eesi": float(total_esi_emp),
            "erPf": float(total_er_pf), "erEsi": float(total_esi_er),
        },
        "employeeDeduction": {
            "pf": float(total_epf), "pt": float(total_pt), "esi": float(total_esi_emp),
        },
        "employerDeduction": {
            "pf": float(total_er_pf), "esi": float(total_esi_er),
        },
    }


# ---------- Activities ----------
@router.get("/activities")
async def list_activities(session: DbSession, _: CurrentUser, limit: int = 50):
    result = await session.execute(
        select(PayrollActivity)
        .order_by(PayrollActivity.created_at.desc())
        .limit(max(1, min(limit, 200)))
    )
    return [
        {
            "id": a.id, "action": a.action, "description": a.description,
            "entityType": a.entity_type, "entityId": a.entity_id,
            "createdAt": a.created_at,
            "user": (
                {
                    "id": a.user.id, "name": a.user.name,
                    "email": a.user.email, "profileImage": a.user.profile_image,
                } if a.user else None
            ),
        }
        for a in result.scalars().all()
    ]