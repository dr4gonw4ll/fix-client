import sys
import simplefix
import os
import socket
import threading
import logging
from datetime import datetime
from datetime import timedelta
import atexit
import shelve
import re
from colorama import Fore, Back,Style


class client():
    def __init__(self):
        if(os.path.isfile(".cache.dat")):
            self.data=shelve.open(".cache")
            self.updateReqSequence(sys.argv[1])
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
    def updateReqSequence(self,new_seq = None):
        if(new_seq):
            self.data["reqseq"] = new_seq
        else:
            self.data["reqseq"] = int(self.data["reqseq"])+1 
        return None
    def updateResSequence(self,seq):
        self.data["resseq"] = seq
        return None
    
    def close(self):
        self.data.close()
        return True
        
    
class socketConnect():
    def __init__(self,seqObj): #Initialize the Fix message objects here
        self.seqObj = seqObj
        self.message = simplefix.FixMessage()
        self.resp_mesg = simplefix.FixParser()

        return
    
    def header(self):  # this is header message
        self.message.append_pair(8,"FIX.4.2")
        self.message.append_pair(49,"BANZAI")
        self.message.append_pair(56,"FIXIMULATOR")
        self.message.append_pair(34,self.seqObj.getReqSequence())
        self.message.append_utc_timestamp(52, precision=3, header=True)
        _message = self.message
        del self.message
        self.message = simplefix.FixMessage()
        self.seqObj.updateReqSequence()
        return _message
    
    def logon(self): #Logon message
        logon = self.header()
        logon.append_pair(35,"A")
        logon.append_pair(108,0)
        logon.append_pair(98,0)

        _temp_logon = logon
        del logon
        return _temp_logon

    def sendMesg(self, msg):
        self._msg = msg
        self.s.send(self._msg.encode())
        return
           
    def recvMesg(self): #function which receives the messages and processes it accordingly
        while True:

            self.received_message = self.s.recv(4096)
            self.resp_mesg.append_buffer(self.received_message)
            self.resp_mesg = self.resp_mesg.get_message()
            print(Fore.GREEN+"Received:\r\n"+str(self.resp_mesg))
            if self.resp_mesg.get(35,1).decode('utf-8') == "0":
                print("Hearbeat Response")
            elif self.resp_mesg.get(35,1).decode('utf-8') == "1":
                print("Test Request")
                self.testreqid = self.resp_mesg.get(112,1)
                self.testRequest(self.testreqid)
            elif self.resp_mesg.get(35,1).decode('utf-8') == "2":
                print("send resend request")
            elif self.resp_mesg.get(35,1).decode('utf-8') == "3":
                print("Message Rejected, Exiting the program")
                exit(1)
            elif self.resp_mesg.get(35,1).decode('utf-8') == "4":
                print("Sequence Reset..")
            elif self.resp_mesg.get(35,1).decode('utf-8') == "5":
                print("Logout")
            elif self.resp_mesg.get(35,1).decode('utf-8') == "A":
                print("Logged in successfully")
            elif self.resp_mesg.get(35,1).decode('utf-8') == "D":
                print("Order Single ")
            else:
                print(self.resp_mesg)
                print("Proceed based on response value of 35")
                del self.resp_mesg
                self.resp_mesg = simplefix.FixParser()

        return 

    def testRequest(self,resultingheartbeatinresp):
        self.header()
        return
    
    
    def resendReq(self,fix_message):
        return
  
       
    def processFix(self,custom_fix):
        self._custom_fix = custom_fix
        self._custom_fix = self._custom_fix.split("")
        self.processed_msg = self.header()
        self._custom_fix.remove(self._custom_fix[-1])
        for i in self._custom_fix:
            self.processed_msg.append_string(i)
        self._processed_msg = self.processed_msg
        del self.processed_msg
        return self._processed_msg

    def hearbeat(self):
        while True:

            if self.counter + timedelta(seconds=5) < datetime.now():
                print(1)
                self.header_fix_message = self.header()
                self.header_fix_message.append_pair(35,0)
                print(Fore.BLUE+"message sent as hearbeat"+str(self.header_fix_message))
                self.s.send(self.header_fix_message.encode())
                #self.recvMesg()
                self.counter = datetime.now()
                del self.header_fix_message 
            else:
                continue
        return
    
    def rolling(self): #starting new thread to accept input from user
        logon_msg = self.logon()
        
        self.sendMesg(logon_msg)
        #self.recvMesg()
        while True:
            self.user_fix_mesg = input("FIX:>")
            
            self.counter = datetime.now()
            self.output = self.processFix(self.user_fix_mesg)
            self.sendMesg(self.output)
            #self.recvMesg()
        return


    def createSocket(self): #connect to the fix engine
        self.counter = datetime.now()
        self.s = socket.socket()
        try:
            self.s.connect(("127.0.0.1",9878))
        except:
            print("Error connecting to server.")
        x = threading.Thread(target = self.rolling)
        x.start()
        y = threading.Thread(target = self.hearbeat)
        y.start()
        z = threading.Thread(target = self.recvMesg)
        z.start()
                      
        return
         
   

clobj = client()
a = socketConnect(clobj)
a.createSocket()
@atexit.register
def exitregister():
    clobj.close()
