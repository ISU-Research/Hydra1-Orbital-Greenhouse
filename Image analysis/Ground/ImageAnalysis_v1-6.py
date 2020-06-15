# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 16:38:19 2019

@author: jay-dell-1

this script will be used to analize images from Hydra1
manual preprocessing of images is required

v1-1:
WT and TG saved in seperate images- cut from the orignal in Paint.NET saved as png with clear background
this script reads in a single image and calculates summary statistics

v1-2:
will use COM as the index
use class structure
assume top of image is WT and bottom is TG
plot COM over time for 4 cases: WT/TG and flight/ground

-uses seperate data lists to store objects- defeats the point of saving metadata in a class structure
    would be better to store all objects in one list then use if statments to extract the data
    
v1-3:
    added pixel counting
    added csv export
    
v1-4:
    added histograms of greenness
    
v1-5:
    adjust time handeling 
    prepare for public release 
    add functionality to avoid file write overs
    
v1-6:
    integrate background calculations

"""

from PIL import Image
from matplotlib import pyplot
import colorsys
import numpy as np
import time
import os
import csv

############### user inputs ################
location='ground' #set the location of the samples flight or ground
index=4 # 0) R, 1) G, 2) B, 3) normalized red, 4) normalized green, 5) normalized blue, 6) ExG, 7) ExGR, 8) VEG, 9) CIVE, 10) COM, 11) DGCI

mask_WT_metal=[0,0,255] #set the mask colors if calculating background
mask_WT_paper=[255,0,0] # list is [R,G,B]
mask_TG_metal=[0,255,0] # 255 is max, 0 is min
mask_TG_paper=[0,255,255] 

calculate_leaves=True
calculate_timeline_plot=True
calculate_histograms=False
calculate_background=True #automatically exports to csv
export_to_csv=True #only applies to leaves


########################## define sample class ######################################
class sample():
    def __init__(self,name): #initilize the class with generic values or ones that can be calculated
        self.name=name
        self.file=name.split('\\')[-1]
        self.time=time.mktime(time.strptime(self.file[4:22],'%Y-%m-%d %H_%M_%S'))
        self.location='unknown' #give as string 'flight' or 'ground'
        self.genetic='unknown' #give as 'WT' or 'TG'
        self.Indexes=[0,1,2,3,4,5,6,7,8,9,10,11]
        self.index=4 #setnormalized green as default 
        self.image=Image.open(name)
        self.data=[]
        self.mask_metal=[]
        self.background_metal_data=[]
        self.background_metal_stats=[np.nan,np.nan,np.nan]
        self.mask_paper=[]
        self.background_paper_data=[]
        self.background_paper_stats=[np.nan,np.nan,np.nan]
        self.plant_stats=[np.nan,np.nan,np.nan]
        self.pixel_count=0
        
        
    def getWT(self): #sets the image for analysis to the top half
        #2048w by 1536h 50% height is 768
        #get top portion of the photo
        #dont use on background or you are going to have a bad time
        self.image=self.image.crop((0,0,2048,768)) #L,T,R,B
        
    def getTG(self): #sets the image for analysis to the bottom half
        #2048w by 1536h 50% height is 768
        #get top portion of the photo
        #dont use on background or you are going to have a bad time
        self.image=self.image.crop((0,769,2048,1536)) #L,T,R,B
        
    def setLocation(self,location): #set flight or ground and addjusts the time accrdingly (the ground unit was run on a delay)
        self.location=location
        if location=='flight':
            self.time=(self.time-1545150962.0)/86400 #normalize to relative time
        if location=='ground':
            self.time=(self.time-1545252424.0)/86400 #normalize to relative time 
        
    def setGenetic(self,genetic): #sets the sample type to transgenic (TG) or wild type (WT)
        self.genetic=genetic
    
    def setIndex(self,index): #sets the specific index type that should be used in analysis
        self.index=index
        
    def getMask(self,color,mask_type):
        path=os.getcwd()#getCWD
    
        files=os.listdir(path)
        for file in files:
            if file==self.location+'_mask.png':
                mask_file=path+'\\'+file 
        if len(mask_file)>1:
            image_mask=Image.open(mask_file)
            image_mask_data=list(image_mask.getdata())
            
            if mask_type=='background_metal':
                for i in range(len(image_mask_data)):
                    if image_mask_data[i][0]==color[0] and image_mask_data[i][1]==color[1] and image_mask_data[i][2]==color[2]: #if pixle is color 
                        self.mask_metal.append(i)
                        
            elif mask_type=='background_paper':
                for i in range(len(image_mask_data)):
                    if image_mask_data[i][0]==color[0] and image_mask_data[i][1]==color[1] and image_mask_data[i][2]==color[2]: #if pixle is color 
                        self.mask_paper.append(i) #stores the pixel location of the mask
                
        else:
            print('Mask file not found: check mask file name and location name')

        #print('getMask len image_mask_data'+str(len(image_mask_data)))
        #print('getMask len self.background_paper: '+str(len(self.mask_paper)))

    def calculateIndexes(self, data_type): # calculates all of the index types for each pixel, self.index sets which of these to use
        
        if data_type=='plants':
            data=list(self.image.getdata())
        elif data_type=='background_metal':
            image=list(self.image.getdata())
            data=[]
            for i in range(len(self.mask_metal)):
                data.append(image[self.mask_metal[i]])
        elif data_type=='background_paper':
            image=list(self.image.getdata())
            data=[]
            for i in range(len(self.mask_paper)):
                data.append(image[self.mask_paper[i]])
        ### thee is an issue in that mask is not storing location but storing the color of the mask...
        #print('calculateIndexs: '+str(len(data)))
        
        
        Rs=[]
        Gs=[]
        Bs=[]
        rs=[]
        gs=[]
        bs=[]
        ExGs=[]
        ExGRs=[]
        VEGs=[]
        CIVEs=[]
        COMs=[]
        DGCIs=[]
        count=0

        for i in range(len(data)):
            #print(data[i])
            if data[i][0]<255 and data[i][1]<255 and data[i][2]<255: #filter out blanks
                
                count=count+1
                R=data[i][0]
                G=data[i][1]
                B=data[i][2]
                
                ### normalized bands
                r=R/(R+G+B)
                g=G/(R+G+B)
                b=B/(R+G+B)
                
                ### RGB indexes
                ExG=2*g-r-b
                ExGR=ExG-(1.4*r-g)
                
                if data_type=='plants': ## the division here is to preserve what was previously 2 different scripts
                    try:# there is an issue where some pixels have no blue casig divide by 0 issue
                        VEG=g/(r**0.667*b**0.333)
                    except:
                        VEG=g/(r**0.667*(1/255)**0.333)# setsB to 1 so not 0 but very small
                        
                else:
                    try:# there is an issue where some pixels have no blue causig divide by 0 issue
                        VEG=g/(r**0.667*b**0.333)
                    except:
                        try:
                            VEG=g/(r**.667*(1/255)**0.333)# setsB to 1 so not 0 but very small
                        except:
                            VEG==g/(1**.667*b**0.333) # a few background pixels had no red- not sure why this caused /0 error
                    
                    
                    
                #print(VEG)      
                CIVE=0.441*r-0.881*g+0.385*b+18.78745
                COM=0.25*ExG+0.30*ExGR+0.33*CIVE+0.12*VEG
                
                ### calculate HSV and HSV indexes
                HSV=colorsys.rgb_to_hsv(R/255, G/255, B/255)
                H=HSV[0]*360
                S=HSV[1]
                V=HSV[2]
                
                DGCI=((H-60)/60+(1-S)+(1-V))/3
                
                Rs.append(R)
                Gs.append(G)
                Bs.append(B)
                rs.append(r)
                gs.append(g)
                bs.append(b)
                ExGs.append(ExG)
                ExGRs.append(ExGR)
                VEGs.append(VEG)
                CIVEs.append(CIVE)
                COMs.append(COM)
                DGCIs.append(DGCI)
                
        
        if data_type=='plants':
            self.Indexes=[Rs,Gs,Bs,rs,gs,bs,ExGs,ExGRs,VEGs,CIVEs,COMs,DGCIs]
            self.pixel_count=count
        elif data_type=='background_metal':
            self.background_metal_data=[Rs,Gs,Bs,rs,gs,bs,ExGs,ExGRs,VEGs,CIVEs,COMs,DGCIs]
        elif data_type=='background_paper':
            self.background_paper_data=[Rs,Gs,Bs,rs,gs,bs,ExGs,ExGRs,VEGs,CIVEs,COMs,DGCIs]
            #print(self.background_paper)
        
    def calculateStatistics(self, data_type): #calculates summary statistics of the pixels for the index type of interest (set in self.index)
        
        if data_type=='plants':
            data=self.Indexes
        elif data_type=='background_paper':
            data=self.background_paper_data
        elif data_type=='background_metal':
            data=self.background_metal_data
        
        mean=np.mean(data[self.index])
        median=np.median(data[self.index])
        std=np.std(data[self.index])
        
        if data_type=='plants':
            self.plant_stats=[mean,median,std]
        elif data_type=='background_paper':
            self.background_paper_stats=[mean,median,std]
        elif data_type=='background_metal':
            self.background_metal_stats=[mean,median,std]
            
##################### end sample class ####################


############################### run script ########################
path=os.getcwd()#get current working directory
results_folder=path+'\\results'+str(time.time())
os.mkdir(results_folder) #make a new folder where outputs are saved. each folder is timestamped with current unix epoch time

if calculate_leaves==True:
        
    ########### get list of files ################
    names=[]
    files=os.listdir(path) #get all files in current working directory
    for file in files:
        if file[-9:-4]=='paste': #pull the files with "paste" extention 
            names.append(path+'\\'+file) #add these files to a list
    
    ########## extract data from images ############
    
    list_WT=[]
    list_TG=[]
    list_time=[]
    
    for name in names: #for each "paste" file
        print(name)# this just helps track progress while script is running
        
        #work through the methods for the WT half of each "paste" image
        sampleWT=sample(name)
        sampleWT.getWT()
        sampleWT.setLocation(location)
        sampleWT.setGenetic('WT')
        sampleWT.setIndex(index)
        sampleWT.calculateIndexes('plants')
        sampleWT.calculateStatistics('plants')
        list_WT.append(sampleWT) #store the sample in a list to recall later
        
        #work through the methods for the TG half of each "paste" image
        sampleTG=sample(name)
        sampleTG.getTG()
        sampleTG.setLocation(location)
        sampleTG.setGenetic('TG')
        sampleTG.setIndex(index)
        sampleTG.calculateIndexes('plants')
        sampleTG.calculateStatistics('plants')
        list_TG.append(sampleTG) #store the sample in a list to recall later
        
        list_time.append(sampleWT.time)# make a list of the sample times for use below
        

    

########## format data for export and write it to csv ##################
if export_to_csv==True and calculate_leaves==True:
    export=[['location','Plant type','Image','Time (s)','Index '+str(index),'Pixel Count']] #header
    
    #add WT data to export list
    flightWT=[]
    for i in range(len(list_WT)):
        flightWT.append(list_WT[i].plant_stats[0])
        row=[location,'WT']
        row.append(list_WT[i].file)
        row.append(list_WT[i].time)
        row.append(list_WT[i].plant_stats[1]) #0=mean, 1=median, 2=stdev
        row.append(list_WT[i].pixel_count)
        export.append(row)
    
    #add TG data to expoer list
    flightTG=[]
    for i in range(len(list_TG)):
        flightTG.append(list_TG[i].plant_stats[1])
        row=[location,'TG']
        row.append(list_TG[i].file)
        row.append(list_WT[i].time)
        row.append(list_TG[i].plant_stats[1])
        row.append(list_TG[i].pixel_count)
        export.append(row)
   
    #export data to csv 
    with open(results_folder+'\\ImageAnalysis_v1-6_output.csv','a', newline='') as out_file:
        out_csv=csv.writer(out_file)
        for row in export:
            out_csv.writerow(row)


############ build plots ###################

if calculate_timeline_plot==True:

    pyplot.figure()
    pyplot.plot(list_time,flightWT,'gs-',label='WT')
    pyplot.plot(list_time,flightTG,'ks-',label='TG')

    pyplot.legend(loc='upper left')
    pyplot.show()


############ build histograms #############################

## try same axis for ground and flight (heighgt) if not use if statment to use 2 different heights
## consider setting bins

if calculate_histograms==True:
    
    os.mkdir(results_folder+'\\histograms')
    
    for i in range(len(list_WT)):
        sampleWT=list_WT[i]
        dataWT=sampleWT.Indexes[sampleWT.index]
        sampleTG=list_TG[i]
        dataTG=sampleTG.Indexes[sampleTG.index]
        
        pyplot.figure()
        pyplot.hist([dataWT,dataTG],stacked=True,color=['g','k'],bins=100)
        pyplot.axis([0.2,0.6,0,4000])
        pyplot.savefig(results_folder+'\\histograms\\'+sampleWT.file[0:-9]+'hist.jpg')
        pyplot.close()


############## calculate background ########################


if calculate_background==True:
    #get cut files
    names=[]
    files=os.listdir(path) #get all files in current working directory
    for file in files:
        if file[-8:]=='_cut.png': #pull the files with "cut" extention, use cut so minimal plats can be in the way
            names.append(path+'\\'+file) #add these files to a list
            
    list_WT=[]
    list_TG=[]
    #list_time=[]
    
    for name in names: #for each "cut" file
        print(name)# this just helps track progress while script is running
        
        #work through the methods for the WT half of each "cut" image
        sampleWT=sample(name)
        #sampleWT.getWT()
        sampleWT.setLocation(location)
        sampleWT.setGenetic('WT')
        sampleWT.setIndex(index)
        sampleWT.getMask(mask_WT_metal,'background_metal')
        sampleWT.getMask(mask_WT_paper,'background_paper')
        sampleWT.calculateIndexes('background_metal')
        sampleWT.calculateIndexes('background_paper')
        sampleWT.calculateStatistics('background_metal')
        sampleWT.calculateStatistics('background_paper')
        list_WT.append(sampleWT) #store the sample in a list to recall later
        
        #work through the methods for the TG half of each "cut" image
        sampleTG=sample(name)
        #sampleTG.getTG()
        sampleTG.setLocation(location)
        sampleTG.setGenetic('TG')
        sampleTG.setIndex(index)
        sampleTG.getMask(mask_TG_metal,'background_metal')
        sampleTG.getMask(mask_TG_paper,'background_paper')
        sampleTG.calculateIndexes('background_metal')
        sampleTG.calculateIndexes('background_paper')
        sampleTG.calculateStatistics('background_metal')
        sampleTG.calculateStatistics('background_paper')
        list_TG.append(sampleTG) #store the sample in a list to recall later
        
        #list_time.append(sampleWT.time)# make a list of the sample times for use below
        
    
    ### export background data
    
    export=[['location','Plant type','Image','Time (s)','Background Paper: Index '+str(index),'Background Metal: Index '+str(index)]] #header
    print('export')
    #add WT data to export list
    #flightWT=[]
    for i in range(len(list_WT)):
        row=[location,'WT']
        row.append(list_WT[i].file)
        row.append(list_WT[i].time)
        row.append(list_WT[i].background_paper_stats[1])
        row.append(list_WT[i].background_metal_stats[1])
        export.append(row)
    
    #add TG data to expoer list
    #flightTG=[]
    for i in range(len(list_TG)):
        row=[location,'TG']
        row.append(list_WT[i].file)
        row.append(list_TG[i].time)
        row.append(list_TG[i].background_paper_stats[1])
        row.append(list_TG[i].background_metal_stats[1])
        export.append(row)
   
    #export data to csv 
    with open(results_folder+'\\ImageAnalysis_v1-6_BackgroundOutput.csv','a', newline='') as out_file:
        out_csv=csv.writer(out_file)
        for row in export:
            out_csv.writerow(row)
    #work through class methods
    #test that outputs are correct
print('done')
