from src.crud.models import BookingsRecord


def generate_unique_string():
    return f"""
CREATE FUNCTION generate_unique_string() RETURNS VARCHAR(6)
BEGIN
    DECLARE alphabet VARCHAR(26) DEFAULT 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    DECLARE length INT DEFAULT 6;
    DECLARE result VARCHAR(6) DEFAULT '';
    DECLARE i INT DEFAULT 1;
    DECLARE rows_count INT;

    WHILE true DO
        SET result = '';
        SET i = 1;
        WHILE i <= length DO
            SET result = CONCAT(result, SUBSTRING(alphabet, ((UUID_SHORT() >> (i * 4)) % 26) + 1, 1));
            SET i = i + 1;
        END WHILE;

        SELECT COUNT(*) INTO rows_count FROM `{BookingsRecord.__tablename__}` 
            WHERE `{BookingsRecord.__tablename__}`.`serial_no` = result;

        IF rows_count = 0 THEN
            RETURN result;
        END IF;
    END WHILE;
END;

"""
