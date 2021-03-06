""" A quick and dirty FIX protocol interactive client for pentest. This client can be used to send fix messages to server which are blocked or validated by publicly available fix clients.
The client is very simple and it does not validate any unexpected inputs.
Uses python3
Usage: python fix-client.py <sequence number to start from> e.g. python fix-client.py 3125

The client manages hearbeat and on successfull connection a message with successfull logon is shown else unhandled error. This client does not handle resend request or test request messages.The client also does not keep track of response messages sequence,
Sample message format given below: Stricly exclude the header tag value pairs, protocol, size, time and hash are automatically added by client

35=D11=123000159876521=155=XXXX115=<SENDER>116=<TARGET>48=XXXX22=554=158=MessageSentUsingCustomFIXCLient60=00:00:0038=1040=1

A dirty code by @dw4ll
"""

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
from colorama import Fore, Back, Style


class client():
    def __init__(self):
        if (os.path.isfile(".cache.dat")):
            self.data = shelve.open(".cache")


        else:
            self.data = shelve.open(".cache")
            self.data["reqseq"] = 0
            self.data["resseq"] = 0
        return

    def getReqSequence(self):
        return int(self.data["reqseq"])

    def getResSequence(self):
        return int(self.data["resseq"])

    def updateReqSequence(self, new_seq=None):
        if (new_seq):
            self.data["reqseq"] = new_seq
        else:
            self.data["reqseq"] = int(self.data["reqseq"]) + 1
        return None

    def updateResSequence(self, seq):
        self.data["resseq"] = seq
        return None

    def close(self):
        self.data.close()
        return True


class socketConnect():
    def __init__(self, seqObj):  # Initialize the Fix message objects here
        self.seqObj = seqObj
        self.message = simplefix.FixMessage()
        self.resp_mesg = simplefix.FixParser()
        self.seqObj.updateReqSequence(sys.argv[1])
        print(self.seqObj.getReqSequence())

        return

    def header(self):  # this is header message
        self.message.append_pair(8, "FIX.4.2") #update if you want to
        self.message.append_pair(49, "banzai") #update sender 
        self.message.append_pair(56, "fiximulator") #update target
        self.message.append_pair(34, self.seqObj.getReqSequence())
        # self.message.append_pair(52,"20200611-16:37:33.764") #faking the timestamp,
        self.message.append_utc_timestamp(52, precision=3, header=True) #comment it out, if you are commenting the above line to send fake time
        _message = self.message
        del self.message
        self.message = simplefix.FixMessage()
        self.seqObj.updateReqSequence()
        return _message

    def logon(self):  # Logon message
        logon = self.header()
        logon.append_pair(35, "A")
        logon.append_pair(108, 0)
        logon.append_pair(98, 0)

        _temp_logon = logon
        del logon
        return _temp_logon

    def sendMesg(self, msg):
        self._msg = msg
        print(self._msg.encode())
        self.s.send(self._msg.encode())
        return

    def recvMesg(self):  # function which receives the messages and processes it accordingly
        while True:

            self.received_message = self.s.recv(4096)
            self.resp_mesg.append_buffer(self.received_message)
            self.resp_mesg = self.resp_mesg.get_message()
            print(f"\r\n Received: {self.resp_mesg}")
            print(Fore.GREEN + "\r\nReceived:\r\n" + str(self.resp_mesg))
            if self.resp_mesg.get(35, 1).decode('utf-8') == "0":
                print("\r\n\r\nHearbeat Response")
            elif self.resp_mesg.get(35, 1).decode('utf-8') == "1":
                print("\r\n\r\nTest Request")
                self.testreqid = self.resp_mesg.get(112, 1)
                self.testRequest(self.testreqid)
            elif self.resp_mesg.get(35, 1).decode('utf-8') == "2":
                print("\r\n\r\nsend resend request")
            elif self.resp_mesg.get(35, 1).decode('utf-8') == "3":
                print("\r\n\r\nMessage Rejected, Exiting the program")
                exit(1)
            elif self.resp_mesg.get(35, 1).decode('utf-8') == "4":
                print("\r\n\r\nSequence Reset..")
            elif self.resp_mesg.get(35, 1).decode('utf-8') == "5":
                print("\r\n\r\nLogout")
            elif self.resp_mesg.get(35, 1).decode('utf-8') == "A":
                print("\r\n\r\nLogged in successfully")
            elif self.resp_mesg.get(35, 1).decode('utf-8') == "D":
                print("\r\n\r\nOrder Single ")
            else:
                print(self.resp_mesg)
                print("\r\n\r\nProceed based on response value of 35")
                del self.resp_mesg
                self.resp_mesg = simplefix.FixParser()

        return

    def testRequest(self, resultingheartbeatinresp):
        self.header()
        return

    def resendReq(self, fix_message):
        return

    def processFix(self, custom_fix):
        self._custom_fix = custom_fix
        self._custom_fix = self._custom_fix.split("")
        self.processed_msg = self.header()
        self._custom_fix.remove(self._custom_fix[-1])
        for i in self._custom_fix:
            self.processed_msg.append_string(i)
        self._processed_msg = self.processed_msg
        # print(self._processed_msg)
        del self.processed_msg
        return self._processed_msg

    def hearbeat(self):
        while True:

            if self.counter + timedelta(seconds=30) < datetime.now():
                # print(1)
                self.header_fix_message = self.header()
                self.header_fix_message.append_pair(35, 0)
                print(Fore.BLUE + "\r\n\r\nmessage sent as hearbeat: " + str(self.header_fix_message))
                self.s.send(self.header_fix_message.encode())
                # self.recvMesg()
                self.counter = datetime.now()
                del self.header_fix_message
            else:
                continue
        return

    def rolling(self):  # starting new thread to accept input from user
        logon_msg = self.logon()

        self.sendMesg(logon_msg)
        # self.recvMesg()
        while True:
            self.user_fix_mesg = input("\r\n:>")

            self.counter = datetime.now()
            self.output = self.processFix(self.user_fix_mesg)
            self.sendMesg(self.output)
            # self.recvMesg()
        return

    def createSocket(self):  # connect to the fix engine
        self.counter = datetime.now()
        self.s = socket.socket()
        try:
            self.s.connect(("127.0.0.1", 9878))
        except:
            print("\r\nError connecting to server.\r\n")
        x = threading.Thread(target=self.rolling)
        x.start()
        y = threading.Thread(target=self.hearbeat)
        y.start()
        z = threading.Thread(target=self.recvMesg)
        z.start()

        return


clobj = client()
a = socketConnect(clobj)
a.createSocket()


@atexit.register
def exitregister():
    clobj.close()
