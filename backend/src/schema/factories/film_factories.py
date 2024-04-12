from typing import List

from src.schema.films import Hall, Film, FilmImage


class FilmFactory:
    @staticmethod
    def get_hall(record):
        return Hall(
            id=record.hall_id,
            hall_name=record.hall_name,
            seats_per_row=record.seats_per_row,
            no_of_rows=record.no_of_rows,
        )

    @staticmethod
    def get_halls(records):
        return [
            FilmFactory.get_hall(x) for x in records
        ]

    @staticmethod
    def get_half_film(record):
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
    def get_image(record):
        return FilmImage(
            id=record.image_id,
            filename=record.filename
        )

    @staticmethod
    def get_full_film(records):
        film = FilmFactory.get_half_film(records["film"])
        film.images = [
            FilmImage.get_image(x) for x in records["images"]
        ]
        return film

    @staticmethod
    def get_half_films(records) -> List[Film]:
        return [
            FilmFactory.get_half_film(x) for x in records
        ]
