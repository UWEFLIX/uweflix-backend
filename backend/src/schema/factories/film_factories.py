from src.schema.films import Hall


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
