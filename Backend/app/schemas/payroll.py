# from datetime import date, datetime
# from decimal import Decimal

# from pydantic import BaseModel, ConfigDict, Field


# class BatchMemberBase(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")
#     user_id: int = Field(validation_alias="userId")
#     monthly_basic: Decimal = Field(default=0, validation_alias="monthlyBasic")
#     monthly_hra: Decimal = Field(default=0, validation_alias="monthlyHra")
#     monthly_allowances: Decimal = Field(default=0, validation_alias="monthlyAllowances")
#     joined_on: date | None = Field(default=None, validation_alias="joinedOn")


# class BatchCreate(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")
#     name: str = Field(min_length=2, max_length=150)
#     description: str | None = None
#     status: str = "Active"
#     members: list[BatchMemberBase] = []


# class BatchUpdate(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")
#     name: str | None = None
#     description: str | None = None
#     status: str | None = None
#     members: list[BatchMemberBase] | None = None


# class BatchRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#     id: int
#     name: str
#     description: str | None = None
#     status: str
#     created_by_id: int | None = Field(default=None, validation_alias="created_by_id")
#     last_payroll_run_at: datetime | None = Field(default=None, validation_alias="last_payroll_run_at")
#     created_at: datetime = Field(validation_alias="created_at")
#     member_count: int = 0
#     members: list[dict] = []


# class AllowanceBase(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")
#     display_name: str = Field(validation_alias="displayName")
#     allowance_code: str = Field(validation_alias="allowanceCode")
#     taxable: str = "Partially"
#     lop: str = "No"
#     pf: str = "No"
#     esi: str = "No"
#     pt: str = "No"
#     amount: str = "0"
#     is_active: bool = Field(default=True, validation_alias="isActive")


# class AllowanceCreate(AllowanceBase):
#     pass


# class AllowanceUpdate(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")
#     display_name: str | None = None
#     allowance_code: str | None = None
#     taxable: str | None = None
#     lop: str | None = None
#     pf: str | None = None
#     esi: str | None = None
#     pt: str | None = None
#     amount: str | None = None
#     is_active: bool | None = None


# class AllowanceRead(AllowanceBase):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#     id: int
#     created_at: datetime


# class DeductionBase(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")
#     display_name: str = Field(validation_alias="displayName")
#     deduction_code: str = Field(validation_alias="deductionCode")
#     dtype: str = Field(default="Percentage", validation_alias="dtype")
#     deduction_on: str = Field(default="Post Tax", validation_alias="deductionOn")
#     amount: str = "0"
#     is_active: bool = Field(default=True, validation_alias="isActive")


# class DeductionCreate(DeductionBase):
#     pass


# class DeductionUpdate(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")
#     display_name: str | None = None
#     deduction_code: str | None = None
#     dtype: str | None = None
#     deduction_on: str | None = None
#     amount: str | None = None
#     is_active: bool | None = None


# class DeductionRead(DeductionBase):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#     id: int
#     created_at: datetime


# class PayrollSettingsRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#     id: int
#     frequency: str
#     pay_period_start_day: int
#     starting_month: int
#     starting_year: int
#     pay_days_basis: str
#     include_weekly_offs: bool
#     include_holidays: bool
#     basic_percentage: int
#     tds_calculation: str
#     tds_preference: str
#     rounding_type: str


# class PayrollSettingsUpdate(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")
#     frequency: str | None = None
#     pay_period_start_day: int | None = None
#     starting_month: int | None = None
#     starting_year: int | None = None
#     pay_days_basis: str | None = None
#     include_weekly_offs: bool | None = None
#     include_holidays: bool | None = None
#     basic_percentage: int | None = None
#     tds_calculation: str | None = None
#     tds_preference: str | None = None
#     rounding_type: str | None = None


# class PaySlipSettingRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#     id: int
#     show_date_of_joining: bool
#     show_department: bool
#     show_ytd_amounts: bool
#     show_address_info: bool
#     show_it_declaration: bool
#     show_aadhaar: bool
#     show_bank_information: bool
#     show_pan: bool
#     show_payment_method: bool
#     show_esi: bool
#     show_paid_days: bool
#     show_pf: bool
#     show_leave_balance: bool
#     show_pf_uan: bool
#     show_additional_income_tax: bool
#     show_tax_regime: bool
#     show_masked_numbers: bool
#     show_loss_of_pay_days: bool


# class PaySlipSettingUpdate(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")
#     show_date_of_joining: bool | None = None
#     show_department: bool | None = None
#     show_ytd_amounts: bool | None = None
#     show_address_info: bool | None = None
#     show_it_declaration: bool | None = None
#     show_aadhaar: bool | None = None
#     show_bank_information: bool | None = None
#     show_pan: bool | None = None
#     show_payment_method: bool | None = None
#     show_esi: bool | None = None
#     show_paid_days: bool | None = None
#     show_pf: bool | None = None
#     show_leave_balance: bool | None = None
#     show_pf_uan: bool | None = None
#     show_additional_income_tax: bool | None = None
#     show_tax_regime: bool | None = None
#     show_masked_numbers: bool | None = None
#     show_loss_of_pay_days: bool | None = None


