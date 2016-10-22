from Crypto.Cipher import AES
import time

JITTER = 0
WINDOW = 0
TIME_SLOTS = 1000

N_0 = '1234567890123456'
K   = '9876543210123456'

E   = AES.new(K, AES.MODE_CFB, N_0)
delays = []


ni = N_0
for _ in range(10000):
    ni = E.encrypt(ni)
    delays.append(int.from_bytes(ni, byteorder="little") % TIME_SLOTS)


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
        self.warningResponse = t + delay + nextDelay/2
        response = Message(self, sender, t + (delay/2 if danger else delay), message)
        self.outbox.append(response)

    def addMessage(self, m):
        self.inbox.append(m)

    def handleMessage(self, m):
        print(self.name, "got message: ", m.content)


        t = (self.time-1 if (self.name == "Alice" and m.content != "Startup") else self.time)

        if(t == self.expectedResponse):
            print("Authenticated")
            self.sendReply(m.sender, t=self.expectedResponse)
        elif(t == self.warningResponse):
            print("Danger Will Robinson")
            self.sendReply(m.sender, t=self.expectedResponse, message="DWR")
        else:
            print("Bad Message")
            print(t, self.expectedResponse)
            self.sendReply(m.sender, t=self.expectedResponse, message="Bad")#, danger=True)


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


Alice = Client("Alice")
Bob = Client("Bob")

Trudy = Client("Trudy")

Alice.inbox.append(Message(Bob, Alice, 0, "Startup"))
Bob.expectedResponse = Bob.next_delay()


def sim_loop():

    Alice.update()
    Bob.update()

while(True):
    time.sleep(0.01)
    sim_loop()
