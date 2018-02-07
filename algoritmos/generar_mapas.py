#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 08:38:15 2017

@author: jorgemauricio
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy.interpolate import griddata as gd
from time import gmtime, strftime
import time
import os
from time import gmtime, strftime
import ftplib
import shutil
import csv
import math
from api import claves

def main():
	print("Init")
	FECHA_PRONOSTICO = descargarInfo()
	mapasExtremos(FECHA_PRONOSTICO)

def descargarInfo():
	# datos del servidor
	serverInfo = claves()
	# conexión al server
	ftp = ftplib.FTP(serverInfo.ip)
	# login al servidor
	ftp.login(serverInfo.usr, serverInfo.pwd)
	# arreglo para determinar fecha
	arregloArchivos = []
	arregloFechas = []
	ftp.dir(arregloArchivos.append)
	for archivo in arregloArchivos:
	    arregloArchivo = archivo.split()
	    arregloFechas.append(arregloArchivo[8])
	FECHA_PRONOSTICO = arregloFechas[-1]
	rutaPronostico = "data/{}".format(FECHA_PRONOSTICO)
	ftp.cwd(FECHA_PRONOSTICO)
	# validar la ruta para guardar los datos
	if not os.path.exists(rutaPronostico):
		os.mkdir(rutaPronostico)
	else:
		print("***** Carpeta ya existe")
		rutaArchivoPronostico = f"{rutaPronostico}/d1.txt"
		if rutaArchivoPronostico:
			print("Archivo d1.txt existe")
		else:
			# descarga de información
			for i in range(1,6):
				rutaArchivoRemoto = "d{}.txt".format(i)
				rutaArchivoLocal = "{}/d{}.txt".format(rutaPronostico,i)
				lf = open(rutaArchivoLocal, "wb")
				ftp.retrbinary("RETR " + rutaArchivoRemoto, lf.write, 8*1024)
				lf.close()
			ftp.close()
	return FECHA_PRONOSTICO

def generarFechas(f):
	"""
	Función que permite generar una lista de fechas a partir del día actual
	param: f: fecha actual
	"""
	arrayF = []
	tanio, tmes, tdia = f.split('-')
	anio = int(tanio)
	mes = int(tmes)
	dia = int(tdia)

	dirAnio = anio
	dirMes = mes
	dirDia = dia

	# generar lista de fechas
	for i in range(0,5,1):
		if i == 0:
			newDiaString = '{}'.format(dia)
			if len(newDiaString) == 1:
				newDiaString = '0' + newDiaString
			newMesString = '{}'.format(mes)
			if len(newMesString) == 1:
				newMesString = '0' + newMesString
			fecha = '{}'.format(anio)+"-"+newMesString+"-"+newDiaString
			arrayF.append(fecha)
		if i > 0:
			dia = dia + 1
			if mes == 2 and anio % 4 == 0:
				diaEnElMes = 29
			elif mes == 2 and anio % 4 != 0:
				diaEnElMes = 28
			elif mes == 1 or mes == 3 or mes == 5 or mes == 7 or mes == 8 or mes == 10 or mes == 12:
				diaEnElMes = 31
			elif mes == 4 or mes == 6 or mes == 9 or mes == 11:
				diaEnElMes = 30
			if dia > diaEnElMes:
				mes = mes + 1
				dia = 1
			if mes > 12:
				anio = anio + 1
				mes = 1
			newDiaString = '{}'.format(dia)
			if len(newDiaString) == 1:
				newDiaString = '0' + newDiaString
			newMesString = '{}'.format(mes)
			if len(newMesString) == 1:
				newMesString = '0' + newMesString
			fecha = '{}'.format(anio)+"-"+newMesString+"-"+newDiaString
			arrayF.append(fecha)
	return arrayF


def generarTexto(f, k,vMn, vMx):
	"""
	Función que nos permite generar el texto correspondiente para cada mapa
	param: f: fecha
	param: k: nombre de la columna
	param: vMn: valor mínimo
	param: vMx: valor máximo
	"""
	titulo = ""
	if k == "Rain":
		titulo = "Precipitación acumulada en 24h {} a {} mm\n Pronóstico válido para: {}".format(vMn, vMx, f)
		return titulo
	elif k == "Tmax":
		titulo = "Temperatura máxima en 24h {} a {} ºC \n Pronóstico válido para: {}".format(vMn, vMx, f)
		return titulo
	elif k == "Tmin":
		titulo = "Temperatura mínima en 24h {} a {} ºC \n Pronóstico válido para: {}".format(vMn, vMx, f)
		return titulo
	elif k == "Windpro":
		titulo = "Viento promedio en 24h {} a {} km/h \n Pronóstico válido para: {}".format(vMn, vMx, f)
		return titulo
	else:
		pass

