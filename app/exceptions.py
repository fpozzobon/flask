class ResourceNotFoundException(Exception):
    pass


class SongNotFoundException(ResourceNotFoundException):
    def __init__(self, song_id):
        self.message = "no song found for the id %s" % song_id
        super().__init__(self.message)


class BadRequestException(Exception):
    pass