# class PayrollRunCreate(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")
#     batch_id: int = Field(validation_alias="batchId")
#     pay_period_start: date = Field(validation_alias="payPeriodStart")
#     pay_period_end: date = Field(validation_alias="payPeriodEnd")
#     payroll_type: str = Field(default="Monthly", validation_alias="payrollType")
#     notes: str | None = None


# class PayrollRunRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#     id: int
#     batch_id: int | None = None
#     pay_period_start: date
#     pay_period_end: date
#     payroll_type: str
#     status: str
#     total_employees: int
#     total_gross: Decimal
#     total_deductions: Decimal
#     total_net: Decimal
#     total_tds: Decimal
#     total_pf: Decimal
#     total_esi: Decimal
#     started_by_id: int | None = None
#     started_at: datetime
#     completed_at: datetime | None = None
#     notes: str | None = None


# class PayslipRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#     id: int
#     payroll_run_id: int
#     user_id: int
#     basic: Decimal
#     hra: Decimal
#     allowances: Decimal
#     gross: Decimal
#     actual_gross: Decimal
#     pf_employee: Decimal
#     pf_employer: Decimal
#     esi_employee: Decimal
#     esi_employer: Decimal
#     professional_tax: Decimal
#     income_tax: Decimal
#     surcharge: Decimal
#     cess: Decimal
#     lop_days: Decimal
#     lop_amount: Decimal
#     total_deductions: Decimal
#     net_amount: Decimal
#     created_at: datetime
#     user: dict | None = None


# class PayrollFormCreate(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")
#     form_type: str = Field(validation_alias="formType")
#     financial_year: str = Field(validation_alias="financialYear")
#     created_for_id: int = Field(validation_alias="createdForId")


# class PayrollFormRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#     id: int
#     form_type: str
#     financial_year: str
#     created_by_id: int | None = None
#     created_for_id: int
#     created_on: date
#     file_url: str | None = None
#     status: str


# class SettlementCreate(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, extra="ignore")
#     user_id: int = Field(validation_alias="userId")
#     pay_period_start: date | None = Field(default=None, validation_alias="payPeriodStart")
#     pay_period_end: date | None = Field(default=None, validation_alias="payPeriodEnd")
#     gross: Decimal = 0
#     income_tax: Decimal = Field(default=0, validation_alias="incomeTax")
#     surcharge: Decimal = 0
#     cess: Decimal = 0
#     net_amount: Decimal = Field(default=0, validation_alias="netAmount")
#     notes: str | None = None


# class SettlementRead(SettlementCreate):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#     id: int
#     run_date: date
#     status: str
#     created_at: datetime





from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# =====================================================================
# Batches
# =====================================================================
class BatchMemberBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    user_id: int = Field(validation_alias="userId")
    monthly_basic: Decimal = Field(default=0, validation_alias="monthlyBasic")
    monthly_hra: Decimal = Field(default=0, validation_alias="monthlyHra")
    monthly_allowances: Decimal = Field(default=0, validation_alias="monthlyAllowances")
    joined_on: date | None = Field(default=None, validation_alias="joinedOn")


class BatchCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None
    status: str = "Active"
    members: list[BatchMemberBase] = []


class BatchUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    name: str | None = None
    description: str | None = None
    status: str | None = None
    members: list[BatchMemberBase] | None = None


class BatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    name: str
    description: str | None = None
    status: str
    created_by_id: int | None = Field(default=None, validation_alias="created_by_id")
    last_payroll_run_at: datetime | None = Field(default=None, validation_alias="last_payroll_run_at")
    created_at: datetime = Field(validation_alias="created_at")
    member_count: int = 0
    members: list[dict] = []


# =====================================================================
# Allowances
# =====================================================================
class AllowanceBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    display_name: str = Field(validation_alias="displayName")
    allowance_code: str = Field(validation_alias="allowanceCode")
    taxable: str = "Partially"
    lop: str = "No"
    pf: str = "No"
    esi: str = "No"
    pt: str = "No"
    amount: str = "0"
    is_active: bool = Field(default=True, validation_alias="isActive")


class AllowanceCreate(AllowanceBase):
    pass


class AllowanceUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    display_name: str | None = None
    allowance_code: str | None = None
    taxable: str | None = None
    lop: str | None = None
    pf: str | None = None
    esi: str | None = None
    pt: str | None = None
    amount: str | None = None
    is_active: bool | None = None


