# -*- coding: utf-8 -*-
"""
Spyder Editor
Behaviour Performance Plotting Based on Mouse
Author: Georgios Foustoukos
Modified by: Chuanqiang Zhang
Date: 2020/01/01
Lab: LSENS BMI EPFL
Version: 3

***Requirement***
Date input structure:
    Mouse\Date\BehavResults.mat
For example:
    CZ004\20191211\BehavResults.mat

Important: This script only works for recordings that contain, whstim, astim and nonstim.

***Issue***
1. stop criteria issue
2. 
"""
#%% 
# Our main plotting package (must have explicit import of submodules)
import bokeh.io
import bokeh.plotting
from bokeh.io import output_file, show
from bokeh.layouts import column, row
from bokeh.plotting import figure
import sys
import glob 
import os 
import scipy.io as sio
import numpy as np
import decimal as dc
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pickle
from natsort import natsorted, ns
from bokeh.models import Legend
from pathlib import Path
from scipy.stats import norm
# Enable viewing Bokeh plots in the notebook
# bokeh.io.output_notebook()

#%% section 1  define some variables  

mouseName = 'CZ003'
Order = []
MouseDict = dict.fromkeys(['MouseName', 'daysName','WhHitR','AudHitR','FAR','dR','AudHit','WhHit','FA'])
imaging_days_new = []
AudMissInaRow = 4
AudHitRate = []
WhHitRate = []
FARate = []
WhHitRunning = []
AudHitRunning = []
FARunning = []
dprimeRunning = []

#%% section 2  load the folder

#behavpath = 'K:\\output\\' + mouseName + '\\'   # for some unknown reason, this line doesn´t work. something related to glob.glob function.
behavpath = '\\\\files7\\data\\czhang\\output\\' + mouseName + '\\'   # however, this works, but they shall be the same.
imaging_days = glob.glob(os.path.join(behavpath, "*")) 

for n, f in enumerate(imaging_days):
    imaging_days[n] = os.path.basename(f)

imaging_days = natsorted(imaging_days)
    
if Order :
    for n, f in enumerate(imaging_days):
        imaging_days_new.append(imaging_days[Order[n]])
    imaging_days = imaging_days_new
    
print(imaging_days)

#%% section 3  load mat file, calculate dprime and plot the contents

