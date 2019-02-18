# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 13:36:14 2019

@author: ASUS ABDOULAH WADIH
"""


#This reference simulation calculates the initial diesel consumption of system
#powered only by diesel generators... Used in other operation scenarios to 
#calculate the Diesel Consumption Savings.

# REFERENCE: Gensets only

import numpy as np

def MinIndex(A, a): # defined function to help for the calculation
    S = np.array([])
    for i in range(len(A)):
        if A[i]>a:
            S = np.append(S, A[i])
    Min= np.amin(S)
    index = A.index(Min)
    return Min, index 

def dispatchStrategy9(load, gensetPar, gensetStatusIn):
    
    # INITIALIZATION
    
        # The stepsize of the simulation in minutes
    global STEPSIZE
    STEPSIZE = 15
    
    # Initialization of auxiliary variables
#    charge = False        # Defines if battery can be charged
#    discharge = False     # Defines if battery can be discharged
#    gensetE = 0           # Energy that the diesel generator must supply
    wasteE = 0            # Energy that is wasted if the battery is full
    missingE = 0          # Energy that is missing
#    batteryPout = 0       # Output of power to battery
#    pvPout = 0
    residualLoad = 0
    
    # Definition of the diesel gensets parameters     
    numberGensets = len(gensetPar[:][:])     # Number of installed gensets
    # numPar = size(gensetPar, 2)           # Number of parameters available
    maxLoading = 1                          # Maximal genset loading
    gensetOn = np.zeros(numberGensets)
    gensetOff= np.zeros(numberGensets)
    gensetOffUnavailable= np.zeros(numberGensets)
    gensetForcedOn = np.zeros(numberGensets)
    # Definition of the genset status
        # Get the current status of the installed sets
    gensetStatus = gensetStatusIn[0][:]
    
            # Loading of the sets
    #gensetActualLoading = gensetStatusIn[1][:]
        # Rated capacity of each genset
    gensetRatedPower = np.zeros(numberGensets)
        # Minimal loading of the genset
    gensetMinLoad = np.zeros(numberGensets)
        # Time from cold to rated P
    gensetTimeCold = np.zeros(numberGensets)
    
    # Allocation from the input vector
    for g in range(numberGensets):
        gensetRatedPower[g] = gensetPar[g][0]
        gensetMinLoad[g] = gensetPar[g][1]
        gensetTimeCold[g] = gensetPar[g][3]
    
    for i in range(numberGensets):
        if gensetStatus[i]==0 or gensetStatus[i]==2: # Currently off (both available and unavailable generators)
            gensetOff[i]= 1
        if gensetStatus[i]==1 or gensetStatus[i]==3: # Currently on
            gensetOn[i] = 1 
        if gensetStatus[i]==2: # Currently off and unavailable for the next step
            gensetOffUnavailable[i] = 1
            gensetRatedPower[i] = 0 
    # Only consider the available gensets (on and off), The rating of unavailable generators will be
    # set to 0 and therefore not considered in the algorithm
        if gensetStatus[i]== 3: # Currently on and must stay on in the next step
            gensetForcedOn[i] = 1
            
    numberGensetUnavailable = sum(gensetOffUnavailable)
    
    # Conversion to units used in the simulation
    gensetRatedPower = gensetRatedPower*1000 # Genset capacities from kW to W
    gensetMinLoad = gensetMinLoad/100 # Minimal load from % to decimal
 
    # PRIMARY GENSETS CONTROL
    
    # Calculation of the power that the generators must supply for the next step 
    gensetPowerRequired = np.absolute(load)
    
    #If there is no power required, turn all gensets off
    #If the strategy considers minimal running time
    #A condition to exempt generators that need to stay on must be added

    loadingV = np.zeros(numberGensets)
    
    if gensetPowerRequired == 0:
        gensetLoading = np.zeros(numberGensets)
    #Otherwise start the Loading Algorithm
    else:
        #START OF LOADING ALGORITHM
        # Check if required power is smaller than a single generator which is on
        gensetLoading = np.zeros(numberGensets)
        #        index = np.array([], dtype=int)
        g = 0
        while (g<numberGensets and gensetOn[g] == 1):
            if gensetPowerRequired < gensetRatedPower[g]:
                loadingV[g] = 1
                #                index = np.append(index, g)
            g += 1
        #-------------------------CASE 1 --------------------
        #------------- ONE GENERATOR IS SUFFICIENT -----------
        if sum(loadingV) >= 1:
            smallestGenset, indexGenset = MinIndex(gensetRatedPower, gensetPowerRequired)
            gensetLoading[indexGenset] = gensetPowerRequired / gensetRatedPower[indexGenset]
            
        #-------------------------CASE 2 ------------------------------------
        #------------- TWO OR MORE GENERATORS NECESSARY ------------------------------
        #------------- GENERATORS CURRENTLY IN OPERATION ARE ENOUGH TO SUPPLY LOAD -----------
        elif sum(loadingV) == 0 and (gensetPowerRequired < sum(np.multiply(gensetRatedPower, gensetOn))):
            # If enough, load all generators equally, dividing the load by the
            # installed genset capacity
            for g in range (numberGensets):
                if gensetOn[g]==1:
                    gensetLoading[g] = gensetPowerRequired / sum(np.multiply(gensetRatedPower, gensetOn))
        #-------------------------CASE 3 ------------------------------------
        #------------- TWO OR MORE GENERATORS NECESSARY ------------------------------
        #------------- GENERATORS CURRENTLY IN OPERATION ARE NOT ENOUGH TO SUPPLY LOAD -----------
        else:
            # Not enough, generators must be turned on
            
            # Auxiliary variable with the required power
            gensetPR = gensetPowerRequired
            # The gensets that are currently on will be loaded to the maximum.
            # This will be subtracted from the power required
            gensetPR = gensetPR - maxLoading*sum(np.multiply(gensetRatedPower, gensetOn))
            #(gensetOn) = maxLoading;
        
            # Define which generators are currently off and sort them. This will assure that:
            # only the smallest generators will be turned on,leading to a better loading of the gensets
            gensetOffRatedPower = np.array([])
            for g in range(numberGensets):
                if gensetOff[g] ==1 :
                    gensetOffRatedPower = np.append(gensetOffRatedPower, gensetRatedPower[g])
            gensetOffRatedPower.sort()
            numberGensetsOff = len(gensetOffRatedPower)
        
            # Remove the generators that are unavailable. Since these will have a rated power of 0, 
            #they will be first in the vector
            gensetOffRatedPower = gensetOffRatedPower[numberGensetUnavailable:]
        
            #Auxiliary variable for algorithm with the current loading of off gensets
            gensetOffLoading = np.zeros(len(gensetOffRatedPower))
            
            #------------ CASE 3.1: All gensets are off and the power required is large--------------
            #In case all generators are off AND the required power is larger 
            #than most of the single generators (50%) then start with the largest generator available
            
            maxG = np.argmax(gensetRatedPower)
            #In case there are two or more generators with the same rating
            # maxG = maxG(1) /// argmax gives the first!
            # Load the largest genset
            count = 0
            g = 0 
            while g < numberGensets:
                if gensetRatedPower[g] < gensetPR:
                    count += 1
                g += 1
            if numberGensetsOff == numberGensets and count >= 0.5*numberGensets:
                # Set the loading of the largest generator. Either maximal loading 
                # or the required power by the rated power
                gensetLoading[maxG] = min(gensetPR/gensetRatedPower[maxG], maxLoading)
                gensetPower = gensetLoading[maxG]*gensetRatedPower[maxG]
                # Calculate new gensetPR            
                gensetPR = gensetPR - gensetPower
                # Updates the Rated Power of Off gensets and the number,
                # removing the genset that was turned on and those that are
                # currently unavailable
                for g in range(numberGensets):
                    if gensetLoading[g]==0:
                        gensetOffRatedPower[g] = gensetRatedPower[g]
                numberGensetsOff = len(gensetOffRatedPower)
                gensetOffRatedPower = gensetOffRatedPower[numberGensetUnavailable:]
                gensetOffRatedPower.sort()
                gensetOffLoading = np.zeros(len(gensetOffRatedPower))
            
            #--------------CASE 3.2 Some gensets are on, therefore turn on the smaller first-------
            # If some generators are already on, start with the smaller generators
            # g will be the iteration variable for the current generator
            g = 0
            while gensetPR > 0.001 and g <numberGensetsOff:
                # This will calculate the needed loading for the generator (which is currently off)
                gensetOffLoading[g] = min(gensetPR / gensetOffRatedPower[g], maxLoading)
                gensetPR = gensetPR - gensetOffLoading[g] * gensetOffRatedPower[g]
                # Now update the main gensetLoading vector according to which genset will be turned on
                for i in range(numberGensets):
                    if gensetRatedPower[i] == gensetOffRatedPower[g] and gensetLoading[i] > 0:
                        indexGenset = i
                gensetLoading[indexGenset] = gensetOffLoading[g]
                if gensetPR < 0.001:
                    break
                g += 1
            # Share the load equally depending on the active gensets
            S = 0 # to calculate sum(gensetRatedPower(gensetLoading > 0))
            for g in range(numberGensets):
                if gensetLoading[g]>0:
                    S= S + gensetRatedPower[g]
            for g in range(numberGensets):
                if gensetLoading[g]>0:
                    gensetLoading[g]= gensetPowerRequired / S 
            # If the load was not met by the generators: Display a warning
            if gensetPR > 1:
                print("The system has not been correctly sized. The load could not be supplied by the available sources.")
                #Calculate the energy which could not be supplied
                missingE = gensetPR * STEPSIZE/60
            
    # -----------------------------------OUTPUTS--------------------------------------------
    
    # Update the vector which outputs which gensets are currently on
    for g in range (numberGensets):
        if gensetLoading[g] > 0:
            gensetOn[g] = 1
    
    # Update the status, adding those gensets which were turned on (0 + 1), the
    # unavailable ones (0 + 2) and those which had to forcibly remain operatio-
    # nal (1 + 2). This results again in a vector with following possible
    # values: 0 (off), 1 (on), 2 (unavailable) and 3 (forcibly on)
    for g in range (numberGensets):
        gensetStatus[g] =  gensetOn[g] + gensetOffUnavailable[g] * 2 + gensetForcedOn[g] * 2
    for g in range(numberGensets):
        if gensetForcedOn[g]==1:
            gensetStatus[g] = 3

    # Calculate the Power that each generator will provide
    gensetPout = np.zeros(numberGensets)
    for g in range (numberGensets):
        gensetPout[g] = gensetLoading[g] * gensetRatedPower[g]
    

    # Output matrix with the gensets status including operation time
    gensetStatusOut = np.array([gensetStatus, gensetLoading, gensetStatusIn[2][:], gensetStatusIn[3][:]])
    # RESIDUAL LOAD
    # (POSITIVE == GENERATION SURPLUS OR NEGATIVE == LOAD SURPLUS)
    
    residualLoad = (wasteE - missingE)*60/STEPSIZE
  
    
    return (gensetPout, gensetStatusOut, residualLoad)

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
##previousStatus=np.array([[0,0,0,0],
##             [0,0,0.0,0],
##             [0,0,0,0],
##             [0,0,0,0]])
#    
#r1, r2, r3 = dispatchStrategy9(100, gensetPar, gensetStatusIn)
#
#print("gensetPout is: ", r1)
#print("gensetStatusOut is: ", r2)
#print("residualLoad is: ", r3)
#    