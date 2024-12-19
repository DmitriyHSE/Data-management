create or replace function create_database()
returns void language plpgsql as $$
begin
    -- Создание таблицы "Disciples"
    execute $sql$
        create table if not exists "Disciplines" (
            "discipline_id" text primary key not null,
            "title" text not null
        );
    $sql$;

    -- Создание таблицы "Teachers"
    execute $sql$
        create table if not exists "Teachers" (
            "teacher_id" text primary key not null,
            "name" text not null
        );
    $sql$;

    -- Создание таблицы "Students"
    execute $sql$
        create table if not exists "Students" (
            "student_id" text primary key not null,
            "name" text not null
        );
    $sql$;

    -- Создание таблицы "Groups"
    execute $sql$
        create table if not exists "Groups" (
            "group_id" text primary key not null,
            "group_name" text not null,
            "amount_of_week_lessons" integer not null
        );
    $sql$;


    -- Создание таблицы "Groups-Students"
    execute $sql$
        create table if not exists "Groups-Students" (
            "group_id" text not null,
            "student_id" text not null,
            primary key ("group_id", "student_id"),
            foreign key ("group_id") references "Groups"("group_id") on delete cascade,
            foreign key ("student_id") references "Students"("student_id") on delete cascade
        );
    $sql$;

    -- Создание таблицы "Schedule"
    execute $sql$
        create table if not exists "Schedule" (
            "lesson_id" text primary key not null,
            "teacher_id" text not null,
            "group_id" text not null,
            "day_of_the_week" text not null,
            "korpus" text not null,
            "number_of_auditoria" text not null,
            "type_of_lesson" text not null,
            "lesson_time" text not null,
            foreign key ("teacher_id") references "Teachers"("teacher_id") on delete cascade,
            foreign key ("group_id") references "Groups"("group_id") on delete cascade
        );
    $sql$;
end;
$$;
select "create_database"();
CREATE OR REPLACE FUNCTION get_schedule()
    RETURNS JSON
    LANGUAGE plpgsql
AS $$
BEGIN
    RETURN (SELECT json_agg(json_build_object(
        'lesson_id', lesson_id,
        'teacher_id', teacher_id,
        'group_id', group_id,
        'day_of_the_week', day_of_the_week,
        'korpus', korpus,
        'number_of_auditoria', number_of_auditoria,
        'type_of_lesson', type_of_lesson,
        'lesson_time', lesson_time
    )) FROM "Schedule");
END;
$$;

CREATE OR REPLACE FUNCTION add_to_schedule(
    IN lesson_id TEXT,
    IN teacher_id TEXT,
    IN group_id TEXT,
    IN day_of_the_week TEXT,
    IN korpus TEXT,
    IN number_of_auditoria TEXT,
    IN type_of_lesson TEXT,
    IN lesson_time TEXT
)
    RETURNS VOID
    LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO "Schedule" (lesson_id, teacher_id, group_id, day_of_the_week, korpus, number_of_auditoria, type_of_lesson, lesson_time)
    VALUES (lesson_id, teacher_id, group_id, day_of_the_week, korpus, number_of_auditoria, type_of_lesson, lesson_time);
END;
$$;
create function add_to_disciplines(in discipline_id text, in title text)
	returns void language sql as $$
		insert into "Disciplines"(discipline_id, title) values (discipline_id, title)
	$$;
create function clear_schedule()
    returns void language sql as $$
        truncate "schedule";
    $$;
-- Function to update the type_of_lesson by lesson_id
create function update_schedule_type_of_lesson(in new_type text, in lesson_id_ text)
    returns void language plpgsql as $$
        begin
            update "schedule" set type_of_lesson = new_type where lesson_id = lesson_id_;
        end;
    $$;
-- Function to update the type_of_lesson by lesson_id
create function update_schedule_korpus(in new_korpus text, in lesson_id_ text)
    returns void language plpgsql as $$
        begin
            update "schedule" set korpus = new_korpus where lesson_id = lesson_id_;
        end;
    $$;
-- Function to update the type_of_lesson by lesson_id
create function update_schedule_teacher_id(in new_teacher_id text, in lesson_id_ text)
    returns void language plpgsql as $$
        begin
            update "schedule" set teacher_id = new_teacher_id where lesson_id = lesson_id_;
        end;
    $$;
-- Function to update the type_of_lesson by lesson_id
create function update_schedule_group_id(in new_group_id text, in lesson_id_ text)
    returns void language plpgsql as $$
        begin
            update "schedule" set group_id = new_group_id where lesson_id = lesson_id_;
        end;
    $$;
-- Function to update the type_of_lesson by lesson_id
create function update_schedule_number_of_auditoria(in new_number_of_auditoria text, in lesson_id_ text)
    returns void language plpgsql as $$
        begin
            update "schedule" set number_of_auditoria = new_number_of_auditoria where lesson_id = lesson_id_;
        end;
    $$;
-- Function to update the type_of_lesson by lesson_id
create function update_schedule_day_of_the_week(in new_day_of_the_week text, in lesson_id_ text)
    returns void language plpgsql as $$
        begin
            update "schedule" set day_of_the_week = new_day_of_the_week where lesson_id = lesson_id_;
        end;
    $$;
create function update_schedule_lesson_id(in new_lesson_id text, in lesson_id_ text)
    returns void language plpgsql as $$
        begin
            update "schedule" set lesson_id = new_lesson_id where lesson_id = lesson_id_;
        end;
    $$;
create function update_schedule_lesson_time(in new_lesson_time text, in lesson_id_ text)
    returns void language plpgsql as $$
        begin
            update "schedule" set lesson_time = new_lesson_time where lesson_id = lesson_id_;
        end;
    $$;
