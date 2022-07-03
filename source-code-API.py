import sys
import pygame
import random
from time import sleep

from keras.preprocessing.image import img_to_array
import imutils
import cv2
from keras.models import load_model
import numpy as np

# parameters for loading data and images
detection_model_path = 'haarcascade_files/haarcascade_frontalface_default.xml'
emotion_model_path = 'models/_mini_XCEPTION.102-0.66.hdf5'

# hyper-parameters for bounding boxes shape
# loading models
face_detection = cv2.CascadeClassifier(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)
EMOTIONS = ["angry" ,"disgust","scared", "happy", "sad", "surprised",
 "neutral"]


white = (255, 255, 255)
pad_width = 1024
pad_height = 512
background_width = 1024

heeheeduck_width = 90
heeheeduck_height = 55

mine_width = 110
mine_height = 67

fireball1_width = 140
fireball1_height = 60
fireball2_width = 86
fireball2_height = 60

cloud_height = 85

def textObj(text, font):
    textSurface = font.render(text, True, "RED")
    return textSurface, textSurface.get_rect()

def displayMessage(text, x_position, y_position):
    global gamepad

    largeText = pygame.font.Font('freesansbold.ttf', 35)
    TextSurf, TextRect = textObj(text, largeText)
    TextRect.center = (x_position, y_position)
    gamepad.blit(TextSurf, TextRect)
    pygame.display.update()    

def crash(score, topscore):
    global gamepad
    global explosion_sound

    pygame.mixer.music.stop()
    pygame.mixer.Sound.play(explosion_sound)
    game_over_img = pygame.image.load('game over.png')
    game_over_img = pygame.transform.scale(game_over_img,(800,400))
    game_over_img_rect = game_over_img.get_rect()
    game_over_img_rect.center = (pad_width/2, pad_height/2)
    drawObject(game_over_img, 100,125)
    
    if topscore < score:
        topscore = score
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                runGame()
        pygame.display.update()

def drawObject(obj, x,y):
    global gamepad
    gamepad.blit(obj, (x,y))

