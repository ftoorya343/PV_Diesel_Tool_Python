# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 16:58:11 2018

@author: Jacky
"""

#Input parameters

from BatterySize import BatteriesInSeries, BatteriesInParallel
CellCapacity=210
NumbersOfCellsInOneBattery=6
CellNominalVoltage=2




#Output parameters
arrayAh=BatteriesInParallel*CellCapacity
maxChargeCurrent=arrayAh*2
maxDischargeCurrent=arrayAh*2
maxVoltage=2.45*(BatteriesInSeries*NumbersOfCellsInOneBattery)
minVoltage=1.7*(BatteriesInSeries*NumbersOfCellsInOneBattery)
MaximalBatterySOC=0.95
MinimalBatterySOC=0.36
numSeries=NumbersOfCellsInOneBattery*BatteriesInSeries
totalV=CellNominalVoltage*(NumbersOfCellsInOneBattery*BatteriesInSeries)
arrayWh=CellNominalVoltage*(NumbersOfCellsInOneBattery*BatteriesInSeries)*arrayAh
numParallel=1*BatteriesInParallel
#Dictionary an dieser Stelle sinnvoll?
parameters={"arrayAh" : arrayAh}


#print
print("arrayAh= ", arrayAh)
print("maxChargeCurrent= ",maxChargeCurrent)
print("maxDischargeCurrent= ",maxDischargeCurrent)
print("maxVoltage= ",maxVoltage)
print("minVoltage= ",minVoltage)
print("MaximalBatterySOC= ",MaximalBatterySOC)
print("MinimalBatterySOC= ",MinimalBatterySOC)
print("numSeries= ",numSeries)
print("numParallel= ",numParallel)
print("totalV= ",totalV)
print("arrayWh= ",arrayWh)