# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 21:01:25 2018

@author: ASUS ABDOULAH WADIH
"""
import numpy as np

def MinIndex(A, a): # defined function to help for the calculation
    S = np.array([])
    for i in range(len(A)):
        if A[i]>a:
            S = np.append(S, A[i])
    Min= np.amin(S)
    index = A.index(Min)
    return Min, index 

def dispatchStrategy1(pvPin, load, gensetPar, gensetStatusIn, batteryStatus, batteryPar):

    # DESCRIPTION (TO BE UPDATED):
    # Simple dispatch strategy for a PV-diesel-battery system
    # PV power has priority, the residual load will be met firstly by the
    #battery system. Only if the battery is unable to meet demand, will the
    # generators be turned on.    
    #--------------------------------- INITIALIZATION
    # The stepsize of the simulation in minutes
    
    global STEPSIZE
    STEPSIZE=15

    # 1. Initialization of auxiliary variables
    charge = False        # Defines if battery can be charged
    discharge = False     # Defines if battery can be discharged
    gensetE = 0           # Energy that the diesel generator must supply
    wasteE = 0            # Energy that is wasted if the battery is full
    missingE = 0          # Energy that is missing
    batteryPout = 0       # power-Output  of battery

    # 2. Calculation of the residual load
    #The residual load is the difference between the PV input and the load for the current step.
    residualLoad = pvPin - load        # negative Residuallast!!!
    
    # 3. Extraction of the battery status

    # The current battery SOC and voltage are extracted from the battery 
    # input vector
    batterySOC = batteryStatus[2]
    batteryV = batteryStatus[4]

    # Other battery status parameters (If necessary)
    # batteryIin = batteryStatus(1);
    # batteryPin = batteryStatus(2);
    # batteryVnoLoad = batteryStatus(4);

    # 4. Extraction of the battery array parameters

    # Return the battery parameters from the parameters vector
    maxChargeCurrent = batteryPar[0]
    maxDischargeCurrent = batteryPar[1]
    upperSOC = batteryPar[4]
    lowerSOC = batteryPar[5]
    arrayWh = batteryPar[9]

    # Other parameters (If necessary)
    # maxVoltage = batteryPar(3);
    # minVoltage = batteryPar(4);
    # numSeries = batteryPar(7);
    # numParallel = batteryPar(8);
    # totalV = batteryPar(9);

    # 5. Definition of the diesel gensets parameters

    numberGensets = len(gensetPar[:][:])      # Number of installed gensets
    # numPar = size(gensetPar, 2);             % Number of parameters available
    maxLoading = 1                          # Maximal genset loading


    # 6. Definition of the genset status  
 
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
    
    # DEBUG
    #disp(residualLoad * STEPSIZE / 60)

    # Convert the residual load from the step to energy in Wh. If the residual
    # load was positive, this number will be the amount of energy that can be
    # charged in the battery (considering the step size), if the number is
    # negative it will be the amount of energy to be discharged within the step
    eResidual = residualLoad * STEPSIZE / 60 # Wh



    # PRIMARY BATTERY CONTROL

    # Define how much energy there is still in the battery
    # There is a distinction between remaining Charge Energy and Remaining
    # Discharge Energy
    eRemDischarge = arrayWh * (batterySOC - lowerSOC)
    eRemCharge = arrayWh * (upperSOC - batterySOC)

    # If the SOC is lower than the maximal SOC, the battery can be charged
    # If the SOC is higher than the minimal SOC, the battery can be discharged
    if batterySOC < upperSOC:
        charge = True
        if batterySOC > lowerSOC:
            discharge = True
    elif batterySOC > lowerSOC:
        discharge = True
    #----------------------------------------------------------------------------------------
    #---------------------------------- CASE 1 ----------------------------------
    # If the PV generation is the same as the load, the residual load will be 0
    # In this case, the PV output will be the same as the PV input.
    # The battery output will be 0

    if residualLoad == 0:
        batteryPout = 0
        pvPout = pvPin
    
    #---------------------------------- CASE 2 ----------------------------------
    # If the PV generation is larger than the load, the residual load will be
    # larger than 0. In this case, the PV output will be set to the same value 
    # as the load. If possible, the battery will be charged

    elif residualLoad > 0:
        pvPout = load           # PV output will be reduced to only supply the load
    
        
        # If the battery can be charged, the battery will be charged according
        # to the amount of the remaining charging capacity
       
        # CASE 2.1 the battery can be charged AND there is enough room for the
        # complete charge over this timestep
        if (charge and (eRemCharge >= eResidual)):
            batteryPout = residualLoad
        
        # CASE 2.2 the battery can be charged, BUT there is not enough room for
        # the complete charge over this timestep
        # The battery will then be charged with the possible energy
        elif (charge and (eRemCharge < eResidual)):
            # Calculate the power from the remaining energy that can be charged
            batteryPout = eRemCharge * 60 / STEPSIZE
            # The energy that cannot be used for the charge will be wasted
            wasteE = eResidual - eRemCharge
    
        # CASE 2.3 battery is already full
        # If the battery is already full, it will not be charged
        elif not charge:
            batteryPout = 0
            wasteE = eResidual
        # if (charge && (eRemCharge >= eResidual))

    
    #---------------------------------- CASE 3 ----------------------------------
    #If the PV generation is smaller than the load, the residual load will be
    # negative. In this case, the PV output will be the same as the PV input
    # In this strategy, the battery power will be used to supply the load

    else:
        # residualLoad < 0
        # PV output stays the same
        pvPout = pvPin
    
        # If the battery can be discharged, the discharge will occur depending
        # on the remaining capacity of the battery and the necessary energy for
        # the timestep
    
        # CASE 3.1 the battery can be discharged AND there is enough capacity
        # for the complete discharge over this timestep
        if (discharge and (eRemDischarge >= abs(eResidual))):
            batteryPout = residualLoad
        
        # CASE 3.2 the battery can be discharged, BUT there is not enough
        # capacity for the complete discharge over this timestep
        # The battery will then be discharged with the possible energy
        elif (discharge and (eRemDischarge < abs(eResidual))):
            # Calculate the power from the remaining energy that can be
            # discharged
            batteryPout = - eRemDischarge * 60 / STEPSIZE
            # The remaining energy will be delivered by the diesel generators
            gensetE = abs(eResidual) - eRemDischarge
            
        # CASE 3.3 Battery empty
        # If the battery is already empty then the battery will not be further
        # discharged. In this case, the diesel generator needs to supply the
        # complete load
        else:
            batteryPout = 0
            gensetE = eResidual
        
        # if (discharge && (eRemDischarge >= abs(eResidual)))
        # if residualLoad == 0

    # ------------------------CONTROL OF BATTERY CURRENT -------------------------------------
    # In this section, the charging/discharging current is estimated from the
    # power from/to the battery and the battery voltage
    batteryIout = batteryPout / batteryV

    # Auxiliary variable to determine if the battery output needs to be
    # changed
    batteryPoutReduced = batteryPout

    # A negative current will discharge the battery
    # If the discharging current is larger than the maximal discharge current,
    # a new battery Pout is calculated
    if (batteryIout < 0 and abs(batteryIout) > maxDischargeCurrent):
        batteryPoutReduced = - batteryV * maxDischargeCurrent

    # A positive current will charge the battery
    elif (batteryIout > 0 and batteryIout > maxChargeCurrent):
        batteryPoutReduced = batteryV * maxChargeCurrent
    
    # If there is a discrepancy between the auxiliary battery output and the
    # one calculated previously, the diesel generator will supply the remaining
    # (in case of a battery discharge) or the energy will be wasted (in the
    # case of a battery charge)

    # This will also change to the real battery power output

    # Charge discrepancy (wasted energy)
    if (batteryPout > 0 and batteryPoutReduced != batteryPout):
        wasteE = wasteE + ((batteryPout - batteryPoutReduced) * STEPSIZE / 60)
        batteryPout = batteryPoutReduced
    
    # Discharge discrepancy (diesel generator)
    elif (batteryPout < 0 and batteryPoutReduced != batteryPout):
        gensetE = gensetE + abs((batteryPout - batteryPoutReduced)* STEPSIZE / 60)
        batteryPout = batteryPoutReduced

#--------------------------------------------------------------------------------------
    # PRIMARY GENSETS CONTROL
        # Calculation of the power that the generators must supply for the next step 
    gensetPowerRequired = np.absolute(gensetE * 60 / STEPSIZE)
    
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
                #Calculate the energy which could not be supplied
                missingE = gensetPR * STEPSIZE/60
                print(gensetPR,'W of unmet load and', missingE, 'Wh of unmet energy!')
               #'The system has not been correctly sized. The load could not be supplied by the available sources.123')

        #if sum(loadingV) >= 1
    # if gensetPowerRequired == 0

               

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

    
    return (pvPout, batteryPout, gensetPout, gensetStatusOut, residualLoad)
  
    
'''Test:''' 

#pvPin = 4000
#load= 5000
#
#batteryStatus=[-19.74,-989,3,0.40,50.11,50.11]
#
#batteryPar=[26040,26040,58.8,40.8,0.95,0.36,24,62,48,624960]
#
#gensetPar=np.array([[32.1,50,0,"nan",4.6,6.5,10.2,0],
#           [29.2,30,0,"nan",4.6,6.5,8.9,0],
#           [11.9,30,0,"nan",2.34,3.22,4.27,2],
#           [4.6,30,0,"nan",0.96,1.32,1.75,0]])
#
#gensetStatusIn=np.array([[0,0,1,0],
#             [0,0,0.6929,0],
#             [0,16.75,0,0],
#             [0,3332,4463,3061]])
#    
#
#r1, r2, r3, r4, r5 = dispatchStrategy1(pvPin, load, gensetPar, gensetStatusIn, batteryStatus, batteryPar)
#
#print("pvPout is: ", r1)
#print("batteryPout is: ", r2)
#print("gensetPout is: ", r3)
#print("gensetStatusOut is: ", r4)
#print("residualLoad is: ", r5)


