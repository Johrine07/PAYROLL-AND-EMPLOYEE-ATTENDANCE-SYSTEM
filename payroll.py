import datetime
from datetime import timedelta, time, date

class PayrollSystem:
    # Constants for deductions and rates
    SSS_RATE = 0.045
    PAGIBIG_RATE = 0.02
    PHILHEALTH_RATE = 0.02
    TAX_RATE = 0.10
    STANDARD_PAID_HOURS = 8  # Standard working hours per day

    LUNCH_BREAK_HOURS = 1  # Paid lunch break

    # Shifts for positions
    POSITION_SHIFTS = {
        "Manager": {"start": time(9, 0), "end": time(17, 0), "window_hours": 8},
        "Sales": {"start": time(7, 0), "end": time(15, 0), "window_hours": 8},
        "HR": {"start": time(8, 0), "end": time(16, 0), "window_hours": 8},
        "Production Worker A": {"start": time(7, 0), "end": time(15, 0), "window_hours": 8},
        "Production Worker B": {"start": time(15, 0), "end": time(23, 0), "window_hours": 8},
    }

    GUARD_SHIFTS = [
        {"start": time(6, 0), "end": time(14, 0), "window_hours": 8, "shift_name": "Shift A (6AM-2PM)"},
        {"start": time(14, 0), "end": time(22, 0), "window_hours": 8, "shift_name": "Shift B (2PM-10PM)"},
        {"start": time(22, 0), "end": time(6, 0), "window_hours": 8, "shift_name": "Shift C (10PM-6AM)"},
    ]

    def __init__(self, db_conn):
        self.conn = db_conn

    def calculate_daily_rate(self, monthly_salary):
        return monthly_salary / 20 if monthly_salary else 0

    def calculate_deductions(self, gross_salary):
        if gross_salary < 1000:
            return 0, 0, 0, 0

        sss = gross_salary * self.SSS_RATE
        pagibig = min(gross_salary, 5000) * self.PAGIBIG_RATE
        philhealth = gross_salary * self.PHILHEALTH_RATE
        taxable_income = gross_salary - (sss + pagibig + philhealth)
        tax = taxable_income * self.TAX_RATE if taxable_income > 0 else 0

        return sss, pagibig, philhealth, tax

    def get_approved_leaves(self, employee_id, start_date, end_date):
        cursor = self.conn.cursor()
        query = """
            SELECT date, leave_type
            FROM leaves
            WHERE employee_id = ? AND status = 'Approved' AND date BETWEEN ? AND ?
        """
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        cursor.execute(query, (employee_id, start_date_str, end_date_str))

        leave_map = {}
        for d, lt in cursor.fetchall():
            if lt == 'SL':
                leave_map[d] = ('SL', 1.0)
            elif lt == 'VL':
                leave_map[d] = ('VL', 1.0)
            elif lt == 'VLH':
                leave_map[d] = ('VLH', 0.5)
        cursor.close()  # Close the cursor manually
        return leave_map

    def get_employee_schedule(self, employee_id, month, year):
        cursor = self.conn.cursor()
        employee_data = cursor.execute(
            "SELECT position, department FROM employees WHERE id=?",
            (employee_id,)
        ).fetchone()
        if not employee_data:
            cursor.close()  # Ensure cursor is closed even if employee is not found
            return "Employee not found."

        position, department = employee_data
        schedule = {}
        start_date = date(year, month, 1)
        end_date = date(year, month, 1).replace(day=28) + timedelta(days=4)
        end_date = end_date - timedelta(days=end_date.day)

        guard_shift_index = 0 
        current_date = start_date
        weekdays = 0

        while current_date <= end_date:
            day_of_week = current_date.weekday()
            is_weekday = day_of_week < 5 

            if is_weekday:
                if position in ("Security Guard A", "Security Guard B", "Security Guard C") and department == "Security":
                    # Assign guards to specific shifts
                    guard_shift = None
                    if position == "Security Guard A":
                        guard_shift = self.GUARD_SHIFTS[0]  # Shift A
                    elif position == "Security Guard B":
                        guard_shift = self.GUARD_SHIFTS[1]  # Shift B
                    elif position == "Security Guard C":
                        guard_shift = self.GUARD_SHIFTS[2]  # Shift C

                    if guard_shift:
                        schedule[current_date.strftime("%Y-%m-%d")] = (
                            f"{position}: {guard_shift['shift_name']} (1HR Break)"
                        )
                else:
                    shift_def = self.POSITION_SHIFTS.get(position)
                    if not shift_def:
                        shift_def = {"start": time(8, 0), "end": time(16, 0), "window_hours": 8}

                    schedule[current_date.strftime("%Y-%m-%d")] = (
                        f"Work Day: {shift_def['start'].strftime('%I:%M %p')} - "
                        f"{shift_def['end'].strftime('%I:%M %p')} (1HR Break)"
                    )
                weekdays += 1
            else:
                schedule[current_date.strftime("%Y-%m-%d")] = "Rest Day (Weekend)"

            current_date += timedelta(days=1)

        cursor.close()  # Ensure cursor is closed after use
        return schedule, weekdays

    def get_attendance_summary(self, employee_id, start_date, end_date):
        cursor = self.conn.cursor()
        query = """
            SELECT date, time_in, time_out
            FROM attendance
            WHERE employee_id = ? AND date BETWEEN ? AND ?
            ORDER BY date
        """
        cursor.execute(query, (employee_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        records = cursor.fetchall()

        approved_leaves = self.get_approved_leaves(employee_id, start_date, end_date)
        full_schedule, _ = self.get_employee_schedule(employee_id, start_date.month, start_date.year)
        schedule = {
            d: full_schedule[d] for d in full_schedule
            if start_date.strftime('%Y-%m-%d') <= d <= end_date.strftime('%Y-%m-%d')
        }

        total_working_days = sum(1 for d, v in schedule.items() if ("Work Day" in v) or ("Shift" in v))

        attendance_map = {}
        for d, tin, tout in records:
            attendance_map[d] = (tin, tout)

        total_overtime_hours = 0.0
        total_tardiness_minutes = 0.0
        total_undertime_minutes = 0.0

        days_present = 0.0
        logged_dates = set()
        
        for d in sorted(schedule.keys()):
            day_label = schedule[d]


            if "Rest Day" in day_label:
                continue

            if d in approved_leaves:
                _, leave_days = approved_leaves[d]
                days_present += leave_days
                continue

            tin_tout = attendance_map.get(d)
            if not tin_tout:
                continue

            time_in_str, time_out_str = tin_tout

            if time_in_str and time_out_str:
                logged_dates.add(d)
                days_present += 1.0

            try:
                if "Shift" in day_label:
                    shift = next((s for s in self.GUARD_SHIFTS if s["shift_name"] in day_label), None)
                    if not shift:
                        continue
                    sch_start = shift["start"]
                    sch_end = shift["end"]
                    window_hours = shift["window_hours"]
                else:
                    emp_pos_row = cursor.execute("SELECT position FROM employees WHERE id=?", (employee_id,)).fetchone()
                    emp_pos = emp_pos_row[0] if emp_pos_row else None
                    shift_def = self.POSITION_SHIFTS.get(emp_pos, {"start": time(8, 0), "end": time(16, 0), "window_hours": 8})
                    sch_start = shift_def["start"]
                    sch_end = shift_def["end"]
                    window_hours = shift_def["window_hours"]

                paid_hours = window_hours - self.LUNCH_BREAK_HOURS

                if not sch_start or not sch_end:
                    continue
                sch_start_dt = datetime.datetime.combine(att_date, sch_start)
                sch_end_dt = datetime.datetime.combine(att_date, sch_end)

                if sch_end <= sch_start:
                    sch_end_dt += timedelta(days=1)
                    if time_out_dt < sch_start_dt:
                        time_out_dt += timedelta(days=1)

                if time_in_dt > sch_start_dt:
                    tardiness_duration = time_in_dt - sch_start_dt
                    total_tardiness += tardiness_duration.total_seconds() / 60 


                if time_out_dt < sch_end_dt:
                     undertime_duration = sch_end_dt - time_out_dt
                     total_undertime += undertime_duration.total_seconds() / 60 


                overtime = 0.0
                if time_out_dt > sch_end_dt:
                    overtime_duration = time_out_dt - sch_end_dt
                    overtime = overtime_duration.total_seconds() / 3600

                total_overtime += overtime

                duration = time_out_dt - time_in_dt
                duration_hours = duration.total_seconds() / 3600
            
            if duration_hours >= 5:
                paid_hours = max(0, duration_hours - self.LUNCH_BREAK_HOURS)
            else:
                paid_hours = duration_hours

            actual_paid_hours = min(paid_hours, self.STANDARD_PAID_HOURS) + overtime
            total_paid_hours += actual_paid_hours

            if actual_paid_hours > 0:
                days_present += 1.0 

        for d, (lt, value) in approved_leaves.items():
            if schedule.get(d) and "Rest Day" not in schedule.get(d):
                days_present += value

        return {
            'days_present': days_present,
            'total_overtime_hours': round(total_overtime_hours, 2),
            'total_working_days': total_working_days,
            'approved_leaves_days': total_leave_days,
            'total_tardiness_minutes': round(total_tardiness_minutes, 2),
            'total_undertime_minutes': round(total_undertime_minutes, 2),
        }

    def calculate_pay(self, employee_id, month, year, period=1):
        cursor = self.conn.cursor()
         emp_row = cursor.execute("SELECT salary FROM employees WHERE id=?", (employee_id,)).fetchone()
        if not emp_row:
            cursor.close()
            return None, "Employee not found."

        monthly_salary = employee_data[0]
        daily_rate = self.calculate_daily_rate(monthly_salary)

        hourly_rate = daily_rate / self.STANDARD_PAID_HOURS  # 8 hours per workday
        minute_rate = hourly_rate / 60

        if period == 1:
            start_date = date(year, month, 1)
            end_date = date(year, month, 15)
            period_label = "1st Half (1-15)"
        else:
            start_date = date(year, month, 16)
            end_of_month = (date(year, month, 1).replace(day=28) + timedelta(days=4))
            end_of_month = end_of_month - timedelta(days=end_of_month.day)
            end_date = end_of_month
            period_label = "2nd Half (16-End)"

        attendance = self.get_attendance_summary(employee_id, start_date, end_date)

        total_working_days = attendance_data['total_working_days']
        days_present = attendance_data['days_present']
        total_overtime_hours = attendance_data['total_overtime_hours']
        approved_leaves_days = attendance_data['approved_leaves_days']
        total_tardiness_minutes = attendance_data['total_tardiness_minutes']
        total_undertime_minutes = attendance_data['total_undertime_minutes']

        days_absent = total_working_days - days_present

        absence_deduction = days_absent * daily_rate
        overtime_pay = total_overtime_hours * hourly_rate * 1.25

        tardiness_deduction = total_tardiness_minutes * minute_rate
        undertime_deduction = total_undertime_minutes * minute_rate
        total_time_based_deduction = tardiness_deduction + undertime_deduction

        base_pay = days_present * daily_rate
        gross_pay = base_pay + overtime_pay

        sss, pagibig, philhealth, tax = self.calculate_deductions(monthly_salary)
        sss /= 2
        pagibig /= 2
        philhealth /= 2
        tax /= 2
        total_mandatory_deductions = sss + pagibig + philhealth + tax

        loan_deduction = 0.0
        loans = cursor.execute("""
            SELECT id, remaining_balance FROM loans
            WHERE employee_id = ? AND status = 'Approved' AND remaining_balance > 0
            ORDER BY date_requested ASC
        """, (employee_id,)).fetchall()

        remaining_to_deduct = gross_pay * 0.10
        for loan_id, remaining_balance in loans:
            if remaining_to_deduct <= 0:
                break
            deduct_now = min(remaining_balance, remaining_to_deduct)
            loan_deduction += deduct_now
            remaining_to_deduct -= deduct_now

            cursor.execute("""
                UPDATE loans SET remaining_balance = remaining_balance - ?
                WHERE id = ?
            """, (deduct_now, loan_id))

        total_deductions = total_mandatory_deductions + absence_deduction + total_time_based_deduction + loan_deduction
        net_pay = gross_pay - total_deductions

        report = {
            'month': date(year, month, 1).strftime("%B %Y"),
            'period_label': period_label,
            'monthly_salary': monthly_salary,
            'daily_rate': daily_rate,
            'hourly_rate': hourly_rate,
            'days_present': round(days_present - approved_leaves_days, 2),
            'approved_leaves_days': approved_leaves_days,
            'days_absent': round(days_absent, 2),
            'total_overtime_hours': total_overtime_hours,
            'base_pay': base_pay,
            'overtime_pay': overtime_pay,
            'gross_pay': gross_pay,
            'sss': sss,
            'pagibig': pagibig,
            'philhealth': philhealth,
            'tax': tax,
            'absence_deduction': absence_deduction,
            'total_tardiness_minutes': total_tardiness_minutes,
            'total_undertime_minutes': total_undertime_minutes,
            'tardiness_deduction': tardiness_deduction,
            'undertime_deduction': undertime_deduction,
            'loan_deduction': loan_deduction,
            'total_mandatory_deductions': total_mandatory_deductions,
            'total_deductions': total_deductions,
            'net_pay': net_pay
        }

        period_key = f"{report['month']} - {period_label}"
        cursor.execute("""
            INSERT OR REPLACE INTO payroll (employee_id, month_year, gross_pay, total_deductions, net_pay)
            VALUES (?, ?, ?, ?, ?)
        """, (employee_id, period_key, gross_pay, total_deductions, net_pay))
        self.conn.commit()

        cursor.close()  # Ensure cursor is closed after use

        return report, None




















