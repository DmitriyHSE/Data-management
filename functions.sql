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

