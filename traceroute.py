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
import numpy

def escribir_trafico(ttl,src,rtt,f):
	print 'TTL:  %d' %ttl, '    IP Source: %s' %src, '    RTT: %sms' %rtt
	f.write('TTL:  %d' %ttl)
	f.write('    IP Source: %s' %src) 
	f.write('    RTT: %sms \n' %rtt)

def escribir_trafico_10(ttl,src,rtt,f):
	print 'TTL: %d' %ttl, '    IP Source: %s' %src, '    RTT: %sms' %rtt
	f.write('TTL: %d' %ttl)
	f.write('    IP Source: %s' %src) 
	f.write('    RTT: %sms \n' %rtt)

def escribir_time_out(ttl,f):
	print 'TTL:  %d' %ttl, '    Time Out!'
	f.write('TTL:  %d' %ttl) 
	f.write('    Time Out! \n')

def escribir_time_out_10(ttl,f):
	print 'TTL: %d' %ttl, '    Time Out!'
	f.write('TTL: %d' %ttl)
	f.write('    Time Out! \n')

def escribir_arreglo(array,f):
	for i in range(0,len(array)):
		f.write(str(array[i]))
		if i!= (len(array)-1):
			f.write(', ')
	f.write('\n')


def traceroute(host, timeLimit, maxhop, f):
	hayEchoReplay = False
	ttl = 1
	ruta_RTT = []

	while (not hayEchoReplay) and (maxhop > ttl-1):

		res = sr(IP(dst=host, ttl=ttl) / ICMP(), timeout = timeLimit, verbose = 0)
		if res[0]:
			rtt = res[0][0][1].time - res[0][0][0].sent_time
			ruta_RTT.insert(ttl-1,rtt)

			if res[0][0][1][1].type == 0:
				hayEchoReplay = True

			if ttl < 10:
				escribir_trafico(ttl,res[0][0][1][0].src,rtt,f)
			else:
				escribir_trafico_10(ttl,res[0][0][1][0].src,rtt,f)

		if res[1]:
			ruta_RTT.insert(ttl-1,0)

			if ttl < 10:
				escribir_time_out(ttl,f)
			else:
				escribir_time_out_10(ttl,f)
				
		ttl = ttl + 1

	return ruta_RTT


def prom_fila(matriz):
	prom_fila = []
	for i in range(0,len(matriz)):
		prom_fila_i = sum(matriz[i])/len(matriz[i])
		prom_fila.insert(i,prom_fila_i)
	return prom_fila

def prom_fila_con_0(matriz):
	prom_fila = []
	for i in range(0,len(matriz)):
		sum_fila = 0
		count = 0
		for j in range(0,len(matriz[i])):
			if matriz[i][j] != 0:
				count = count +1
			sum_fila = sum_fila + matriz[i][j]
		prom_fila.insert(i,sum_fila/count)
	return prom_fila

def prom_col(matriz):
	prom_col = []
	count = []
	for i in range(0,len(matriz)):
		for j in range(0,len(matriz[i])):
			if not existeIndice(j,prom_col):
				prom_col.insert(j,matriz[i][j])
				count.insert(j,1)
			else:
				prom_col[j] = matriz[i][j] + prom_col[j]
				count[j] = count[j]+1
	for j in range(0,len(prom_col)):
		prom_col[j] = prom_col[j]/count[j]
	return prom_col

def interpolar(matriz, a):
	for i in range(0, len(matriz)):
		for j in range(0,len(matriz[i])):
			if matriz[i][j] == 0:
				k = j+1
				while matriz[i][k] == 0:
					k = k+1
				l = j	
				while matriz[i][j] == 0: 
					matriz[i][j] = (matriz[i][l-1]+matriz[i][k])/2
					j = j+1

def calculator_delta(matriz):
	res = []
	for i in range(0, len(matriz)):
		res.insert(i, [])
		for j in range(0,len(matriz[i])):
			if j==0:
				res[i].insert(j, matriz[i][j])
			else:
				res[i].insert(j, matriz[i][j] - matriz[i][j-1])
	return res

def existeIndice(k, array):
	return k < len(array)

def varianza_matriz(matriz, array):
	var = []
	count = []
	for i in range(0,len(matriz)):
		for j in range(0,len(matriz[i])):
			if not existeIndice(j,var):
				var.insert(j,(matriz[i][j]-array[j])**2)
				count.insert(j,1)
			else:
				var[j] = var[j] + (matriz[i][j] - array[j])**2
				count[j] = count[j]+1
	for j in range(0,len(var)):
		if count[j] != 1:
			var[j] = var[j]/(count[j]-1)
	return var

def varianza_array(array, prom):
	res = 0
	for i in range(0, len(array)):
		res = res + (array[i]-prom)**2
	return res/(len(array)-1)


def desvio_estandar_array(V):
	for i in range(0,len(V)):
		V[i]= math.sqrt(V[i])
	return V

