from database import Database

# Initialize the database
db = Database(name="schedule_db", user="user", password="password", host="localhost", port="5432")

# Example usage
db.add_schedule_entry(
    lesson_id="MATH101",
    teacher_id="T123",
    group_id="G456",
    day_of_the_week="Monday",
    korpus_or_online="online",
    number_of_auditoria="101",
    type_of_lesson="lecture",
    time="09:00 AM",
)

entries = db.get_all_schedule_entries()
print("All Schedule Entries:", entries)

teacher_schedule = db.find_schedule_by_teacher("T123")
print("Schedule for Teacher T123:", teacher_schedule)

monday_schedule = db.find_schedule_by_day("Monday")
print("Schedule for Monday:", monday_schedule)

db.update_schedule_type_of_lesson("seminar", "MATH101")
db.delete_schedule_entry("MATH101")
db.clear_schedule()
