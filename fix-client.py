import sys
import simplefix
import os
import socket
import threading
import logging
import atexit
import shelve

class client():
    def __init__(self):
        if(os.path.isfile(".cache.dat")):
            self.data=shelve.open(".cache")
            print(self.data["reqseq"])
            print(self.data["resseq"])
            
        else:
            self.data = shelve.open(".cache")
            self.data["reqseq"] = 0
            self.data["resseq"] = 0
        return

    def getReqSequence(self):
         return int(self.data["reqseq"])
    def getResSequence(self):
        return int(self.data["resseq"])
    def updateReqSequence(self):
        self.data["reqseq"] += 1 
        return None
    def updateResSequence(self,seq):
        self.data["resseq"] = seq
        return None
    
    def close(self):
        self.data.close()
        return True
        
    
class socketConnect():
    def __init__(self,seqObj):
        self.seqObj = seqObj
        self.message = simplefix.FixMessage()
        self.resp_mesg = simplefix.FixParser()
        return
    
    def receiver(self):
        self.resp_mesg.append_buffer(self.s.recv(2048))
        self.resp = self.resp_mesg.get_message()
        if(self.resp.get(35) == "A"):
            self.resendReq(self.resp)
        print("\r\nOutput:"+str(self.resp_mesg.get_message()))
        self.customFix()
        
        return
      
    def createSocket(self):
        self.s=socket.socket()
        self.s.connect(("127.0.0.1",9878))
        x = threading.Thread(target=self.receiver,args=())
        x.start()
        self.logon()
    
    def header(self):
        self.message.append_pair(8,"FIX.4.2")
        self.message.append_pair(49,"BANZAI")
        self.message.append_pair(56,"FIXIMULATOR")
        self.message.append_pair(34,self.seqObj.getReqSequence())
        self.message.append_utc_timestamp(52, precision=3, header=True)
        return self.message

    def resendReq(self,fix_message):
        return


    def logon(self):
        self.message = self.header()
        self.message.append_pair(35,"A")
        self.message.append_pair(108,0)
        self.message.append_pair(98,0)
        self.sendRequest(self.message.encode())
        return
    
    def sendRequest(self,r):
        self.seqObj.updateReqSequence()
        self.s.send(r)
        return
    
    def customFix(self):
        r = input("FIX:>")
        r = r.split(";")
        new_msg = self.header()
        r.remove(r[-1])
        for i in r:
            new_msg.append_string(i)
        new_msg.append_pair(49,"WHATFFFFFFFFFF")
        print("NewMessageis"+str(new_msg.encode()))
        self.sendRequest(new_msg.encode())
        self.receiver()
        return

clobj = client()
a = socketConnect(clobj)
a.createSocket()
@atexit.register
def exitregister():
    clobj.close()

    
import socket
import threading
import requests
import time
from datetime import datetime
from datetime import timedelta
class client():

    def hearbeat(self):
        while True:
            if self.counter + timedelta(seconds=5) < datetime.now():
                res = requests.get("http://demo.testfire.net/")
                print(res.cookies)
                self.counter = datetime.now()
            else:
                continue
        return
    
    def acceptInput(self):
        while True:
            mesg = input("FIX:>")
            self.counter = datetime.now()
        return
           
    def __init__(self):
        self.flag = True
        self.counter = datetime.now()
        event = threading.Event()
        with socket.socket() as s:
            try:
                s.connect(("127.0.0.1",9878))
            except:
                print("Error creating")
            x = threading.Thread(target = self.acceptInput)
            x.start()
            y = threading.Thread(target = self.hearbeat)
            y.start()
            
            
c = client()
