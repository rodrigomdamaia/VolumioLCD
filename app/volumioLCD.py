import time
import threading
from Adafruit_CharLCD import Adafruit_CharLCD
from .source import MusicData as md
from socketIO_client import SocketIO
import socketio

class socketVolumio:
    def __init__(self):
        self.sio = socketio.Client()
        for i in range(10) :
            try:
                self.sio.connect(f"http://localhost:3000")
                break
            except socketio.exceptions.ConnectionError:
                time.sleep(1)
                print("Error connecting to socket")

        self.musicdata = md.MusicData()
        #self.musicdata = Musicdata.musicdata_init.copy()

        self._running = False
        self._thread = threading.Thread(target=self.InitServer)
        self._thread.daemon = True

    def InitServer(self):
        @self.sio.event
        def pushState(data):
            # print(data)
            self.tratarStatus(data)

        @self.sio.event
        def pushQueue(data):
            # print(data)
            print('teste')

        if self.sio.connected:
            print('connected to volumio3')
            while self.sio.connected:
                self.sio.sleep(seconds=1)
                # self.sio.emit(u'getQueue', '')
                self.sio.emit(u'getState', '')
                #self.musicdata_lock = threading.Lock()

    def start(self):
        self._running = True
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join()

    def floatn(self, val):
        # A version of float that returns 0.0 if the value is not convertable
        try:
            retval = float(val)
        except:
            retval = 0.0
        return retval

    def tratarStatus(self,*data):
        playerState = data[0]

        self.musicdata.status = playerState.get(u'status').lower()

        if self.musicdata.status in [u'stop', u'pause', u'play']:
            self.musicdata.status = self.musicdata.status
        else:
            self.musicdata.status = u'stop'

        self.musicdata.position = playerState[u'position'] if u'position' in playerState else u'1'
        self.musicdata.album = playerState[u'album'] if u'album' in playerState else u''
        self.musicdata.artist = playerState[u'artist'] if u'artist' in playerState else u'Volumio'
        self.musicdata.title = playerState[u'title'] if u'title' in playerState else u'V3.0'
        #self.musicdata[u'uri'] self.musicdata.= playerState[u'uri'] if u'uri' in playerState else u''
        self.musicdata.albumArt = playerState[u'albumart'] if u'albumart' in playerState else u''
        self.musicdata.trackType = playerState[u'trackType'] if u'trackType' in playerState else u''
        self.musicdata.codec = playerState[u'codec'] if u'codec' in playerState else u''
        self.musicdata.seek = playerState[u'seek'] if u'seek' in playerState else 0
        self.musicdata.duration = time.strftime(u"%M:%S", time.gmtime(int(playerState[u'duration']))) if u'duration' in playerState else 0
        self.musicdata.elapsed = int(self.floatn(playerState[u'seek']) / 1000) if u'seek' in playerState else 0
        self.musicdata.samplerate = playerState[u'samplerate'] if u'samplerate' in playerState else u''
        self.musicdata.bitdepth = playerState[u'bitdepth'] if u'bitdepth' in playerState else u''
        self.musicdata.random = playerState[u'random'] if u'random' in playerState else u''
        self.musicdata.repeat = playerState[u'repeat'] if u'repeat' in playerState else u''
        self.musicdata.repeatSingle = playerState[u'repeatSingle'] if u'repeatSingle' in playerState else u''
        self.musicdata.stream = playerState[u'stream'] if u'stream' in playerState else u''

        # if duration is not available, then suppress its display
        if int(self.musicdata.length) > 0:
            timepos = time.strftime("%M:%S", time.gmtime(int(self.musicdata.elapsed))) + u"/" + time.strftime(
                "%M:%S", time.gmtime(int(self.musicdata.length)))
            remaining = time.strftime("%-M:%S",
                                      time.gmtime(int(self.musicdata.length) - int(self.musicdata.elapsed)))
        else:
            timepos = time.strftime(u"%M:%S", time.gmtime(int(self.musicdata.elapsed)))
            remaining = timepos

        self.musicdata.remaining = remaining
        self.musicdata.elapsed_formatted = timepos

        #print(self.musicdata.remaining)
        #print(self.musicdata.duration)

