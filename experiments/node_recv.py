import socket
import argparse
import pickle
from threading import Thread
import numpy as np

START_PORT = 9000

parser = argparse.ArgumentParser()
parser.add_argument('-i', dest='ip', default='')
parser.add_argument('-g', dest='group_id', type=int)
parser.add_argument('-d', dest='receiver_index', type=int)
parser.add_argument('-m', dest='member', type=int)

args = parser.parse_args()


# class ReceiverThread(Thread):
#     def __init__(self, sock):
#         super(ReceiverThread, self).__init__()
#         self.message = b''
#         self.s = sock
#
#     def run(self):
#         while True:
#             data, addr = self.s.recvfrom(102400)
#             print(f'received :{data}')
#             self.message = data
#             np.save(f'message/rec_obs_{addr}', np.fromstring(data, np.float32))
#             break
#             # f.write("%s: %s\n" % (addr, data))
#             # f.flush()
#
#     def get_obs(self):
#         return self.message


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('start to bind port')
s.bind((args.ip, START_PORT + args.receiver_index))

message = b''
print('ready to receive data.')
while True:
    data, addr = s.recvfrom(1024)
    print('perform receive once.')
    message += data
    with open(f'shared_buffer/message_received/msg_from_agent_{args.receiver_index}', 'w') as f:
        f.write('%s' % np.fromstring(message, dtype=np.float32))
    break

print('receive ok.')



