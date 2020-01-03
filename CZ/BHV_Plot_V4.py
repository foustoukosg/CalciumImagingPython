# -*- coding: utf-8 -*-
"""
Spyder Editor
Behaviour Performance Plotting Based on Mouse
Author: Chuanqiang Zhang

Based on code: BHV_George_CZ
Original Author: Georgios Foustoukos

Date: 2020/01/03
Lab: LSENS BMI EPFL
Version: 4

***Requirement***
Date input structure:
    Mouse\Date\BehavResults.mat
For example:
    CZ004\20191211\BehavResults.mat

***Note***
1. This is not a very concised code. But it works. 
2. In the future, we could write a better one, using function calls more often.
3. Currently the code readability is very very low.

# To use, change the Inputs:
mouseName = 'CZ003'
SmoothStandard = 20
default_path = '\\\\files7\\data\\czhang\\output\\'

# Caution! Please verify with your data, to find possible bugs.

"""

#%% 
# Our main plotting package (must have explicit import of submodules)
from collections import Counter
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
# Input:
mouseName = 'CZ004'
SmoothStandard = 20
default_path = '\\\\files7\\data\\czhang\\output\\'

Order = []
MouseDict = dict.fromkeys(['MouseName', 'daysName','WhHitR','AudHitR','FAR','dR','AudHit','WhHit','FA'])
imaging_days_new = []


AudMissInaRow = 3
AudHitRate = []
WhHitRate = []
FARate = []

WhHitRunning = []
AudHitRunning = []
FARunning = []
dprimeRunning = []
SearchReport = False
AudupdateReport = False
WhupdateReport = False
FAupdateReport = False

#%% section 2  load the folder