print("****Big LOOP Start****")
for m, d in enumerate(imaging_days):
    print("*****Mouse Session:*****")
    print(m, d)
    behav_path = behavpath + d + '\\BehavResults.mat'    
    print(behav_path)
    beh = sio.loadmat(behav_path)
    vals = beh['BehavResults'][0,0]
    keys = beh['BehavResults'][0,0].dtype.descr
    beh = np.array(vals[keys[0][0]][:][:])
    performance = np.array(beh[:,9])
    performance = performance.astype(int)
    stim = np.array(beh[:,5])
    stim = stim.astype(int)
    whstim = np.array(beh[:,6])
    whstim = whstim.astype(int)
    audstim =  np.array(beh[:,7])
    audstim = audstim.astype(int)
    
    #Testing purpose
    aN=sum(stim==0)
    bN=sum(whstim==1)
    cN=sum(audstim==1)
    print("AudStim: WhStim: NoStim  (total numbers) ")
    print(cN, bN ,aN)
    
    AudHit = 0
    AudMiss = 0
    WhHit = 0
    WhMiss = 0
    FAc = 0
    CR = 0
    MissFlag = []
    WhStim = 0
    AudStim = 0
    NoStim = 0
    StopSession = False
    TotalTrials = 0
    TrialNumber = len(beh)
    RecentTrials = 50
    
    print('Total number of Trials ' + str(TrialNumber))
    
    WhHitChunk = np.zeros(TrialNumber)                  # Whhit Rate
    AudHitChunk =  np.zeros(TrialNumber)                # Audhit Rate
    FAChunk =  np.zeros(TrialNumber)                    # FArate
    dprime =  np.zeros(TrialNumber)                     # dprime
    # print("WhHitChunk, AudHitChunk, FAChunk, dprime")
    # print(len(WhHitChunk), len(AudHitChunk), len(FAChunk), len(dprime))
    
    for n in range(TrialNumber):
        # Chunk is difined as a smoothing average, it equals RecentTrials+1
        ChunkPer = performance[np.max([0,n-RecentTrials]) : (n+1)]
        ChunkStim = stim[np.max([0,n-RecentTrials]) : (n+1)]
        ChunkWhStim = whstim[np.max([0,n-RecentTrials]) : (n+1)]
        ChunkAuStim = audstim[np.max([0,n-RecentTrials]) : (n+1)]
        
        # following part I have changed a lot.
        if sum((ChunkWhStim == 1)) > 0 :
            WhHitChunk[n] = sum((ChunkPer == 2))/sum((ChunkWhStim == 1))   
        if sum((ChunkAuStim == 1)) > 0 :
            AudHitChunk[n] = sum((ChunkPer == 3))/sum((ChunkAuStim == 1))               
        if sum((ChunkStim == 0)) > 0 :
            FAChunk[n] = sum((ChunkPer == 5))/sum((ChunkStim == 0))                     
        
        # Performance definition:
        # Perf=0; % 0 for WMisses
        # Perf=1; % 1 for AMisses
        # Perf=2; % 2 for WHits
        # Perf=3; % 3 for AHits
        # Perf=4; % 4 for Correct Rejection
        # Perf=5; % 5 for False Alarm
        # Perf=6; % 0 for EarlyLick
        # Above, calculate the WhHit, AudHit and FA rate
        
        # Following part calculate dprime
        # Regarding dprime definition
        # https://www.nature.com/articles/ncpneuro0794/figures/1
        # Regarding dprime correction for 0 and 1 problem.
        # http://www.kangleelab.com/sdt-d-prime-calculation---other-tips.html    
                      
        if WhHitChunk[n] == 1:
            Half_WhHit = 0.5/(sum((ChunkPer == 2)) + sum((ChunkPer == 0)))             
            WHit = 1-Half_WhHit            
        elif WhHitChunk[n] == 0:            
            Half_WhHit = 0.5/(sum((ChunkPer == 2)) + sum((ChunkPer == 0)))  # Note sometimes, denomitor is 0. The problem arises for the first 50 Chunk..
            WHit = Half_WhHit
        else:
            WHit = WhHitChunk[n]
            
        if FAChunk[n] == 1:        
            Half_FA = 0.5/(sum((ChunkPer == 5)) + sum((ChunkPer == 4)) )   # Assumme that nonstim trails exist.
            FA = 1-Half_FA            
        elif FAChunk[n] == 0:
            Half_FA = 0.5/(sum((ChunkPer == 5)) + sum((ChunkPer == 4)) )   
            FA = Half_FA            
        else:
            FA = FAChunk[n]
            
        dprime[n] = norm.ppf(WHit) - norm.ppf(FA)
        
        # Above dprime calculation definition I don´t understand, needs explaination.
        # change finished on above line
        
    # Using bokeh plot the result
    # Things plotted are: WhHit, AudHit, FA rate and dprime
    # They corresponds to the following variables:
    # WhHitChunk, AudHitChunk and FAChunk
    # dprime
        
    p = bokeh.plotting.figure(
    width=600,
    height=400,
    x_axis_label='Trial Number',
    y_axis_label='AudHit/WhHit/FA',
    x_range=(1, TrialNumber),
    title = mouseName + '|' + d    
    )    
    
    dp = bokeh.plotting.figure(
    width=500,
    height=300,
    x_axis_label='Trial Number',
    y_axis_label='dprime',
    x_range=(1, TrialNumber),
    title= mouseName + '|' + d    
    )    

    p.yaxis.axis_label_text_font_style = "bold"
    p.xaxis.axis_label_text_font_style = "bold"
    p.title.align = 'center'
    
    dp.yaxis.axis_label_text_font_style = "bold"
    dp.xaxis.axis_label_text_font_style = "bold"
    dp.title.align = 'center'
    

    audh = p.line(
    x= range(TrialNumber),
    y= np.array(AudHitChunk),
    line_join='bevel',
    line_width=2,
    color = 'blue',
    )
    
    fa = p.line(
    x= range(TrialNumber),
    y= np.array(FAChunk),
    line_join='bevel',
    line_width=2,
    color = 'red',
    )    
       
    whhit = p.line(
    x= range(TrialNumber),
    y= np.array(WhHitChunk),
    line_join='bevel',
    line_width=2,
    color = 'black',
    )
    
    d = dp.line(
    x= range(TrialNumber),
    y= np.array(dprime),
    line_join='bevel',
    line_width=2,
    color = 'green',
    )
    
    legend = Legend(items=[
    ("AudHit" , [audh]),
    ("WhHit" , [whhit]),
    ("FA" , [fa])   
    ], location="center")
    
    p.add_layout(legend, 'right')    
    p.legend.click_policy="hide"
    bokeh.io.show(row(dp,p))
    
    WhHitRunning.append(WhHitChunk)
    AudHitRunning.append(AudHitChunk)
    FARunning.append(FAChunk)
    dprimeRunning.append(dprime)
    # These few append lines are used to prepare for the next plot.
    
    #%% Following part is used to prepare and plotting learning Curve.
    # Be aware of that, now we are still under the big for loop.
    # Where for loops and enumerate(imaging_days)    
    
    # Performance definition:
        # Perf=0; % 0 for WMisses
        # Perf=1; % 1 for AMisses
        # Perf=2; % 2 for WHits
        # Perf=3; % 3 for AHits
        # Perf=4; % 4 for Correct Rejection
        # Perf=5; % 5 for False Alarm
        # Perf=6; % 0 for EarlyLick
    
    for k in range(TrialNumber):        
        if not(StopSession):            
            TotalTrials += 1
            if performance[k] == 0:
                WhMiss += 1 
                if len(MissFlag) < AudMissInaRow:
                    MissFlag.append(0)
                else:
                    MissFlag = MissFlag[1::]
                    MissFlag.append(0)

                if (sum(MissFlag) == AudMissInaRow):
                    print(str(AudMissInaRow) + 'AudMiss in row detected')
                    StopSession = True

            elif performance[k] == 1:
                AudMiss += 1
                if len(MissFlag) < AudMissInaRow:
                    MissFlag.append(1)
                else:
                    MissFlag = MissFlag[1::]
                    MissFlag.append(1)

                if (sum(MissFlag) == AudMissInaRow):
                    print(str(AudMissInaRow) + 'AudMiss in row detected')
                    StopSession = True
                    print("AudMiss criteria fullfilled at TrialNumber:")
                    print(k)

            elif performance[k] == 2:
                WhHit += 1
                if len(MissFlag) < AudMissInaRow:
                    MissFlag.append(0)
                else:
                    MissFlag = MissFlag[1::]
                    MissFlag.append(0)

                if (sum(MissFlag) == AudMissInaRow):
                    print(str(AudMissInaRow) + 'AudMiss in row detected')
                    StopSession = True

            elif performance[k] == 3:
                AudHit += 1
                if len(MissFlag) < AudMissInaRow:
                    MissFlag.append(0)
                else:
                    MissFlag = MissFlag[1::]
                    MissFlag.append(0)

                if (sum(MissFlag) == AudMissInaRow):
                    print(str(AudMissInaRow) + 'AudMiss in row detected')
                    StopSession = True

            elif performance[k] == 4:
                CR += 1
                if len(MissFlag) < AudMissInaRow:
                    MissFlag.append(0)
                else:
                    MissFlag = MissFlag[1::]
                    MissFlag.append(0)

                if (sum(MissFlag) == AudMissInaRow):
                    print(str(AudMissInaRow) + 'AudMiss in row detected')
                    StopSession = True

            elif performance[k] == 5:
                FAc += 1
                if len(MissFlag) < AudMissInaRow:
                    MissFlag.append(0)
                else:
                    MissFlag = MissFlag[1::]
                    MissFlag.append(0)

                if (sum(MissFlag) == AudMissInaRow):                
                    print(str(AudMissInaRow) + 'AudMiss in row detected')
                    StopSession = True            
                    
            if whstim[k] == 1:                
                WhStim += 1                
            if audstim[k] == 1:                
                AudStim += 1                
            if  stim[k] == 0:                
                NoStim += 1
                
    if AudStim == 0:
        AudHitRate.append(0.0)
    else:
        AudHitRate.append(AudHit/AudStim)
    
    if WhStim == 0:   
        WhHitRate.append(0.0)
    else:
        WhHitRate.append(WhHit/WhStim)
    if NoStim == 0:
        FARate.append(0.0)
    else:
        FARate.append(FAc/NoStim)     
    print("AudStim  :  WhStim  :  NoStim")
    print( AudStim ,  WhStim  , NoStim)
    
