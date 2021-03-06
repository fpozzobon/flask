def createSong(id):
    return {'_id': id,
            'artist': "artist%s" % id,
            'title': "title%s" % id,
            'level': "level%s" % id,
            'difficulty': "difficulty%s" % id,
            'released': "released%s" % id
            }


def createNSongs(n):
    result = []
    for i in range(n):
        result.append(createSong(str(i)))
    return result


def insertNSongsInDb(n, mockedSongCollection):
    expectedResult = createNSongs(n)
    mockedSongCollection.insert_many(expectedResult)
    return expectedResult