def grubbs_test_outliers(array, alpha):
	G = 0
	enlaces_submarinos = []
	saltos_submarinos = []
	hay_outliers = False
	index = -1
	N = len(array)
	media = sum(array)/N
	S = math.sqrt(varianza_array(array,media))
	########## T-Student ############
	t = stats.t.isf((1 - alpha)/(N), N-2)			#t = stats.t.isf(1 - alpha/(2*N), N-2) --> For the two-sided tests
	Gtest = (N-1)/numpy.sqrt(N) * numpy.sqrt(t**2 / (N-2+t**2))
	####### Calculator Grubbs #######
	for i in range(0,N):
		if Gtest < abs(array[i]-media)/S:
			saltos_submarinos.append(abs(array[i]-media)/S) 	#G = abs(array[i]-Prom)/S --> For the two-sided tests
			enlaces_submarinos.append(i+1)
			hay_outliers = True
	### Hipotesis de no outliers ####
	#hay_outliers = G > Gtest
	return saltos_submarinos, Gtest, enlaces_submarinos, hay_outliers



if __name__ == '__main__':

	if len(sys.argv) != 6:			# El programa tiene 5 argumentos de entrada
		raise AssertionError("\n\n # Se debe setear 5 argumentos de entrada.\n # Ejemplo: sudo python traceroute.py www.google.com 10 5 30 0.90\n # Si se quiere entender cada argumento, ver el codigo. En el mismo se indica detalladamente cada uno.\n")

	host = sys.argv[1]				# (1) Host para localizar la ruta (puede ser IP o una direccion web)
	timeLimit = int(sys.argv[2])	# (2) Tiempo limite para cortar la funcion de envio de paquetes a un nodo
	n = int(sys.argv[3])			# (3) Cantidad de corridas para trazar la ruta
	maxhop = int(sys.argv[4])		# (4) Cantidad de TTL maximo, en caso que no llegue a encontrar un echo-replay
	alpha = float(sys.argv[5])		# (5) Alpha para el test de hipotesis de Grubbs, sobre el t-student

	#### Abrimos archivo para copiar captura ####
	f = open ("captura.txt", "w")

	#### Escribo los parametros de entrada
	f.write("Parametros de entrada\n")
	f.write("Host: %s \n" %str(host))
	f.write("Tiempo Limite: %d \n" %timeLimit)
	f.write("Cant. Rutas: %d \n" %n)
	f.write("TTL Maximo: %d \n" %maxhop)
	f.write("Alpha: %f \n" %alpha)
	f.write('\n\n')


	######################################
	# Traceroute, RTT Prom (ejercicio A) #
	######################################

	matriz_RTT = []

	j = 0
	for i in range(0,n):
		os.system('cls' if os.name == 'nt' else 'clear')
		print 'Ruta Nro: %d \n' %(i+1)
		f.write('Ruta Nro: %d \n' %(i+1))
		f.write('\n')
		ruta  = traceroute(host, timeLimit, maxhop, f)
		f.write('\n\n')
		### Chqueo que no me den todos "time out". Si sucede, no tomo en cuenta dicha ruta
		if sum(ruta) != 0:
			matriz_RTT.insert(j, ruta)
			j = j+1
	
	prom_ruta = prom_fila_con_0(matriz_RTT)
	interpolar(matriz_RTT,prom_ruta)
	prom_RTT = prom_col(matriz_RTT)
	f.write('Promedio RTT: ') 
	escribir_arreglo(prom_RTT,f)
	f.write('\n')

	
	##############################
	# Estadisticas (ejercicio B) #
	##############################

	matriz_delta_RTT = calculator_delta(matriz_RTT)
	prom_delta_ruta = prom_fila(matriz_delta_RTT)
	prom_delta_RTT = prom_col(matriz_delta_RTT)
	f.write('Promedio Delta RTT: ') 
	escribir_arreglo(prom_delta_RTT,f)
	f.write('\n')

	ds_RTT = varianza_matriz(matriz_RTT,prom_RTT)
	ds_delta_RTT = varianza_matriz(matriz_delta_RTT, prom_delta_RTT)

	desvio_estandar_array(ds_RTT)
	desvio_estandar_array(ds_delta_RTT)
	f.write('Desvio Estandar Delta RTT: ') 
	escribir_arreglo(ds_delta_RTT,f)
	f.write('\n')


	##########################################
	# Test de Hipotesis Normal (ejercicio C) #
	##########################################

	os.system('cls' if os.name == 'nt' else 'clear')
	
	normalTest = stats.normaltest(prom_delta_RTT, axis=0)	
	if normalTest[1] > 0.055 :
		print 'Hay distribucion Normal\n'
		f.write('Hay distribucion Normal\n')
		f.write('\n')

	else:
		print 'No hay distribucion Normal\n'
		f.write('No hay distribucion Normal\n')
		f.write('\n')


	##########################################
	# Test de Hipotesis Grubbs (ejercicio D) #
	##########################################

	saltos_submarinos, Gtest, enlaces_submarinos, hay_outliers = grubbs_test_outliers(prom_delta_RTT, alpha)    

	if hay_outliers:
		print 'Hay outlier'
		f.write('Hay outlier\n')
		f.write('\n')
		print 'Enlaces submarinos: ', enlaces_submarinos
		f.write('Enlaces submarinos: ')
		escribir_arreglo(enlaces_submarinos,f)
		f.write('\n')
		print 'Valores de los saltos: ', saltos_submarinos
		f.write('Valores de los saltos: ')
		escribir_arreglo(saltos_submarinos,f)
		f.write('\n')
	else:
		print 'No hay outlier\n'
		f.write('No hay outlier\n')
		f.write('\n')


	#### Cerramos archivo ####
	f.close()

