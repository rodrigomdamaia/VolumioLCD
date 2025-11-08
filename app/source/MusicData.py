class Musicdata:

    status: str
    position: int
    artist: str
    title: str
    album: str
    albumArt: str
    trackType: str
    trackArt: str
    codec: str
    seek: int
    elapsed: float
    duration: int
    length: int
    samplerate: str
    bitdepth: str
    channels: int
    random: bool
    repeat: bool
    repeatSingle: bool
    stream: str

    def __init__(self):
        self.status = u'stop'
        self.position = 0
        self.artist = u''
        self.title = u''
        self.album = u''
        self.albumArt = u''
        self.trackType = u''
        self.trackArt = u''
        self.codec = u''
        self.seek = 0
        self.duration = -1
        self.length = -1
        self.remaining = u''
        self.elapsed_formatted = u''
        self.samplerate = u''
        self.bitdepth = u''
        self.channels = 1
        self.random = False
        self.repeat = False
        self.repeatSingle = False
        self.stream = u''