class AllowanceRead(AllowanceBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    created_at: datetime


# =====================================================================
# Deductions
# =====================================================================
class DeductionBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    display_name: str = Field(validation_alias="displayName")
    deduction_code: str = Field(validation_alias="deductionCode")
    dtype: str = Field(default="Percentage", validation_alias="dtype")
    deduction_on: str = Field(default="Post Tax", validation_alias="deductionOn")
    amount: str = "0"
    is_active: bool = Field(default=True, validation_alias="isActive")


class DeductionCreate(DeductionBase):
    pass


class DeductionUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    display_name: str | None = None
    deduction_code: str | None = None
    dtype: str | None = None
    deduction_on: str | None = None
    amount: str | None = None
    is_active: bool | None = None


class DeductionRead(DeductionBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    created_at: datetime


# =====================================================================
# Settings
# =====================================================================
class PayrollSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    frequency: str
    pay_period_start_day: int
    starting_month: int
    starting_year: int
    pay_days_basis: str
    include_weekly_offs: bool
    include_holidays: bool
    basic_percentage: int
    tds_calculation: str
    tds_preference: str
    rounding_type: str


class PayrollSettingsUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    frequency: str | None = None
    pay_period_start_day: int | None = None
    starting_month: int | None = None
    starting_year: int | None = None
    pay_days_basis: str | None = None
    include_weekly_offs: bool | None = None
    include_holidays: bool | None = None
    basic_percentage: int | None = None
    tds_calculation: str | None = None
    tds_preference: str | None = None
    rounding_type: str | None = None


class PaySlipSettingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    show_date_of_joining: bool
    show_department: bool
    show_ytd_amounts: bool
    show_address_info: bool
    show_it_declaration: bool
    show_aadhaar: bool
    show_bank_information: bool
    show_pan: bool
    show_payment_method: bool
    show_esi: bool
    show_paid_days: bool
    show_pf: bool
    show_leave_balance: bool
    show_pf_uan: bool
    show_additional_income_tax: bool
    show_tax_regime: bool
    show_masked_numbers: bool
    show_loss_of_pay_days: bool


class PaySlipSettingUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    show_date_of_joining: bool | None = None
    show_department: bool | None = None
    show_ytd_amounts: bool | None = None
    show_address_info: bool | None = None
    show_it_declaration: bool | None = None
    show_aadhaar: bool | None = None
    show_bank_information: bool | None = None
    show_pan: bool | None = None
    show_payment_method: bool | None = None
    show_esi: bool | None = None
    show_paid_days: bool | None = None
    show_pf: bool | None = None
    show_leave_balance: bool | None = None
    show_pf_uan: bool | None = None
    show_additional_income_tax: bool | None = None
    show_tax_regime: bool | None = None
    show_masked_numbers: bool | None = None
    show_loss_of_pay_days: bool | None = None


# =====================================================================
# Payroll Runs
# =====================================================================
class PayrollRunCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    batch_id: int = Field(validation_alias="batchId")
    pay_period_start: date = Field(validation_alias="payPeriodStart")
    pay_period_end: date = Field(validation_alias="payPeriodEnd")
    payroll_type: str = Field(default="Monthly", validation_alias="payrollType")
    notes: str | None = None


class PayrollRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    batch_id: int | None = None
    pay_period_start: date
    pay_period_end: date
    payroll_type: str
    status: str
    total_employees: int
    total_gross: Decimal
    total_deductions: Decimal
    total_net: Decimal
    total_tds: Decimal
    total_pf: Decimal
    total_esi: Decimal
    started_by_id: int | None = None
    started_at: datetime
    completed_at: datetime | None = None
    notes: str | None = None


# =====================================================================
# Payslips
# =====================================================================
class PayslipUserInfo(BaseModel):
    """Nested user info returned with each payslip."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    email: str
    profileImage: str | None = Field(default=None, validation_alias="profile_image")
    designation: str | None = None


class PayslipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    payroll_run_id: int
    user_id: int
    basic: Decimal
    hra: Decimal
    allowances: Decimal
    gross: Decimal
    actual_gross: Decimal
    pf_employee: Decimal
    pf_employer: Decimal
    esi_employee: Decimal
    esi_employer: Decimal
    professional_tax: Decimal
    income_tax: Decimal
    surcharge: Decimal
    cess: Decimal
    lop_days: Decimal
    lop_amount: Decimal
    total_deductions: Decimal
    net_amount: Decimal
    created_at: datetime

    # ← THIS is the fixed line. Was `dict | None` before; now it's a
    # proper nested Pydantic model with from_attributes=True, which
    # lets Pydantic read the `User` ORM object's attributes directly.
    user: PayslipUserInfo | None = None


# =====================================================================
# Payroll Forms
# =====================================================================
class PayrollFormCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    form_type: str = Field(validation_alias="formType")
    financial_year: str = Field(validation_alias="financialYear")
    created_for_id: int = Field(validation_alias="createdForId")


class PayrollFormRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    form_type: str
    financial_year: str
    created_by_id: int | None = None
    created_for_id: int
    created_on: date
    file_url: str | None = None
    status: str


# =====================================================================
# Settlements
# =====================================================================
class SettlementCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    user_id: int = Field(validation_alias="userId")
    pay_period_start: date | None = Field(default=None, validation_alias="payPeriodStart")
    pay_period_end: date | None = Field(default=None, validation_alias="payPeriodEnd")
    gross: Decimal = 0
    income_tax: Decimal = Field(default=0, validation_alias="incomeTax")
    surcharge: Decimal = 0
    cess: Decimal = 0
    net_amount: Decimal = Field(default=0, validation_alias="netAmount")
    notes: str | None = None


class SettlementRead(SettlementCreate):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    run_date: date
    status: str
    created_at: datetime