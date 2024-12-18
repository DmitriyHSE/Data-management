-- Function to insert a record into the schedule table
CREATE OR REPLACE FUNCTION add_schedule_entry(
    lesson_id TEXT,
    teacher_id TEXT,
    group_id TEXT,
    day_of_the_week TEXT,
    korpus_or_online TEXT,
    number_of_auditoria TEXT,
    type_of_lesson TEXT,
    time TEXT
)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO schedule (
        lesson_id, teacher_id, group_id, day_of_the_week, korpus_or_online,
        number_of_auditoria, type_of_lesson, time
    )
    VALUES (
        lesson_id, teacher_id, group_id, day_of_the_week, korpus_or_online,
        number_of_auditoria, type_of_lesson, time
    );
END;
$$;

-- Function to delete a record from the schedule table by lesson_id
CREATE OR REPLACE FUNCTION delete_schedule_entry(lesson_id TEXT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM schedule WHERE lesson_id = lesson_id;
END;
$$;

-- Function to retrieve all records from the schedule table
CREATE OR REPLACE FUNCTION get_all_schedule_entries()
RETURNS TABLE (
    lesson_id TEXT,
    teacher_id TEXT,
    group_id TEXT,
    day_of_the_week TEXT,
    korpus_or_online TEXT,
    number_of_auditoria TEXT,
    type_of_lesson TEXT,
    time TEXT
)
LANGUAGE sql AS $$
    SELECT * FROM schedule;
$$;