#behavpath = 'K:\\output\\' + mouseName + '\\'   # for some unknown reason, this line doesn´t work. something related to glob.glob function.
behavpath = default_path + mouseName + '\\'   # however, this works, but essentially they are the same.
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
    fN=sum(stim==0)
    wN=sum(whstim==1)
    aN=sum(audstim==1)
    eN=sum(performance==6)

    print("AudStim: WhStim: NoStim : EarlyLicks  (total numbers) ")
    print(aN, wN ,fN, eN)
    if len(performance)==(aN+wN+fN+eN):
        print('Trial numbers fit')
    else:
        print('Error exists, trial number does not fit.')
    
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
    
    print('Total number of Trials ' + str(TrialNumber))
    
    # print("WhHitChunk, AudHitChunk, FAChunk, dprime")
    # print(len(WhHitChunk), len(AudHitChunk), len(FAChunk), len(dprime))
    # print(performance)
    TrialNumber=len(performance)
    #print('Total trialnumber: ',TrialNumber)
    
    # Plot dPrime in a signal based moving average
    Aud_standard = SmoothStandard
    Aud_StimCounter = []
    Aud_SearchDone = False
        
    Wh_standard = SmoothStandard
    Wh_StimCounter = []
    Wh_SearchDone = False
   
    FA_standard = SmoothStandard
    FA_Counter = []
    FA_SearchDone = False
    
    
    WhHitChunk = np.zeros(TrialNumber)                  # Whhit Rate
    AudHitChunk =  np.zeros(TrialNumber)                # Audhit Rate
    FAChunk =  np.zeros(TrialNumber)                    # FArate
    
    # For probability plot, uncorrected for 0 and 1 issue.
    pWhHitChunk = np.zeros(TrialNumber)                  # Whhit Rate
    pAudHitChunk =  np.zeros(TrialNumber)                # Audhit Rate
    pFAChunk =  np.zeros(TrialNumber)                    # FArate

    
    dprime_wh =  np.zeros(TrialNumber)                  # dprime
    dprime_aud =  np.zeros(TrialNumber)  
    
    # Note, python has 0 based indexing, while matlab has 1 based indexing.
    print('***calculation report starts***')
    for k in range(TrialNumber):        
            if (performance[k] == 1 or performance[k] == 3):
                if AudupdateReport:
                    print(k+1, '# trial  was updated.')
                Aud_count=Counter(performance[0:k+1])
                #print(Aud_count)
                if (Aud_count[1]+Aud_count[3]) <= Aud_standard:
                    if SearchReport:
                        print('*normal update')
                    ChunkPer = performance[0 : (k+1)]
                    ChunkStim = stim[0 : (k+1)]
                    ChunkAuStim = audstim[0 : (k+1)]                              
                    if sum((ChunkAuStim == 1)) > 0 :
                        AudHitChunk[k] = sum((ChunkPer == 3))/sum((ChunkAuStim == 1))                
                elif (Aud_count[1]+Aud_count[3]) > Aud_standard:
                    for n in reversed(range(0,k)):
                        if not Aud_SearchDone:
                            Aud_count=Counter(performance[n:k+1])
                            if (Aud_count[1]+Aud_count[3]) == Aud_standard:
                                Aud_SearchDone= True
                                if SearchReport:
                                    print('**searched update')
                                    print('**search report position: ', n)
                                ChunkPer = performance[n : (k+1)]
                                ChunkStim = stim[n : (k+1)]
                                ChunkAuStim = audstim[n : (k+1)]
                                # following part I have changed a lot.                
                                if sum((ChunkAuStim == 1)) > 0 :
                                    AudHitChunk[k] = sum((ChunkPer == 3))/sum((ChunkAuStim == 1))
                    Aud_SearchDone= False  # Note this indent shoud be out of for loop.        
                pAudHitChunk[k] = AudHitChunk[k]
                if AudHitChunk[k] == 1:
                    Half_AudHit = 0.5/(sum((ChunkPer == 3)) + sum((ChunkPer == 1)))             
                    AudHitChunk[k] = 1-Half_AudHit                
                elif AudHitChunk[k] == 0:            
                    Half_AudHit = 0.5/(sum((ChunkPer == 3)) + sum((ChunkPer == 1)))  
                    AudHitChunk[k] = Half_AudHit                
                else:
                    AudHitChunk[k] = AudHitChunk[k]
            else:            
                AudHitChunk[k]   =  AudHitChunk[k-1]
                pAudHitChunk[k] = pAudHitChunk[k-1]
    
    print('***Above report for Audio calculation***')
                
    for k in range(TrialNumber):        
            if (performance[k] == 0 or performance[k] == 2):
                if WhupdateReport:
                    print(k+1, '# trial  was updated.')
                Wh_count=Counter(performance[0:k+1])
                #print(Aud_count)
                if (Wh_count[0]+Wh_count[2]) <= Wh_standard:
                    if SearchReport:
                        print('*normal update')
                    ChunkPer = performance[0 : (k+1)]
                    ChunkStim = stim[0 : (k+1)]
                    ChunkWhStim = whstim[0 : (k+1)]                              
                    if sum((ChunkWhStim == 1)) > 0 :
                        WhHitChunk[k] = sum((ChunkPer == 2))/sum((ChunkWhStim == 1))                
                elif (Wh_count[0]+Wh_count[2]) > Wh_standard:
                    for n in reversed(range(0,k)):
                        if not Wh_SearchDone:
                            Wh_count=Counter(performance[n:k+1])
                            if (Wh_count[0]+Wh_count[2]) == Wh_standard:
                                Wh_SearchDone= True
                                if SearchReport:
                                    print('**searched update')
                                    print('**search report position: ', n)
                                ChunkPer = performance[n : (k+1)]
                                ChunkStim = stim[n : (k+1)]
                                ChunkWhStim = whstim[n : (k+1)]
                                # following part I have changed a lot.                
                                if sum((ChunkWhStim == 1)) > 0 :
                                    WhHitChunk[k] = sum((ChunkPer == 2))/sum((ChunkWhStim == 1))
                    Wh_SearchDone= False  # Note this indent shoud be out of for loop.        
                pWhHitChunk[k] = WhHitChunk[k]
                if WhHitChunk[k] == 1:
                    Half_WhHit = 0.5/(sum((ChunkPer == 2)) + sum((ChunkPer == 0)))             
                    WhHitChunk[k] = 1-Half_WhHit                
                elif WhHitChunk[k] == 0:            
                    Half_WhHit = 0.5/(sum((ChunkPer == 2)) + sum((ChunkPer == 0)))  
                    WhHitChunk[k] = Half_WhHit                
                else:
                    WhHitChunk[k] = WhHitChunk[k]
            else:            
                WhHitChunk[k]   =  WhHitChunk[k-1]
                pWhHitChunk[k] =  pWhHitChunk[k-1]
                   
    print('***Above report for Whisker calculation***')
    
    for k in range(TrialNumber):        
            if (performance[k] == 4 or performance[k] == 5):
                if FAupdateReport:
                    print(k+1, '# trial  was updated.')
                FA_count=Counter(performance[0:k+1])            
                if (FA_count[4]+FA_count[5]) <= FA_standard:
                    if SearchReport:
                        print('*normal update')
                    ChunkPer = performance[0 : (k+1)]
                    ChunkStim = stim[0 : (k+1)]                                            
                    if sum((ChunkStim == 0)) > 0 :
                        FAChunk[k] = sum((ChunkPer == 5))/sum((ChunkStim == 0))                
                elif (FA_count[4]+FA_count[5]) > FA_standard:
                    for n in reversed(range(0,k)):
                        if not FA_SearchDone:
                            FA_count=Counter(performance[n:k+1])
                            if (FA_count[4]+FA_count[5]) == FA_standard:
                                FA_SearchDone= True
                                if SearchReport:
                                    print('**searched update')
                                    print('**search report position: ', n)
                                ChunkPer = performance[n : (k+1)]
                                ChunkStim = stim[n : (k+1)]                                           
                                if sum((ChunkStim == 0)) > 0 :
                                    FAChunk[k] = sum((ChunkPer == 5))/sum((ChunkStim == 0))
                    FA_SearchDone= False  # Note this indent shoud be out of for loop.        
                pFAChunk[k] = FAChunk[k]
                if FAChunk[k] == 1:
                    Half_FAHit = 0.5/(sum((ChunkPer == 5)) + sum((ChunkPer == 4)))             
                    FAChunk[k] = 1-Half_FAHit                
                elif FAChunk[k] == 0:            
                    Half_FAHit = 0.5/(sum((ChunkPer == 5)) + sum((ChunkPer == 4)))  
                    FAChunk[k] = Half_FAHit                
                else:
                    FAChunk[k] = pFAChunk[k]
            else:            
                FAChunk[k]   =  FAChunk[k-1]
                pFAChunk[k] = pFAChunk[k-1]
    print('***Above report for FA calculation***')
    print('***calculation report finished***')
    
    print('***dprime calculation report starts***')
    
    for k in range(TrialNumber):
        if not ((WhHitChunk[k] == 0) or (FAChunk[k] == 0)):
            if (performance[k] == 0 or performance[k] == 2):
                dprime_wh[k] = norm.ppf(WhHitChunk[k]) - norm.ppf(FAChunk[k])
            else:
                dprime_wh[k]= dprime_wh[k-1]
        else:
            dprime_wh[k] = np.nan
    
    print('***Above report for WhHit Dprime calculation***') 
    
    for k in range(TrialNumber):
        if not ((AudHitChunk[k] == 0) or (FAChunk[k] == 0)):
            if (performance[k] == 1 or performance[k] == 3):
                dprime_aud[k] = norm.ppf(AudHitChunk[k]) - norm.ppf(FAChunk[k])
            else:
                dprime_aud[k]= dprime_aud[k-1]
        else:
            dprime_aud[k] = np.nan
    
    print('***Above report for AudHit Dprime calculation***')
    
    
    print('***dprime calculation report finished***')
    
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
    y_axis_label='Probability AudHit/WhHit/FA',
    x_range=(1, TrialNumber),
    title = mouseName + '|' + d 
    )    
    
    dp = bokeh.plotting.figure(
    width=600,
    height=400,
    x_axis_label='Trial Number',
    y_axis_label='dPrime',
    x_range=(1, TrialNumber),
    title = mouseName + '|' + d  
    )    
    
    p.yaxis.axis_label_text_font_style = "bold"
    p.xaxis.axis_label_text_font_style = "bold"
    p.title.align = 'center'
    
    dp.yaxis.axis_label_text_font_style = "bold"
    dp.xaxis.axis_label_text_font_style = "bold"
    dp.title.align = 'center'
    
    
    audh = p.line(
    x= range(TrialNumber),
    y= np.array(pAudHitChunk),
    line_join='bevel',
    line_width=2,
    color = 'blue',
    )
    
    fa = p.line(
    x= range(TrialNumber),
    y= np.array(pFAChunk),
    line_join='bevel',
    line_width=2,
    color = 'red',
    )    
       
    whhit = p.line(
    x= range(TrialNumber),
    y= np.array(pWhHitChunk),
    line_join='bevel',
    line_width=2,
    color = 'black',
    )
    
    d_wh = dp.line(
    x= range(TrialNumber),
    y= np.array(dprime_wh),
    line_join='bevel',
    line_width=2,
    color = 'black',
    )
    
    d_aud = dp.line(
    x= range(TrialNumber),
    y= np.array(dprime_aud),
    line_join='bevel',
    line_width=2,
    color = 'blue',
    )
    
    legend_dp = Legend(items=[
    ("AudStim" , [d_aud]),
    ("WhStim" , [d_wh])
    ], location="center")
    
    
    legend_p = Legend(items=[
    ("AudHit" , [audh]),
    ("WhHit" , [whhit]),
    ("FA" , [fa])   
    ], location="center")
    
    dp.add_layout(legend_dp, 'right')    
    dp.legend.click_policy="hide"
    
    p.add_layout(legend_p, 'right')    
    p.legend.click_policy="hide"
    bokeh.io.show(row(dp,p))
    
    
    WhHitRunning.append(WhHitChunk)
    AudHitRunning.append(AudHitChunk)
    FARunning.append(FAChunk)
    dprimeRunning.append(dprime_wh)
    # These few append lines are used to prepare for the next plot.
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
    print('***Mouse based performance calculation starts***')
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
                    print('***Here ' + str(AudMissInaRow) + ' AudMiss in row detected')
                    StopSession = True

            elif performance[k] == 1:
                AudMiss += 1
                if len(MissFlag) < AudMissInaRow:
                    MissFlag.append(1)
                else:
                    MissFlag = MissFlag[1::]
                    MissFlag.append(1)

                if (sum(MissFlag) == AudMissInaRow):
                    print('***Here ' + str(AudMissInaRow) + ' AudMiss in row detected')
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
                    print('***Here ' + str(AudMissInaRow) + ' AudMiss in row detected')
                    StopSession = True

            elif performance[k] == 3:
                AudHit += 1
                if len(MissFlag) < AudMissInaRow:
                    MissFlag.append(0)
                else:
                    MissFlag = MissFlag[1::]
                    MissFlag.append(0)

                if (sum(MissFlag) == AudMissInaRow):
                    print('***Here ' + str(AudMissInaRow) + ' AudMiss in row detected')
                    StopSession = True

            elif performance[k] == 4:
                CR += 1
                if len(MissFlag) < AudMissInaRow:
                    MissFlag.append(0)
                else:
                    MissFlag = MissFlag[1::]
                    MissFlag.append(0)

                if (sum(MissFlag) == AudMissInaRow):
                    print('***Here ' + str(AudMissInaRow) + ' AudMiss in row detected')
                    StopSession = True

            elif performance[k] == 5:
                FAc += 1
                if len(MissFlag) < AudMissInaRow:
                    MissFlag.append(0)
                else:
                    MissFlag = MissFlag[1::]
                    MissFlag.append(0)

                if (sum(MissFlag) == AudMissInaRow):                
                    print('***Here ' + str(AudMissInaRow) + ' AudMiss in row detected')
                    StopSession = True            
                    
            if whstim[k] == 1:                
                WhStim += 1                
            if audstim[k] == 1:                
                AudStim += 1                
            if  stim[k] == 0:                
                NoStim += 1
    print('***Mouse based information appending starts***')            
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
    print('***Mouse based information appending finished***')
    print('***Mouse based performance calculation finished***')
    
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
