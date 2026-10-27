from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func,
)
from sqlalchemy.dialects.mysql import BIGINT, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PayrollBatch(Base):
    __tablename__ = "payroll_batches"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="Active")
    created_by_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    last_payroll_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    members = relationship(
        "PayrollBatchMember", back_populates="batch",
        cascade="all, delete-orphan", lazy="selectin",
    )
    created_by = relationship("User", foreign_keys=[created_by_id], lazy="selectin")


class PayrollBatchMember(Base):
    __tablename__ = "payroll_batch_members"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("payroll_batches.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    monthly_basic: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    monthly_hra: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    monthly_allowances: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    joined_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    batch = relationship("PayrollBatch", back_populates="members")
    user = relationship("User", lazy="selectin")


class Allowance(Base):
    __tablename__ = "payroll_allowances"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    allowance_code: Mapped[str] = mapped_column(String(100), nullable=False)
    taxable: Mapped[str] = mapped_column(String(30), default="Partially")
    lop: Mapped[str] = mapped_column(String(10), default="No")
    pf: Mapped[str] = mapped_column(String(10), default="No")
    esi: Mapped[str] = mapped_column(String(10), default="No")
    pt: Mapped[str] = mapped_column(String(10), default="No")
    amount: Mapped[str] = mapped_column(String(100), default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Deduction(Base):
    __tablename__ = "payroll_deductions"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    deduction_code: Mapped[str] = mapped_column(String(100), nullable=False)
    dtype: Mapped[str] = mapped_column("dtype", String(30), default="Percentage")
    deduction_on: Mapped[str] = mapped_column(String(30), default="Post Tax")
    amount: Mapped[str] = mapped_column(String(100), default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class PayrollSettings(Base):
    __tablename__ = "payroll_settings"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    frequency: Mapped[str] = mapped_column(String(30), default="Monthly")
    pay_period_start_day: Mapped[int] = mapped_column(Integer, default=1)
    starting_month: Mapped[int] = mapped_column(Integer, default=1)
    starting_year: Mapped[int] = mapped_column(Integer, default=2024)
    pay_days_basis: Mapped[str] = mapped_column(String(50), default="Actual Days in Month")
    include_weekly_offs: Mapped[bool] = mapped_column(Boolean, default=True)
    include_holidays: Mapped[bool] = mapped_column(Boolean, default=True)
    basic_percentage: Mapped[int] = mapped_column(Integer, default=20)
    tds_calculation: Mapped[str] = mapped_column(String(30), default="Monthly")
    tds_preference: Mapped[str] = mapped_column(String(10), default="1")
    rounding_type: Mapped[str] = mapped_column(String(30), default="No Round")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False,
    )


class PaySlipSetting(Base):
    __tablename__ = "payslip_settings"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    show_date_of_joining: Mapped[bool] = mapped_column(Boolean, default=False)
    show_department: Mapped[bool] = mapped_column(Boolean, default=False)
    show_ytd_amounts: Mapped[bool] = mapped_column(Boolean, default=False)
    show_address_info: Mapped[bool] = mapped_column(Boolean, default=False)
    show_it_declaration: Mapped[bool] = mapped_column(Boolean, default=False)
    show_aadhaar: Mapped[bool] = mapped_column(Boolean, default=False)
    show_bank_information: Mapped[bool] = mapped_column(Boolean, default=False)
    show_pan: Mapped[bool] = mapped_column(Boolean, default=False)
    show_payment_method: Mapped[bool] = mapped_column(Boolean, default=False)
    show_esi: Mapped[bool] = mapped_column(Boolean, default=False)
    show_paid_days: Mapped[bool] = mapped_column(Boolean, default=False)
    show_pf: Mapped[bool] = mapped_column(Boolean, default=False)
    show_leave_balance: Mapped[bool] = mapped_column(Boolean, default=False)
    show_pf_uan: Mapped[bool] = mapped_column(Boolean, default=False)
    show_additional_income_tax: Mapped[bool] = mapped_column(Boolean, default=False)
    show_tax_regime: Mapped[bool] = mapped_column(Boolean, default=False)
    show_masked_numbers: Mapped[bool] = mapped_column(Boolean, default=False)
    show_loss_of_pay_days: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False,
    )


class PayrollRun(Base):
    __tablename__ = "payroll_runs"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    batch_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("payroll_batches.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    pay_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    pay_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    payroll_type: Mapped[str] = mapped_column(String(30), default="Monthly")
    status: Mapped[str] = mapped_column(String(30), default="Draft")

    total_employees: Mapped[int] = mapped_column(Integer, default=0)
    total_gross: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_net: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_tds: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_pf: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_esi: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)

    started_by_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    batch = relationship("PayrollBatch", lazy="selectin")
    started_by = relationship("User", foreign_keys=[started_by_id], lazy="selectin")
    payslips = relationship(
        "Payslip", back_populates="payroll_run",
        cascade="all, delete-orphan", lazy="selectin",
    )


class Payslip(Base):
    __tablename__ = "payslips"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    payroll_run_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("payroll_runs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    basic: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    hra: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    allowances: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    gross: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    actual_gross: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    pf_employee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pf_employer: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    esi_employee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    esi_employer: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    professional_tax: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    income_tax: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    surcharge: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    cess: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    lop_days: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0)
    lop_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    total_deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    earnings_json: Mapped[str | None] = mapped_column(LONGTEXT, nullable=True)
    deductions_json: Mapped[str | None] = mapped_column(LONGTEXT, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    payroll_run = relationship("PayrollRun", back_populates="payslips")
    user = relationship("User", lazy="selectin")


class PayrollForm(Base):
    __tablename__ = "payroll_forms"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    form_type: Mapped[str] = mapped_column(String(50), nullable=False)
    financial_year: Mapped[str] = mapped_column(String(20), nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    created_for_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    created_on: Mapped[date] = mapped_column(Date, default=date.today)
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="Generated")

    created_by = relationship("User", foreign_keys=[created_by_id], lazy="selectin")
    created_for = relationship("User", foreign_keys=[created_for_id], lazy="selectin")


class Settlement(Base):
    __tablename__ = "settlements"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    run_date: Mapped[date] = mapped_column(Date, default=date.today)
    status: Mapped[str] = mapped_column(String(30), default="Pending")
    pay_period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    pay_period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    gross: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    income_tax: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    surcharge: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    cess: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", lazy="selectin")


class PayrollActivity(Base):
    __tablename__ = "payroll_activities"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[int | None] = mapped_column(BIGINT(unsigned=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", lazy="selectin")