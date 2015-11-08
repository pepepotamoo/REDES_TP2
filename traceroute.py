#! /usr/bin/env python
from __future__ import with_statement # Required in 2.5
from contextlib import contextmanager
import sys, os
import time
from scapy.all import *
import signal
import math
import scipy.stats as stats
import copy



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

def promedioFila(matriz):
	arrayPromFila = []
	for i in range(0,len(matriz)):
		promFila = 0
		for j in range(0,len(matriz[i])):
			promFila = promFila + matriz[i][j]
		arrayPromFila.insert(i,promFila/len(matriz[i]))
	return arrayPromFila

def promedioFilaCon0(matriz):
	arrayPromFila = []
	for i in range(0,len(matriz)):
		promFila = 0
		contador = 0
		for j in range(0,len(matriz[i])):
			if matriz[i][j] != 0:
				contador = contador +1
			promFila = promFila + matriz[i][j]
		arrayPromFila.insert(i,promFila/contador)
	return arrayPromFila

def promedioColumna(matriz):
	arrayPromColumna = []
	arrayContador = []
	for i in range(0,len(matriz)):
		for j in range(0,len(matriz[i])):
			if not existeIndice(j,arrayPromColumna):
				arrayPromColumna.insert(j,matriz[i][j])
				arrayContador.insert(j,1)
			else:
				arrayPromColumna[j] = matriz[i][j] + arrayPromColumna[j]
				arrayContador[j] = arrayContador[j]+1
	for j in range(0,len(arrayPromColumna)):
		arrayPromColumna[j] = arrayPromColumna[j]/arrayContador[j]
	return arrayPromColumna

def completarTimeOut(matriz, a):
	for i in range(0, len(matriz)):
		for j in range(0,len(matriz[i])):
			if matriz[i][j] == 0:
				matriz[i][j] = a[i]

def enlace(matriz):
	res = []
	for i in range(0, len(matriz)):
		res.insert(i, [])
		for j in range(0,len(matriz[i])):
			if j==0:
				res[i].insert(j, matriz[i][j])
			else:
				res[i].insert(j, matriz[i][j] - matriz[i][j-1])
	return res


def promedio(array, n):
	EX = []
	for i in range(0,len(array)):
		EX.append(array[i]/n)
	return EX

def existeIndice(k, array):
	return k < len(array)

def varianza(matriz, array):
	arrayColumna = []
	arrayContador = []
	for i in range(0,len(matriz)):
		for j in range(0,len(matriz[i])):
			if not existeIndice(j,arrayColumna):
				arrayColumna.insert(j,(matriz[i][j]-array[j])**2)
				arrayContador.insert(j,1)
			else:
				arrayColumna[j] = arrayColumna[j] + (matriz[i][j] - array[j])**2
				arrayContador[j] = arrayContador[j]+1
	for j in range(0,len(arrayPromColumna)):
		arrayPromColumna[j] = arrayPromColumna[j]/(arrayContador[j]-1)

	return arrayColumna

def desvioEstandar(V):
	for i in range(0,len(V)):
		V[i]= math.sqrt(V[i])
	return V

# def Grubbs(EXEnlace, EX):



if __name__ == '__main__':

	print len(sys.argv)
	if len(sys.argv) != 4:			# El programa tiene 3 argumentos de entrada
		raise AssertionError("\n\n # Se debe setear 3 argumentos de entrada.\n # Ejemplo: sudo python traceroute.py www.google.com 10 5\n # Si se quiere entender cada argumento, ver el codigo. En el mismo se indica detalladamente cada uno.\n")

	host = sys.argv[1]				# (1) Host para localizar la ruta (puede ser IP o una direccion web)
	timeLimit = int(sys.argv[2])	# (2) Tiempo limite para cortar la funcion de envio de paquetes a un nodo
	n = int(sys.argv[3])			# (3) Cantidad de corridas para trazar la ruta

	array = []
	matrizRTT = []

	for i in range(0,n):

		hayEchoReplay = False
		ttl = 1

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

			print 'rtt: %s' %rtt
			print ' '

			if not TimeOut:

			
				array.insert(ttl-1,rtt)
			
				if res[0][0][1][1].type == 11:
					print 'TTL: %d' %ttl, '    RTT: %s' %rtt, '    IP Source: %s' %res[0][ICMP][0][1][0].src
				if res[0][0][1][1].type == 0:
					hayEchoReplay = True
					print 'TTL: %d' %ttl, '    RTT: %s' %rtt, '    IP Source: %s' %res[0][ICMP][0][1][0].src

			if TimeOut:

				array.insert(ttl-1,0)

				print 'TTL: %d' %ttl, '    Time Out!'

			ttl = ttl + 1

		matrizRTT.insert(i,array)


	arrayPromFila = promedioFilaCon0(matrizRTT)
	completarTimeOut(matrizRTT,arrayPromFila)
	arrayPromColumna = promedioColumna(matrizRTT)
	arrayPromFila2 = promedioFila(matrizRTT)

	matrizEnlace = enlace(matrizRTT)

	arrayEnlacePromFila = promedioFila(matrizEnlace)
	arrayEnlacePromColumna = promedioColumna(matrizEnlace)



	# EX = promedio(array, n)						# Promedio comun (ejercicio A)
	# EX2 = promedio(array2, n)						# Promedio con la muestra elevada al cuadrado (para calcular la varianza)
	# EXEnlace = promedio(arrayEnlace, n)			# Promedio pero con RTT de cada enlace, o sea "RTT_{i} - RTT_{i-1}" (ejercicio B)
	#V = varianza(matrizRTT,arrayPromColumna)						# Varianza comun (ejercicio B)
	#V2 = varianza(matrizEnlace, arrayEnlacePromColumna)
	#desvioEstandar(V)						# Desvio Estandar comun (ejercicio B)
	#desvioEstandar(V2)
	# print EXEnlace		
	print stats.normaltest(arrayEnlacePromColumna, axis=0)	# Test de Hipotesis (ejercicio C)

	#G = Grubbs(EXEnlace, EX)


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
