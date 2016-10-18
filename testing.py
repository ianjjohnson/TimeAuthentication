from Crypto.Cipher import AES

JITTER = 0

N_0 = '1234567890123456'
K   = '9876543210123456'

E   = AES.new(K, AES.MODE_OFB, N_0)


class Message:

    def __init__(self, sender, recipient, arrival, content, malicious=False):
        self.sender = sender
        self.recipient = recipient
        self.arrival = arrival
        self.content = content
        self.malicious = malicious

class Client:

    def __init__(self, name, key, n_not):
        self.inbox = []
        self.outbox = []
        self.name = name
        self.E = AES.new(key, AES.MODE_CBC, n_not)
        self.stream = self.E.encrypt(n_not)
        self.expectedResponse = 0
        self.warningResponse  = 0
        self.time = 0

    def next_delay(self):
        self.stream = E.encrypt(self.stream)
        return int.from_bytes(self.stream, byteorder="little") % 128

    def sendReply(self, m, t = -1, danger = False):
        if t == -1:
            t = self.time
        delay = self.next_delay()
        nextDelay = self.next_delay()
        self.expectedResponse = t + delay + nextDelay
        self.warningResponse = t + delay + nextDelay/2
        response = Message(self, m.sender, t + (delay/2 if danger else delay), "Ping")
        self.outbox.append(response)

    def addMessage(self, m):
        self.inbox.append(m)

    def handleMessage(self, m):
        print(m.recipient.name, "got message: ")
        print(m.content)

        if(self.time == self.expectedResponse):
            print("Authenticated")
            self.sendReply(m)
        elif(self.time == self.warningResponse):
            print("Danger Will Robinson")
            self.sendReply(m, self.expectedResponse)
        else:
            print("Bad Message")
            self.sendReply(m, self.expectedResponse, True)


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

    Alice.update()
    Bob.update()


Alice = Client("Alice", N_0, K)
Bob = Client("Bob", N_0, K)
Alice.addMessage(Message(Bob, Alice, 0, "Ping"))

while(True):
    sim_loop()
