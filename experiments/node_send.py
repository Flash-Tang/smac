import socket
import argparse
import pickle
import numpy as np


START_PORT = 9000

parser = argparse.ArgumentParser()
parser.add_argument('-i', dest='ip', default='')
parser.add_argument('-d', dest='agent', type=int)
parser.add_argument('-m', dest='message', default=b'hello')

args = parser.parse_args()

obs = np.load(f'shared_buffer/message_to_sent/agent_{args.agent}_obs.npy')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(obs.tostring(), (args.ip, START_PORT + args.agent))
print('[node_send send ok.]')
s.close()
