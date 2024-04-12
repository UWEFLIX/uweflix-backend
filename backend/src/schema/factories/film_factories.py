from typing import List

from src.schema.films import Hall, Film, FilmImage, Schedule, ScheduleDetailed


class FilmFactory:
    @staticmethod
    def get_hall(record) -> Hall:
        return Hall(
            id=record.hall_id,
            hall_name=record.hall_name,
            seats_per_row=record.seats_per_row,
            no_of_rows=record.no_of_rows,
        )

    @staticmethod
    def get_halls(records) -> List[Hall]:
        return [
            FilmFactory.get_hall(x) for x in records
        ]

    @staticmethod
    def get_half_film(record) -> Film:
        return Film(
            id=record.film_id,
            title=record.title,
            age_rating=record.age_rating,
            duration_sec=record.duration_sec,
            trailer_desc=record.trailer_desc,
            on_air_from=record.on_air_from,
            on_air_to=record.on_air_to,
            is_active=record.is_active,
        )

    @staticmethod
    def get_image(record) -> FilmImage:
        return FilmImage(
            id=record.image_id,
            filename=f"{record.filename}.jpg"
        )

    @staticmethod
    def get_full_film(records) -> Film:
        film = FilmFactory.get_half_film(records["film"])
        film.images = FilmFactory.get_images(records["images"])
        return film

    @staticmethod
    def get_half_films(records) -> List[Film]:
        return [
            FilmFactory.get_half_film(x) for x in records
        ]

    @staticmethod
    def get_images(records) -> List[FilmImage]:
        return [
            FilmFactory.get_image(x) for x in records
        ]

    @staticmethod
    def get_schedule(record, class_=Schedule) -> Schedule | ScheduleDetailed:
        return class_(
            id=record.schedule_id,
            hall_id=record.hall_id,
            film_id=record.film_id,
            show_time=record.show_time,
            on_schedule=record.on_schedule,
            ticket_price=record.ticket_price,
        )

    @staticmethod
    def get_schedules(records) -> List[Schedule]:
        return [
            FilmFactory.get_schedule(x) for x in records
        ]

    @staticmethod
    def get_film_schedules(records) -> Film:
        film = FilmFactory.get_half_film(records["film"])
        film.schedules = FilmFactory.get_schedules(
            records["schedules"]
        )
        return film

    @staticmethod
    def get_detailed_schedule(records) -> ScheduleDetailed:
        schedule = FilmFactory.get_schedule(records[0], class_=ScheduleDetailed)
        schedule.film = FilmFactory.get_half_film(records[1])
        schedule.hall = FilmFactory.get_hall(records[2])
        return schedule

    @staticmethod
    def get_detailed_schedules(records) -> List[ScheduleDetailed]:
        return [
            FilmFactory.get_detailed_schedule(x) for x in records
        ]
