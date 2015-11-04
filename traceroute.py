#! /usr/bin/env python

if __name__ == '__main__':

	h = '157.92.27.21'
	ttl = 1
	answer = null

	while answer != 'Echo Reply':
		res = sr(IP(dst=h, ttl=ttl) / ICMP())
		if res.type = 'Time Exceede':
			print(res.IP)
		ttl = ttl + 1
		answer = res

