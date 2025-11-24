import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from datetime import timedelta, date
from config import DB_NAME
from database import AppDB
from payroll import PayrollSystem


class EmployeeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Employee Management System (Payroll & Attendance)")
        self.geometry("1000x700")
        self.db = AppDB(DB_NAME)
        self.payroll_system = PayrollSystem(self.db.conn)

        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        self.style.configure('TFrame', background='white')
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=10, background='lightgray', foreground='black')
        self.style.map('TButton', background=[('active', 'gray')])
        self.style.configure('TLabel', font=('Arial', 10), background='white', foreground='black')
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='black', background='white')
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='black', background='lightgray')

        self.style.configure('Bw.TLabelframe', background='white', foreground='black')
        self.style.configure('Bw.TLabelframe.Label', background='white', foreground='black', font=('Arial', 12, 'bold'))

        self.user_id = None
        self.show_login_page()

    def _logout(self):
        self.user_id = None
        self.show_login_page()

    def show_login_page(self):
        for widget in self.winfo_children():
            widget.destroy()

        login_frame = ttk.Frame(self, padding="20 20 20 20")
        login_frame.pack(expand=True, fill='both')

        ttk.Label(login_frame, text="System Login", style='Title.TLabel').pack(pady=20)

        ttk.Label(login_frame, text="Admin Code:").pack(pady=5)
        self.admin_code_entry = ttk.Entry(login_frame, show='*', width=30)
        self.admin_code_entry.pack(pady=5)
        ttk.Button(login_frame, text="Admin Login", command=self.admin_login).pack(pady=10)

        ttk.Separator(login_frame, orient='horizontal').pack(fill='x', pady=20)

        ttk.Label(login_frame, text="Employee ID: (e.g., EMP001)").pack(pady=5)
        self.employee_id_entry = ttk.Entry(login_frame, width=30)
        self.employee_id_entry.pack(pady=5)
        ttk.Button(login_frame, text="Employee Time Clock", command=self.employee_login).pack(pady=10)

    def admin_login(self):
        code = self.admin_code_entry.get()
        if code == 'admin0107':
            self.show_admin_interface()
        else:
            messagebox.showerror("Login Failed", "Invalid Admin Code.")
            self.admin_code_entry.delete(0, tk.END)

    def employee_login(self):
        employee_id = self.employee_id_entry.get().upper().strip()
        cursor = self.db.conn.cursor()
        if cursor.execute("SELECT name FROM employees WHERE id=?", (employee_id,)).fetchone():
            self.user_id = employee_id
            self.show_employee_interface()
        else:
            messagebox.showerror("Login Failed", "Invalid Employee ID.")

    def show_admin_interface(self):
        for widget in self.winfo_children():
            widget.destroy()

        admin_frame = ttk.Frame(self, padding="10")
        admin_frame.pack(expand=True, fill='both')

        top_bar = ttk.Frame(admin_frame)
        top_bar.pack(fill='x')
        ttk.Label(top_bar, text="Admin Dashboard", style='Title.TLabel').pack(side='left', pady=10, padx=10)
        ttk.Button(top_bar, text="Logout", command=self._logout).pack(side='right', pady=10, padx=10)

        notebook = ttk.Notebook(admin_frame)
        notebook.pack(expand=True, fill='both', pady=10)

        self.payroll_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.payroll_tab, text='Payroll & Deductions')
        self._setup_payroll_tab()

        self.attendance_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.attendance_tab, text='Attendance & Absences')
        self._setup_attendance_tab()

        self.schedule_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.schedule_tab, text='Schedules & Shifts')
        self._setup_schedule_tab()

        self.employee_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.employee_tab, text='Employee Data')
        self._setup_employee_tab()

        self.leave_management_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.leave_management_tab, text='Leave Management')
        self._setup_leave_tab()

        self.loan_management_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.loan_management_tab, text='Loan Management')
        self._setup_loan_tab()

    def _setup_payroll_tab(self):
        select_frame = ttk.Frame(self.payroll_tab, padding="10", style='Header.TLabel')
        select_frame.pack(fill='x', pady=5)

        ttk.Label(select_frame, text="Search Name:").pack(side='left', padx=5)
        self.payroll_search_entry = ttk.Entry(select_frame, width=20)
        self.payroll_search_entry.pack(side='left', padx=5)
        ttk.Button(select_frame, text="Search", command=self._refresh_payroll_employee_list).pack(side='left', padx=5)

        ttk.Label(select_frame, text="Employee:").pack(side='left', padx=(20, 5))
        self.payroll_employee_var = tk.StringVar(self.payroll_tab)
        self.payroll_employee_combo = ttk.Combobox(select_frame, textvariable=self.payroll_employee_var, state='readonly', width=30)
        self.payroll_employee_combo.pack(side='left', padx=10)

        current_month = datetime.date.today().month
        current_year = datetime.date.today().year
        months = [str(i) for i in range(1, 13)]
        years = [str(current_year - 1), str(current_year), str(current_year + 1)]

        self.payroll_month_var = tk.StringVar(self.payroll_tab, value=str(current_month))
        self.payroll_year_var = tk.StringVar(self.payroll_tab, value=str(current_year))

        ttk.Label(select_frame, text="Month:").pack(side='left', padx=(20, 5))
        ttk.Combobox(select_frame, textvariable=self.payroll_month_var, values=months, state='readonly', width=5).pack(side='left', padx=5)
        ttk.Label(select_frame, text="Year:").pack(side='left', padx=(10, 5))
        ttk.Combobox(select_frame, textvariable=self.payroll_year_var, values=years, state='readonly', width=7).pack(side='left', padx=5)

        ttk.Label(select_frame, text="Period:").pack(side='left', padx=(10, 5))
        self.payroll_period_var = tk.StringVar(self.payroll_tab, value="1")
        ttk.Combobox(
            select_frame,
            textvariable=self.payroll_period_var,
            values=["1", "2"],
            state='readonly',
            width=5
        ).pack(side='left', padx=5)

        ttk.Button(select_frame, text="Generate Payroll", command=self._generate_payroll_report).pack(side='left', padx=10)
        ttk.Button(select_frame, text="Generate Payroll for All", command=self._generate_all_payroll_reports).pack(side='left', padx=10)

        self.payroll_output = tk.Text(self.payroll_tab, wrap='word', height=25, font=('Courier New', 10), padx=10, pady=10)
        self.payroll_output.pack(expand=True, fill='both', pady=10)

        self._refresh_payroll_employee_list()

    def _refresh_payroll_employee_list(self):
        cursor = self.db.conn.cursor()
        keyword = self.payroll_search_entry.get().strip()
        if keyword:
            employees = cursor.execute("SELECT id, name FROM employees WHERE name LIKE ? ORDER BY id", (f"%{keyword}%",)).fetchall()
        else:
            employees = cursor.execute("SELECT id, name FROM employees ORDER BY id").fetchall()

        self.payroll_employees = [f"{eid} - {name}" for eid, name in employees]
        self.payroll_employee_combo['values'] = self.payroll_employees
        if self.payroll_employees:
            self.payroll_employee_var.set(self.payroll_employees[0])
        else:
            self.payroll_employee_var.set("")

    def _generate_payroll_report(self):
        selected_emp = self.payroll_employee_var.get()
        if not selected_emp:
            messagebox.showerror("Input Error", "No employee selected.")
            return
        emp_id = selected_emp.split(' - ')[0]

        try:
            month = int(self.payroll_month_var.get())
            year = int(self.payroll_year_var.get())
            period = int(self.payroll_period_var.get())
        except Exception:
            messagebox.showerror("Input Error", "Please select valid month/year/period.")
            return

        report, err = self.payroll_system.calculate_pay(emp_id, month, year, period)
        self.payroll_output.delete('1.0', tk.END)

        if err or not report:
            self.payroll_output.insert(tk.END, f"Error: {err or 'Could not generate payroll'}")
            return

        self.payroll_output.insert(tk.END, self._format_payroll(report, selected_emp))
        messagebox.showinfo("Payroll Generated", f"Payroll for {selected_emp} in {report['month']} ({report['period_label']}) calculated.")

    def _generate_all_payroll_reports(self):
        try:
            month = int(self.payroll_month_var.get())
            year = int(self.payroll_year_var.get())
            period = int(self.payroll_period_var.get())
        except Exception:
            messagebox.showerror("Input Error", "Please select valid month/year/period.")
            return

        cursor = self.db.conn.cursor()
        employees = cursor.execute("SELECT id, name FROM employees ORDER BY id").fetchall()
        self.payroll_output.delete('1.0', tk.END)

        if not employees:
            self.payroll_output.insert(tk.END, "No employees found. Add employees first.")
            return

        for eid, name in employees:
            report, err = self.payroll_system.calculate_pay(eid, month, year, period)
            if report:
                self.payroll_output.insert(tk.END, self._format_payroll(report, f"{eid} - {name}"))
                self.payroll_output.insert(tk.END, "\n\n")

        messagebox.showinfo("Payroll Generated", f"Payroll for ALL employees in {date(year, month, 1).strftime('%B %Y')} ({'1st Half' if period==1 else '2nd Half'}) calculated.")

    def _format_payroll(self, report, selected_emp):
        return f"""
=========================================================
PAYROLL STATEMENT for {report['month']} - {report['period_label']}
Employee: {selected_emp}
=========================================================
1. BASIC COMPENSATION
---------------------------------------------------------
Monthly Salary:       PHP {report['monthly_salary']:,.2f}
Daily Rate:           PHP {report['daily_rate']:,.2f}
Hourly Rate (7hrs):   PHP {report['hourly_rate']:,.2f}

2. ATTENDANCE & EARNINGS
---------------------------------------------------------
Days Present (Logged):{report['days_present']} days
Approved Leaves (Paid):{report['approved_leaves_days']} days
Unpaid Absences:      {report['days_absent']} days
Overtime Hours:       {report['total_overtime_hours']:.2f} hrs

Base Pay:             PHP {report['base_pay']:,.2f}
Overtime Pay (125%):  PHP {report['overtime_pay']:,.2f}
---------------------------------------------------------
GROSS PAY:            PHP {report['gross_pay']:,.2f}
=========================================================
3. MANDATORY DEDUCTIONS (Semi-monthly share)
---------------------------------------------------------
SSS Contribution:     PHP {report['sss']:,.2f}
Pag-Ibig (HDMF):      PHP {report['pagibig']:,.2f}
Philhealth:           PHP {report['philhealth']:,.2f}
Tax Withholding:      PHP {report['tax']:,.2f}
---------------------------------------------------------
TOTAL MANDATORY DEDUCTIONS: PHP {report['total_mandatory_deductions']:,.2f}

4. ADJUSTMENTS & TIME DEDUCTIONS
---------------------------------------------------------
Absence Deduction:    PHP {report['absence_deduction']:,.2f}
Tardiness (Minutes):  {report['total_tardiness_minutes']:.2f} min
Tardiness Deduction:  PHP {report['tardiness_deduction']:,.2f}
Undertime (Minutes):  {report['total_undertime_minutes']:.2f} min
Undertime Deduction:  PHP {report['undertime_deduction']:,.2f}
Loan Deduction:       PHP {report['loan_deduction']:,.2f}

5. SUMMARY
---------------------------------------------------------
Total Deductions:     PHP {report['total_deductions']:,.2f}
GROSS PAY:            PHP {report['gross_pay']:,.2f}
---------------------------------------------------------
NET PAY:              PHP {report['net_pay']:,.2f}
=========================================================
"""

    def _setup_attendance_tab(self):
        select_frame = ttk.Frame(self.attendance_tab, padding="10", style='Header.TLabel')
        select_frame.pack(fill='x', pady=5)
        ttk.Label(select_frame, text="Track Attendance for:").pack(side='left', padx=5)

        cursor = self.db.conn.cursor()
        employees = cursor.execute("SELECT id, name FROM employees ORDER BY id").fetchall()
        self.att_employees = [f"{eid} - {name}" for eid, name in employees]

        self.att_employee_var = tk.StringVar(self.attendance_tab)
        self.att_employee_combo = ttk.Combobox(select_frame, textvariable=self.att_employee_var, values=self.att_employees, state='readonly', width=30)
        self.att_employee_combo.pack(side='left', padx=10)
        if self.att_employees:
            self.att_employee_var.set(self.att_employees[0])

        ttk.Button(select_frame, text="Refresh Employees", command=self._refresh_attendance_employees).pack(side='left', padx=10)

        current_month = datetime.date.today().month
        current_year = datetime.date.today().year
        months = [str(i) for i in range(1, 13)]
        years = [str(current_year - 1), str(current_year), str(current_year + 1)]

        self.att_month_var = tk.StringVar(self.attendance_tab, value=str(current_month))
        self.att_year_var = tk.StringVar(self.attendance_tab, value=str(current_year))

        ttk.Label(select_frame, text="Month:").pack(side='left', padx=(20, 5))
        ttk.Combobox(select_frame, textvariable=self.att_month_var, values=months, state='readonly', width=5).pack(side='left', padx=5)
        ttk.Label(select_frame, text="Year:").pack(side='left', padx=(10, 5))
        ttk.Combobox(select_frame, textvariable=self.att_year_var, values=years, state='readonly', width=7).pack(side='left', padx=5)

        ttk.Button(select_frame, text="View Attendance Summary", command=self._view_attendance_summary).pack(side='left', padx=15)

        manual_log_frame = ttk.LabelFrame(self.attendance_tab, text="Admin Manual Attendance Logging (Add/Update Log by Date)", padding="10")
        manual_log_frame.pack(fill='x', pady=10)

        ttk.Label(manual_log_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.manual_att_date_entry = ttk.Entry(manual_log_frame, width=15)
        self.manual_att_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(manual_log_frame, text="Time In (HH:MM:SS):").grid(row=0, column=2, padx=15, pady=5, sticky='w')
        self.manual_att_time_in_entry = ttk.Entry(manual_log_frame, width=12)
        self.manual_att_time_in_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(manual_log_frame, text="Time Out (HH:MM:SS):").grid(row=0, column=4, padx=15, pady=5, sticky='w')
        self.manual_att_time_out_entry = ttk.Entry(manual_log_frame, width=12)
        self.manual_att_time_out_entry.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        ttk.Button(manual_log_frame, text="Add/Update Log", command=self._add_update_attendance_log).grid(row=0, column=6, padx=15, sticky='e')

        columns = ('date', 'time_in', 'time_out', 'hours', 'overtime', 'type')
        self.attendance_tree = ttk.Treeview(self.attendance_tab, columns=columns, show='headings')
        for col in columns:
            self.attendance_tree.heading(col, text=col.replace('_', ' ').title())
        self.attendance_tree.column('date', width=100, anchor='center')
        self.attendance_tree.column('time_in', width=80, anchor='center')
        self.attendance_tree.column('time_out', width=80, anchor='center')
        self.attendance_tree.column('hours', width=80, anchor='center')
        self.attendance_tree.column('overtime', width=80, anchor='center')
        self.attendance_tree.column('type', width=120, anchor='center')
        self.attendance_tree.pack(expand=True, fill='both', pady=10)

        self.attendance_tree.bind("<<TreeviewSelect>>", self._load_log_for_edit)

        self.att_summary_label = ttk.Label(self.attendance_tab, text="Select an employee and month, then click 'View Attendance Summary' to begin.", style='Header.TLabel')
        self.att_summary_label.pack(fill='x', pady=5)

    def _refresh_attendance_employees(self):
        cursor = self.db.conn.cursor()
        employees = cursor.execute("SELECT id, name FROM employees ORDER BY id").fetchall()
        self.att_employees = [f"{eid} - {name}" for eid, name in employees]
        self.att_employee_combo['values'] = self.att_employees
        if self.att_employees:
            self.att_employee_var.set(self.att_employees[0])
        else:
            self.att_employee_var.set("")

    def _load_log_for_edit(self, event):
        selected_item = self.attendance_tree.focus()
        if not selected_item:
            return
        values = self.attendance_tree.item(selected_item, 'values')
        if not values:
            return
        status = values[5].strip()
        if status not in ("Present"):
            return
        self.manual_att_date_entry.delete(0, tk.END)
        self.manual_att_time_in_entry.delete(0, tk.END)
        self.manual_att_time_out_entry.delete(0, tk.END)
        self.manual_att_date_entry.insert(0, values[0])
        self.manual_att_time_in_entry.insert(0, values[1] if values[1] != 'N/A' else '')
        self.manual_att_time_out_entry.insert(0, values[2] if values[2] != 'N/A' else '')

    def _add_update_attendance_log(self):
        try:
            selected_emp = self.att_employee_var.get()
            if not selected_emp:
                messagebox.showerror("Input Error", "No employee selected.")
                return
            emp_id = selected_emp.split(' - ')[0]

            log_date = self.manual_att_date_entry.get().strip()
            time_in = self.manual_att_time_in_entry.get().strip()
            time_out = self.manual_att_time_out_entry.get().strip()

            if not all([emp_id, log_date, time_in, time_out]):
                messagebox.showerror("Input Error", "All fields must be filled.")
                return

            datetime.datetime.strptime(log_date, '%Y-%m-%d')
            datetime.datetime.strptime(time_in, '%H:%M:%S')
            datetime.datetime.strptime(time_out, '%H:%M:%S')
        except ValueError:
            messagebox.showerror("Format Error", "Date must be YYYY-MM-DD and Time HH:MM:SS.")
            return

        cursor = self.db.conn.cursor()
        existing_log = cursor.execute("SELECT time_in FROM attendance WHERE employee_id=? AND date=?", (emp_id, log_date)).fetchone()
        action_type = "Updated" if existing_log else "Added"

        self.db.cursor.execute("""
            INSERT OR REPLACE INTO attendance (employee_id, date, time_in, time_out)
            VALUES (?, ?, ?, ?)
        """, (emp_id, log_date, time_in, time_out))
        self.db.conn.commit()

        messagebox.showinfo(f"Log {action_type}", f"Attendance log for {emp_id} on {log_date} {action_type.lower()}.")

        log_date_obj = datetime.datetime.strptime(log_date, '%Y-%m-%d').date()
        if int(self.att_month_var.get()) == log_date_obj.month and int(self.att_year_var.get()) == log_date_obj.year:
            self._view_attendance_summary()

    def _view_attendance_summary(self):
        for i in self.attendance_tree.get_children():
            self.attendance_tree.delete(i)

        selected_emp = self.att_employee_var.get()
        if not selected_emp:
            self.att_summary_label.config(text="No employee selected.", foreground='red')
            return
        emp_id = selected_emp.split(' - ')[0]

        month = int(self.att_month_var.get())
        year = int(self.att_year_var.get())

        start_date = date(year, month, 1)
        end_date = date(year, month, 1).replace(day=28) + timedelta(days=4)
        end_date = end_date - timedelta(days=end_date.day)

        schedule, total_working_days = self.payroll_system.get_employee_schedule(emp_id, month, year)
        approved_leaves = self.payroll_system.get_approved_leaves(emp_id, start_date, end_date)

        cursor = self.db.conn.cursor()
        records = cursor.execute(
            "SELECT date, time_in, time_out FROM attendance WHERE employee_id=? AND date BETWEEN ? AND ?",
            (emp_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        ).fetchall()

        logged_dates = {rec[0] for rec in records}
        total_overtime = 0.0
        days_logged = 0
        days_on_leave = sum(v for _, v in approved_leaves.values())

        self.attendance_tree.tag_configure('rest_day', background='#e0e0e0')
        self.attendance_tree.tag_configure('absent', background='#ffcccc', foreground='darkred')
        self.attendance_tree.tag_configure('present', background='#ccffcc')
        self.attendance_tree.tag_configure('approved_leave', background='#99ccff')
        self.attendance_tree.tag_configure('partial_log', background='#ffeb99', foreground='darkorange')

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            day_name = current_date.strftime('%a')

            shift_info = schedule.get(date_str, "Rest Day")
            if shift_info.startswith("Work Day"):
                if date_str in approved_leaves:
                    lt, val = approved_leaves[date_str]
                    self.attendance_tree.insert('', tk.END, values=(
                        date_str, '--- PAID ---', '--- LEAVE ---',
                        f"{val * 7:.2f}h", '0.00h',
                        f"Approved {lt}"
                    ), tags=('approved_leave',))
                elif date_str in logged_dates:
                    days_logged += 1
                    time_in, time_out = next(((t_in, t_out) for d, t_in, t_out in records if d == date_str), ('', ''))

                    duration_hours, overtime = 0.0, 0.0
                    log_status = "Present"
                    tags = ('present',)

                    if time_in and time_out:
                        try:
                            dt_in = datetime.datetime.strptime(f"{date_str} {time_in}", '%Y-%m-%d %H:%M:%S')
                            dt_out = datetime.datetime.strptime(f"{date_str} {time_out}", '%Y-%m-%d %H:%M:%S')
                            if dt_out <= dt_in:
                                dt_out += timedelta(days=1)
                            duration = dt_out - dt_in
                            duration_hours = duration.total_seconds() / 3600

                            if duration_hours >= 5:
                                duration_hours = max(0, duration_hours - 1)

                            details = shift_info
                            if "Shift A" in details or "Shift B" in details or "Shift C" in details:
                                overtime = max(0.0, duration_hours - 7)
                            else:
                                overtime = max(0.0, duration_hours - 7)

                            total_overtime += overtime
                        except ValueError:
                            log_status = "Data Error"
                            tags = ('absent',)
                    else:
                        log_status = "Partial Log"
                        tags = ('partial_log',)

                    self.attendance_tree.insert('', tk.END, values=(
                        date_str,
                        time_in or 'N/A',
                        time_out or 'N/A',
                        f"{duration_hours:.2f}h",
                        f"{overtime:.2f}h",
                        log_status
                    ), tags=tags)
                else:
                    self.attendance_tree.insert('', tk.END, values=(
                        date_str, '--- UNPAID ---', '--- ABSENT ---',
                        '0.00h', '0.00h', "Absent"
                    ), tags=('absent',))
            else:
                self.attendance_tree.insert('', tk.END, values=(
                    date_str, '---', shift_info.split('(')[0].strip(),
                    '0.00h', '0.00h', day_name
                ), tags=('rest_day',))

            current_date += timedelta(days=1)

        days_paid = days_logged + days_on_leave
        days_absent_unpaid = total_working_days - days_paid

        self.att_summary_label.config(
            text=(
                f"Summary for {selected_emp} in {start_date.strftime('%B %Y')}: "
                f"Work Days: {total_working_days} | "
                f"Days Logged: {days_logged} | "
                f"Approved Leaves: {days_on_leave} | "
                f"Unpaid Absences: {days_absent_unpaid} | "
                f"Total OT: {total_overtime:.2f} hrs"
            ),
            foreground='black'
        )

    def _setup_schedule_tab(self):
        select_frame = ttk.Frame(self.schedule_tab, padding="10", style='Header.TLabel')
        select_frame.pack(fill='x', pady=5)
        ttk.Label(select_frame, text="View Schedule for:").pack(side='left', padx=5)

        cursor = self.db.conn.cursor()
        employees = cursor.execute("SELECT id, name FROM employees ORDER BY id").fetchall()
        self.sched_employees = [f"{eid} - {name}" for eid, name in employees]
        self.sched_employee_var = tk.StringVar(self.schedule_tab)
        self.sched_employee_combo = ttk.Combobox(select_frame, textvariable=self.sched_employee_var, values=self.sched_employees, state='readonly', width=30)
        self.sched_employee_combo.pack(side='left', padx=10)
        if self.sched_employees:
            self.sched_employee_var.set(self.sched_employees[0])

        ttk.Button(select_frame, text="Refresh Employees", command=self._refresh_schedule_employees).pack(side='left', padx=10)

        current_month = datetime.date.today().month
        current_year = datetime.date.today().year
        self.sched_month_var = tk.StringVar(self.schedule_tab, value=str(current_month))
        self.sched_year_var = tk.StringVar(self.schedule_tab, value=str(current_year))

        ttk.Label(select_frame, text="Month:").pack(side='left', padx=(20, 5))
        ttk.Combobox(select_frame, textvariable=self.sched_month_var, values=[str(i) for i in range(1, 13)], state='readonly', width=5).pack(side='left', padx=5)
        ttk.Label(select_frame, text="Year:").pack(side='left', padx=(10, 5))
        ttk.Combobox(select_frame, textvariable=self.sched_year_var, values=[str(current_year - 1), str(current_year), str(current_year + 1)], state='readonly', width=7).pack(side='left', padx=5)

        ttk.Button(select_frame, text="Generate Schedule", command=self._generate_schedule_view).pack(side='left', padx=15)
        ttk.Button(select_frame, text="Open Calendar View", command=self._open_calendar_view).pack(side='left', padx=5)

        columns = ('date', 'day', 'shift_details')
        self.schedule_tree = ttk.Treeview(self.schedule_tab, columns=columns, show='headings')
        for col in columns:
            self.schedule_tree.heading(col, text=col.capitalize())
        self.schedule_tree.column('date', width=100, anchor='center')
        self.schedule_tree.column('day', width=80, anchor='center')
        self.schedule_tree.column('shift_details', minwidth=200, anchor='w')
        self.schedule_tree.pack(expand=True, fill='both', pady=10)

        self.schedule_tree.tag_configure('work_day', background='#ccffcc')
        self.schedule_tree.tag_configure('rest_day', background='#e0e0e0')

        self.schedule_info_label = ttk.Label(self.schedule_tab, text="", style='Header.TLabel')
        self.schedule_info_label.pack(fill='x', pady=5)

    def _refresh_schedule_employees(self):
        cursor = self.db.conn.cursor()
        employees = cursor.execute("SELECT id, name FROM employees ORDER BY id").fetchall()
        self.sched_employees = [f"{eid} - {name}" for eid, name in employees]
        self.sched_employee_combo['values'] = self.sched_employees
        if self.sched_employees:
            self.sched_employee_var.set(self.sched_employees[0])
        else:
            self.sched_employee_var.set("")

    def _generate_schedule_view(self):
        for i in self.schedule_tree.get_children():
            self.schedule_tree.delete(i)

        selected_emp = self.sched_employee_var.get()
        if not selected_emp:
            self.schedule_info_label.config(text="No employee selected.", foreground='red')
            return

        emp_id = selected_emp.split(' - ')[0]
        month = int(self.sched_month_var.get())
        year = int(self.sched_year_var.get())

        schedule, total_workdays = self.payroll_system.get_employee_schedule(emp_id, month, year)
        if isinstance(schedule, str):
            self.schedule_info_label.config(text=f"Error: {schedule}", foreground='red')
            return

        import datetime as _dt
        for date_str, details in schedule.items():
            date_obj = _dt.datetime.strptime(date_str, '%Y-%m-%d').date()
            day_name = date_obj.strftime('%a')
            tag = 'work_day' if details.startswith("Work Day") else 'rest_day'
            self.schedule_tree.insert('', tk.END, values=(date_str, day_name, details), tags=(tag,))

        self.schedule_info_label.config(
            text=f"Schedule generated for {selected_emp} in {date(year, month, 1).strftime('%B %Y')}. Total expected workdays: {total_workdays}.",
            foreground='black'
        )

    def _open_calendar_view(self):
        try:
            from tkcalendar import Calendar
        except Exception:
            messagebox.showinfo("Calendar Not Installed", "tkcalendar is not installed. Install it to enable calendar view.\n\npip install tkcalendar")
            return

        selected_emp = self.sched_employee_var.get()
        if not selected_emp:
            messagebox.showerror("Error", "No employee selected.")
            return
        emp_id = selected_emp.split(' - ')[0]
        month = int(self.sched_month_var.get())
        year = int(self.sched_year_var.get())

        schedule, _ = self.payroll_system.get_employee_schedule(emp_id, month, year)

        win = tk.Toplevel(self)
        win.title(f"Calendar View - {selected_emp}")
        win.geometry("600x500")

        cal = Calendar(win, selectmode='day', year=year, month=month, day=1)
        cal.pack(pady=10, fill='both', expand=True)

        for dstr, info in schedule.items():
            if info.startswith("Work Day"):
                y, m, dd = map(int, dstr.split("-"))
                cal.calevent_create(date(y, m, dd), info, 'work')

        cal.tag_config('work', background='lightgreen', foreground='black')

    def _setup_employee_tab(self):
        input_frame = ttk.LabelFrame(self.employee_tab, text="Employee Details (Add New or Edit Selected)", padding="10")
        input_frame.pack(fill='x', pady=10)

        fields = ['ID (e.g., EMP051):', 'Name:', 'Position:', 'Department:', 'Monthly Salary:']
        self.emp_entries = {}

        for i, field in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            ttk.Label(input_frame, text=field).grid(row=row, column=col, padx=10, pady=5, sticky='w')
            entry = ttk.Entry(input_frame, width=30)
            entry.grid(row=row, column=col + 1, padx=10, pady=5, sticky='w')
            self.emp_entries[field] = entry

        button_frame = ttk.Frame(self.employee_tab)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Add New Employee", command=self._add_employee).pack(side='left', padx=10)
        self.edit_button = ttk.Button(button_frame, text="Save Edits", command=self._edit_employee, state='disabled')
        self.edit_button.pack(side='left', padx=10)
        self.cancel_edit_button = ttk.Button(button_frame, text="Cancel Edit", command=self._cancel_edit, state='disabled')
        self.cancel_edit_button.pack(side='left', padx=10)
        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self._delete_employee, state='disabled')
        self.delete_button.pack(side='left', padx=10)

        ttk.Label(self.employee_tab, text="All Employees (Click to Edit or Delete)", style='Header.TLabel').pack(fill='x', pady=10)
        columns = ('id', 'name', 'position', 'department', 'salary')
        self.employee_tree = ttk.Treeview(self.employee_tab, columns=columns, show='headings')
        for col in columns:
            self.employee_tree.heading(col, text=col.capitalize())
            self.employee_tree.column(col, width=100 if col in ('id', 'salary') else 150, anchor='center' if col in ('id', 'salary') else 'w')
        self.employee_tree.pack(expand=True, fill='both', pady=5)

        self.employee_tree.bind("<<TreeviewSelect>>", self._load_employee_for_edit)
        self._load_all_employees()

    def _load_all_employees(self):
        for i in self.employee_tree.get_children():
            self.employee_tree.delete(i)
        cursor = self.db.conn.cursor()
        employees = cursor.execute("SELECT id, name, position, department, salary FROM employees ORDER BY id").fetchall()
        for emp in employees:
            formatted_salary = f"PHP {emp[4]:,.2f}"
            self.employee_tree.insert('', tk.END, values=(emp[0], emp[1], emp[2], emp[3], formatted_salary))

    def _cancel_edit(self):
        for entry in self.emp_entries.values():
            entry.delete(0, tk.END)
        self.emp_entries['ID (e.g., EMP051):'].config(state='normal')
        self.edit_button.config(state='disabled')
        self.cancel_edit_button.config(state='disabled')
        self.delete_button.config(state='disabled')
        self.employee_tree.selection_remove(self.employee_tree.selection())

    def _load_employee_for_edit(self, event):
        selected_item = self.employee_tree.focus()
        if not selected_item:
            return
        values = self.employee_tree.item(selected_item, 'values')
        if not values:
            return

        for entry in self.emp_entries.values():
            entry.delete(0, tk.END)

        id_field = self.emp_entries['ID (e.g., EMP051):']
        id_field.insert(0, values[0])
        id_field.config(state='disabled')

        self.emp_entries['Name:'].insert(0, values[1])
        self.emp_entries['Position:'].insert(0, values[2])
        self.emp_entries['Department:'].insert(0, values[3])
        salary_str = values[4].replace("PHP ", "").replace(",", "")
        self.emp_entries['Monthly Salary:'].insert(0, salary_str)

        self.edit_button.config(state='normal')
        self.cancel_edit_button.config(state='normal')
        self.delete_button.config(state='normal')

    def _add_employee(self):
        data = {k: v.get() for k, v in self.emp_entries.items()}
        emp_id = data['ID (e.g., EMP051):'].strip().upper()
        name = data['Name:']
        position = data['Position:']
        department = data['Department:']

        try:
            salary = float(data['Monthly Salary:'])
        except ValueError:
            messagebox.showerror("Input Error", "Salary must be a valid number.")
            return

        if not all([emp_id, name, position, department, salary]):
            messagebox.showerror("Input Error", "All fields are required.")
            return

        quotas = {
            "Manager": 3,
            "Sales": 7,
            "HR": 3,
            "Production Worker A": 5,
            "Production Worker B": 5,
            "Security Guard": 2,
        }
        cursor = self.db.conn.cursor()
        if position in quotas:
            count = cursor.execute("SELECT COUNT(*) FROM employees WHERE position=?", (position,)).fetchone()[0]
            if count >= quotas[position]:
                messagebox.showerror("Quota Error", f"Maximum for {position} is {quotas[position]}.")
                return

        try:
            self.db.cursor.execute("INSERT INTO employees VALUES (?, ?, ?, ?, ?)",
                                   (emp_id, name, position, department, salary))
            self.db.conn.commit()
            messagebox.showinfo("Success", f"Employee {emp_id} ({name}) added successfully.")
            self._load_all_employees()
            self._cancel_edit()
        except Exception:
            messagebox.showerror("Database Error", f"Employee ID {emp_id} already exists or cannot be added.")

    def _edit_employee(self):
        emp_id = self.emp_entries['ID (e.g., EMP051):'].get().strip().upper()
        if not emp_id:
            messagebox.showerror("Error", "No Employee ID selected for edit.")
            return

        data = {k: v.get() for k, v in self.emp_entries.items()}
        name = data['Name:']
        position = data['Position:']
        department = data['Department:']

        try:
            salary = float(data['Monthly Salary:'])
        except ValueError:
            messagebox.showerror("Input Error", "Salary must be a valid number.")
            return

        if not all([name, position, department, salary]):
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            self.db.cursor.execute("""
                UPDATE employees SET name=?, position=?, department=?, salary=? WHERE id=?
            """, (name, position, department, salary, emp_id))
            self.db.conn.commit()
            messagebox.showinfo("Success", f"Employee {emp_id} details updated successfully.")
            self._load_all_employees()
            self._cancel_edit()
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during update: {e}")

    def _delete_employee(self):
        self.emp_entries['ID (e.g., EMP051):'].config(state='normal')
        emp_id = self.emp_entries['ID (e.g., EMP051):'].get().strip().upper()
        was_in_edit_mode = (self.edit_button.cget('state') == 'normal')
        if was_in_edit_mode:
            self.emp_entries['ID (e.g., EMP051):'].config(state='disabled')

        if not emp_id:
            messagebox.showerror("Error", "Please select an employee from the list to delete.")
            return

        if not messagebox.askyesno("Confirm Deletion", f"Delete employee {emp_id} and ALL their records?"):
            return

        try:
            self.db.cursor.execute("DELETE FROM leaves WHERE employee_id=?", (emp_id,))
            self.db.cursor.execute("DELETE FROM attendance WHERE employee_id=?", (emp_id,))
            self.db.cursor.execute("DELETE FROM payroll WHERE employee_id=?", (emp_id,))
            self.db.cursor.execute("DELETE FROM loans WHERE employee_id=?", (emp_id,))
            self.db.cursor.execute("DELETE FROM employees WHERE id=?", (emp_id,))
            self.db.conn.commit()
            messagebox.showinfo("Success", f"Employee {emp_id} deleted.")
            self._load_all_employees()
            self._cancel_edit()
        except Exception as e:
            messagebox.showerror("Error", f"Deletion failed: {e}")

    def _setup_leave_tab(self):
        ttk.Label(self.leave_management_tab, text="Leave Requests (All Statuses)", style='Header.TLabel').pack(fill='x', pady=10)

        columns = ('id', 'employee_id', 'name', 'date', 'type', 'status')
        self.leave_tree = ttk.Treeview(self.leave_management_tab, columns=columns, show='headings')
        for col in columns:
            self.leave_tree.heading(col, text=col.replace('_', ' ').title())
        self.leave_tree.column('id', width=50, anchor='center')
        self.leave_tree.column('employee_id', width=100, anchor='center')
        self.leave_tree.column('name', width=150, anchor='w')
        self.leave_tree.column('date', width=100, anchor='center')
        self.leave_tree.column('type', width=80, anchor='center')
        self.leave_tree.column('status', width=100, anchor='center')
        self.leave_tree.pack(expand=True, fill='both', pady=5)

        action_frame = ttk.Frame(self.leave_management_tab)
        action_frame.pack(pady=10)

        ttk.Button(action_frame, text="Approve Selected Leave", command=lambda: self._approve_reject_leave('Approved')).pack(side='left', padx=10)
        ttk.Button(action_frame, text="Reject Selected Leave", command=lambda: self._approve_reject_leave('Rejected')).pack(side='left', padx=10)
        ttk.Button(action_frame, text="Delete Selected Leave", command=self._delete_leave).pack(side='left', padx=10)
        ttk.Button(action_frame, text="Refresh List", command=self._load_leave_requests).pack(side='left', padx=10)

        self.leave_tree.tag_configure('pending', background='#ffeb99')
        self.leave_tree.tag_configure('approved', background='#ccffcc')
        self.leave_tree.tag_configure('rejected', background='#ffcccc', foreground='darkred')
        self._load_leave_requests()

    def _load_leave_requests(self):
        for i in self.leave_tree.get_children():
            self.leave_tree.delete(i)

        cursor = self.db.conn.cursor()
        requests = cursor.execute("""
            SELECT l.id, l.employee_id, e.name, l.date, l.leave_type, l.status
            FROM leaves l
            JOIN employees e ON l.employee_id = e.id
            ORDER BY l.date DESC, l.status ASC
        """).fetchall()

        for req in requests:
            tag = req[5].lower()
            self.leave_tree.insert('', tk.END, values=req, tags=(tag,))

    def _approve_reject_leave(self, status):
        selected_item = self.leave_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a leave request.")
            return
        values = self.leave_tree.item(selected_item, 'values')
        leave_id = values[0]

        if messagebox.askyesno("Confirm Action", f"Set leave ID {leave_id} to '{status}'?"):
            self.db.cursor.execute("UPDATE leaves SET status=? WHERE id=?", (status, leave_id))
            self.db.conn.commit()
            self._load_leave_requests()

    def _delete_leave(self):
        selected_item = self.leave_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Select a leave to delete.")
            return
        values = self.leave_tree.item(selected_item, 'values')
        leave_id = values[0]
        if messagebox.askyesno("Confirm Deletion", f"Delete leave ID {leave_id}?"):
            self.db.cursor.execute("DELETE FROM leaves WHERE id=?", (leave_id,))
            self.db.conn.commit()
            self._load_leave_requests()

    def _setup_loan_tab(self):
        ttk.Label(self.loan_management_tab, text="Loan Requests", style='Header.TLabel').pack(fill='x', pady=10)

        columns = ('id', 'employee_id', 'name', 'amount', 'remaining', 'date', 'status')
        self.loan_tree = ttk.Treeview(self.loan_management_tab, columns=columns, show='headings')
        for col in columns:
            self.loan_tree.heading(col, text=col.replace('_', ' ').title())
        self.loan_tree.column('id', width=50, anchor='center')
        self.loan_tree.column('employee_id', width=100, anchor='center')
        self.loan_tree.column('name', width=150, anchor='w')
        self.loan_tree.column('amount', width=100, anchor='center')
        self.loan_tree.column('remaining', width=100, anchor='center')
        self.loan_tree.column('date', width=120, anchor='center')
        self.loan_tree.column('status', width=100, anchor='center')
        self.loan_tree.pack(expand=True, fill='both', pady=5)

        action_frame = ttk.Frame(self.loan_management_tab)
        action_frame.pack(pady=10)

        ttk.Button(action_frame, text="Approve Selected Loan", command=lambda: self._approve_reject_loan('Approved')).pack(side='left', padx=10)
        ttk.Button(action_frame, text="Reject Selected Loan", command=lambda: self._approve_reject_loan('Rejected')).pack(side='left', padx=10)
        ttk.Button(action_frame, text="Refresh List", command=self._load_loans).pack(side='left', padx=10)

        self.loan_tree.tag_configure('pending', background='#ffeb99')
        self.loan_tree.tag_configure('approved', background='#ccffcc')
        self.loan_tree.tag_configure('rejected', background='#ffcccc', foreground='darkred')

        self._load_loans()

    def _load_loans(self):
        for i in self.loan_tree.get_children():
            self.loan_tree.delete(i)

        cursor = self.db.conn.cursor()
        loans = cursor.execute("""
            SELECT l.id, l.employee_id, e.name, l.amount, l.remaining_balance, l.date_requested, l.status
            FROM loans l
            JOIN employees e ON l.employee_id = e.id
            ORDER BY l.date_requested DESC
        """).fetchall()

        for ln in loans:
            tag = ln[6].lower()
            self.loan_tree.insert('', tk.END, values=ln, tags=(tag,))

    def _approve_reject_loan(self, status):
        selected_item = self.loan_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a loan request.")
            return
        values = self.loan_tree.item(selected_item, 'values')
        loan_id = values[0]
        if messagebox.askyesno("Confirm Action", f"Set loan ID {loan_id} to '{status}'?"):
            if status == "Approved":
                self.db.cursor.execute("""
                    UPDATE loans SET status='Approved', remaining_balance=amount WHERE id=?
                """, (loan_id,))
            else:
                self.db.cursor.execute("UPDATE loans SET status=? WHERE id=?", (status, loan_id))
            self.db.conn.commit()
            self._load_loans()

    def show_employee_interface(self):
        for widget in self.winfo_children():
            widget.destroy()

        emp_frame = ttk.Frame(self, padding="50 50 50 50")
        emp_frame.pack(expand=True, fill='both')

        cursor = self.db.conn.cursor()
        emp_name = cursor.execute("SELECT name FROM employees WHERE id=?", (self.user_id,)).fetchone()[0]

        top_bar = ttk.Frame(emp_frame)
        top_bar.pack(fill='x')
        ttk.Label(top_bar, text=f"Welcome, {emp_name}", style='Title.TLabel').pack(side='left', pady=10)
        ttk.Label(top_bar, text=f"Employee ID: {self.user_id}", font=('Arial', 12), background='white', foreground='black').pack(side='left', padx=20)
        ttk.Button(top_bar, text="Logout", command=self._logout).pack(side='right', padx=10)

        clock_frame = ttk.LabelFrame(emp_frame, text="Time Clock", padding="20", style='Bw.TLabelframe')
        clock_frame.pack(pady=10, fill='x')

        self.status_label = ttk.Label(clock_frame, text="Ready to Clock In/Out.", font=('Arial', 14, 'bold'), foreground='black', background='white')
        self.status_label.pack(pady=10)

        button_frame = ttk.Frame(clock_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="TIME IN", command=self._time_in, style='TButton').grid(row=0, column=0, padx=20, ipadx=20, ipady=10)
        ttk.Button(button_frame, text="TIME OUT", command=self._time_out, style='TButton').grid(row=0, column=1, padx=20, ipadx=20, ipady=10)

        leave_frame = ttk.LabelFrame(emp_frame, text="Request Leave", padding="20", style='Bw.TLabelframe')
        leave_frame.pack(pady=20, fill='x')

        ttk.Label(leave_frame, text="Date for Leave (YYYY-MM-DD):", background='white', foreground='black').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.leave_date_entry = ttk.Entry(leave_frame, width=15)
        self.leave_date_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        self.leave_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(leave_frame, text="Leave Type:", background='white', foreground='black').grid(row=0, column=2, padx=15, pady=5, sticky='w')
        self.leave_type_var = tk.StringVar(leave_frame)
        self.leave_type_var.set('Sick Leave')
        leave_types = ['Sick Leave', 'Vacation Leave', 'Vacation Leave (Half Day)']
        ttk.Combobox(leave_frame, textvariable=self.leave_type_var, values=leave_types, state='readonly', width=20).grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Button(leave_frame, text="Submit Leave Request", command=self._submit_leave_request, style='TButton').grid(row=0, column=4, padx=15, sticky='e')

        loan_frame = ttk.LabelFrame(emp_frame, text="Request Loan", padding="20", style='Bw.TLabelframe')
        loan_frame.pack(pady=10, fill='x')

        ttk.Label(loan_frame, text="Loan Amount (PHP):", background='white', foreground='black').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.loan_amount_entry = ttk.Entry(loan_frame, width=15)
        self.loan_amount_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Button(loan_frame, text="Submit Loan Request", command=self._submit_loan_request, style='TButton').grid(row=0, column=2, padx=15, sticky='e')

    def _time_in(self):
        current_date = date.today().strftime('%Y-%m-%d')
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        emp_id = self.user_id

        cursor = self.db.conn.cursor()
        record = cursor.execute("SELECT time_in, time_out FROM attendance WHERE employee_id=? AND date=?",
                                (emp_id, current_date)).fetchone()

        if record and record[0]:
            messagebox.showwarning("Warning", f"Already timed in at {record[0]}.")
            return

        if record:
            self.db.cursor.execute("UPDATE attendance SET time_in=? WHERE employee_id=? AND date=?",
                                   (current_time, emp_id, current_date))
        else:
            self.db.cursor.execute("INSERT INTO attendance (employee_id, date, time_in) VALUES (?, ?, ?)",
                                   (emp_id, current_date, current_time))
        self.db.conn.commit()

        self.status_label.config(text=f"SUCCESS: Time In Recorded at: {current_time}")
        messagebox.showinfo("Success", f"Time In recorded for {emp_id} at {current_time}.")

    def _time_out(self):
        current_date = date.today().strftime('%Y-%m-%d')
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        emp_id = self.user_id

        cursor = self.db.conn.cursor()
        record = cursor.execute("SELECT time_in, time_out FROM attendance WHERE employee_id=? AND date=?",
                                (emp_id, current_date)).fetchone()

        if not record or not record[0]:
            messagebox.showerror("Error", "You must Time In first.")
            return
        if record[1]:
            messagebox.showwarning("Warning", f"Already timed out at {record[1]}.")
            return

        self.db.cursor.execute("UPDATE attendance SET time_out=? WHERE employee_id=? AND date=?",
                               (current_time, emp_id, current_date))
        self.db.conn.commit()

        self.status_label.config(text=f"SUCCESS: Time Out Recorded at: {current_time}")
        messagebox.showinfo("Success", f"Time Out recorded for {emp_id} at {current_time}.")

    def _submit_leave_request(self):
        emp_id = self.user_id
        leave_date_str = self.leave_date_entry.get().strip()
        leave_type = self.leave_type_var.get()

        try:
            leave_date = datetime.datetime.strptime(leave_date_str, '%Y-%m-%d').date()
            if leave_date < date.today():
                messagebox.showerror("Input Error", "Cannot request leave for a past date.")
                return
        except ValueError:
            messagebox.showerror("Format Error", "Date must be in YYYY-MM-DD format.")
            return

        cursor = self.db.conn.cursor()

        month_start = leave_date.replace(day=1)
        month_end = leave_date.replace(day=28) + timedelta(days=4)
        month_end = month_end - timedelta(days=month_end.day)

        existing = cursor.execute("""
            SELECT leave_type, status FROM leaves
            WHERE employee_id=? AND date BETWEEN ? AND ? AND status IN ('Pending','Approved')
        """, (emp_id, month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d'))).fetchall()

        sl_count = sum(1 for lt, _ in existing if lt == 'SL')
        vl_total = sum(1.0 for lt, _ in existing if lt == 'VL') + sum(0.5 for lt, _ in existing if lt == 'VLH')

        if leave_type == 'Sick Leave' and sl_count >= 1:
            messagebox.showerror("Limit Exceeded", "You already used 1 Sick Leave this month.")
            return

        if leave_type.startswith('Vacation'):
            add_val = 1.0 if leave_type == 'Vacation Leave' else 0.5
            if vl_total + add_val > 1.5:
                messagebox.showerror("Limit Exceeded", "Vacation Leave limit is 1.5 days per month.")
                return

        conflict_leave = cursor.execute("SELECT COUNT(*) FROM leaves WHERE employee_id=? AND date=?",
                                        (emp_id, leave_date_str)).fetchone()[0]
        conflict_att = cursor.execute("SELECT COUNT(*) FROM attendance WHERE employee_id=? AND date=?",
                                      (emp_id, leave_date_str)).fetchone()[0]

        if conflict_leave > 0:
            messagebox.showwarning("Conflict", "A leave request already exists for this date.")
            return
        if conflict_att > 0:
            messagebox.showwarning("Conflict", "Attendance is already logged for this date.")
            return

        if leave_type == 'Sick Leave':
            type_abbr = 'SL'
        elif leave_type == 'Vacation Leave':
            type_abbr = 'VL'
        else:
            type_abbr = 'VLH'

        self.db.cursor.execute("""
            INSERT INTO leaves (employee_id, date, leave_type, status)
            VALUES (?, ?, ?, 'Pending')
        """, (emp_id, leave_date_str, type_abbr))
        self.db.conn.commit()

        messagebox.showinfo("Request Sent", f"{leave_type} request for {leave_date_str} sent to Admin.")

    def _submit_loan_request(self):
        emp_id = self.user_id
        amt_str = self.loan_amount_entry.get().strip()
        try:
            amt = float(amt_str)
            if amt <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid positive loan amount.")
            return

        self.db.cursor.execute("""
            INSERT INTO loans (employee_id, amount, remaining_balance, date_requested, status)
            VALUES (?, ?, ?, ?, 'Pending')
        """, (emp_id, amt, 0, date.today().strftime('%Y-%m-%d')))
        self.db.conn.commit()

        self.loan_amount_entry.delete(0, tk.END)
        messagebox.showinfo("Loan Request Sent", f"Loan request of PHP {amt:,.2f} sent to Admin.")


if __name__ == '__main__':
    app = EmployeeApp()
    app.mainloop()