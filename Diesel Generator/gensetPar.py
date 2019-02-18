# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 21:26:20 2018

@author: Jacky
"""
import numpy as np

gensetPar=np.array([[32.1,50,0,"nan",4.6,6.5,10.2,0],
           [29.2,30,0,"nan",4.6,6.5,8.9,0],
           [11.9,30,0,"nan",2.34,3.22,4.27,2],
           [4.6,30,0,"nan",0.96,1.32,1.75,0]])

print(gensetPar)
print("Number of installed gensets= ",gensetPar.shape[0])
numPar =  gensetPar.shape[1];
print("Number of parameters= ",numPar)