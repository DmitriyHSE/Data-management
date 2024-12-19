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

    -- Проверка и добавление столбца last_update к таблице "Groups"
    if not exists (
        select 1
        from information_schema.columns
        where table_name = 'Groups' and column_name = 'last_update'
    ) then
        execute $sql$
            alter table "Groups"
            add column "last_update" timestamptz default current_timestamp not null;
        $sql$;
    end if;

    -- Создание функции для обновления времени последнего изменения
    execute $sql$
        create or replace function update_time()
        returns trigger as $u$
        begin
            new.last_update = current_timestamp;
            return new;
        end;
        $u$ language plpgsql;
    $sql$;

    -- Удаление старого триггера, если он существует, и создание нового
    execute $sql$
        drop trigger if exists trigger_update on "Groups";
        create trigger trigger_update
        before update on "Groups"
        for each row execute procedure update_time();
    $sql$;

    -- Создание таблицы "Groups-Students"
    execute $sql$
        create table if not exists "Groups-Students" (
            "group_id" integer not null,
            "student_id" integer not null,
            primary key ("group_id", "student_id"),
            foreign key ("group_id") references "Groups"("group_id") on delete cascade,
            foreign key ("student_id") references "Students"("student_id") on delete cascade
        );
    $sql$;

    -- Создание таблицы "Schedule"
    execute $sql$
        create table if not exists "Schedule" (
            "lesson_id" text primary key not null,
            "teacher_id" integer not null,
            "group_id" integer not null,
            "day_of_the_week" text not null,
            "korpus" text not null,
            "number_of_auditoria" text not null,
            "type_of_lesson" text not null,
            "lesson_time" time not null,
            foreign key ("teacher_id") references "Teachers"("teacher_id") on delete cascade,
            foreign key ("group_id") references "Groups"("group_id") on delete cascade
        );
    $sql$;
end;
$$;
select "create_database"();
create function add_to_schedule(in lesson_id text, in teacher_id integer,in group_id integer,in day_of_the_week text,in korpus text,in number_of_auditoria text,in type_of_lesson text,in lesson_time text)
	returns void language sql as $$
		insert into "Schedule"(lesson_id,teacher_id,group_id,day_of_the_week,korpus,number_of_auditoria,type_of_lesson,lesson_time) values (lesson_id text,teacher_id,group_id,day_of_the_week,korpus,number_of_auditoria,type_of_lesson,lesson_time)
	$$;
create function add_to_disciplines(in discipline_id text, in title text)
	returns void language sql as $$
		insert into "Disciplines"(discipline_id, title) values (discipline_id, title)
	$$;