################################# Hydra 1 ##############################################
#This is intial release of the Hydra 1 software. The software will be modified in accordance with the software requirements for the project.
#Written by: Yadvender S Dhillon
# Functionalities of the Program:
#1. To activate and deactivate the valve based on the User Input
#2. To activate the Camera and Camera lights based on User input
#3. To activate the fully automatic functionality of the Hydra1 code based on User Input, which is as follows
#   - Turn on the Growth LEDs
#   - Turn off the Growth LEDs every 6 hours
#   - Tun on the Growth LEDs
#   - Turn on the Camera, click a high definition image
#   - To store the the time stamped image on Rasperry Pi memeory card
#   - Turn off the white LEDs
#   - Turn the Growth LEds back on
#   - Repeat the steps above every 6 hours
#4. To log the errors generated (if anay) in the program
#5. To create a time stamped log of switching and switching off the valve
#6. Create a log of time satamped manaually taken pictures
#Another code runs simultaneoulsy to this program to monitor the Temperature in the cube.
########################################################################################


#Importing all the Libraries required for the code
import RPi.GPIO as GPIO # to control the GPIO pins of the Pi
import time # To control the time stamp and time the evets in the program
import os
import os.path
import sys
import csv   # To store the files in Csv format
import datetime # Another library to keep time the ecvents
import cv2 # Opencv to activate camera
import math # to perform matehematical functions, caluation on number of hours etc
import numpy # in addition opencv library, this library is required to render images

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)



Valve_Port=15
WhiteLED_Port =11
GrowthLED_Port=13

GPIO.setup(Valve_Port,GPIO.OUT)
GPIO.setup(WhiteLED_Port,GPIO.OUT)
GPIO.setup(GrowthLED_Port,GPIO.OUT)

GPIO.output(GrowthLED_Port, 0) # Growth LED off
GPIO.output(Valve_Port,0) # vALVE off
GPIO.output(WhiteLED_Port, 0) # White LED off

