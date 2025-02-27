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
BUSY_PERIODS = [(16, 21)]  # 4pm-9pm (busy)
MODERATE_PERIODS = [(11, 14)]  # 11am-2pm (moderately busy)
OPENING_SHIFT = 3
CLOSING_SHIFT = 3
HIGH_SCHOOL_END_TIME = 22  # 10pm for high school students

# Function to create a schedule
def create_schedule(input_file, output_file):
    with open(input_file, 'r') as file:
        reader = csv.DictReader(file)
        employees = [row for row in reader]

    # Convert employee data to usable formats
    for employee in employees:
        employee['Rating'] = float(employee['Rating'])
        employee['Highschool'] = employee['Highschool'].strip().upper() == 'Y'

    schedule = []

    for day, max_hours in HOURS_PER_DAY.items():
        remaining_hours = max_hours
        day_schedule = []

        for current_hour in range(OPENING_HOUR, CLOSING_HOUR):
            shift_candidates = [e for e in employees if e[day] != 'Unavailible']

            # Ensure a manager, assistant manager, or shift lead is scheduled
            manager_candidates = [e for e in shift_candidates if e['Position'] in ['Manager', 'Assistant Manager', 'Shiftlead']]
            if not any(s['Start'] <= current_hour < s['End'] and s['Position'] in ['Manager', 'Assistant Manager', 'Shiftlead'] for s in day_schedule):
                if manager_candidates:
                    emp = max(manager_candidates, key=lambda x: x['Rating'])
                    shift_start = current_hour
                    shift_end = min(shift_start + 4, CLOSING_HOUR)
                    day_schedule.append({
                        "Day": day,
                        "First_Name": emp['First Name'],
                        "Last_Name": emp['Last Name'],
                        "Position": emp['Position'],
                        "Start": shift_start,
                        "End": shift_end
                    })
                    remaining_hours -= (shift_end - shift_start)
                    continue

            for emp in shift_candidates:
                shift_start = current_hour
                shift_end = min(shift_start + 4, CLOSING_HOUR)

                # Determine shift length based on availability
                if emp['Availability'] == 'day':
                    shift_end = min(17, shift_end)
                elif emp['Availability'] == 'mid day':
                    shift_start = max(12, shift_start)
                    shift_end = min(17, shift_end)
                elif emp['Availability'] == 'night':
                    shift_start = max(17, shift_start)
                elif emp['Highschool'] and shift_end > HIGH_SCHOOL_END_TIME:
                    shift_end = HIGH_SCHOOL_END_TIME

                if shift_start >= shift_end:
                    continue

                day_schedule.append({
                    "Day": day,
                    "First_Name": emp['First Name'],
                    "Last_Name": emp['Last Name'],
                    "Position": emp['Position'],
                    "Start": shift_start,
                    "End": shift_end
                })

                remaining_hours -= (shift_end - shift_start)

                if remaining_hours <= 0:
                    break

            if remaining_hours <= 0:
                break

        schedule.extend(day_schedule)

    # Write schedule to output CSV
    with open(output_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Day", "First_Name", "Last_Name", "Position", "Start", "End"])
        writer.writeheader()
        writer.writerows(schedule)

# Example usage
create_schedule('Wingstop Uniforms - Portland Schedule (1).csv', 'schedule.csv')
