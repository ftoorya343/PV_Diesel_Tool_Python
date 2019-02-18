# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 19:24:57 2018

@author: Jacky
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 17:00:27 2018

@author: Jacky
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 14:19:55 2018

@author: Jacky

"""

#Start
import math as m
from BatterySize import BatteriesInSeries, BatteriesInParallel
from Parameters import numParallel
#variables


Vnom=2
n=0.995
CellCapacity=210
Efull=2.7
Eexp=2.1067
Enom=1.875
numCellBlatt=6


#subvariables
Gain3=0.2

#ZwischenOutputs
numSeries=BatteriesInSeries*numCellBlatt
Qnom=CellCapacity*(9.5/10)
Qexp=CellCapacity*7.5*(10**(-3))

#Outputs

riCell=Vnom*((1-0.995)/(Qnom*Gain3))*numSeries
A=(Efull-Eexp)*numSeries
K=numSeries*(((CellCapacity-Qnom)/Qnom)*(Efull-Enom+((Efull-Eexp)*(m.exp((3/Qexp)*Qnom*(-1))-1))))
E0=numSeries*(((1-n)*Vnom)/(Qnom*Gain3)-(Efull-Eexp)+Efull+(((CellCapacity-Qnom)/Qnom)*(Efull-Enom+((Efull-Eexp)*(m.exp((3/Qexp)*Qnom*(-1))-1)))))
B=numParallel*(3/Qexp)
#Test

Test=(Efull-Eexp)*(m.exp((3/Qexp)*Qnom*(-1))-1)

#Print

print("riCell=",riCell)
print("A=",A)
print("E0=",E0)
print("K=",K)
print("B= ",B)
