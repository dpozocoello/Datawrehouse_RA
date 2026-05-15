CREATE OR REPLACE FUNCTION dw.test_func()
RETURNS INTEGER AS $$
DECLARE 
    v_id INTEGER;
BEGIN
    INSERT INTO dw.etl_process_log (process_name, status)
    VALUES ('test', 'success')
    RETURNING id INTO v_id;
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;
