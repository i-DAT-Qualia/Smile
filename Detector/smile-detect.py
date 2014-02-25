#!/usr/bin/env python
import cv
import time
import Image
import mosquitto
import threading

#sets up the UI window
cv.NamedWindow("camera", 1)
capture = cv.CreateCameraCapture(0)

#Set the resolution to your camera
#width = int(320 * 1.5)
#height = int(240 * 1.5)
#To Match MS Lifecam studio
width = 640
height = 360
smileness = 0
smilecount = 0

smileList = []

#Sets colours 
smilecolor = cv.RGB(0, 255, 0)
lowercolor = cv.RGB(0, 0, 255)
facecolor = cv.RGB(255, 0, 0)
font = cv.InitFont(1, 1, 1, 1, 1, 1)
sFont = cv.InitFont(1, 0.7, 0.7, 1, 1, 1)

#sets up the output from the camera
cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_WIDTH,width)    
cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_HEIGHT,height) 
result = cv.CreateImage((width,height),cv.IPL_DEPTH_8U,3) 

#loads the MQTT client and connects in a seperate thread -
#So we don't block the script running
class mqThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.mqttc = mosquitto.Mosquitto()
    def run(self):
        self.mqttc.connect("127.0.0.1", 1883, 60)
        print "connected"
        
        while True:
            self.mqttc.loop()
    def publish(self):
        self.mqttc.publish("smiles", "smile", 0)
            
mT = mqThread()
mT.start()
        



#openCV functions
def Load():

    return (faceCascade, smileCascade)

def Display(image):
    #opens up the window
    cv.NamedWindow("Smile Test")
    cv.ShowImage("Smile Test", image)
    cv.WaitKey(0)
    cv.DestroyWindow("Smile Test")

def DetectFacesSmiles(image, faceCascade, smileCascade):
    min_size = (20,20)
    image_scale = 2
    haar_scale = 1.2
    min_neighbors = 2
    haar_flags = 0
    
    global smileList

    # Allocate the temporary images
    gray = cv.CreateImage((image.width, image.height), 8, 1)
    smallImage = cv.CreateImage((cv.Round(image.width / image_scale),cv.Round (image.height / image_scale)), 8 ,1)

    # Convert color input image to grayscale
    cv.CvtColor(image, gray, cv.CV_BGR2GRAY)

    # Scale input image for faster processing
    cv.Resize(gray, smallImage, cv.CV_INTER_LINEAR)

    # Equalize the histogram
    cv.EqualizeHist(smallImage, smallImage)

    # Detect the faces
    faces = cv.HaarDetectObjects(smallImage, faceCascade, cv.CreateMemStorage(0),
    haar_scale, min_neighbors, haar_flags, min_size)

    # If faces are found
    if faces:
        

        for ((x, y, w, h), n) in faces:
            pt1 = (int(x * image_scale), int(y * image_scale))
            pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
            cv.Rectangle(image, pt1, pt2, facecolor, 1, 8, 0)
            cv.PutText(image, "face", pt1, font, facecolor)
            face_region = cv.GetSubRect(image,(x,int(y + (h/4)),w,int(h/2)))

            #split face
            cv.Rectangle(image, (pt1[0],(pt1[1] + (abs(pt1[1]-pt2[1]) / 2 ))), pt2, lowercolor, 1, 8, 0)
            cv.PutText(image, "lower", (pt1[0],(pt1[1] + (abs(pt1[1]-pt2[1]) / 2 ))), font, lowercolor)
            cv.SetImageROI(image, (pt1[0],
                               (pt1[1] + (abs(pt1[1]-pt2[1]) / 2 )),
                               pt2[0] - pt1[0],
                               int((pt2[1] - (pt1[1] + (abs(pt1[1]-pt2[1]) / 2 ))))))
            
            smiles = cv.HaarDetectObjects(image, smileCascade, cv.CreateMemStorage(0), 1.1, 5, 0, (15,15))
        
            if smiles:
                smileList.append(str(smiles)[0:25])
            
                for smile in smiles:
                    cv.Rectangle(image,
                    (smile[0][0],smile[0][1]),
                    (smile[0][0] + smile[0][2], smile[0][1] + smile[0][3]),
                    smilecolor, 1, 8, 0)

                    cv.PutText(image, "smile", (smile[0][0],smile[0][1]), font, smilecolor)

                    cv.PutText(image,str(smile[1]), (smile[0][0], smile[0][1] + smile[0][3]), font, smilecolor)
                    #print ((abs(smile[0][1] - smile[0][2]) / abs(pt1[0] - pt2[0])) * 100) 
                    
                    global smileness 
                    smileness = smile[1]
            cv.ResetImageROI(image)



    cv.ResetImageROI(image)
    
    
    if smileList.__len__() >= 10:
        smileList = smileList[-10:]
    #for smiles in smileList:
    for idx, val in enumerate(smileList):
        cv.PutText(image, val, (5,20 * idx), sFont, smilecolor)
        print idx, val
        #print smiles
    return image

#loads the training data
faceCascade = cv.Load("haarcascade_frontalface_alt.xml")
smileCascade = cv.Load("haarcascade_smile.xml")

while True:
    if smileness > 15:
        smilecount+= 1
    else:
        smilecount = 0
        
    if smilecount >=4:
        smilecount = 0
        mT.publish()
        print "Got Smile!"
        smileList.append("Got Smile!")
        time.sleep(2)
    
    
    img = cv.QueryFrame(capture)
    
    smileness = 0
    image = DetectFacesSmiles(img, faceCascade, smileCascade)
    cv.ShowImage("camera", image)
    #print smileness
    
    #allows us to kill the script to exit it
    k = cv.WaitKey(10);
    if k == 'f':
        break
