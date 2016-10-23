from Crypto.Cipher import AES
import time
import random

JITTER = 0
WINDOW = 0
TIME_SLOTS = 1000

sent_count = 0
type_I_count = 0
type_II_count = 0

N_0 = '1234567890123456'
K   = '9876543210123456'

E   = AES.new(K, AES.MODE_CFB, N_0)
delays = []



class Message:

    def __init__(self, sender, recipient, arrival, content, malicious=False):
        self.sender = sender
        self.recipient = recipient
        self.arrival = arrival
        self.content = content
        self.malicious = malicious

class Client:

    def __init__(self, name):
        self.inbox = []
        self.outbox = []
        self.name = name
        self.i = 0
        self.expectedResponse = 0
        self.warningResponse  = 0
        self.time = 0

    def next_delay(self):
        self.i = self.i + 1
        return delays[self.i]

    def sendReply(self, sender, t = -1, danger = False, message="Ping"):

        if t == -1:
            t = self.time

        delay = self.next_delay()
        nextDelay = self.next_delay()
        self.expectedResponse = t + delay + nextDelay
        self.warningResponse = int(t + delay + nextDelay/2)
        response = Message(self, sender, t + (delay/2 if danger else delay), message)
        self.outbox.append(response)

    def addMessage(self, m):
        self.inbox.append(m)

    def handleMessage(self, m):
        #print(self.name, "got message: ", m.content)
        global type_I_count
        global type_II_count
        global WINDOW

        t = (self.time-1 if (self.name == "Alice" and m.content != "Startup") else self.time)


        #if m.sender.name == "Trudy":
        #    print(t, self.expectedResponse-WINDOW, self.expectedResponse+WINDOW)

        if(t >= self.expectedResponse-WINDOW and t <= self.expectedResponse+WINDOW):
            #print("Authenticated")
            if(m.sender.name == "Trudy"):
                type_I_count = type_I_count+1
            else:
                self.sendReply(m.sender, t=self.expectedResponse)

        elif(t >= self.warningResponse-WINDOW and t <= self.warningResponse+WINDOW):
            #print("Got Danger Will Robinson")
            if(m.sender.name == "Trudy"):
                type_I_count = type_I_count+1
            else:
                self.sendReply(m.sender, t=self.expectedResponse)

        elif(self.name == "Alice"):
            if m.sender.name == "Bob":
                type_II_count
            #print(t, self.expectedResponse)
            #self.sendReply(m.sender, t=self.expectedResponse, message="DWR")#, danger=True)
        #elif(m.sender.name == "Trudy"):


    def checkForMessage(self):
        for m in self.inbox:
            self.handleMessage(m)
        self.inbox = []

    def handleOutbox(self):
        for m in self.outbox:
            if m.arrival == self.time:
                m.recipient.addMessage(m)
                self.outbox.remove(m)

    def update(self):
        self.checkForMessage()
        self.handleOutbox()
        self.time = self.time + 1



def sim_loop():

    global sent_count

    if(random.randint(1,10) == 1):
        Trudy.outbox.append(Message(Trudy, Alice, Trudy.time+random.randint(1,TIME_SLOTS), "ATTACK"))
        sent_count = sent_count+1
    Alice.update()
    Bob.update()
    Trudy.update()

typeIs = []
typeIIs = []
sent = []
windows = []

for i in range(0,110,10):


    delays = []

    sent_count = 0
    type_I_count = 0
    type_II_count = 0

    Alice = Client("Alice")
    Bob = Client("Bob")

    Trudy = Client("Trudy")

    ni = N_0
    for _ in range(10000):
        ni = E.encrypt(ni)
        delays.append(int.from_bytes(ni, byteorder="little") % TIME_SLOTS + WINDOW)

    Alice.inbox.append(Message(Bob, Alice, 0, "Startup"))
    Bob.expectedResponse = Bob.next_delay()

    WINDOW = i
    print("Window is: ", i)

    for _ in range(10000):
        sim_loop()

    #print(type_I_count, type_II_count, sent_count)
    typeIs.append(type_I_count)
    typeIIs.append(type_II_count)
    sent.append(sent_count - len(Trudy.outbox))
    windows.append(WINDOW)

f = open('linearRange.txt', 'w')
f.write("t1 <- c(")
f.write(str(typeIs).strip('[]'))
f.write(")\nt2 <- c(")
f.write(str(typeIIs).strip('[]'))
f.write(")\ns <- c(")
f.write(str(sent).strip('[]'))
f.write(")\nw<-c(")
f.write(str(windows).strip('[]'))
f.write(")")
f.close()