############################################################################################
#Mentod name Name: ActivateValve()
#Input parameters: none
#Output: None
#Functionality: To activae the Valve. This is to be used in manaul Mode. This method should be followed with command to de activate the valve.
def ActivateValve():
    try:
        
        GPIO.output(WhiteLED_Port, 0) # This command deactivates the White LEDs, if it is on
        GPIO.output(GrowthLED_Port,0) # This command deactivates the Growth LEDs, if it is on
        GPIO.output(Valve_Port,1) # This command activates the Valave
        x = time.asctime()  # for time stamp in the temperature file file
        with open(os.path.join('/home/pi/Hydra1Log/Valve/ValveLog.txt'), 'a') as csvfile:  # to valave activation log
                writer = csv.DictWriter(csvfile, fieldnames=['Time', 'ValveStatus'], lineterminator='\n')
                writer.writerow({'Time': x, 'ValveStatus': 'valve Openend'})
        csvfile.close()
        time.sleep(10)
    except:
        x=time.asctime()
        with open(os.path.join('/home/pi/Hydra1Log/TryCatch/Trycatch.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
                writer = csv.DictWriter(csvfile, fieldnames=['Time', 'tryCatch'], lineterminator='\n')
                writer.writerow({'Time': x, 'tryCatch': 'Activatevalve'})
        csvfile.close()

    
############################################################################################
#Mentod name Name: DeActivateValve()
#Input parameters: none
#Output: None
#Functionality: To deactivate the Valve. This is to be function is used in manaul Mode. This method should be followed with command to de activate the valve.
def DeActivateValve():
    try:
        
        GPIO.output(WhiteLED_Port, 0) # This command deactivates the White LEDs, if it is on
        GPIO.output(GrowthLED_Port,0) # This command deactivates the Growth LEDs, if it is on
        GPIO.output(Valve_Port,0) # This command deactivates the Valave
        x = time.asctime()  # for time stamp in the temperature file file
        with open(os.path.join('/home/pi/Hydra1Log/Valve/ValveLog.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
                writer = csv.DictWriter(csvfile, fieldnames=['Time', 'ValveStatus'], lineterminator='\n')
                writer.writerow({'Time': x, 'ValveStatus': 'Valve Closed'})
        csvfile.close()
        time.sleep(10)
    except:
        x=time.asctime()
        with open(os.path.join('/home/pi/Hydra1Log/TryCatch/Trycatch.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
                writer = csv.DictWriter(csvfile, fieldnames=['Time', 'tryCatch'], lineterminator='\n')
                writer.writerow({'Time': x, 'tryCatch': 'Deactivatevalve'})
        csvfile.close()

    
############################################################################################
#Mentod name Name: CaptureImage()
#Input parameters: none
#Output: None
    
#Functionality:
#   -To activate the White LEDs
#   -Open the file to read the brightness
#   -To capture the Image
#   -To Store the timestamped Image
#   -To turnoff the growth LEDs
def CaptureImage():
    try:
        
        GPIO.output(Valve_Port,0) # This command deactivates the Valave, if it is on
        GPIO.output(GrowthLED_Port, 0) # This command activates the White LEDs
        # To set the intensity of the White LEds from the file
        PWMIntensity=0
        PWMError= 'No Error' # 
        if(os.path.exists('/home/pi/Hydra1/LEDConfiguration/WhiteLEDConfiguration.txt')):
            file= open('/home/pi/Hydra1/LEDConfiguration/WhiteLEDConfiguration.txt','r')
            File_Read=file.readline()
            file.close()
            In_File_Read=int(File_Read)
            if(In_File_Read >= 0 and In_File_Read <= 100):
                PWMIntensity = In_File_Read
            else:
                PWMIntensity =100
                PWMError='File Error- Value out of range'
        else:
            PWMIntensity = 100
            PWMError='File Error- File Not Present'
                              
        WhiteLED=GPIO.PWM(WhiteLED_Port,100)
        WhiteLED.start(0)
        WhiteLED.ChangeDutyCycle(PWMIntensity)
        #White Light Intensity set
        
            
        camera = cv2.VideoCapture(0)# Open the Camera
        
        IsCameraOpened = camera.isOpened() # check if the camera is opened
        #Setting the resolution for the Camera
        camera.set(3,1920)
        camera.set(4,1080)

        # capture the image, Image contains the image taken and rerturn_value contains if the Value is taken.
        return_value, image = camera.read()
       
        #print return_value
        
        image_name= "/home/pi/Hydra1/ManaualImageCapture/Img-"+str(datetime.datetime.now())+".png"
        #print 'image name set'
        cv2.imwrite(os.path.join(image_name), image) # File Stored
        
        #camera.release()
        del(camera) # Camerta instance deleted

        x=time.asctime()
        with open(os.path.join('/home/pi/Hydra1Log/manualImageCapture/ImageLog.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
                writer = csv.DictWriter(csvfile, fieldnames=['Time', 'WhiteLEDStatus','PWM Intensity','LEDError','IsCameraOpened', 'IsImageTaken'], lineterminator='\n')
                writer.writerow({'Time': x, 'WhiteLEDStatus': 'ActivatedWhiteLEDs','PWMIntensity':PWMIntensity,'LEDError':PWMError,'IsCameraOpened': IsCameraOpened, 'IsImageTaken': return_value})
        csvfile.close()

        WhiteLED.ChangeDutyCycle(0)

       
        GPIO.output(13, 0)
        GPIO.output(11, 0)
        GPIO.output(15,0)
    except:
        x=time.asctime()
        with open(os.path.join('/home/pi/Hydra1Log/TryCatch/Trycatch.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
                writer = csv.DictWriter(csvfile, fieldnames=['Time', 'tryCatch'], lineterminator='\n')
                writer.writerow({'Time': x, 'tryCatch': 'CaptureImage'})
        csvfile.close()
   


############################################################################################
#Mentod name Name: GrowthLeds()
#Input parameters: none
#Output: None
#Functionality: 
#   -To activate the Growth LEDs
#   -To read LED intensity from the configuration file
#   -To log error if the file is not present and set the LED intensity to 100
#   -To log error is the read intensity vale is out of range and set the Light Intensity to maximum
#   - To Turn off the Growth LED when requested by User
#   - To record if wrong command is given to tun off the LEDs by user
def GrowthLeds():
    try:
        
        GPIO.output(Valve_Port,0) # This command deactivates the Valave, if it is on
        GPIO.output(WhiteLED_Port, 0) # This command activates the White LEDs
        PWMIntensity=0
        PWMError= 'No Error' # 
        
        if(os.path.exists('/home/pi/Hydra1/LEDConfiguration/GrowthLEDConfiguration.txt')):
            file= open('/home/pi/Hydra1/LEDConfiguration/GrowthLEDConfiguration.txt','r')
            File_Read=int(file.readline())
            file.close()
            
            if(File_Read >= 0 and File_Read <= 100):
                PWMIntensity = File_Read
                
            else:
                PWMIntensity =100
                PWMError='File Error- Value out of range'
                
        else:
            PWMIntensity = 100
            PWMError='File Error- File Not Present'
            
                              
        GrowthLED=GPIO.PWM(GrowthLED_Port,100)
        GrowthLED.start(0)
        x=time.asctime()
        
        with open(os.path.join('/home/pi/Hydra1Log/GrowthLED/GrowthLEDLog.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
                writer = csv.DictWriter(csvfile, fieldnames=['Time', 'GrowthLEDStatus','PWMIntensity','Error'], lineterminator='\n')
                writer.writerow({'Time': x, 'GrowthLEDStatus': 'ActivatedGrowthLEDs','PWMIntensity':PWMIntensity,'Error':PWMError})
        csvfile.close()
        
        while True:
            GrowthLED.ChangeDutyCycle(PWMIntensity)
            time.sleep(10)
            
            commandtwo=sys.stdin.readline().rstrip('\n')       

            if (commandtwo== 'StopGrowthLED'):
                GrowthLED.ChangeDutyCycle(0)
                x=time.asctime()
                with open(os.path.join('/home/pi/Hydra1Log/GrowthLED/GrowthLEDLog.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
                    writer = csv.DictWriter(csvfile, fieldnames=['Time', 'GrowthLEDStatus','PWM Intensity','Error'], lineterminator='\n')
                    writer.writerow({'Time': x, 'GrowthLEDStatus': 'Deactivated Growth LEds','PWMIntensity':'N/A','Error':'N/A'})
                csvfile.close()
                break
            else:
                x=time.asctime()
                with open(os.path.join('/home/pi/Hydra1Log/GrowthLED/GrowthLEDLog.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
                    writer = csv.DictWriter(csvfile, fieldnames=['Time', 'GrowthLEDStatus','PWM Intensity','Error'], lineterminator='\n')
                    writer.writerow({'Time': x, 'GrowthLEDStatus': 'Wrong Command for Deactivation','PWMIntensity':'N/A','Error':commandtwo})
                csvfile.close()
                continue
    except:
        x=time.asctime()
        with open(os.path.join('/home/pi/Hydra1Log/TryCatch/Trycatch.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
            writer = csv.DictWriter(csvfile, fieldnames=['Time', 'tryCatch'], lineterminator='\n')
            writer.writerow({'Time': x, 'tryCatch': 'GrowthLEDs'})
        csvfile.close()
        
############################################################################################
#Mentod name Name: WhiteLeds()
#Input parameters: none
#Output: None
#Functionality: 
#   -To activate theWhite LEDs
#   -To read white LED intensity from the configuration file
#   -To log error if the file is not present and set the white LED intensity to 100
#   -To log error is the read white led intensity vale is out of range and set the Light Intensity to maximum
#   - To Turn off the white LED when requested by User
#   - To record if wrong command is given to tun off the white LEDs by user

def WhiteLeds():
    try:
        
        GPIO.output(Valve_Port,0) # This command deactivates the Valave, if it is on
        GPIO.output(GrowthLED_Port, 0) # This command activates the White LEDs
        PWMIntensity=0
        PWMError= 'No Error' # 
        #print 'step 1'
        if(os.path.exists('/home/pi/Hydra1/LEDConfiguration/WhiteLEDConfiguration.txt')):
            file= open('/home/pi/Hydra1/LEDConfiguration/WhiteLEDConfiguration.txt','r')
            File_Read=int(file.readline())
            file.close()
            if(File_Read >= 0 and File_Read <= 100):
                PWMIntensity = File_Read
            else:
                PWMIntensity =100
                PWMError='File Error- Value out of range'
        else:
            PWMIntensity = 100
            PWMError='File Error- File Not Present'
            #print PWMError
                              
        WhiteLED=GPIO.PWM(WhiteLED_Port,100)
        WhiteLED.start(0)
        x=time.asctime()
        with open(os.path.join('/home/pi/Hydra1Log/WhiteLED/WhiteLEDLog.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
                writer = csv.DictWriter(csvfile, fieldnames=['Time','WhiteLEDStatus','PWMIntensity','Error'], lineterminator='\n')
                writer.writerow({'Time': x, 'WhiteLEDStatus': 'ActivatedWhiteLEDs','PWMIntensity':PWMIntensity,'Error':PWMError})
        csvfile.close()
        #print 'just before while'
        while True:
            WhiteLED.ChangeDutyCycle(PWMIntensity)
            time.sleep(0.1)
            commandtwo=sys.stdin.readline().rstrip('\n')
            if commandtwo== 'StopWhiteLED':
                WhiteLED.ChangeDutyCycle(0)
                x=time.asctime()
                with open(os.path.join('/home/pi/Hydra1Log/WhiteLED/WhiteLEDLog.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
                    writer = csv.DictWriter(csvfile, fieldnames=['Time', 'WhiteLEDStatus','PWMIntensity','Error'], lineterminator='\n')
                    writer.writerow({'Time': x, 'WhiteLEDStatus': 'Deactivated LEds','PWMIntensity':'N/A','Error':'N/A'})
                csvfile.close()
                break
            else:
                x=time.asctime()
                with open(os.path.join('/home/pi/Hydra1Log/WhiteLED/WhiteLEDLog.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
                    writer = csv.DictWriter(csvfile, fieldnames=['Time', 'WhiteLEDStatus','PWMIntensity','Error'], lineterminator='\n')
                    writer.writerow({'Time': x, 'WhiteLEDStatus': 'Wrong Command Given','PWMIntensity':'N/A','Error':commandtwo})
                csvfile.close()
                continue
    except:
        x=time.asctime()
        with open(os.path.join('/home/pi/Hydra1Log/TryCatch/Trycatch.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
            writer = csv.DictWriter(csvfile, fieldnames=['Time', 'tryCatch'], lineterminator='\n')
            writer.writerow({'Time': x, 'tryCatch': 'WhiteLEds'})
        csvfile.close()
            
        
#######################################################################################################

def Hydra1Automatic():
    GPIO.output(GrowthLED_Port, 0) # Growth LED off
    GPIO.output(Valve_Port,0) # vALVE off
    GPIO.output(WhiteLED_Port, 0) # White LED off
    GPIO.output(Valve_Port,0) # This command deactivates the Valave, if it is on
    GPIO.output(WhiteLED_Port, 0) # This command activates the White LEDs
    try:
                
        PWMIntensity=0
        PWMError= 'No Error' #
        print 'Try 1' 
        if(os.path.exists('/home/pi/Hydra1/LEDConfiguration/GrowthLEDConfiguration.txt')):
            file= open('/home/pi/Hydra1/LEDConfiguration/GrowthLEDConfiguration.txt','r')
            File_Read=int(file.readline())
            file.close()
            if(File_Read >= 0 and File_Read <= 100):
                PWMIntensity = File_Read
            else:
                PWMIntensity =100
                PWMError='File Error- Value out of range'
        else:
            PWMIntensity = 100
            PWMError='File Error- File Not Present'
            print 'Growth LED file not present'                  
        GrowthLED=GPIO.PWM(GrowthLED_Port,100)
        GrowthLED.start(0)
        x=time.asctime()
        with open(os.path.join('/home/pi/Hydra1Log/Automatic/GrowthLED/GrowthLEDLog.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
                writer = csv.DictWriter(csvfile, fieldnames=['Time', 'GrowthLEDStatus','PWMIntensity','Error'], lineterminator='\n')
                writer.writerow({'Time': x, 'GrowthLEDStatus': 'ActivatedGrowthLEDs','PWMIntensity':PWMIntensity,'Error':PWMError})
        csvfile.close()
        datebefore=datetime.datetime.now()

        print 'Just before while'
        while True:
            #command2=sys.stdin.readline().rstrip('\n')
            #if command2 == "StopHydra1":
             #   break
            #else:
             #   continue
            
            print 'after second input'
            
            GrowthLED.ChangeDutyCycle(PWMIntensity)
            time.sleep(0.1)
            dateafter=datetime.datetime.now()
            hours=math.floor(((dateafter-datebefore).seconds)/60)  ## Change to 3600
            if (hours > 1):
                    print 'enter while loop after 4 minutes'
                    GrowthLED.ChangeDutyCycle(0)

                    GPIO.output(GrowthLED_Port, 0)
                    # To set the intensity of the White LEds from the file
                    WhitePWMIntensity=0
                    WhitePWMError= 'No Error' # 
                    x=time.asctime()
                    if(os.path.exists('/home/pi/Hydra1/LEDConfiguration/WhiteLEDConfiguration.txt')):
                        file= open('/home/pi/Hydra1/LEDConfiguration/WhiteLEDConfiguration.txt','r')
                        File_Read=int(file.readline())
                        file.close()
                        if(File_Read >= 0 and File_Read <= 100):
                            WhitePWMIntensity = File_Read
                        else:
                            WhitePWMIntensity =100
                            WhitePWMError='File Error- Value out of range'
                    else:
                        WhitePWMIntensity = 100
                        WhitePWMError='File Error- File Not Present'
                                          
                    WhiteLED=GPIO.PWM(WhiteLED_Port,100)
                    WhiteLED.start(0)
                    time.sleep(0.1)
                    WhiteLED.ChangeDutyCycle(WhitePWMIntensity)
                    #White Light Intensity set
                    
                        
                    camera = cv2.VideoCapture(0)# Open the Camera
                    
                    IsCameraOpened = camera.isOpened() # check if the camera is opened
                    #Setting the resolution for the Camera
                    camera.set(3,1920)
                    camera.set(4,1080)

                    # capture the image, Image contains the image taken and rerturn_value contains if the Value is taken.
                    return_value, image = camera.read()
                   
                    print return_value
                    x=time.asctime()
                    image_name= "/home/pi/Hydra1/AutomaticImageCapture/Img-"+str(datetime.datetime.now())+".png"
                    print 'image name set'
                    

                    cv2.imwrite(os.path.join(image_name), image) # File Stored
                    print 'image captured'
                    #camera.release()
                    del(camera) # Camerta instance deleted

                    x=time.asctime()
                    print x
                    with open(os.path.join('/home/pi/Hydra1Log/Automatic/AutomaticImageCapture/ImageLog.txt'), 'a') as csvfile:  # to store log data in a file, as txt file
                            writer = csv.DictWriter(csvfile, fieldnames=['Time', 'WhiteLEDStatus', 'PWMIntensity', 'LEDError', 'IsCameraOpened', 'IsImageTaken'], lineterminator='\n')
                            writer.writerow({'Time': x, 'WhiteLEDStatus': 'ActivatedWhiteLEDs', 'PWMIntensity': WhitePWMIntensity, 'LEDError': WhitePWMError, 'IsCameraOpened': IsCameraOpened, 'IsImageTaken': return_value})
                    csvfile.close()
                    print 'stored in file'

                    WhiteLED.ChangeDutyCycle(0)
                    
                    GPIO.output(WhiteLED_Port, 0)
                    
                    GrowthLED=GPIO.PWM(GrowthLED_Port,100)
                    GrowthLED.start(0)
                    datebefore=datetime.datetime.now()
                    print 'end of if'
                    #break
            else:
                continue
    except:
        x=time.asctime()
        with open(os.path.join('/home/pi/Hydra1Log/TryCatch/Trycatch.txt'), 'a') as csvfile:  # to store temperature data in a file, as txt file
            writer = csv.DictWriter(csvfile, fieldnames=['Time', 'tryCatch'], lineterminator='\n')
            writer.writerow({'Time': x, 'tryCatch': 'Hydra1Automatic'})
        csvfile.close()
            
                 
            
          
    
        
while True:
    command=sys.stdin.readline().rstrip('\n')
    if command== "ActivateValve":
        ActivateValve()
    elif command== "DeactivateValve":
        DeActivateValve()
    elif command== "ActivateGrowthLED":
        GrowthLeds()
    elif command=="ActivateWhiteLED":
        WhiteLeds()
    elif command=="CaptureImage":
        CaptureImage()
    elif command =="ActivateHydra1":
        Hydra1Automatic()
        
        
        
    
        



