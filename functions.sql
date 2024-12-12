create function create_database()
returns void language sql as $$
    -- Создание таблицы "Disciples"
    create table if not exists "Disciples" (
        "disciple_id" serial primary key not null,
        "title" text not null
    );

    -- Создание таблицы "Teachers"
    create table if not exists "Teachers" (
        "teacher_id" serial primary key not null,
        "name" text not null
    );

    -- Создание таблицы "Students"
    create table if not exists "Students" (
        "student_id" serial primary key not null,
        "name" text not null
    );

    -- Создание таблицы "Groups-Students"
    create table if not exists "Groups-Students" (
        "group_id" integer not null,
        "student_id" integer not null,
        primary key ("group_id", "student_id"),
        foreign key ("group_id") references "Groups"("group_id") on delete cascade,
        foreign key ("student_id") references "Students"("student_id") on delete cascade
    );

    -- Создание таблицы "Groups"
    create table if not exists "Groups" (
        "group_id" serial primary key not null,
        "group_name" text not null,
        "amount_of_week_lessons" integer not null
    );

    -- Создание таблицы "Schedule"
    create table if not exists "Schedule" (
        "lesson_id" serial primary key not null,
        "teacher_id" integer not null,
        "group_id" integer not null,
        "day_of_the_week" text not null,
        "korpus/online" text not null,
        "number_of_auditoria" text not null,
        "type_of_lesson" text not null,
        "time" time not null,
        foreign key ("teacher_id") references "Teachers"("teacher_id") on delete cascade,
        foreign key ("group_id") references "Groups"("group_id") on delete cascade
    );

    -- Создание функции для обновления времени последнего изменения
    create or replace function update_time()
        returns trigger as $u$
        begin
            new.last_update = current_timestamp;
            return new;
        end;
    $u$ language plpgsql;

    -- Добавление столбца last_update и триггера для "Groups"
    alter table if not exists "Groups"
    add column if not exists "last_update" timestamptz default current_timestamp not null;

    drop trigger if exists trigger_update on "Groups";

    create trigger trigger_update before update on "Groups"
        for each row execute procedure update_time();
$$;