def runGame():
    global gamepad, heeheeduck, clock, background1, background2
    global mine, fires, laser, boom
    global shot_sound
    global score, topscore

    pygame.mixer.music.play()
    
    score = 0

    isShotMine = False
    boom_count = 0
    
    laser_xy = []

    x = pad_width*0.05
    y = pad_height*0.8
    y_change = 0

    background1_x = 0
    background2_x = background_width
    land = pygame.image.load('land.png')
    land = pygame.transform.scale(land, (pad_width, 90))

    cloud = pygame.image.load('cloud.png')
    cloud = pygame.transform.scale(cloud, (pad_width, 90))

    mine_x = pad_width
    mine_y = random.randrange(0, pad_height)

    fire_x = pad_width
    fire_y = random.randrange(0, pad_height)
    random.shuffle(fires)
    fire = fires[0]

    #starting video streaming
    cv2.namedWindow('your_face')
    camera = cv2.VideoCapture(0)

    crashed = False
    global label
    
    while not crashed:
        frame = camera.read()[1]
        #reading the frames
        frame = imutils.resize(frame,width=300)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detection.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)
        
        canvas = np.zeros((250, 300, 3), dtype="uint8")
        frameClone = frame.copy()
        if len(faces) > 0:
            faces = sorted(faces, reverse=True,
            key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
            (fX, fY, fW, fH) = faces
                        # Extract the ROI of the face from the grayscale image, resize it to a fixed 28x28 pixels, and then prepare
                # the ROI for classification via the CNN
            roi = gray[fY:fY + fH, fX:fX + fW]
            roi = cv2.resize(roi, (64, 64))
            roi = roi.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)
            
            
            preds = emotion_classifier.predict(roi)[0]
            emotion_probability = np.max(preds)
            label = EMOTIONS[preds.argmax()]

            print(label)
    
        else: continue
            
        for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):
            # construct the label text
            text = "{}: {:.2f}%".format(emotion, prob * 100)

            # draw the label + probability bar on the canvas
            # emoji_face = feelings_faces[np.argmax(preds)]

            
            w = int(prob * 300)
            cv2.rectangle(canvas, (7, (i * 35) + 5),
            (w, (i * 35) + 35), (0, 0, 255), -1)
            cv2.putText(canvas, text, (10, (i * 35) + 23),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45,
            (255, 255, 255), 2)
            cv2.putText(frameClone, label, (fX, fY - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
            cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH),
                        (0, 0, 255), 2)
    #    for c in range(0, 3):
    #        frame[200:320, 10:130, c] = emoji_face[:, :, c] * \
    #        (emoji_face[:, :, 3] / 255.0) + frame[200:320,
    #        10:130, c] * (1.0 - emoji_face[:, :, 3] / 255.0)

        cv2.imshow('your_face', frameClone)
        cv2.imshow("Probabilities", canvas)
        
        displayMessage('Score:' + str(score), pad_width/4, pad_height*0.07)
        displayMessage('Top Score:' + str(topscore), pad_width*3/4, pad_height*0.07)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
           
            if label == 'happy':
                y_change = -5
            elif label == 'neutral':
                y_change = 5
            elif label == 'angry' or label == 'disgust':
                pygame.mixer.Sound.play(shot_sound)
                laser_x = x + heeheeduck_width
                laser_y = y + heeheeduck_height/2
                laser_xy.append([laser_x, laser_y])
            '''        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    y_change = -5
                elif event.key == pygame.K_DOWN:
                    y_change = 5
                elif event.key == pygame.K_RIGHT:
                    pygame.mixer.Sound.play(shot_sound)
                    laser_x = x + heeheeduck_width
                    laser_y = y + heeheeduck_height/2
                    laser_xy.append([laser_x, laser_y])
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    y_change = 0
            '''
        
        #Clear gamepad
        gamepad.fill(white)

        #Draw Background
        background1_x -= 2
        background2_x -= 2

        if background1_x == -background_width:
            background1_x = background_width
        
        if background2_x == -background_width:
            background2_x = background_width
        
        drawObject(background1, background1_x, 0)
        drawObject(background2, background2_x, 0)
        drawObject(land, 0, pad_height-78)
        drawObject(cloud, 0, -30)

        #Heeheeduck Position
        y += y_change
        if y < 0:
            y = 0
        elif y > pad_height - heeheeduck_height:
            y = pad_height - heeheeduck_height
        
        #Mine Position
        mine_x -= 7
        if mine_x <= 0:
            mine_x = pad_width
            mine_y = random.randrange(0, pad_height)
        
        #Fireball Position
        if fire[1] == None:
            fire_x -= 30
        else:
            fire_x -= 15
        
        if fire_x <= 0:
            fire_x = pad_width
            fire_y = random.randrange(0, pad_height)
            random.shuffle(fires)
            fire = fires[0]
        
        #Laser Position
        if len(laser_xy) != 0:
            for i, lxy in enumerate(laser_xy):
                lxy[0] += 15
                laser_xy[i][0] = lxy[0]
                
                #check if laser strike mine
                if lxy[0] > mine_x:
                    if lxy[1] > mine_y and lxy[1] < mine_y + mine_height:
                        laser_xy.remove(lxy)
                        isShotMine = True
                        score += 1
                        if topscore < score:
                            topscore = score

                if lxy[0] >= pad_width:
                    try:
                        laser_xy.remove(lxy)
                    except:
                        pass

        #Check Heeheeduck crashed by mine
        if x + heeheeduck_width > mine_x:
            if(y > mine_y and y < mine_y + mine_height) or (y+heeheeduck_height > mine_y and y+heeheeduck_height < mine_y + mine_height):
                crash(score, topscore)
                
        
        #Check Heeheeduck crashed by fireball
        if fire[1] != None:
            if fire[0] == 0:
                fireball_width = fireball1_width
                fireball_height = fireball1_height
            elif fire[0] == 1:
                fireball_width = fireball2_width
                fireball_height = fireball2_height
            
            if x + heeheeduck_width > fire_x:
                if(y > fire_y and y < fire_y + fireball_height) or (y+heeheeduck_height > fire_y and y + heeheeduck_height < fire_y + fireball_height):
                    crash(score, topscore)
        
        #Check Heeheeduck crashed by cloud
        if y + heeheeduck_height < cloud_height:
                    crash(score, topscore)


        drawObject(heeheeduck, x,y)
        
        if len(laser_xy) != 0:
            for lx, ly in laser_xy:
                drawObject(laser, lx, ly)
        
        if not isShotMine:
            drawObject(mine, mine_x, mine_y)
        else:
            drawObject(boom, mine_x, mine_y)
            boom_count += 1
            if boom_count > 5:
                boom_count = 0
                mine_x = pad_width
                mine_y = random.randrange(0, pad_height-mine_height)
                isShotMine = False
        
        if fire[1] != None:
            drawObject(fire[1], fire_x, fire_y)
        
        pygame.display.update()
        clock.tick(60)
    
    pygame.quit()
    quit()

def start_game():
    global gamepad
        
    gamepad = pygame.display.set_mode((pad_width, pad_height))
    start_img = pygame.image.load('start.png')
    start_img = pygame.transform.scale(start_img,(1024,512))
    start_img_rect = start_img.get_rect()
    start_img_rect.center = (pad_width/2, pad_height/2)
    drawObject(start_img, 0,0)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                initGame()
        pygame.display.update()

def initGame():
    global gamepad, heeheeduck, clock, background1, background2
    global mine, fires, laser, boom
    global shot_sound, explosion_sound
    global score, topscore
    score = 0
    topscore = 0
    
    pygame.mixer.init()
    pygame.mixer.music.load("Fluffing a Duck.mp3")
    pygame.mixer.music.play(-1, 0.0)

    shot_sound = pygame.mixer.Sound('shot.wav')
    explosion_sound = pygame.mixer.Sound('explosion.wav')

    fires = []
    
    pygame.init()
    gamepad = pygame.display.set_mode((pad_width, pad_height))
    pygame.display.set_caption('Heeheeduck')
    heeheeduck = pygame.image.load('duck.png')
    heeheeduck = pygame.transform.scale(heeheeduck,(50,60))
    background1 = pygame.image.load('background.png')
    background1 = pygame.transform.scale(background1,(1024,550))
    background2 = background1.copy()
    mine = pygame.image.load('mine.png')
    mine = pygame.transform.scale(mine,(30,40))
    fires.append((0, pygame.image.load('fireball.png')))
    fires.append((1, pygame.image.load('fireball2.png')))
    boom = pygame.image.load('boom.png')

    for i in range(3):
        fires.append((i+2, None))
    
    laser = pygame.image.load('laser.png')

    clock = pygame.time.Clock()
    runGame()

if __name__ == '__main__':
    start_game()
