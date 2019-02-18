# -*- coding: utf-8 -*-
"""
Created on Sat Dec  8 21:07:34 2018

@author: Jacky
"""

#function [gensetStatusOut,...
 #         gensetFuelConsumption] = gensetManager(gensetStatusIn,...
  #                                               gensetPar,...
   #                                              previousStatus)  Was bewirkt das in Matlab bzw C++?

## FUNCTION DESCRIPTION (TO BE UPDATED):

# Diesel genset management and calculation of fuel consumption
#
# Syntax
#   [pvPout, batteryPout, dslPout] = dispatchStrategy1(pvPin, load, dslData, batteryData)
#

# Input Parameters:

# gensetStatusIn - Matrix with four rows and n columns, where n is the
# number of installed generators. The first row defines the actual status
# of the generator (on/off), the second row is the actual loading of the
# genset, the third row is the actual running time in hours and the last
# row is the total running time of the genset in hours.

# Output:
#   IL - Light-generated current in amperes at irradiance=S and


#for Python:
import numpy as np
global STEPSIZE #Variable als Global definiert?
from scipy import interpolate
import matplotlib.pyplot as plt
STEPSIZE=15

gensetPar=np.array([[32.1,50,0,"nan",4.6,6.5,10.2,0],
           [29.2,30,0,"nan",4.6,6.5,8.9,0],
           [11.9,30,0,"nan",2.34,3.22,4.27,2],
           [4.6,30,0,"nan",0.96,1.32,1.75,0]])
# geht nicht wenn gensetPar importiert wird

gensetStatusIn=np.array([[0,0,1,0],
             [0,0,0.6929,0],
             [0,16.75,0,0],
             [0,3332,4463,3061]])

previousStatus=np.array([[0,0,0,0],
             [0,0,0.0,0],
             [0,0,0,0],
             [0,0,0,0]])

# Notes:                             


## INITIALIZATION


# Definition of variables

# Number of installed gensets
numberGensets = gensetPar.shape[0]; #Anzahl Dieselgeneratoren
print("Number of installed gensets= ",gensetPar.shape[0])
# Number of parameters
numPar =  gensetPar.shape[1]; #Anzahl Eingangsparameter
print("Number of parameters= ",numPar)
# Capacity of each genset
gensetRatedPower = np.zeros((numberGensets));  
print("Capacity of each genset= ",gensetRatedPower)  
# Minimal loading of the genset
gensetMinLoad = np.zeros(( numberGensets));
print("Minimal loading of the genset= ",gensetMinLoad)       
# Time from cold to rated P
gensetTimeCold = np.zeros(( numberGensets));
print("Time from cold to rated P= ",gensetTimeCold)
# The rated fuel consumption
ratedFuelConsumption = np.zeros((numberGensets, 4));
print("The rated fuel consumption= ",ratedFuelConsumption)
FuelConsumptionCurve = np.zeros((numberGensets, 5));
print("FuelConsumptionCurve = ",FuelConsumptionCurve)
Fuelticks = np.array([0.25,0.5,0.75,1]);
print("Fuelticks =",Fuelticks)
gensetFuelConsumption = np.zeros((2, numberGensets));
print("gensetFuelConsumption = ", gensetFuelConsumption)
# The minimal running time of the generators
gensetMinRuntime = np.zeros((numberGensets));
print("gensetMinRuntime = ",gensetMinRuntime)
# The current status of the generators
gensetStatus = gensetStatusIn[0];# Zustand Generator(An/Aus)
print("The current status of the generators= ",gensetStatus) 
# Actual loading of the installed sets
gensetLoading = gensetStatusIn[1];#elektrischer Verbrauch
print("Actual loading of the installed sets= ",gensetLoading)
# The actual running time
gensetCurrentOperTime = gensetStatusIn[2]; #Laufzeit seit dem Startzeitpunkt?
print("The actual running time= ",gensetCurrentOperTime)
# The total running time
gensetTotalOperTime = gensetStatusIn[3]; #Gesamtlaufzeit
print("The total running time= ",gensetTotalOperTime)
# loading of installed sets in previous step
prevgensetLoading = previousStatus[1];
print("loading of installed sets in previous step= ",previousStatus)

# Allocation from the input vector
for g in range(0,numberGensets):
    print("Genset ",g+1)
    gensetRatedPower[g] = gensetPar[g, 0];#Nennleistung
    print("gensetRatedPower : ",gensetRatedPower[g])
    gensetMinLoad[g] = gensetPar[g, 1];#Mindestleistung
    print("gensetMinLoad : ",gensetMinLoad[g])
    gensetTimeCold[g] = gensetPar[g, 2];
    print("gensetTimeCold: ",gensetTimeCold[g])
    ratedFuelConsumption [g] = gensetPar[g,3:7];
    print("ratedFuelConsumption: ",ratedFuelConsumption[g])
    gensetMinRuntime[g] = gensetPar[g,7];
    print("gensetMinRuntime: ",gensetMinRuntime[g])
    print("gensetCurrentOperTime: ", gensetCurrentOperTime[g])
## CALCULATION OF RUNNING TIME
   # Actual operation time in hours, if the genset is off, the value is reset
# Conversion from timestep to hours 
for g in range(0,numberGensets):
    print(gensetCurrentOperTime[g])
    
    if gensetStatus[g] ==1 or gensetStatus[g] ==3:
        gensetCurrentOperTime[g]=gensetCurrentOperTime[g]+1 * STEPSIZE / 60;
    else:
        gensetCurrentOperTime[g]=0;     
    print(gensetCurrentOperTime[g])
print(gensetCurrentOperTime)