print("****Big LOOP Finish****")

# prepare for plotting
# what was plotted here is the mean rate (however, whether the stop criteria is fullfilled or not is not controlled)    
# discuss with george about that.
    
MouseDict = { 'MouseName' : mouseName,
              'daysName' : imaging_days,
              'WhHitR' : WhHitRunning,
              'AudHitR' : AudHitRunning,
              'FAR' : FARunning,
              'dR' : dprimeRunning,
              'AudHit' : AudHitRate,
              'WhHit' : WhHitRate,
              'FA' : FARate
}


#%% Section for plotting

p = bokeh.plotting.figure(
    width=700,
    height=500,
    x_axis_label='Days',
    y_axis_label='AudHit/WhHit/FA',
    title= mouseName  
    )

p.yaxis.axis_label_text_font_style = "bold"
p.xaxis.axis_label_text_font_style = "bold"
p.title.align = 'center'

audh = p.line(
x= range(len(imaging_days)),
y= np.array(MouseDict['AudHit']),
line_join='bevel',
line_width=2,
color = 'blue',
)

fa = p.line(
x= range(len(imaging_days)),
y= np.array(MouseDict['FA']),
line_join='bevel',
line_width=2,
color = 'red',
)

whhit = p.line(
x= range(len(imaging_days)),
y= np.array(MouseDict['WhHit']),
line_join='bevel',
line_width=2,
color = 'black',
)

legend = Legend(items=[
    ("AudHit" , [audh]),
    ("WhHit" , [whhit]),
    ("FA" , [fa])   
    ], location="center")
    
p.add_layout(legend, 'right')    
p.legend.click_policy="hide"
    
bokeh.io.show(p)

print("Please check if stop criteria was ever fullfilled.")
print("*****finished*****")
   














