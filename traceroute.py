#! /usr/bin/env python
from __future__ import with_statement # Required in 2.5
from contextlib import contextmanager
import sys, os
import time
from scapy.all import *
import signal


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

	if len(sys.argv) != 1:
		assert("Error")

	host = sys.argv[1]
	ttl = 1
	hayEchoReplay = False

	while not(hayEchoReplay):

		try:
			with time_limit(5):
				with suppress_stdout():
					t0 = time.time()
					res = sr(IP(dst=host, ttl=ttl) / ICMP())
					t1 = time.time()
					rtt = t1 - t0
				TimeOut = False
		except TimeoutException, msg:
			TimeOut = True

		if not TimeOut:
			if res[0][0][1][1].type == 11:
				print 'TTL: %d' %ttl, '    RTT: %s' %rtt, '    IP Source: %s' %res[0][ICMP][0][1][0].src
			if res[0][0][1][1].type == 0:
				hayEchoReplay = True
				print 'TTL: %d' %ttl, '    RTT: %s' %rtt, '    IP Source: %s' %res[0][ICMP][0][1][0].src

		if TimeOut:
			print 'TTL: %d' %ttl, '    Time Out!'

		ttl = ttl + 1