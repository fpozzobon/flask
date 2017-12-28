def createSong(id):
  return {
          '_id': id,
          'artist': "artist%s"%id,
          'title': "title%s"%id,
          'level': "level%s"%id,
          'difficulty': "difficulty%s"%id,
          'released': "released%s"%id,
          'ratings': []
        }

def createNSongs(n):
  result = []
  for i in range(n):
    result.append(createSong(str(i)))
  return result

def insertNSongsInDb(n, mockedSongCollection):
  expectedResult = createNSongs(n)
  for song in expectedResult:
    mockedSongCollection.insert(song)
  return expectedResult
