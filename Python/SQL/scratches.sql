-- ALTER TABLE stays
-- ALTER COLUMN start TYPE integer;

-- ALTER TABLE stays
-- ALTER COLUMN "end" TYPE integer;



-- SELECT
-- 	ordinal_position,
-- 	column_name,
-- 	data_type,
-- 	is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'stays'
--   AND table_schema = 'main'
-- ORDER BY ordinal_position;


-- SELECT *
-- FROM stays
-- LIMIT 20;

-- We verified that start and end are integers.
-- SELECT *
-- FROM stays
-- WHERE start != TRUNC(start)
--    OR "end" != TRUNC("end");


-- SELECT COUNT(*)
-- FROM patients
-- WHERE patient_id IS NULL;


-- SELECT
-- 	stay_id,
-- 	COUNT(*) AS n
-- FROM patients
-- GROUP BY stay_id
-- HAVING COUNT(*) > 1;