# Set the generators that have not reached the minimal running time as
# forced on (status 3)
# If the generator is running and has already passed the minimal run time
# then set it back to 1 (on)
for g in range(0,numberGensets):
    if gensetCurrentOperTime[g] > 0 and gensetCurrentOperTime[g] < gensetMinRuntime[g]:
        gensetStatus[g] = 3;
    elif gensetCurrentOperTime[g] > 0 and gensetCurrentOperTime [g] >= gensetMinRuntime[g]:
        gensetStatus[g] = 1;
    print("Generator Status",g+1, "= ", gensetStatus[g]);
    
# Total operation time in hours
# Conversion from timestep to hours
for g in range(0,numberGensets):
    print(gensetTotalOperTime[g])
    if gensetStatus[g] ==1 or gensetStatus[g] ==3:
        gensetTotalOperTime[g]=gensetTotalOperTime[g]+1 * STEPSIZE / 60;
    else:
        gensetTotalOperTime[g]=gensetTotalOperTime[g];     
    print(gensetTotalOperTime[g])
print(gensetTotalOperTime)

## FUEL CONSUMPTION
############### VORHER ##################################################
# # Calculation of the fuel consumption following the model presented in
# # R. Dufo-López, J. L. Bernal-Agustín, J. M. Yusta-Loyo,
# # J. A. Domínguez-Navarro, I. J. Ramírez-Rosado, J. Lujano, and I. Aso, 
# # “Multi-objective optimization minimizing cost and life cycle emissions of 
# # stand-alone PV–wind–diesel systems with batteries storage,” Appl. Energy, 
# # vol. 88, no. 11, pp. 4033–4041, 2011.
# 
# # Actual power of the gensets for this step
# gensetActualPower = gensetRatedPower.* gensetLoading;
# 
# # Model coefficients
# A = 0.246; # l/kWh
# B = 0.08145; # l/kWh
# 
# # Calculate the consumption for each generator for the STEPSIZE
# # Since the model is for the consumption per kWh, it must be converted
# # according to the STEPSIZE used in the simulation
# 
# gensetFuelConsumption = B * gensetRatedPower + A * gensetActualPower;
############### VORHER ##################################################

# # Get fuel consumption curve of dieselgenerator (polyfit of highest degree (number of points-1) and
# # determine fuel consumption (polyval of genset Loading over this curve) in
# # l/h
# for g = 1:numberGensets
#     [v i] = find(~isnan(ratedFuelConsumption(g,:)));
#     FuelConsumptionCurve(g,1:length(i)) = polyfit([0 Fuelticks(i)],...
#         [0 ratedFuelConsumption(g,i)],length(i)-1);
#     gensetFuelConsumption(1,g) = polyval(FuelConsumptionCurve(g,1:length(i)),...
#         gensetLoading(g));
#     
#     
# end

##############################
# # # POLYFIT REPLACEMENT: 


for g in range(0,numberGensets):
    [i]=(np.nonzero(~np.isnan(ratedFuelConsumption[g,:]))); #reject NaN
    v=np.isnan(ratedFuelConsumption[g,:]);
    print("i ",[i])
    print("gensetFuelConsumption ",gensetFuelConsumption[0,g]);
    print("Fuelticks",Fuelticks[i])
    print("gensetLoading[g]",gensetLoading[g])
    print("ratedFuelConsumption[g,i] ",ratedFuelConsumption[g,i])
    xnew=gensetLoading[g]
    x=np.insert(Fuelticks[i],0,0)
    y=np.insert(ratedFuelConsumption[g,i],0,0)
    gensetFuelConsumption[0,g] = interpolate.pchip_interpolate(x,y, xnew)
    print("interpl",gensetFuelConsumption[0,g])
    plt.plot(x, y, 'o', xnew, gensetFuelConsumption[0,g], '-')
    plt.show()   
    #Previous Fuel Consumption
    a=np.insert(Fuelticks[i],0,0)
    b=np.insert(ratedFuelConsumption[g,i],0,0)
    anew=prevgensetLoading[g]
    prevFuelCons=interpolate.pchip_interpolate(a,b, anew)
    print("prevFuelCons ",prevFuelCons)
    stepFuelConsumption = max(gensetFuelConsumption[0,g], prevFuelCons);
    print("stepFuelConsumption ",stepFuelConsumption)
    #Dynamic consumption
    if abs(prevgensetLoading[g]-gensetLoading[g])>=0.5:
        gensetFuelConsumption[1,g]=(abs(prevgensetLoading[g]-gensetLoading[g])*0.16-0.07)*stepFuelConsumption;#linear additional consumption of y=0.16*x-0.07
        print("gensetFuelConsumption[1,g] ",gensetFuelConsumption[1,g])

##############################
# Convert l/h to l 
gensetFuelConsumption = gensetFuelConsumption * STEPSIZE / 60;



# Variable for the definition of which generators are running in order to
# calculate the fuel consumption
gensetOn = gensetStatus.all == 1 or gensetStatus == 3;
print("gensetOn ",gensetOn)

# Calculate the fuel consumption only if the generator is running
print(gensetFuelConsumption[0,:])
gensetFuelConsumption[0,:] = gensetFuelConsumption[0,:]* gensetOn;
print("gensetFuelConsumption[0,:] ",gensetFuelConsumption[0,:])
gensetFuelConsumption[1,:] = gensetFuelConsumption[1,:]* gensetOn;
print("gensetFuelConsumption[1,:] ",gensetFuelConsumption[1,:])

# Test the current status 2 (Maintenance, not available for the next step)
#gensetStatus(2) = 2;    

gensetStatusOut = np.array([gensetStatus, gensetLoading, gensetCurrentOperTime, gensetTotalOperTime]);
print("gensetStatusOut ",gensetStatusOut)
        