class displayLCD:
    _running = False

    def createSpecialChar(self):
        play_char = [
            0b00000,
            0b01000,
            0b01100,
            0b01110,
            0b01100,
            0b01000,
            0b00000,
            0b00000
        ]
        stop_char = [
            0b00000,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b00000,
            0b00000,
        ]
        pause_char = [
            0b00000,
            0b11011,
            0b11011,
            0b11011,
            0b11011,
            0b11011,
            0b00000,
            0b00000,
        ]

        cedilha_char = [
            0b00000,
            0b00000,
            0b01110,
            0b10001,
            0b10000,
            0b10101,
            0b01110,
            0b01000,
        ]

        self.lcd.create_char(0, play_char)
        #self.lcd.clear()
        self.lcd.create_char(1, stop_char)
        #self.lcd.clear()
        self.lcd.create_char(2, pause_char)
        #self.lcd.clear()
        self.lcd.create_char(3, cedilha_char)
        self.lcd.clear()

    def traduzirAcentos(self,text):
        newText = ''
        newText = text.replace('ç', '\x03')
        newText = newText.replace('Ç', '\x03')
        newText = newText.replace('á', 'a')
        newText = newText.replace('à', 'a')
        newText = newText.replace('â', 'a')
        newText = newText.replace('ä', 'a')
        newText = newText.replace('ã', 'a')
        newText = newText.replace('Á', 'A')
        newText = newText.replace('À', 'A')
        newText = newText.replace('Â', 'A')
        newText = newText.replace('Ä', 'A')
        newText = newText.replace('Ã', 'A')

        newText = newText.replace('é', 'e')
        newText = newText.replace('è', 'e')
        newText = newText.replace('ê', 'e')
        newText = newText.replace('ë', 'e')
        newText = newText.replace('É', 'E')
        newText = newText.replace('È', 'E')
        newText = newText.replace('Ê', 'E')
        newText = newText.replace('Ë', 'E')

        newText = newText.replace('í', 'i')
        newText = newText.replace('ì', 'i')
        newText = newText.replace('î', 'i')
        newText = newText.replace('ï', 'i')
        newText = newText.replace('Í', 'I')
        newText = newText.replace('Ì', 'I')
        newText = newText.replace('Î', 'I')
        newText = newText.replace('Ï', 'I')

        newText = newText.replace('ó', 'o')
        newText = newText.replace('ò', 'o')
        newText = newText.replace('ô', 'o')
        newText = newText.replace('ö', 'o')
        newText = newText.replace('õ', 'o')
        newText = newText.replace('Ó', 'O')
        newText = newText.replace('Ò', 'O')
        newText = newText.replace('Ô', 'O')
        newText = newText.replace('Ö', 'O')
        newText = newText.replace('Õ', 'O')


        newText = newText.replace('ú', 'u')
        newText = newText.replace('ù', 'u')
        newText = newText.replace('û', 'u')
        newText = newText.replace('ü', 'u')
        newText = newText.replace('Ú', 'U')
        newText = newText.replace('Ù', 'U')
        newText = newText.replace('Û', 'U')
        newText = newText.replace('Ü', 'U')

        return newText


    def convertStatusToChar(self, status):
        if status == u'play':
            return '\x00'
        elif status == 'stop':
            return '\x01'
        elif status == 'pause':
            return '\x02'
        else:
            return ''

    def __init__(self,musicdata, coluna = 0,  linha = 0, scroll = False, delay= 0.5):
        self.scroll = scroll
        self.delay = delay
        self.lcd = Adafruit_CharLCD(rs=7, en=8, d4=25, d5=24, d6=23, d7=18, cols=16, lines=2)

        self.createSpecialChar()
        #time.sleep(10)
        #self.text = text
        self.musicdata = musicdata
        self.coluna = coluna
        self.linha = linha

        self._running = False
        self._thread = threading.Thread(target=self.update)
        self._thread.daemon = True

        #lcd = Adafruit_CharLCD(rs=7, en=8, d4=25, d5=24, d6=23, d7=18, cols=16, lines=2)
    def start(self):
        self._running = True
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join()

    def update(self):
        #self.lcd.set_cursor(self.coluna, self.linha)
        text = ""
        self.lcd.clear()
        while self._running:
            if self.musicdata.artist == u'' and self.musicdata.title == u'':
                text = u'  Volumio v3.0  '
            else:
                text = self.traduzirAcentos(str(self.musicdata.position) + '.' + self.musicdata.artist + ' - ' + self.musicdata.title + ' (' + self.musicdata.duration + ')')
            self.lcd.set_cursor(self.coluna, self.linha)
            self.lcd.message(text)
            #self.lcd.set_cursor(self.coluna, 1)
            #self.lcd.message(str("                "))
            if self.scroll:
                if len(text) > 16:
                    #print("maior")
                    self.lcd.set_cursor(self.coluna, self.linha)
                    self.lcd.message(text)
                    self.lcd.set_cursor(self.coluna, 1)
                    self.lcd.message(str(self.musicdata.elapsed_formatted))
                    #self.lcd.set_cursor(11, 1)
                    self.lcd.set_cursor(15, 1)
                    self.lcd.message(self.convertStatusToChar(self.musicdata.status))
                    time.sleep(0.5)
                    i=0
                    for i in range(len(text) - 15):
                        if self.musicdata.status == u'stop':
                            break
                        if len(text) < 16:
                            break
                        if not self._running:
                            break
                        #self.lcd.clear()
                        self.lcd.set_cursor(self.coluna, self.linha)
                        self.lcd.message(text[i:i+16])
                        self.lcd.set_cursor(self.coluna, 1)
                        self.lcd.message(str(self.musicdata.elapsed_formatted))
                        self.lcd.set_cursor(15, 1)
                        self.lcd.message(self.convertStatusToChar(self.musicdata.status))
                        time.sleep(self.delay)
                    self.lcd.set_cursor(self.coluna, self.linha)
                    self.lcd.message(text[i:i+16])
                    self.lcd.set_cursor(self.coluna, 1)
                    self.lcd.message(str(self.musicdata.elapsed_formatted))
                    self.lcd.set_cursor(15, 1)
                    self.lcd.message(self.convertStatusToChar(self.musicdata.status))
                    time.sleep(0.5)
                else:
                    #print("menor q 16")
                    if self.musicdata.status == u'stop':
                        self.lcd.set_cursor(self.coluna, self.linha)
                        self.lcd.message(u'                ')
                    self.lcd.set_cursor(self.coluna, self.linha)
                    self.lcd.message(text)
                    if self.musicdata.artist == u'' and self.musicdata.title == u'':
                        self.lcd.set_cursor(0, 1)
                        self.lcd.message(u'                ')
                    else:
                        self.lcd.set_cursor(self.coluna, 1)
                        self.lcd.message(str(self.musicdata.elapsed_formatted))
                        self.lcd.set_cursor(15, 1)
                        self.lcd.message(self.convertStatusToChar(self.musicdata.status))
                        '''self.lcd.set_cursor(12, 1)
                        self.lcd.message(str(self.musicdata[u'status']))'''
                    time.sleep(1)
            else:
                if not self._running:
                    break
                self.lcd.set_cursor(self.coluna, self.linha)
                self.lcd.message(text)
                if self.musicdata.artist == u'' and self.musicdata.title == u'':
                    self.lcd.set_cursor(0, 1)
                    self.lcd.message(u'                ')
                else:
                    self.lcd.set_cursor(self.coluna, 1)
                    self.lcd.message(str(self.musicdata.elapsed_formatted))
                    self.lcd.set_cursor(12, 1)
                    self.lcd.message(str(self.musicdata.status))
                time.sleep(self.delay)


    def updateTexto(self, text):
        self.text = text

    def clear(self):
        self.lcd.clear()

    def print(self, text, coluna = 0, linha = 0):
        self.lcd.set_cursor(coluna, linha)
        self.lcd.message(text)

if __name__ == '__main__':

    socketVolumio = socketVolumio()
    socketVolumio.start()
    display = displayLCD(socketVolumio.musicdata, 0,0,True,0.3)
    display.clear()
    display.print("Volumio",5,0)
    time.sleep(5)
    display.clear()
    display.start()

    try:
        while True:
            #print("Chamando o socket")
            time.sleep(1)
            #display.updateTexto(socketVolumio.musicdata[u'artist'] + ' - ' + socketVolumio.musicdata[u'title'] )

    except KeyboardInterrupt:
        display.stop()
        socketVolumio.stop()
        #display2.stop()
        print("fim")

    #display.clear()
    #display.print(u'Hello World',2,0)
'''lcd.message(message)
for i in range(16-len(message)):
    time.sleep(0.5)
    lcd.move_right()
for i in range(16-len(message)):
    time.sleep(0.5)
    lcd.move_left()
for i in range(len(message) - 15):
    lcd.clear()
    lcd.message(message[i:i+16])
    time.sleep(0.3)'''

