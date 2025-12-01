Payroll and Employee Attendance System
Project Overview
This system is a Payroll and Employee Attendance System designed to automate and simplify how an organization manages its workforce. It replaces manual tracking with a centralized software solution that records attendance, computes salaries, manages employee information, handles deductions, and supports administrative decisions through a clean Graphical User Interface (GUI).
It is built primarily using Python and utilizes Tkinter for the user interface and SQLite3 for persistent internal data storage.
Key Features
•	Automated Payroll Computation: Calculates net pay based on attendance, absences, tardiness, overtime, and leaves.
•	Centralized Employee Records: Securely stores employee IDs, names, positions, salary rates, and departments.
•	Attendance Tracking: Records daily time-in and time-out used for payroll computation.
•	Deduction Management: Automatically handles mandatory government deductions (SSS, PhilHealth, Pag-IBIG, Tax) and applies deductions for loans, tardiness, and undertime.
•	Leave and Loan Management: Allows tracking and approval of employee leave requests and loan balances.
•	User-Friendly GUI: Provides an intuitive interface for staff and administrators (built with Tkinter).
System Architecture and File Structure
The system is organized into four main Python modules, demonstrating a clear separation of concerns (Model-View-Controller-like pattern): 
File	Role	Description
config.py	Configuration	Stores global constants, primarily the database file name (employee_management.db).
database.py	Model/Data Layer	Handles all database connectivity (SQLite3). Contains the AppDB class responsible for creating tables (employees, attendance, payroll, leaves, loans) and executing all CRUD operations.
payroll.py	Controller/Logic	Contains the PayrollSystem class. This is the core business logic handler for all complex calculations, including payroll formulas, deduction rates, attendance summaries, and schedule generation.
gui.py	View/Presentation	Contains the EmployeeApp class (inherits from tk.Tk). This file sets up the entire graphical user interface, manages user inputs, displays data, and uses the methods from AppDB and PayrollSystem.

Access and Login
The application has two main login modes: Admin and Employee Time Clock.
1. Admin Access (Full Management)
•	Admin Code (Default): admin0107
•	Functionality: Allows access to the Admin Dashboard, which includes:
o	Employee Data management (Add, Edit, Delete)
o	Payroll Calculation and Review
o	Attendance and Absence tracking
o	Leave and Loan management
2. Employee Time Clock
•	Requirement: Requires a valid Employee ID (e.g., EMP001).
•	Functionality: Allows the specific employee to:
o	Clock IN for the day.
o	Clock OUT for the day.
o	View their personal attendance history.

HOW THE SYSTEM WORKS (Step-by-Step Explanation)
Here is the flow of the system 
1. User opens the program
The program starts the Tkinter GUI, which allows the user to access modules:
Employee Management
Attendance Module
Payroll Module
Leaves & Loans Module
2. Employee Registration
Through the GUI, the user can add:
Employee ID
Name
Position
Department
Monthly Salary
3. Attendance Recording
The user enters:
Employee ID
Date
Time In
Time Out
The system also handles:
Overnight shifts (e.g., 10PM–6AM) - GUARD
This data becomes the basis for payroll computation.
4. Payroll Computation
When generating payroll, the system reads:
Employee Information
Attendance Records
Leave Records
Loan Records
The system computes:
Earnings:
Base pay for the days worked
Overtime pays
leave pay
Deductions:
Absence deduction
Tardiness deduction
Undertime deduction
Government contributions
Loan repayment
The result is:
NET PAY = GROSS PAY – TOTAL DEDUCTIONS
5. Displaying Payroll / Pay slips
The system shows a breakdown
Daily rate
Hourly rate
Days present
Days absent
Overtime
Tardy minutes
All deductions
Gross pay
Net pay
