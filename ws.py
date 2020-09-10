import asyncio
import time
from watchdog.observers import Observer
from watchdog.events import *
import websockets


msg = '1'
def _print(str):
    global msg
    msg = open(str).readlines()[0]
    print("file modified:{0}".format(msg))

def setMsg(m):
    msg = m
def getMsg():
    return msg

patterns = [".\client.py"]
class FileEventHandler(FileSystemEventHandler):

    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            if event.src_path in patterns:
                _print(event.src_path)

async def echo(websocket, path):
    global msg
    async for message in websocket:
        message = "I got your message: {}".format(message)
        await websocket.send(message)
        old_msg = msg
        while True:
            #print("oldmsg=%s msg=%s" %(old_msg,msg))
            if old_msg != msg:
                await websocket.send(msg)
                old_msg = msg
            time.sleep(0.2)

observer = Observer()
event_handler = FileEventHandler()
observer.schedule(event_handler, ".", False)
observer.start()

asyncio.get_event_loop().run_until_complete(websockets.serve(echo, 'localhost', 8765))
asyncio.get_event_loop().run_forever()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()