SELECT EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = 'main'
      AND table_name = ?
)