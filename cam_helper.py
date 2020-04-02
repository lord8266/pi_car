import cv2
import urllib.request
import numpy as np
import time
import queue
stream = urllib.request.urlopen('http://192.168.1.158:8000/stream.mjpg')

def check_stop(sq: queue.Queue):
    try:
        f = sq.get_nowait()
        return 1
    except Exception as e:
        return 0

def get_image_stream(q: queue.Queue,sq: queue.Queue):
    data = b''
    while True:
        # print(stream)
        try:
            if check_stop(sq):
                stream.close()
                break
            data += stream.read(1024)
            a = data.find(b'\xff\xd8')
            b = data.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = data[a:b+2]
                data = data[b+2:]
                i = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8),cv2.cv2.IMREAD_COLOR)
                prev=time.time()

                q.put_nowait(i)
        except Exception as e:
            pass