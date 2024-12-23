-- Функция для получения списка баз данных
CREATE OR REPLACE FUNCTION get_databases()
RETURNS TABLE(datname TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT pg_database.datname::text
    FROM pg_database
    WHERE pg_database.datistemplate = false;
END;
$$;
-- Функция для получения списка таблиц в public схеме
CREATE OR REPLACE FUNCTION get_public_tables()
RETURNS TABLE(table_name TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT information_schema.tables.table_name::TEXT
    FROM information_schema.tables
    WHERE information_schema.tables.table_schema = 'public' AND information_schema.tables.table_type = 'BASE TABLE';
END;
$$;
-- Функция для очистки таблицы с каскадным удалением зависимостей
CREATE OR REPLACE FUNCTION truncate_table(
    table_name TEXT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format('TRUNCATE TABLE %I CASCADE;', table_name);
END;
$$;
-- Функция для получения всех имен столбцов таблицы
CREATE OR REPLACE FUNCTION public.get_column_names(
    p_table_name TEXT
)
RETURNS TABLE(col_name TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT c.column_name::TEXT
    FROM information_schema.columns AS c
    WHERE c.table_name = p_table_name;
END;
$$;

-- Функция для получения типа данных и возможности NULL для заданного столбца
CREATE OR REPLACE FUNCTION public.get_column_info(
    table_name_param TEXT,
    col_name_param TEXT
)
RETURNS TABLE (data_type TEXT, is_nullable TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT c.data_type::TEXT, c.is_nullable::TEXT
    FROM information_schema.columns AS c
    WHERE c.table_name = table_name_param
      AND c.column_name = col_name_param;
END;
$$;

-- Функция для проверки, является ли столбец первичным ключом
CREATE OR REPLACE FUNCTION public.check_primary_key(
    table_name_param TEXT,
    column_name_param TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    count_result INTEGER;
BEGIN
    SELECT COUNT(*) INTO count_result
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
        AND tc.table_name = kcu.table_name
    WHERE tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_name = table_name_param
        AND kcu.column_name = column_name_param;

    RETURN count_result > 0;
END;
$$;
CREATE OR REPLACE FUNCTION public.get_table_columns(
    table_name_param TEXT
)
RETURNS TEXT[]
LANGUAGE plpgsql
AS $$
DECLARE
    column_names TEXT[];
BEGIN
    SELECT array_agg(column_name) INTO column_names
    FROM information_schema.columns
    WHERE table_name = table_name_param;

    RETURN column_names;
END;
$$;
-- Функция для обновления данных в таблице
CREATE OR REPLACE FUNCTION public.update_table_record(
    table_name_param TEXT,
    primary_keys_param TEXT[],
    primary_values_param TEXT[],
    update_column_param TEXT,
    new_value_param TEXT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    where_clause TEXT;
    update_query TEXT;
BEGIN
    -- 1. Проверка количества первичных ключей и значений
    IF array_length(primary_keys_param, 1) <> array_length(primary_values_param, 1) THEN
        RAISE EXCEPTION 'Количество первичных ключей и значений не совпадает.';
    END IF;

    -- 2. Формирование условия WHERE
    where_clause := array_to_string(
      ARRAY(
        SELECT format('%I = %L', key, val)
        FROM unnest(primary_keys_param, primary_values_param) AS t(key, val)
      ),
      ' AND '
    );

    -- 3. Формирование запроса UPDATE
   update_query := format('UPDATE %I SET %I = %L WHERE %s',
                           table_name_param,
                           update_column_param,
                           new_value_param,
                           where_clause
                          );

    -- 4. Выполнение запроса UPDATE
    EXECUTE update_query;

END;
$$;
-- Функция для удаления данных из таблицы
CREATE OR REPLACE FUNCTION public.delete_table_record(
    table_name_param TEXT,
    primary_keys_param TEXT[],
    primary_values_param TEXT[]
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    where_clause TEXT;
    delete_query TEXT;
BEGIN
    -- 1. Проверка количества первичных ключей и значений
    IF array_length(primary_keys_param, 1) <> array_length(primary_values_param, 1) THEN
        RAISE EXCEPTION 'Количество первичных ключей и значений не совпадает.';
    END IF;

    -- 2. Формирование условия WHERE
    where_clause := array_to_string(
      ARRAY(
        SELECT format('%I = %L', key, val)
        FROM unnest(primary_keys_param, primary_values_param) AS t(key, val)
      ),
      ' AND '
    );

    -- 3. Формирование запроса DELETE
    delete_query := format('DELETE FROM %I WHERE %s',
                           table_name_param,
                           where_clause
                          );

    -- 4. Выполнение запроса DELETE
    EXECUTE delete_query;

END;
$$;
--  Получение команды для удаления базы данных
CREATE OR REPLACE FUNCTION drop_database_command(p_db_name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN format('DROP DATABASE %I', p_db_name);
END;
$$ LANGUAGE plpgsql;
-- Функция для вставки данных в таблицу (без VARIADIC)
CREATE OR REPLACE FUNCTION public.insert_table_data_no_variadic(
    table_name_param TEXT,
    data_param JSONB
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    columns_arr TEXT[];
    values_arr TEXT[];
    placeholders TEXT;
    query TEXT;
BEGIN
    SELECT array_agg(key), array_agg(value::TEXT)
    INTO columns_arr, values_arr
    FROM jsonb_each_text(data_param);

    IF array_length(columns_arr, 1) IS NULL THEN
      RAISE EXCEPTION 'Не предоставлены данные для вставки.';
    END IF;

    placeholders := array_to_string(array_fill('%s'::text, ARRAY[array_length(values_arr, 1)]), ', ');

    query := format('INSERT INTO %I (%s) VALUES (%s);',
        table_name_param,
        array_to_string(columns_arr, ', '),
        placeholders
    );

    EXECUTE query USING (values_arr[1], values_arr[2], values_arr[3], values_arr[4], values_arr[5],
                        values_arr[6], values_arr[7], values_arr[8], values_arr[9], values_arr[10],
                        values_arr[11], values_arr[12], values_arr[13], values_arr[14], values_arr[15],
                        values_arr[16], values_arr[17], values_arr[18], values_arr[19], values_arr[20]);
END;
$$;
-- Функция для получения списка ключевых столбцов таблицы
CREATE OR REPLACE FUNCTION public.get_primary_key_columns(
    table_name_param TEXT
)
RETURNS TEXT[]
LANGUAGE plpgsql
AS $$
DECLARE
    key_columns TEXT[];
BEGIN
    SELECT array_agg(kcu.column_name)
    INTO key_columns
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
    AND tc.table_name = kcu.table_name
    WHERE tc.constraint_type = 'PRIMARY KEY'
    AND tc.table_name = table_name_param;

    RETURN key_columns;
END;
$$;
-- Функция для обновления lessons_per_week в таблице groups
CREATE OR REPLACE FUNCTION public.update_lessons_per_week()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE groups
    SET lessons_per_week = (
        SELECT COUNT(*)
        FROM schedule
        WHERE schedule.group_id = groups.group_id
    );
END;
$$;
-- Функция для получения списка имен всех таблиц из схемы public
CREATE OR REPLACE FUNCTION public.get_all_table_names()
RETURNS TEXT[]
LANGUAGE plpgsql
AS $$
DECLARE
    table_names TEXT[];
BEGIN
    SELECT array_agg(table_name)
    INTO table_names
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE';

    RETURN table_names;
END;
$$;
-- Функция для поиска данных в таблице по столбцу и шаблону
CREATE OR REPLACE FUNCTION public.search_table_data(
    table_name_param TEXT,
    column_name_param TEXT,
    search_pattern_param TEXT
)
RETURNS TABLE(rec record)
LANGUAGE plpgsql
AS $$
DECLARE
    query TEXT;
BEGIN
    query := format('SELECT * FROM %I WHERE %I LIKE %L',
        table_name_param,
        column_name_param,
        '%' || search_pattern_param || '%'
    );

    RETURN QUERY EXECUTE query;
END;
$$;
-- Функция для получения списка имен всех таблиц из схемы public
CREATE OR REPLACE FUNCTION public.get_table_names()
RETURNS TABLE (table_name TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT table_name
  FROM information_schema.tables
  WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE';
END;
$$;
-- Функция для удаления данных из таблицы по столбцу и шаблону
CREATE OR REPLACE FUNCTION public.delete_table_data(
    table_name_param TEXT,
    column_name_param TEXT,
    search_pattern_param TEXT
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    query TEXT;
    rows_deleted INTEGER;
BEGIN
    query := format('DELETE FROM %I WHERE %I LIKE %L',
        table_name_param,
        column_name_param,
        '%' || search_pattern_param || '%'
    );

    GET DIAGNOSTICS rows_deleted = ROW_COUNT;
    EXECUTE query;
    GET DIAGNOSTICS rows_deleted = ROW_COUNT;

    RETURN rows_deleted;
END;
$$;
--  Получение команды для создания базы данных
CREATE OR REPLACE FUNCTION create_database_command(p_db_name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN format('CREATE DATABASE %I', p_db_name);
END;
$$ LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION set_lessons_per_week() RETURNS TRIGGER AS $$
        BEGIN
            UPDATE Groups SET "lessons_per_week" = (
                SELECT COUNT(*)
                FROM Schedule
                WHERE group_id = NEW.group_id
            )
        WHERE group_id = NEW.group_id;
        RETURN NEW;
        END;
    $$ LANGUAGE plpgsql;

   CREATE OR REPLACE PROCEDURE create_schedule_trigger()
LANGUAGE plpgsql
AS $$
BEGIN
   CREATE OR REPLACE TRIGGER schedule_changes
        AFTER INSERT OR UPDATE OR DELETE ON Schedule
        FOR EACH ROW
        EXECUTE PROCEDURE set_lessons_per_week();
END;
$$;
CREATE OR REPLACE PROCEDURE create_group_students_table()
LANGUAGE plpgsql
AS $$
BEGIN
     CREATE TABLE IF NOT EXISTS Group_Students (
        Group_id TEXT REFERENCES Groups(Group_id),
        Student_id TEXT REFERENCES Students(Student_id),
        PRIMARY KEY(Group_id, Student_id)
    );
END;
$$;

-- Создание таблицы Schedule
CREATE OR REPLACE PROCEDURE create_schedule_table()
LANGUAGE plpgsql
AS $$
BEGIN
    CREATE TABLE IF NOT EXISTS Schedule (
        Lesson_id TEXT PRIMARY KEY,
        Teacher_id TEXT REFERENCES Teachers(Teacher_id),
        Group_id TEXT REFERENCES Groups(Group_id),
        DayOfWeek TEXT,
        Building_online TEXT,
        RoomNumber TEXT,
        LessonType TEXT,
        LessonTime TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_schedule_group_id ON Schedule(Group_id);
END;
$$;
-- Создание таблицы Teachers
CREATE OR REPLACE PROCEDURE create_teachers_table()
LANGUAGE plpgsql
AS $$
BEGIN
    CREATE TABLE IF NOT EXISTS Teachers (
        Teacher_id TEXT PRIMARY KEY,
        FIO TEXT
    );
END;
$$;

-- Создание таблицы Groups
CREATE OR REPLACE PROCEDURE create_groups_table()
LANGUAGE plpgsql
AS $$
BEGIN
    CREATE TABLE IF NOT EXISTS Groups (
        Group_id TEXT PRIMARY KEY,
        GroupName TEXT,
        Lessons_per_week INT DEFAULT 0
    );
END;
$$;

-- Создание таблицы Students
CREATE OR REPLACE PROCEDURE create_students_table()
LANGUAGE plpgsql
AS $$
BEGIN
    CREATE TABLE IF NOT EXISTS Students (
        Student_id TEXT PRIMARY KEY,
        FIO TEXT
    );
END;
$$;
-- Создание таблицы Disciplines
CREATE OR REPLACE PROCEDURE create_disciplines_table()
LANGUAGE plpgsql
AS $$
BEGIN
    CREATE TABLE IF NOT EXISTS Disciplines (
        Disciple_id TEXT PRIMARY KEY,
        Name TEXT
    );
END;
$$;
