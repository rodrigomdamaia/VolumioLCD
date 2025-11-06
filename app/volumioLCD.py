import time
import threading
from socket import socket

from Adafruit_CharLCD import Adafruit_CharLCD
from socketIO_client import SocketIO
import socketio

class musicdata_init:
    musicdata_init = {
        'musicdatasource': u"",
        'stream': u"",
        'actPlayer': u"",
        'artist': u"",
        'title': u"Volumio v3.0",
        'uri': u"",
        'encoding': u"",
        'tracktype': u"",
        'bitdepth': u"",
        'bitrate': u"",
        'samplerate': u"",
        'elapsed_formatted': u"",
        'album': u"",
        'elapsed': -1,
        'channels': 0,
        'length': 0,
        'remaining': u"",
        'volume': -1,
        'repeat': False,
        'single': False,
        'random': False,
        'playlist_display': u"",
        'playlist_position': -1,
        'playlist_length': -1,

        'my_name': u"",  # Volumio 2 only

        # Deprecated values
        'current': -1,
        'duration': -1,
        'position': u"",
        'playlist_count': -1,
        'type': u""
    }



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

        self.musicdata = {}
        self.musicdata = musicdata_init.musicdata_init.copy()

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
        status = data[0]

        #print(status)

        #self.musicdata[u'state'] = status.get(u'status').lower()

        #print(self.musicdata)

        #print(self.musicdata)
        state = status.get(u'status').lower()
        #print(state)
        if state in [u'stop', u'pause', u'play']:
            self.musicdata[u'status'] = state
        else:
            self.musicdata[u'status'] = u'stop'

        self.musicdata[u'album'] = status[u'album'] if u'album' in status else u''
        self.musicdata[u'artist'] = status[u'artist'] if u'artist' in status else u'Volumio'

        self.musicdata[u'title'] = status[u'title'] if u'title' in status else u'V3.0'
        self.musicdata[u'uri'] = status[u'uri'] if u'uri' in status else u''
        self.musicdata[u'elapsed'] = int(self.floatn(status[u'seek']) / 1000) if u'seek' in status else 0

        # if duration is not available, then suppress its display
        if int(self.musicdata[u'length']) > 0:
            timepos = time.strftime("%M:%S", time.gmtime(int(self.musicdata['elapsed']))) + u"/" + time.strftime(
                "%M:%S", time.gmtime(int(self.musicdata['length'])))
            remaining = time.strftime("%-M:%S",
                                      time.gmtime(int(self.musicdata['length']) - int(self.musicdata['elapsed'])))
        else:
            timepos = time.strftime(u"%M:%S", time.gmtime(int(self.musicdata[u'elapsed'])))
            remaining = timepos

        self.musicdata[u'remaining'] = remaining
        self.musicdata[u'elapsed_formatted'] = timepos

        #print(self.musicdata)

class displayLCD:
    _running = False

    def __init__(self,musicdata, coluna = 0,  linha = 0, scroll = False, delay= 0.5):
        self.scroll = scroll
        self.delay = delay
        self.lcd = Adafruit_CharLCD(rs=7, en=8, d4=25, d5=24, d6=23, d7=18, cols=16, lines=2)
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
            if self.musicdata[u'artist'] == u'' and self.musicdata[u'title'] == u'':
                text = u'  Volumio v3.0  '
            else:
                text = str(self.musicdata[u'artist'] + ' - ' + self.musicdata[u'title'])
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
                    self.lcd.message(str(self.musicdata[u'elapsed_formatted']))
                    self.lcd.set_cursor(11, 1)
                    if self.musicdata[u'status'] == u'pause':
                        self.lcd.message(str(self.musicdata[u'status']))
                    else:
                        self.lcd.message(str(' ' + self.musicdata[u'status']))

                    #print(text)
                    time.sleep(0.5)
                    i=0
                    for i in range(len(text) - 15):
                        if self.musicdata[u'status'] == u'stop':
                            break
                        if len(text) < 16:
                            break
                        if not self._running:
                            break
                        #self.lcd.clear()
                        self.lcd.set_cursor(self.coluna, self.linha)
                        self.lcd.message(text[i:i+16])
                        self.lcd.set_cursor(self.coluna, 1)
                        self.lcd.message(str(self.musicdata[u'elapsed_formatted']))
                        self.lcd.set_cursor(11, 1)
                        if self.musicdata[u'status'] == u'pause':
                            self.lcd.message(str(self.musicdata[u'status']))
                        else:
                            self.lcd.message(str(' ' + self.musicdata[u'status']))
                        time.sleep(self.delay)
                    self.lcd.set_cursor(self.coluna, self.linha)
                    self.lcd.message(text[i:i+16])
                    self.lcd.set_cursor(self.coluna, 1)
                    self.lcd.message(str(self.musicdata[u'elapsed_formatted']))
                    self.lcd.set_cursor(11, 1)
                    if self.musicdata[u'status'] == u'pause':
                        self.lcd.message(str(self.musicdata[u'status']))
                    else:
                        self.lcd.message(str(' ' + self.musicdata[u'status']))
                    time.sleep(0.5)
                else:
                    #print("menor q 16")
                    if self.musicdata[u'status'] == u'stop':
                        self.lcd.set_cursor(self.coluna, self.linha)
                        self.lcd.message(u'                ')
                    self.lcd.set_cursor(self.coluna, self.linha)
                    self.lcd.message(text)
                    if self.musicdata[u'artist'] == u'' and self.musicdata[u'title'] == u'':
                        self.lcd.set_cursor(0, 1)
                        self.lcd.message(u'                ')
                    else:
                        self.lcd.set_cursor(self.coluna, 1)
                        self.lcd.message(str(self.musicdata[u'elapsed_formatted']))
                        self.lcd.set_cursor(12, 1)
                        self.lcd.message(str(self.musicdata[u'status']))
                    time.sleep(1)
            else:
                if not self._running:
                    break
                self.lcd.set_cursor(self.coluna, self.linha)
                self.lcd.message(text)
                if self.musicdata[u'artist'] == u'' and self.musicdata[u'title'] == u'':
                    self.lcd.set_cursor(0, 1)
                    self.lcd.message(u'                ')
                else:
                    self.lcd.set_cursor(self.coluna, 1)
                    self.lcd.message(str(self.musicdata[u'elapsed_formatted']))
                    self.lcd.set_cursor(12, 1)
                    self.lcd.message(str(self.musicdata[u'status']))
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
    time.sleep(1)
    display.print("by @maiar85", 3, 1)
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

