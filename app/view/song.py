def formatSong(s):
    return {'_id': str(s.get('_id')),
            'artist': s.get('artist'),
            'title': s.get('title'),
            'level': s.get('level'),
            'difficulty': s.get('difficulty'),
            'released': s.get('released')
            }


def append_songs(songs):
    output = []
    for s in songs:
        output.append(formatSong(s))
    return output
