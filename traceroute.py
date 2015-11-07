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

def esperanza(array, n):
	EX = []
	for i in range(0,len(array)):
		EX.append(array[i]/n)
	return EX

def varianza(EX2, EX):
	VX = []
	E2X = []
	for i in range(0,len(EX)):
		E2X.append(EX[i]**2)
	for i in range(0,len(EX)):
		VX.append(EX2[i] - E2X[i])
	return VX

def desvioEstandar(VX):
	DS = []
	for i in range(0,len(VX)):
		DS.append(math.sqrt(VX[i]))
	return DS



if __name__ == '__main__':

	print len(sys.argv)
	if len(sys.argv) != 4:			# El programa tiene 3 argumentos de entrada
		raise AssertionError("\n\n # Se debe setear 3 argumentos de entrada.\n # Ejemplo: sudo python traceroute.py www.google.com 10 5\n # Si se quiere entender cada argumento, ver el codigo. En el mismo se indica detalladamente cada uno.\n")

	host = sys.argv[1]				# (1) Host para localizar la ruta (puede ser IP o una direccion web)
	timeLimit = int(sys.argv[2])	# (2) Tiempo limite para cortar la funcion de envio de paquetes a un nodo
	n = int(sys.argv[3])			# (3) Cantidad de corridas para trazar la ruta

	array = []
	array2 = []
	arrayEnlace = []

	for i in range(0,n):

		hayEchoReplay = False
		ttl = 1
		rttA = 0 		# rtt Anterior

		print ' '
		print 'Ruta Nro: %d' %(i+1)
		print ' '

		while not(hayEchoReplay):

			try:
				with time_limit(timeLimit):
					with suppress_stdout():
						t0 = time.time()
						res = sr(IP(dst=host, ttl=ttl) / ICMP())
						t1 = time.time()
					rtt = t1 - t0
					TimeOut = False
			except TimeoutException, msg:
				TimeOut = True


			print ' '

			if not TimeOut:

				if len(array) < ttl:
					array.insert(ttl-1,rtt)
					array2.insert(ttl-1,rtt**2)
					arrayEnlace.insert(ttl-1,rtt-rttA)
				else:
					array.insert(ttl-1,array[ttl-1] + rtt)
					array2.insert(ttl-1,array[ttl-1] + rtt**2)
					arrayEnlace.insert(ttl-1,array[ttl-1] + rtt-rttA)
				
				if res[0][0][1][1].type == 11:
					print 'TTL: %d' %ttl, '    RTT: %s' %rtt, '    IP Source: %s' %res[0][ICMP][0][1][0].src
				if res[0][0][1][1].type == 0:
					hayEchoReplay = True
					print 'TTL: %d' %ttl, '    RTT: %s' %rtt, '    IP Source: %s' %res[0][ICMP][0][1][0].src

			if TimeOut:

				if len(array) < ttl:
					array.insert(ttl-1,0)
					array2.insert(ttl-1,0)
					arrayEnlace.insert(ttl-1,0-rttA)
				else:
					array.insert(ttl-1,array[ttl-1] + 0)
					array2.insert(ttl-1,array[ttl-1] + 0)
					arrayEnlace.insert(ttl-1,array[ttl-1] + 0-rttA)

				print 'TTL: %d' %ttl, '    Time Out!'

			ttl = ttl + 1
			rttA = rtt

	EX = esperanza(array, n)						# Esperanza comun (ejercicio A)
	EX2 = esperanza(array2, n)						# Esperanza con la muestra elevada al cuadrado (para calcular la varianza)
	EXEnlace = esperanza(arrayEnlace, n)			# Esperanza pero con RTT de cada enlace, o sea "RTT_{i} - RTT_{i-1}" (ejercicio B)
	VX = varianza(EX2,EX)						# Varianza comun (ejercicio B)
	DS = desvioEstandar(VX)						# Desvio Estandar comun (ejercicio B)
	print stats.normaltest(EXEnlace, axis=0)	# Test de Hipotesis (ejercicio C)


#for i in range(0,1):
#				with suppress_stdout():
#					t0 = time.time()
#					sr(IP(dst=host, ttl=ttl) / ICMP())
#					t1 = time.time()
#				rtt = rtt + t1-t0
#				rtt2 = rtt2 + (t1-t0)**2
#			EX = rtt/1					#Esperanza E(X) --- rttPromedio
#			EX2 = rtt2/1				#E(X^2)
#			E2X = EX**2					#(E(X))^2
#			VX = E2X - EX2				#Varianza V(X)
#			DS = math.sqrt(VX)			#Desvio Estandar
#			array.append(EX-EXA)		#Guardo en un arreglo los tiempos (promedios) de cada enlace. Por es la resta de la esperanza nueva con respecto a la anterior 
