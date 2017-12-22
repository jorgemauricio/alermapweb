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


# fecha del pronóstico
#fechaPronostico = strftime("%Y-%m-%d")
fechaPronostico = '2017-12-21'

# generate arrayFechas
# Generate Days
arrayFechas = []
tanio, tmes, tdia = fechaPronostico.split('-')
anio = int(tanio)
mes = int(tmes)
dia = int(tdia)

dirAnio = anio
dirMes = mes
dirDia = dia

#%% generate arrayFechas

for i in range(0,5,1):
	if i == 0:
		newDiaString = '{}'.format(dia)
		if len(newDiaString) == 1:
			newDiaString = '0' + newDiaString
		newMesString = '{}'.format(mes)
		if len(newMesString) == 1:
			newMesString = '0' + newMesString
		fecha = '{}'.format(anio)+"-"+newMesString+"-"+newDiaString
		arrayFechas.append(fecha)
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
		arrayFechas.append(fecha)

# path server
# os.chdir("/home/jorge/Documents/work/autoPronosticoSonora")
# path local
os.chdir("/Users/jorgemauricio/Documents/Research/alermapweb")

# leer csv's
pathFile1 = '/Users/jorgemauricio/Documents/Research/alermapweb/data/{}/d1.txt'.format(fechaPronostico)
pathFile2 = '/Users/jorgemauricio/Documents/Research/alermapweb/data/{}/d2.txt'.format(fechaPronostico)
pathFile3 = '/Users/jorgemauricio/Documents/Research/alermapweb/data/{}/d3.txt'.format(fechaPronostico)
pathFile4 = '/Users/jorgemauricio/Documents/Research/alermapweb/data/{}/d4.txt'.format(fechaPronostico)
pathFile5 = '/Users/jorgemauricio/Documents/Research/alermapweb/data/{}/d5.txt'.format(fechaPronostico)

# crear data frames
data1 = pd.read_table(pathFile1, sep=',')
data2 = pd.read_table(pathFile2, sep=',')
data3 = pd.read_table(pathFile3, sep=',')
data4 = pd.read_table(pathFile4, sep=',')
data5 = pd.read_table(pathFile5, sep=',')

# crear un solo data frame
data = data1.filter(items=['Long', 'Lat','Tmin'])
data['Tmin1'] = data1['Tmin']
data['Tmin2'] = data2['Tmin']
data['Tmin3'] = data3['Tmin']
data['Tmin4'] = data4['Tmin']
data['Tmin5'] = data5['Tmin']

# ciclo para valores diarios
counterFecha = 0
for i in range(1,6,1):

	# título temporal de columna
	tempTitleColumn = "Tmin{}".format(i)
	dataTemp = data.loc[(data[tempTitleColumn] >= 0) & (data[tempTitleColumn] <= 10)]

	print(dataTemp.info())
	print(dataTemp.max())
	print(dataTemp.min())

	#obtener valores de x y y
	lons = np.array(dataTemp['Long'])
	lats = np.array(dataTemp['Lat'])

	#%% set up plot
	plt.clf()

	#fig = plt.figure(figsize=(48,24))
	m = Basemap(projection='mill',llcrnrlat=12.37,urcrnrlat=33.5791,llcrnrlon=-118.2360,urcrnrlon=-86.1010,resolution='h')

	#%% generate lats, lons
	x, y = m(lons,lats)

	#%% number of cols and rows
	numcols = len(x)
	numrows = len(y)
	print(numcols, numrows)

	#%% generate xi, yi
	xi = np.linspace(x.min(), x.max(), numcols)
	yi = np.linspace(y.min(), y.max(), numrows)

	#%% generate meshgrid
	xi, yi = np.meshgrid(xi,yi)

	# generar zi
	z = np.array(dataTemp[tempTitleColumn])

	print('***** print z',z)
	zi = gd((x,y), z, (xi,yi), method='cubic')

	#generate clevs
	clevs = np.linspace(z.min(), z.max(), 10)
	#clevs = [1, 5, 10,15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
	
	#%% contour plot
	cs = m.contourf(xi,yi,zi, clevs, zorder=4, alpha=0.6, cmap='inferno_r')
	#%% draw map details
	#m.drawcoastlines()
	#m.drawstates(linewidth=0.7)
	#m.drawcountries()
	#%% read municipios shape file
	m.readshapefile('shapes/Estados', 'Estados')
	#m.readshapefile('shapes/Estados', 'Estados')
	#m.drawmapscale(22, -103, 23, -102, 100, units='km', fontsize=14, yoffset=None, barstyle='fancy', labelstyle='simple', fillcolor1='w', fillcolor2='#000000',fontcolor='#000000', zorder=5)

	#%% colorbar
	cbar = m.colorbar(cs, location='right', pad="5%")
	cbar.set_label('mm')
	tempMapTitle = "Temperatura mínima 24h\nPronóstico válido para: {}".format(arrayFechas[counterFecha])
	plt.title(tempMapTitle)
	tempFileName = "/Users/jorgemauricio/Documents/Research/alermapweb/data/{}/{}.png".format(fechaPronostico,i)
	plt.annotate('@2017 INIFAP', xy=(-118,33), xycoords='figure fraction', xytext=(0.45,0.45), color='g')
	plt.savefig(tempFileName, dpi=300)
	counterFecha += 1
	print('****** Genereate: {}'.format(tempFileName))
