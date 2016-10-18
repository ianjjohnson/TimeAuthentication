from Crypto.Cipher import AES

system_time = 0
JITTER = 0

N_0 = 123456789
K   = 987654321

E   = AES.new(K, AES.MODE_CBC, N_0)
