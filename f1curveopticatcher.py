# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 00:13:57 2026

@author: GIO
"""

import duckdb
import fastf1
import pandas as pd
import matplotlib.pyplot as plt

curvas=['C1','C2','C3','C4','C5','C6','C7','C8','C9','C10','C11','C12','C13','C14','C15','C16']
dtcur={}
trayectoria={}
lapnum=[]
j=0
i=0
fastf1.Cache.enable_cache('C:/Users/GIO/ETL')

session = fastf1.get_session(2022, 'Silverstone', 'R')
session.load(laps=True, telemetry=True, weather=False)
laps = session.laps
driver_laps = laps.pick_drivers('PER').reset_index(drop=True)
print(f"Total de vueltas: {len(driver_laps)}")

# Lista para acumular la telemetría de todas las vueltas
all_telemetry = []
masa = 798
for _, lap in driver_laps.iterrows():
    try:
        tel = lap.get_telemetry().add_distance()
        tel['Velocidad_ms'] = tel['Speed'] / 3.6
        tel['Energia_cinetica_J'] = 0.5 * masa * tel['Velocidad_ms']**2
        tel['LapNumber'] = lap['LapNumber']     
       
        all_telemetry.append(tel[['LapNumber', 'Energia_cinetica_J','Distance','X','Y']])
        
    except Exception as e:
        print(f"Vuelta {lap['LapNumber']} sin telemetría: {e}")

full_telemetry = pd.concat(all_telemetry, ignore_index=True)
circuit_info = session.get_circuit_info()
corners = circuit_info.corners

def asignar_curva(distancia, corners):
    for _, corner in corners.iterrows():
        # Si la distancia está cerca del inicio de la curva
        if abs(distancia - corner['Distance']) < 100:  # margen de 100m
            return f"C{corner['Number']}"
    return 'Recta'

full_telemetry['Curva'] = full_telemetry['Distance'].apply(lambda d: asignar_curva(d, corners))
# buscar y elimninar outliers
q1 = full_telemetry['Energia_cinetica_J'].quantile(0.25)
q3 = full_telemetry['Energia_cinetica_J'].quantile(0.75)
IQR=q3-q1
higher=q3+1.5*(IQR)
lower=q1-1.5*(IQR)
df_sin_outliers = full_telemetry[
    (full_telemetry['Energia_cinetica_J'] >= lower) &
    (full_telemetry['Energia_cinetica_J']  <= higher)
    ]

#extraer datos por numero de curva
for curva in curvas:

    dtcur[curva] = full_telemetry[full_telemetry['Curva'] == curva]

# agrupar dataframe por numero de vuelta y obtener el numero de vuelta con la curva que mejor conserva la energia del auto
for nombre, dtf in dtcur.items():
    newdtf=dtf.groupby('LapNumber')['Energia_cinetica_J'].mean().reset_index()
    lapnum.append(newdtf['Energia_cinetica_J'].idxmax())
# obtener datos de telemetria de la  curva en la vuelta especifica
for cruva ,lap in zip(curvas,lapnum):
        trayectoria[cruva]=full_telemetry[(full_telemetry['Curva'] == cruva) & (full_telemetry['LapNumber'] == lap)]
# graficar coordenadas obtenidas
for name, coords in trayectoria.items():
    plt.plot(coords['X'],coords['Y'])
    plt.axis('equal')
plt.show()

