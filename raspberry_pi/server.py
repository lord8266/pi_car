import socket
import queue

import time
import logging
import random
import functools
import serial


data_ba  ={
    'motor1':1,
    'motor2':2,
    'servo1':3,
    'servo2':4,
}
def decode(b: bytes):
    return map(int,b)
def encode(data):
    return bytes(data)

class Driver:
    def __init__(self,port='/dev/ttyUSB1'):
        self.i = 0
        self.ser = serial.Serial(port, 57600)

    def send(self,data):
        self.ser.write(b'\x00')
        self.ser.write(data)
        print("send",data)

    def recieve(self):
        while 1:
            d = self.ser.read(1)
            if d==b'\x00':
                data = self.ser.read(5)
                self.ser.reset_input_buffer()
                print("recv",data)
                return data
            else:
                print("miss")
                

    # def run(self):
    #     while 1:
    #         try:
    #             s =self.send_q.get_nowait()
                
    #             if s is None:
    #                 break
    #             self.send(s)
    #         except:
    #             pass

    #         try:
    #             self.recieve()
    #             self.recv_q.put_nowait(self.curr_ret)
    #         except Exception as e:
    #             if not isinstance(e,queue.Full) and not isinstance(e,queue.Empty):
    #                 print(e)

            
    #     self.close()

    def close(self):
        self.ser.close()


class Client:
    def __init__(self,conn,port='/dev/ttyUSB1'):
        self.conn =conn
        self.driver = Driver(port)
    def send(self,data=b'\x00'):
        # print("recv:",data)
        self.conn.sendall(data)
        
    def receive(self):
        return self.conn.recv(4)

    def run(self):
        while 1:
            try:
                data = self.receive()
                if data==b'\x00':
                    self.send()
                    break
                self.driver.send(data)
                data = self.driver.recieve()
                self.send(data)
            except Exception as e:
                print(e)
                break
        self.driver.close()

ip='192.168.1.158'    
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
sock.bind((ip,1234)) 
sock.listen(1)
while 1:
    conn,_  =sock.accept()
    print("new client",_)
    c =Client(conn,port='/dev/serial0')
    c.run()
    
