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


def main():
	print("Init")
	mapasExtremos()

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

def mapasExtremos():
	"""
	Función que permite generar los mapas de eventos extremos
	"""
	# ********** fecha pronóstico
	fechaPronostico = '2017-12-21'
	# fechaPronostico = strftime("%Y-%m-%d")
	
	# ********** path
	# path server
	# path = "/home/jorge/Documents/work/autoPronosticoSonora"
	# os.chdir(path)
	# path local

	path = "/Users/jorgemauricio/Documents/Research/alermapweb"
	os.chdir(path)

	# ********** dict de análisis
	d = {"Rain" : ['20/50', '50/70', '70/150', '150/300', '300/500'], "Tmax":['30/35', '35/40', '40/45', '45/50', '50/60'], "Tmin" : ['-10/-3'], "Windpro" : ['62/74', '75/88', '89/102', '103/117', '118/150']}
	
	# generar fechas mediante función
	arrayFechas = generarFechas(fechaPronostico)

	# leer csv
	for j in range(1, 6, 1):
		pathFile = '{}/data/{}/d{}.txt'.format(path,fechaPronostico,j)
		data = pd.read_table(pathFile, sep=',')

		for key, value in d.items():
			for i in value:
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

				fig = plt.figure(figsize=(12,8))
				m = Basemap(projection='mill',llcrnrlat=12.37,urcrnrlat=33.5791,llcrnrlon=-118.2360,urcrnrlon=-86.1010,resolution='h')

				# generar xp
				xp = np.array(dataTemp['Long'])

				# generar yp
				yp = np.array(dataTemp['Lat'])

				# leer archivo shape Estados
				m.readshapefile('shapes/Estados', 'Estados')

				# agregar raster
				# m.bluemarble()

				# gráficar puntos
				m.scatter(xp, yp, latlon=True, s=3, marker='o', color='b', zorder=25, alpha=0.5)

				# titulo del mapa
				tituloTemporalMapa = generarTexto(arrayFechas[j-1], key, vMin, vMax)
				plt.title(tituloTemporalMapa)
				
				tituloTemporalArchivo = "{}/data/{}/{}_{}_{}_{}.png".format(path,fechaPronostico,arrayFechas[j-1],key,vMin, vMax)
				
				# crear anotación
				plt.annotate('@2017 INIFAP', xy=(-118,33), xycoords='figure fraction', xytext=(0.45,0.45), color='g')
				
				# guardar mapa
				plt.savefig(tituloTemporalArchivo, dpi=300)
				print('****** Genereate: {}'.format(tituloTemporalArchivo))


if __name__ == '__main__':
    main()
