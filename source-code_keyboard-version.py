import sys
import pygame
import random
from time import sleep

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

    crashed = False
    
    while not crashed:
        displayMessage('Score:' + str(score), pad_width/4, pad_height*0.07)
        displayMessage('Top Score:' + str(topscore), pad_width*3/4, pad_height*0.07)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            
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
