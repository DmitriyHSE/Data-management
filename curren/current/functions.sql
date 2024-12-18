-- Function to create the schedule table and associated triggers
create function create_schedule_table() 
    returns void language sql as $$
        create table if not exists "schedule" (
            lesson_id text primary key not null,
            teacher_id text not null,
            group_id text not null,
            day_of_the_week text not null,
            korpus_or_online text not null,
            number_of_auditoria text not null,
            type_of_lesson text not null,
            time text not null,
            foreign key (teacher_id) references "Teachers"(teacher_id) on delete cascade,
            foreign key (group_id) references "Groups"(group_id) on delete cascade
        );

        create or replace function update_last_time()
            returns trigger as $update$
            begin
                new.time = current_timestamp;
                return new;
            end;
        $update$ language plpgsql;

        drop trigger if exists trigger_update_time on "schedule";

        create trigger trigger_update_time before update on "schedule"
            for row execute procedure update_last_time();
$$;

select create_schedule_table();

-- Function to retrieve all schedule entries as JSON
create function get_schedule_entries()
    returns json language plpgsql as $$
        begin
            return (select json_agg(json_build_object(
                'lesson_id', lesson_id,
                'teacher_id', teacher_id,
                'group_id', group_id,
                'day_of_the_week', day_of_the_week,
                'korpus_or_online', korpus_or_online,
                'number_of_auditoria', number_of_auditoria,
                'type_of_lesson', type_of_lesson,
                'time', time
            )) from "schedule");
        end
    $$;

-- Function to add an entry to the schedule
create function add_to_schedule(
    in lesson_id text,
    in teacher_id text,
    in group_id text,
    in day_of_the_week text,
    in korpus_or_online text,
    in number_of_auditoria text,
    in type_of_lesson text,
    in time text
)
    returns void language sql as $$
        insert into "schedule" (
            lesson_id, teacher_id, group_id, day_of_the_week, korpus_or_online,
            number_of_auditoria, type_of_lesson, time
        ) values (
            lesson_id, teacher_id, group_id, day_of_the_week, korpus_or_online,
            number_of_auditoria, type_of_lesson, time
        );
    $$;

-- Function to clear all entries in the schedule
create function clear_schedule()
    returns void language sql as $$
        truncate "schedule";
    $$;

-- Function to delete a schedule entry by lesson_id
create function delete_schedule_entry_by_id(in lesson_id text)
    returns void language plpgsql as $$
        begin
            delete from "schedule" where lesson_id = lesson_id;
        end;
    $$;

-- Function to update the type_of_lesson by lesson_id
create function update_schedule_type_of_lesson(in new_type text, in lesson_id text)
    returns void language plpgsql as $$
        begin
            update "schedule" set type_of_lesson = new_type where lesson_id = lesson_id;
        end;
    $$;

-- Function to find schedule entries by teacher_id
create function find_schedule_by_teacher(in teacher_id text)
    returns json language plpgsql as $$
        begin
            return (select json_agg(json_build_object(
                'lesson_id', lesson_id,
                'teacher_id', teacher_id,
                'group_id', group_id,
                'day_of_the_week', day_of_the_week,
                'korpus_or_online', korpus_or_online,
                'number_of_auditoria', number_of_auditoria,
                'type_of_lesson', type_of_lesson,
                'time', time
            )) from "schedule" where teacher_id = teacher_id);
        end;
    $$;

-- Function to find schedule entries by day_of_the_week
create function find_schedule_by_day(in day_of_the_week text)
    returns json language plpgsql as $$
        begin
            return (select json_agg(json_build_object(
                'lesson_id', lesson_id,
                'teacher_id', teacher_id,
                'group_id', group_id,
                'day_of_the_week', day_of_the_week,
                'korpus_or_online', korpus_or_online,
                'number_of_auditoria', number_of_auditoria,
                'type_of_lesson', type_of_lesson,
                'time', time
            )) from "schedule" where day_of_the_week = day_of_the_week);
        end;
    $$;
