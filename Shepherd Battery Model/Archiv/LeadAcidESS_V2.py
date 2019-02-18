# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 21:04:46 2018

@author: Jacky
"""

#PowerfromEMS powerIn=? bzw. Pin
from BatterySize import BatteriesInSeries, BatteriesInParallel
from Parameters import MaximalBatterySOC, MinimalBatterySOC
from scipy.integrate import quad
Pin=-8245#aus EMS?
Vin=50.5246336650568#aus EMS? #Zeitpunkt 0
SOC=0.874 #Zeitpunkt 0
c=MaximalBatterySOC-MinimalBatterySOC

#BatteryController 
from BatteryModelParametersOfTheMasterThesisByEvandroDresch import riCell
from Parameters import maxChargeCurrent,\
maxVoltage,\
MaximalBatterySOC, \
MinimalBatterySOC, \
numSeries,\
numParallel,\
minVoltage, \
maxDischargeCurrent,\
totalV

currentIn=Pin/Vin
#powerIn/voltageIn

#% Check SOC and if the battery can be charged/discharged

if SOC<MaximalBatterySOC:
    canCharge=1
else:
    canCharge=0

if SOC>MinimalBatterySOC:
    canDischarge=1
else:
    canDischarge=0
    
#first set currentOut to currentIn
currentOut = currentIn

#if there is a positive Current but you can't charge or 
#'there is a negative Current but you can't discharge 
# set currentOut to zero

if currentOut>0 and canCharge==0 or currentOut<0 and canDischarge==0:  
   currentOut=0 
    
#Current on each string:  
currentOut=currentOut/numParallel

# Final Check if currentOut to high respectively to low
if currentOut>maxChargeCurrent:
    currentOut=maxChargeCurrent
elif currentOut<-maxChargeCurrent:
    currentOut=np.sign(currentIn)*maxDischargeCurrent

Vout=Vin+currentOut*riCell*numSeries/numParallel

#Check if Voltage doesn't exceeds max. or min. limits
if abs(Vin)>maxVoltage:
    Vout=minVoltage
elif abs(Vout)<minVoltage:
    voltageOut=minVoltage

#print
print("Vout= ",Vout)
print("currentOut= ",currentOut)
print("currentIn= ",currentIn)
print("Vin= ",Vin)

#VoltageControlledBatteryModule
Vin=Vout
print("neuesVin= ",Vin)

from Parameters import arrayAh




#Zeitpunkt 0, Startwert
Ah=1640


    

        #ControlledVoltageSource
import math as m
from BatteryModelParametersOfTheMasterThesisByEvandroDresch import B, K, E0, A
from Parameters import arrayAh, maxVoltage, minVoltage, numParallel


#sum
#1
sum1=A*m.exp(-B*Ah/numParallel)
sum2=K*(arrayAh/numParallel)/(arrayAh/numParallel-Ah/numParallel)

#Output
E=E0-sum2+sum1

print("E= ",E)



   
        #BatteryEquotation
Iout=((Vin-E)/riCell)*numParallel
print("Iout= ",Iout)
print("Vin= ",Vin)
print("No load Voltage= ",E)




    #Iout

from Parameters import numParallel
from BatteryModelParametersOfTheMasterThesisByEvandroDresch import riCell


Iout=((Vin-E)/riCell)*numParallel
print("Iout= ",Iout)
print("Vin= ",Vin)

    #Pbatt
Pbatt=Vin*Iout
print("Pbatt= ",Pbatt)

#Ah
EinsMinusSOC0=0.6 #1-SOC0
stepsize=15
In=(-stepsize/60)*Iout
IC=arrayAh*EinsMinusSOC0    
        #Integrator
if IC >=0 and IC<arrayAh:
    Out=In+1640#In(t-1)
Ah=Out #Unit Delay External IC


#SOC
SOC=-(Out/arrayAh)+1
print("SOC= ",SOC)




    
    #cycles
#if SOC(t-1)-SOC>0
   # Cycles=(SOC(t-1)-SOC)/c
   # else Cycles=0
    #print
#print("Iout= ",Iout)