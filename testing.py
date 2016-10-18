from Crypto.Cipher import AES

system_time = 0
JITTER = 0

N_0 = '1234567890123456'
K   = '9876543210123456'

E   = AES.new(K, AES.MODE_CBC, N_0)

class Message:

    def __init__(self, sender, recipient, arrival, content):
        self.sender = sender
        self.recipient = recipient
        self.arrival = arrival
        self.content = content

class Client:

    def __init__(self, name):
        self.inbox = []
        self.expectedTime = 0
        self.name = name

    def messagesForTime(self, t):
        ls = []
        for msg in self.inbox:
            if msg.arrival == t:
                ls.append(msg)
        return ls

    def sendReply(self, m):
        response = Message(self, m.sender, 0, "Ping")
        m.sender.addMessage(response)

    def addMessage(self, m):
        self.inbox.append(m)

    def handleMessage(self, m):
        print(m.recipient.name, "got message: ")
        print(m.content)
        self.sendReply(m)

    def checkForMessage(self, time):
        messages = self.messagesForTime(time)
        for m in messages:
            self.handleMessage(m)

def sim_loop():
    Alice.checkForMessage(system_time)
    Bob.checkForMessage(system_time)


Alice = Client("Alice")
Bob = Client("Bob")
Alice.addMessage(Message(Bob, Alice, 0, "Ping"))

while(True):
    sim_loop()
