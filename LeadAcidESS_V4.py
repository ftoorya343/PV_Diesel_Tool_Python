# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 21:04:46 2018

@author: Jacky
"""

#PowerfromEMS powerIn=? bzw. Pin
from BatterySize import BatteriesInSeries, BatteriesInParallel
from Parameters import upperSOC, lowerSOC
from scipy.integrate import quad
from BatteryModelParametersOfTheMasterThesisByEvandroDresch import riCell
from Parameters import maxChargeCurrent,\
maxVoltage,\
upperSOC, \
lowerSOC, \
numSeries,\
numParallel,\
minVoltage, \
maxDischargeCurrent,\
totalV
from Parameters import arrayAh
import math as m
from BatteryModelParametersOfTheMasterThesisByEvandroDresch import B, K, E0, A
from Parameters import arrayAh, maxVoltage, minVoltage, numParallel
from Parameters import numParallel
from BatteryModelParametersOfTheMasterThesisByEvandroDresch import riCell

Cycles_int=0
Out=7812
Ah=7812 #Anfangswert#Delay VoltageControlledBatteryModule#Integrator
In_int=7812 #Anfangswert
Pin_dict={1:-6025.7695044,2:-4961.997512,3:-3898.2255196,4:-3959.2358836,5:-6141.7098788,6:-5338.8784892,7:-4024.707396,8:-4564.3578832,9:-3819.474184,10:-2555.895928}#aus EMS?
#Vin=50.127804511278#aus EMS? #Zeitpunkt 0
SOC=0.400000000 #Zeitpunkt 0
c=upperSOC-lowerSOC

#for-Schleife
for time,Pin in Pin_dict.items():
    print("__________________________________________________")
    print("for time{}:Pin={}".format(time,Pin))
    #Vin berechnen für Battery Controller
    sum1=A*m.exp(-B*Ah/numParallel)
    sum2=K*(arrayAh/numParallel)/(arrayAh/numParallel-Ah/numParallel)
    E=E0-sum2+sum1
    Vin=E
    
    print("Vin= ",Vin)

#BatteryController 


    currentIn=Pin/Vin
    
#powerIn/voltageIn

#% Check SOC and if the battery can be charged/discharged

    if SOC<upperSOC:
        canCharge=1
    else:
        canCharge=0

    if SOC>lowerSOC:
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
    

#VoltageControlledBatteryModule
    Vin=Vout
       



   
        #BatteryEquotation
    Iout=((Vin-E)/riCell)*numParallel
    print("Iout= ",Iout)
    print("Vin= ",Vin)
    print("No load Voltage= ",E)




    #Iout




    Iout=((Vin-E)/riCell)*numParallel
    print("Iout= ",Iout)
   

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
        Out=In+Out
        Ah=Out
        
     #In(t-1)
         #Unit Delay External IC

    #cycles
    Cycles=Cycles_int
    
    
    if SOC+((Out/arrayAh)+1)>0:
        Cycles_int=Cycles+(SOC-(-(Out/arrayAh)+1))/c
    else: 
        Cycles_int=Cycles+0
    print("Cycles= ", Cycles)

#SOC
    SOC=-(Out/arrayAh)+1
    print("SOC= ",SOC)


    
  
  
    
   
    
else:
    print("BatteryDead")