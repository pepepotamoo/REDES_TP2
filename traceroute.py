#! /usr/bin/env python
from __future__ import with_statement # Required in 2.5
from contextlib import contextmanager
import sys, os
import time
from scapy.all import *
import signal
import math
import scipy.stats as stats



class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException, "Timed out!"
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

@contextmanager
def suppress_stdout():
	with open(os.devnull, "w") as devnull:
		old_stdout = sys.stdout
		sys.stdout = devnull
		try:  
			yield
		finally:
			sys.stdout = old_stdout


if __name__ == '__main__':

	if len(sys.argv) != 2:
		assert("Error")

	host = sys.argv[1]
	timeLimit = int(sys.argv[2]) 
	ttl = 1
	hayEchoReplay = False
	rttA = 0
	array = []

	while not(hayEchoReplay):

		try:
			with time_limit(timeLimit):
				with suppress_stdout():
					res = sr(IP(dst=host, ttl=ttl) / ICMP())
				TimeOut = False
		except TimeoutException, msg:
			TimeOut = True

		rtt = 0
		rtt2 = 0

		if not TimeOut:
			for i in range(0,10):
				with suppress_stdout():
					t0 = time.time()
					sr(IP(dst=host, ttl=ttl) / ICMP())
					t1 = time.time()
				rtt = rtt + t1-t0
				rtt2 = rtt2 + (t1-t0)**2
			rttSuma2Prom = rtt2/10
			rttProm = rtt/10
			array.append(rttProm-rttA)
			rttProm2 = rttProm**2
			varianza = rttSuma2Prom - rttProm2
			desvioStandar = math.sqrt(varianza)

			if res[0][0][1][1].type == 11:
				print 'TTL: %d' %ttl, '    RTT: %s' %rttProm, '		DS: %s' %desvioStandar, '		RTTResta: %s' %(rttProm-rttA), '    IP Source: %s' %res[0][ICMP][0][1][0].src
			if res[0][0][1][1].type == 0:
				hayEchoReplay = True
				print 'TTL: %d' %ttl, '    RTT: %s' %rttProm, '		DS: %s' %desvioStandar, '		RTTResta: %s' %(rttProm-rttA), '    IP Source: %s' %res[0][ICMP][0][1][0].src
			rttA = rttProm

		if TimeOut:
			print 'TTL: %d' %ttl, '    Time Out!'

		ttl = ttl + 1

	print stats.normaltest(array, axis=0)