def colorPuntoEnMapa(variable,rango):
	"""
	Función que permite generar el color del putno que se va a mostrar en el mapa
	"""
	if variable == "Rain":
		if rango == "20/50":
			return 'aqua'
		elif rango == "50/70":
			return 'azure'
		elif rango == "70/150":
			return 'darkblue'
		elif rango == "150/300":
			return 'tomato'
		elif rango == "300/500":
			return 'crimson'

	if variable == "Tmax":
		if rango == "30/35":
			return 'coral'
		elif rango == "35/40":
			return 'orange'
		elif rango == "40/45":
			return 'crimson'
		elif rango == "45/50":
			return 'tomato'
		elif rango == "50/60":
			return 'maroon'

	if variable == "Tmin":
		if rango == "6/3":
			return 'powderblue'
		elif rango == "3/0":
			return 'lightskyblue'
		elif rango == "0/-3":
			return 'dodgerblue'
		elif rango == "-3/-6":
			return 'steelblue'
		elif rango == "-6/-9":
			return 'darkblue'

	if variable == "Windpro":
		if rango == "62/74":
			return 'gold'
		elif rango == "75/88":
			return 'sandybrown'
		elif rango == "89/102":
			return 'darksalmon'
		elif rango == "103/117":
			return 'darkorange'
		elif rango == "118/150":
			return 'maroon'


def mapasExtremos(fp):
	"""
	Función que permite generar los mapas de eventos extremos
	"""
	# ********** fecha pronóstico
	fechaPronostico = fp
	# fechaPronostico = strftime("%Y-%m-%d")

	# ********** path
	# path server
	# path = "/home/jorge/Documents/work/autoPronosticoSonora"
	# os.chdir(path)
	# path local


	# ********* Lat y Long
	LONG_MAX = -86.1010
	LONG_MIN = -118.2360
	LAT_MAX = 33.5791
	LAT_MIN = 12.37

	# ********** Path
	path = "/Users/jorgemauricio/Documents/Research/alermapweb"
	os.chdir(path)

	# ********** dict de análisis
	d = {"Rain" : ['20/50', '50/70', '70/150', '150/300', '300/500'], "Tmax":['30/35', '35/40', '40/45', '45/50', '50/60'], "Tmin" : ['6/3','3/0','0/-3','-3/-6','-6/-9'], "Windpro" : ['62/74', '75/88', '89/102', '103/117', '118/150']}

	# ********** array colores
	# generar fechas mediante función
	arrayFechas = generarFechas(fechaPronostico)

	# leer csv
	for j in range(1, 6, 1):
		pathFile = '{}/data/{}/d{}.txt'.format(path,fechaPronostico,j)
		data = pd.read_table(pathFile, sep=',')

		for key, value in d.items():
			for i in value:
				# comenzar con el proceso
				tiempoInicio = strftime("%Y-%m-%d %H:%M:%S")
				print("Empezar procesamiento {} {} tiempo: {}".format(key, i, tiempoInicio))

				# obtener rangos
				vMin, vMax = i.split('/')
				vMin = int(vMin)
				vMax = int(vMax)

				# título temporal de la columna a procesar
				tituloTemporalColumna = key
				dataTemp = data.loc[(data[tituloTemporalColumna] >= vMin) & (data[tituloTemporalColumna] <= vMax)]

				#obtener valores de x y y
				lons = np.array(dataTemp['Long'])
				lats = np.array(dataTemp['Lat'])

				#%% set up plot
				plt.clf()

				fig = plt.figure(figsize=(8,4))
				m = Basemap(projection='mill',llcrnrlat=LAT_MIN,urcrnrlat=LAT_MAX,llcrnrlon=LONG_MIN,urcrnrlon=LONG_MAX,resolution='h')

				# generar xp
				xp = np.array(dataTemp['Long'])

				# generar yp
				yp = np.array(dataTemp['Lat'])

				# leer archivo shape Estados
				m.readshapefile('shapes/Estados', 'Estados')

				# agregar raster
				# m.bluemarble()

				# gráficar puntos
				colorTemporalDelPunto = colorPuntoEnMapa(key, i)
				m.scatter(xp, yp, latlon=True, s=3, marker='o', color=colorTemporalDelPunto, zorder=25, alpha=0.5)

				# titulo del mapa
				tituloTemporalMapa = generarTexto(arrayFechas[j-1], key, vMin, vMax)
				plt.title(tituloTemporalMapa)

				tituloTemporalArchivo = "{}/data/{}/{}_{}_{}_{}.png".format(path,fechaPronostico,arrayFechas[j-1],key,vMin, vMax)

				# crear anotación
				latitudAnotacion = (LAT_MAX + LAT_MIN) / 2
				longitudAnotacion = (LONG_MAX + LONG_MIN) / 2
				plt.annotate('@2018 INIFAP', xy=(longitudAnotacion,latitudAnotacion), xycoords='figure fraction', xytext=(0.45,0.45), color='g')

				# guardar mapa
				plt.savefig(tituloTemporalArchivo, dpi=300)
				print('****** Genereate: {}'.format(tituloTemporalArchivo))

				# finalizar con el proceso
				tiempoFinal = strftime("%Y-%m-%d %H:%M:%S")
				print("Terminar procesamiento {} {} tiempo: {}".format(key, i, tiempoInicio))


if __name__ == '__main__':
    main()
