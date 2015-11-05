#! /usr/bin/env python
import sys
import time
from scapy.all import *
import multiprocessing
import signal


if __name__ == '__main__':

	if len(sys.argv) != 1:
		assert("Error")

	h = sys.argv[0] #Duda
	ttl = 1
	hayEchoReplay = False

	while not(hayEchoReplay):
		t0 = time.time()
		res = sr(IP(dst='www.google.com', ttl=ttl) / ICMP())
		t1 = time.time()
		rtt = t1 - t0
		print(rtt)
		if res[0][0][1][1].type == 11:
			print(res[0][ICMP][0][1][0].src)
		if res[0][0][1][1].type == 0:
			hayEchoReplay = True
		ttl = ttl + 1

