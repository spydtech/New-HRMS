from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from app.models.payroll import PayrollRun, PayrollSettings, Payslip

TWO = Decimal("0.01")
PF_WAGE_CEILING = Decimal("15000")
ESI_GROSS_CEILING = Decimal("21000")


def _d(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(TWO, rounding=ROUND_HALF_UP)


def _apply_rounding(amount: Decimal, rounding_type: str) -> Decimal:
    if not amount:
        return amount
    if rounding_type == "Round Up":
        return amount.to_integral_value(rounding="ROUND_CEILING")
    if rounding_type == "Round Down":
        return amount.to_integral_value(rounding="ROUND_FLOOR")
    if rounding_type == "Actual Round":
        return amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return amount


def compute_income_tax_monthly(annual_gross: Decimal) -> Decimal:
    ag = annual_gross - Decimal("50000")
    if ag <= 300000:
        annual_tax = Decimal("0")
    elif ag <= 600000:
        annual_tax = (ag - 300000) * Decimal("0.05")
    elif ag <= 900000:
        annual_tax = Decimal("15000") + (ag - 600000) * Decimal("0.10")
    elif ag <= 1200000:
        annual_tax = Decimal("45000") + (ag - 900000) * Decimal("0.15")
    elif ag <= 1500000:
        annual_tax = Decimal("90000") + (ag - 1200000) * Decimal("0.20")
    else:
        annual_tax = Decimal("150000") + (ag - 1500000) * Decimal("0.30")
    if ag <= 700000:
        annual_tax = Decimal("0")
    return _d(annual_tax / Decimal("12"))


def compute_payslip_for_member(member, run: PayrollRun, settings: PayrollSettings) -> Payslip:
    basic = _d(member.monthly_basic)
    hra = _d(member.monthly_hra)
    allowances = _d(member.monthly_allowances)
    gross = _d(basic + hra + allowances)

    pf_base = min(basic, PF_WAGE_CEILING)
    pf_employee = _d(pf_base * Decimal("0.12"))
    pf_employer = _d(pf_base * Decimal("0.12"))

    if gross <= ESI_GROSS_CEILING:
        esi_employee = _d(gross * Decimal("0.0075"))
        esi_employer = _d(gross * Decimal("0.0325"))
    else:
        esi_employee = Decimal("0.00")
        esi_employer = Decimal("0.00")

    professional_tax = Decimal("200.00")
    annual_gross = gross * Decimal("12")
    income_tax = compute_income_tax_monthly(annual_gross)
    surcharge = Decimal("0.00")
    cess = _d(income_tax * Decimal("0.04"))

    lop_days = Decimal("0.00")
    lop_amount = Decimal("0.00")

    total_deductions = _d(
        pf_employee + esi_employee + professional_tax + income_tax + surcharge + cess + lop_amount
    )
    net_amount = _d(gross - total_deductions)
    net_amount = _apply_rounding(net_amount, settings.rounding_type)

    return Payslip(
        payroll_run_id=run.id,
        user_id=member.user_id,
        basic=basic, hra=hra, allowances=allowances,
        gross=gross, actual_gross=gross,
        pf_employee=pf_employee, pf_employer=pf_employer,
        esi_employee=esi_employee, esi_employer=esi_employer,
        professional_tax=professional_tax,
        income_tax=income_tax, surcharge=surcharge, cess=cess,
        lop_days=lop_days, lop_amount=lop_amount,
        total_deductions=total_deductions, net_amount=net_amount,
    )


def compute_run_totals(run: PayrollRun) -> None:
    slips = run.payslips or []
    run.total_employees = len(slips)
    run.total_gross = _d(sum((s.gross for s in slips), Decimal("0")))
    run.total_deductions = _d(sum((s.total_deductions for s in slips), Decimal("0")))
    run.total_net = _d(sum((s.net_amount for s in slips), Decimal("0")))
    run.total_tds = _d(sum((s.income_tax + s.surcharge + s.cess for s in slips), Decimal("0")))
    run.total_pf = _d(sum((s.pf_employee + s.pf_employer for s in slips), Decimal("0")))
    run.total_esi = _d(sum((s.esi_employee + s.esi_employer for s in slips), Decimal("0")))