from src.crud.models import (
    BookingsRecord, AccountsRecord, ClubMembersRecords, ClubsRecord,
    UsersRecord, HallsRecord, SchedulesRecord, PersonTypesRecord
)

select_batch_data: str = f"""
SELECT 
    `batch_ref`, 
    MIN(`created`) AS created,
    COUNT(*) AS occurrences,
    SUM(`amount`) AS total_amount
FROM 
    {BookingsRecord.__tablename__}
GROUP BY 
    `batch_ref`;
"""

user_pre_booking_details: str = f"""
SELECT *
FROM `{AccountsRecord.__tablename__}`

LEFT JOIN `{PersonTypesRecord.__tablename__}` ON 
`{PersonTypesRecord.__tablename__}`.`person_type_id` >= 1

LEFT JOIN `{SchedulesRecord.__tablename__}` ON 
`{SchedulesRecord.__tablename__}`.`schedule_id` = %s

LEFT JOIN `{HallsRecord.__tablename__}` ON 
`{HallsRecord.__tablename__}`.`hall_id` = 
`{SchedulesRecord.__tablename__}`.`hall_id`

WHERE `{AccountsRecord.__tablename__}`.`entity_id` = %s 
AND `{AccountsRecord.__tablename__}`.`entity_type` = 'USER'
"""


club_pre_booking_details: str = f"""
SELECT *
FROM `{AccountsRecord.__tablename__}`

LEFT JOIN `{PersonTypesRecord.__tablename__}` ON 
`{PersonTypesRecord.__tablename__}`.`person_type_id` >= 1

LEFT JOIN `{SchedulesRecord.__tablename__}` ON 
`{SchedulesRecord.__tablename__}`.`schedule_id` = %s

LEFT JOIN `{HallsRecord.__tablename__}` ON 
`{HallsRecord.__tablename__}`.`hall_id` = 
`{SchedulesRecord.__tablename__}`.`hall_id`

LEFT JOIN `{ClubMembersRecords.__tablename__}` ON 
`{ClubMembersRecords.__tablename__}`.`club` = 
`{AccountsRecord.__tablename__}`.`entity_id`

LEFT JOIN `{UsersRecord.__tablename__}` ON 
`{ClubMembersRecords.__tablename__}`.`member` = 
`{UsersRecord.__tablename__}`.`user_id`

WHERE `{AccountsRecord.__tablename__}`.`entity_id` = %s 
AND `{AccountsRecord.__tablename__}`.`entity_type` = 'CLUB'
"""
