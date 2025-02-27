import csv
from datetime import datetime, timedelta
import random

# Constants
HOURS_PER_DAY = {
    "Sunday": 80, "Monday": 54, "Tuesday": 54, "Wednesday": 60,
    "Thursday": 68, "Friday": 80, "Saturday": 80
}
OPENING_HOUR = 9
CLOSING_HOUR = 25  # 1am of the next day
HIGH_SCHOOL_END_TIME = 22  # 10pm for high school students
MAX_WORK_DAYS = 5

# Manager/Shift Lead requirements
MANAGER_POSITIONS = ['Manager', 'Assistant Manager', 'Shiftlead']
MANAGER_SHIFTS = [(9, 17), (17, 25)]  # 9am-5pm and 5pm-1am
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Function to format shift time
def format_time(hour):
    if hour >= 24:
        hour -= 24
    suffix = "am" if hour < 12 or hour == 24 else "pm"
    if hour == 0:  # Handle midnight correctly
        hour = 12
    elif hour > 12:
        hour -= 12
    return f"{hour}:00{suffix}"

# Function to create a schedule
def create_schedule(input_file, output_file):
    with open(input_file, 'r') as file:
        reader = csv.DictReader(file)
        employees = [row for row in reader]

    for employee in employees:
        employee['Rating'] = float(employee['Rating'])
        employee['Highschool'] = employee['Highschool'].strip().upper() == 'Y'
        employee['Scheduled Days'] = 0

    schedule = {}

    for employee in employees:
        schedule[f"{employee['Last Name']},{employee['First Name']}"] = {
            "Sunday": "",
            "Monday": "",
            "Tuesday": "",
            "Wednesday": "",
            "Thursday": "",
            "Friday": "",
            "Saturday": ""
        }

    for day, max_hours in HOURS_PER_DAY.items():
        remaining_hours = max_hours

        for shift_start, shift_end in MANAGER_SHIFTS:
            manager_candidates = [e for e in employees if e['Position'] in MANAGER_POSITIONS and e[day] != 'Unavailible' and e['Scheduled Days'] < MAX_WORK_DAYS]
            if manager_candidates:
                manager = manager_candidates[0]
                schedule[f"{manager['Last Name']},{manager['First Name']}"][day] = f"{format_time(shift_start)}-{format_time(shift_end)}"
                manager['Scheduled Days'] += 1
                remaining_hours -= (shift_end - shift_start)

        for current_hour in range(OPENING_HOUR, CLOSING_HOUR):
            shift_candidates = [e for e in employees if e[day] != 'Unavailible' and e['Scheduled Days'] < MAX_WORK_DAYS]

            for emp in shift_candidates:
                shift_start = current_hour
                shift_end = min(shift_start + 4, CLOSING_HOUR)

                # Apply availability restrictions
                availability = emp['Availability'].lower()
                if availability == 'day' and shift_end > 17:
                    continue
                if availability == 'night' and shift_start < 17:
                    continue
                if availability == 'mid day' and (shift_start < 12 or shift_end > 17):
                    continue

                # High school students restrictions
                if emp['Highschool']:
                    if shift_end > HIGH_SCHOOL_END_TIME:
                        shift_end = min(shift_end, HIGH_SCHOOL_END_TIME)
                    if day in WEEKDAYS and shift_start < 17:
                        continue

                if shift_start >= shift_end:
                    continue

                schedule[f"{emp['Last Name']},{emp['First Name']}"].update({
                    day: f"{format_time(shift_start)}-{format_time(shift_end)}"
                })
                emp['Scheduled Days'] += 1

                remaining_hours -= (shift_end - shift_start)

                if remaining_hours <= 0:
                    break

            if remaining_hours <= 0:
                break

    with open(output_file, 'w', newline='') as file:
        fieldnames = ["Last Name", "First Name", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for key, value in schedule.items():
            last_name, first_name = key.split(",")
            row = {
                "Last Name": last_name,
                "First Name": first_name,
                **value
            }
            writer.writerow(row)

# Example usage
create_schedule('Wingstop Uniforms - Portland Schedule (1).csv', 'schedule2.csv')
