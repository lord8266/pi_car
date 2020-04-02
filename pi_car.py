import socket
import queue
import time
import pygame
from pygame.locals import *
import random
import threading
import cam_helper
class Logic:
    @staticmethod
    def encode(data):
        return bytes(data)

    @staticmethod
    def decode(data):
        return [int(i) for i in data]

class Transmitter:
    def __init__(self,host='localhost',port=1234,word_size=5):
        self.status = 0
        self.connect(host,port)
        self.word_size =word_size

    def communicate(self,data):
        self.send(Logic.encode(data))
        return Logic.decode(self.receive())

    def connect(self,host='localhost',port=1234):
        print(host)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.sock.connect((host,port))

    def disconnect(self):
        self.close()
        self.sock.close()

    def send(self,data):
        self.sock.sendall(data)
        
    def receive(self):
        return self.sock.recv(self.word_size)
        
    def close(self):
        self.sock.sendall(b'\x00')
        self.sock.recv(1)

pygame.init()
class UserInterface:
    def __init__(self,res=(1280,1000),host='localhost',port=1234):
        self.res = res
        self.display = pygame.display.set_mode(res, HWSURFACE|DOUBLEBUF|RESIZABLE)
        self.sensor_data = [0,0,0,0,0]
        self.curr_state = [1,2,120,110]
        self.font = pygame.font.Font('freesansbold.ttf', 64)
        self.running =True
        self.transmitter = Transmitter(host,port,5)
        self.image_queue = queue.Queue(20)
        self.stop_queue =queue.Queue(2)
        self.cam_thread =  threading.Thread(target=cam_helper.get_image_stream,args=[self.image_queue,self.stop_queue])
        self.cam_thread.start()
        self.cam_surface=None
        self.cam_rect = Rect(64,36,1152,648)
        self.load_arrows()

    def print(self,text,pos,height):
        text = self.font.render(text, True,(255,255,255))
        w,h = text.get_width(),text.get_height()
        w,h = int(w/h*height),height
        text = pygame.transform.scale(text,(w,h))
        rect = text.get_rect()
        rect.center = pos
        self.prev_mouse = None
        self.display.blit(text,rect)

    def load_arrows(self):
        white = pygame.image.load("arrow_white.png")
        white=pygame.transform.scale(white,(100,100))
        green =pygame.image.load("arrow_green.png")
        green=pygame.transform.scale(green,(100,100))
        rect =pygame.Rect(0,0,120,120)
        rect.center =(150+640,720+100)
        self.arrows_top=[2,rect.copy(),pygame.transform.rotate(white,90),pygame.transform.rotate(green,90) ]
        rect.center= (150+640-130,720+230)
        self.arrows_left=[2,rect.copy(),pygame.transform.rotate(white,180),pygame.transform.rotate(green,180) ]
        rect.center = (150+640,720+230)
        self.arrows_bottom=[2,rect.copy(),pygame.transform.rotate(white,270),pygame.transform.rotate(green,270) ]
        rect.center = (150+640+130,720+230)
        self.arrows_right=[2,rect.copy(),white,green]

    def blit_arrows(self):
        self.display.blit(self.arrows_top[self.arrows_top[0]],self.arrows_top[1])
        self.display.blit(self.arrows_bottom[self.arrows_bottom[0]],self.arrows_bottom[1])
        self.display.blit(self.arrows_left[self.arrows_left[0]],self.arrows_left[1])
        self.display.blit(self.arrows_right[self.arrows_right[0]],self.arrows_right[1])

    def event(self):
        for event in pygame.event.get() : 
            if event.type == pygame.QUIT : 
                pygame.quit() 
                self.running = False   
     
    def update_state(self):
        keys = pygame.key.get_pressed()
        self.curr_state[0:2] = [2,2]
        (self.arrows_top[0],self.arrows_bottom[0],self.arrows_right[0],self.arrows_left[0])=(2,2,2,2)
        if (keys[K_UP]):
            self.arrows_top[0]=3
            self.curr_state[0]+=1
            self.curr_state[1]+=1
            self.arrows_top[0]=3
        if (keys[K_DOWN]):
            self.curr_state[0]-=1
            self.curr_state[1]-=1
            self.arrows_bottom[0]=3
        if (keys[K_LEFT]) and not (keys[K_RIGHT] ):
            self.arrows_left[0]=3
            if keys[K_LSHIFT]:
                self.curr_state[0] = 1
                self.curr_state[1] = 3
            else:
                self.curr_state[0] = 2
        if (keys[K_RIGHT]) and not (keys[K_LEFT]):
            self.arrows_right[0]=3
            if keys[K_LSHIFT]:
                self.curr_state[1] = 1
                self.curr_state[0] = 3
            else:
                self.curr_state[1] = 2
        
        if keys[K_w]:
            self.curr_state[2]+=int(10*(1+keys[K_SPACE]-0.5*keys[K_c]))
        if keys[K_s]:
            self.curr_state[2]-=int(10*(1+keys[K_SPACE]-0.5*keys[K_c]))
        if keys[K_a]:
            self.curr_state[3]+=int(10*(1+keys[K_SPACE]-0.5*keys[K_c]))
        if keys[K_d]:
            self.curr_state[3]-=int(10*(1+keys[K_SPACE]-0.5*keys[K_c]))
        self.curr_state[2:4] = [max(1,min(i,180)) for i in self.curr_state[2:4] ]
        if keys[K_c]:
            self.curr_state[2:4] = [120,110]
        state = self.curr_state
        # self.control.send(state)
        # self.sensors = decode(self.control.receive())
    def draw_servos(self):
        pygame.draw.rect(self.display, (0,0,255), (720-430,720+25,230,230),1) 
        start_x,start_y,end_x,end_y=720-430+50,720+40,720-430+50+180,720+40+180
        curr_x,curr_y = self.curr_state[3],self.curr_state[2]-30
        curr_x,curr_y = max(0,min(curr_x,180)),max(0,min(curr_y,180))
        print(curr_x,curr_y)
        curr_x,curr_y = start_x+int((181-curr_x)*(end_x-start_x)/180),start_y+int(curr_y*(end_y-start_y)/180)
        pygame.draw.circle(self.display,(0,0,255),(curr_x,curr_y),20)
        
    def update_frame(self):
        try:
            frame =self.image_queue.get_nowait()
            print(frame.shape)
            self.cam_surface = pygame.surfarray.make_surface(frame.swapaxes(0,1)[:,:,::-1])
            self.cam_surface =pygame.transform.scale(self.cam_surface,(1152,648))

        except queue.Empty as e:
            pass

    def run(self):
        prev = time.time()
        while self.running:
            self.display.fill((0,0,0))
            if (time.time()-prev)>0.050:
                prev = time.time()
                self.update_state()
                self.sensor_data = self.transmitter.communicate(self.curr_state)
            self.print(" ".join(map(lambda w:"%03d"%(w),self.sensor_data)),(320,300),30 )
            self.update_frame()
            if self.cam_surface:
                self.display.blit(self.cam_surface,self.cam_rect)
            self.blit_arrows()
            self.draw_servos()
            pygame.display.flip()
            self.event()
    def close(self):
        self.transmitter.disconnect()
        self.stop_queue.put(None)
        print("here")
        self.cam_thread.join()
        pygame.quit()


# g = Game(ip='localhost')
g = UserInterface(host='192.168.1.158',port=1234)
g.run()
g.close()
