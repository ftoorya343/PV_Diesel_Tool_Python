# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 00:45:03 2019

@author: ASUS ABDOULAH WADIH
"""
#import numpy as np
import math
import numpy as np
from scipy import interpolate
#import matplotlib.pyplot as plt

global STEPSIZE
STEPSIZE = 15

def gensetManager(previousStatus, gensetPar, gensetStatusIn):
    
    # Allocation from the input vector
    numberGensets = len(gensetPar[:][:])
    ratedFuelConsumption = np.zeros((numberGensets, 4))
    gensetMinRuntime = np.zeros(numberGensets)
    gensetFuelConsumption = np.zeros((2, numberGensets))
    gensetOn = np.zeros(numberGensets)
    gensetRatedPower = np.zeros(numberGensets)
    gensetMinLoad = np.zeros(numberGensets)
    gensetTimeCold = np.zeros(numberGensets)
    gensetStatus = np.zeros(numberGensets, dtype=int)
    gensetStatus = gensetStatusIn[0][:]
    gensetCurrentOperTime = gensetStatusIn[2][:]

    Fuelticks = np.array([0.25, 0.50, 0.75, 1])

    gensetLoading = gensetStatusIn[1]
    prevgensetLoading = previousStatus[1]
    
    for g in range(numberGensets):
        gensetRatedPower[g] = gensetPar[g, 0]
        gensetMinLoad[g] = gensetPar[g, 1]
        gensetTimeCold[g] = gensetPar[g, 2]
        ratedFuelConsumption[g,:] = gensetPar[g, 3:7]
        gensetMinRuntime[g] = gensetPar[g, 7]
    
    # CALCULATION OF RUNNING TIME
            # Conversion from timestep to hours
    i = 0
    while i<numberGensets:
        if (gensetStatus[i]==1 or gensetStatus[i]==3):
            gensetCurrentOperTime[i] = gensetCurrentOperTime[i] + STEPSIZE/60
        elif gensetStatus[i]==0:
            gensetCurrentOperTime[i] = 0
        elif gensetStatus[i]!=2:
            print("Please check the given status of Genset number: ", i+1)
        i += 1
        
    """
    Set the generators that have not reached the minimal running time as
    forced on (status 3)
    If the generator is running and has already passed the minimal run time
    then set it back to 1 (on)
    """     
    for g in range(0, numberGensets):
        if gensetCurrentOperTime[g] > 0 and gensetCurrentOperTime[g] < gensetMinRuntime[g]:
            gensetStatus[g]=3
        elif gensetCurrentOperTime[g] > 0 and gensetCurrentOperTime[g] >= gensetMinRuntime[g]:
            gensetStatus[g]=1
    """
    Total operation time in hours - Conversion from timestep to hours        
    """
    gensetTotalOperTime = gensetStatusIn[3][:]
    i = 0
    while (i<numberGensets) and (gensetStatus[i]==1 or gensetStatus[i]==3):
        gensetTotalOperTime[i] = gensetTotalOperTime[i] + STEPSIZE/60
        i += 1
    
    # FUEL CONSUMPTION
    
    # POLYFIT REPLACEMENT:
    
    g = 0
    while g < numberGensets:
        Indexes = np.array([], dtype=int)
        for k in range(4):
            if math.isnan(float(ratedFuelConsumption[g][k])) == False:
                Indexes = np.append(Indexes, k)
        Xnew = gensetLoading[g]
        Y = [0]; X = [0]
        for j in range(len(Indexes)):
            Y = np.append(Y, ratedFuelConsumption[g, Indexes[j]])
            X = np.append(X, Fuelticks[Indexes[j]])
        
#        print("X is: ", X)
#        print("Y is: ", Y)
        gensetFuelConsumption[0,g] = interpolate.pchip_interpolate(X,Y, Xnew)
#        print("interpl", gensetFuelConsumption[0,g])
#        plt.plot(X, Y, 'o', Xnew, gensetFuelConsumption[0,g], '-')
#        plt.show() 
        
        #Previous Fuel Consumption

        Xnew_prev = prevgensetLoading[g]
        prevFuelCons = interpolate.pchip_interpolate(X,Y, Xnew_prev)
#        print("prevFuelCons ",prevFuelCons)
        stepFuelConsumption = max(gensetFuelConsumption[0,g], prevFuelCons)
#        print("stepFuelConsumption ",stepFuelConsumption)
    
        #Dynamic consumption / Linear additional consumption of y=0.16*x-0.07
        if abs(prevgensetLoading[g]-gensetLoading[g])>=0.5:
            gensetFuelConsumption[1,g]=(abs(prevgensetLoading[g]-gensetLoading[g])*0.16-0.07)*stepFuelConsumption
#            print("gensetFuelConsumption[1,g] ",gensetFuelConsumption[1,g])
        
        g += 1

    # Convert l/h to l 
    gensetFuelConsumption = gensetFuelConsumption * STEPSIZE / 60
    
    # Variable for the definition of which generators are running in order to
    # calculate the fuel consumption
    for i in range(numberGensets):
        if gensetStatus[i] == 1 or gensetStatus[i] == 3:
            gensetOn[i] = 1
    #    print("gensetOn ", gensetOn)
    
    # Calculate the fuel consumption only if the generator is running
    gensetFuelConsumption[0,:] = gensetFuelConsumption[0,:]* gensetOn
    gensetFuelConsumption[1,:] = gensetFuelConsumption[1,:]* gensetOn
    
    
    gensetStatusOut = np.array([gensetStatus, gensetLoading, gensetCurrentOperTime, gensetTotalOperTime])
#    print("gensetFuelConsumption ", gensetFuelConsumption)
#    print("gensetStatusOut ", gensetStatusOut)
    return(gensetStatusOut, gensetFuelConsumption) 
    
'''Test:''' 
#gensetPar=np.array([[32.1,50,0,"nan",4.6,6.5,10.2,0],
#           [29.2,30,0,"nan",4.6,6.5,8.9,0],
#           [11.9,30,0,"nan",2.34,3.22,4.27,2],
#           [4.6,30,0,"nan",0.96,1.32,1.75,0]])
#
#
#gensetStatusIn=np.array([[0,0,1,0],
#             [0,0,0.6929,0],
#             [0,16.75,0,0],
#             [0,3332,4463,3061]])
#
#previousStatus=np.array([[0,0,0,0],
#             [0,0,0.0,0],
#             [0,0,0,0],
#             [0,0,0,0]])
#
#print(gensetManager(previousStatus, gensetPar, gensetStatusIn))






    
