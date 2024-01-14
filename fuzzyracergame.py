import random
import os
import numpy as np
import pygame
import neat

pygame.init()
pygame.font.init()
winbr,winh = (600,900)
win_dim = (winbr,winh)
pygame.display.set_caption("Fuzzy Racer")
fonts = pygame.font.SysFont("comicsans", 50)
icon = pygame.image.load('imgs/icon.svg')
pygame.display.set_icon(icon)
win = pygame.display.set_mode(win_dim)

fps = 30
delay = (0.5)*winh
bg_vel = 7
truck_vel = 20
level = 1
truck_on_frame = 1
tr = (25,winbr - 125)
truck_lock = True
# variable for levels
level_2_lock = True
level_5_lock = True
it = 2

car_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","car.png")).convert_alpha(), (70, 100))
truck_img = [pygame.transform.scale(pygame.image.load(os.path.join("imgs","truck.png")).convert_alpha(), (95,125)),pygame.transform.scale(pygame.image.load(os.path.join("imgs","random.png")).convert_alpha(), (95,125)),pygame.transform.scale(pygame.image.load(os.path.join("imgs","big_truck.png")).convert_alpha(), (400,100)),pygame.transform.scale(pygame.image.load(os.path.join("imgs","bus.png")).convert_alpha(), (100,100))]
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","road.png")).convert_alpha(), (600, 900))
blast_img = [pygame.transform.scale(pygame.image.load(os.path.join("imgs","blast.png")).convert_alpha(), (75,75)),pygame.transform.scale(pygame.image.load(os.path.join("imgs","blast.png")).convert_alpha(),(150,150))]

class vehicle:
    img = car_img
    bl_img = blast_img
    collision = False
    turn = 20
    tilt_angle = 20

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def tilt(self,dir):
        if dir == 'l' and self.x - self.turn > 25:
            self.img = pygame.transform.rotate(car_img,self.tilt_angle)
        elif dir == 'r' and self.x + self.turn < (winbr-95):
            self.img = pygame.transform.rotate(car_img,-self.tilt_angle)
        elif dir == '|':
            self.img = pygame.transform.rotate(car_img,0)
        
    def turn_left(self):
        if self.x - self.turn > 25: 
            self.x = self.x - self.turn

    def turn_right(self):
        if self.x + self.turn < (winbr-95): 
            self.x = self.x + self.turn

    def draw(self, win):
        if not self.collision :
            win.blit(self.img,(self.x,self.y))
        if self.collision :
            win.blit(self.img,(self.x,self.y))
            win.blit(self.bl_img[0],(self.x,self.y))
            win.blit(self.bl_img[1],(self.x,self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class obstacle:
    img = truck_img[0]
    vel = truck_vel

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.passed = False

    def move(self):
        self.y += self.vel

    def draw(self, win):
        win.blit(self.img,(self.x,self.y))
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    def collide(self,car):
        car_mask = car.get_mask()
        truck_mask = obstacle.get_mask(self)
        offset = (self.x - round(car.x),self.y - car.y)
        collision = car_mask.overlap(truck_mask, offset)
        if collision :
            return True
        return False

class background:
    img = bg_img
    height = img.get_height()
    vel = bg_vel

    def __init__(self,x):
        self.x=x
        self.y1 = 0
        self.y2 = self.height

    def move(self):
        self.y1 += self.vel
        self.y2 += self.vel
        if self.y1 - self.height > 0:
            self.y1 = self.y2 - self.height

        if self.y2 - self.height > 0:
            self.y2 = self.y1 - self.height

    def draw(self, win):
        win.blit(self.img, (self.x,self.y1))
        win.blit(self.img, (self.x,self.y2))

def add_truck(trucks):
    global level, delay, truck_on_frame, tr, truck_lock, level_2_lock, level_5_lock, it
    if level == 1: 
        random_truck = obstacle(random.randint(tr[0],tr[1]),0)
        if random.randint(0,1):
            random_truck.img = truck_img[1]
    elif level == 2:
        random_truck = obstacle(random.randint(tr[0],tr[1]),0)
        if random.randint(0,1):
            random_truck.img = truck_img[1]
        if level_2_lock:
            delay = (1.5)*delay # Increasing Delay In 2nd Level
            level_2_lock = False
        obstacle.vel = 40          # Increasing Velocity In 2nd Level
    elif level == 3:
        rng = np.linspace(tr[0], tr[1],5)
        random_truck = obstacle(rng[random.randint(0,4)],0)
        if random.randint(0,1):
            random_truck.img = truck_img[1]
        if truck_lock:
            # delay = (1.26)*delay
            truck_lock = False
        obstacle.vel = 35
        truck_on_frame = 2
    elif level == 4:
        if truck_lock:
            delay = (1.26)*delay
            truck_lock = False
        obstacle.vel = 30
        if random.randint(0,1):
            random_truck = obstacle(50,0)
        else :
            random_truck = obstacle(170,0)
        random_truck.img = truck_img[2]
        truck_on_frame = 1
    elif level == 5:
        if level_5_lock :
            if truck_lock:
                random_truck = obstacle(50,0)
                random_truck.img = truck_img[3]
                truck_lock = False
            else :
                random_truck = obstacle(250,0)
                random_truck.img = pygame.transform.scale(truck_img[2],(300,100))
                truck_lock = True
            it -= 1
            if it == 0:
                level_5_lock = False
                it = 2
        else :
            if truck_lock:
                random_truck = obstacle(winbr - 150,0)
                random_truck.img = pygame.transform.rotate(truck_img[3],180)
                truck_lock = False
            else :
                random_truck = obstacle(50,0)
                random_truck.img = pygame.transform.rotate(pygame.transform.scale(truck_img[2],(300,100)),180)
                truck_lock = True
            it -= 1
            if it == 0:
                level_5_lock = True
                it = 2

        truck_on_frame = 2
    
    trucks.append(random_truck)
    return trucks

def draw_window(car,trucks,bg,score):
    global level
    bg.draw(win)
    car.draw(win)
    for tr in trucks:
        tr.draw(win)
    score_label = fonts.render("SCORE : " + str(score),1,(255,255,255))
    win.blit(score_label, (winbr - score_label.get_width() - 15, 10))
    level_label = fonts.render("LEVEL : " + str(level),1,(255,255,255))
    win.blit(level_label, (15, 10))
    pygame.display.update()

def main():
    global delay, level, truck_on_frame
    clock = pygame.time.Clock()
    run=True
    score = 0

    car = vehicle(250,750)

    trucks = []
    truck_count = 1
    for _ in range(truck_on_frame):
        trucks = add_truck(trucks)
    bg = background(0)

    tl = 0
    truck_on_level = [20,20,20,20,20]           # Number Of Trucks At A Each Level
    while run:         
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # Moving Background
        bg.move()
        # Moving Trucks
        if trucks[len(trucks)-1].y > delay and truck_count < truck_on_level[tl]:
            for _ in range(truck_on_frame):
                truck_count += 1
                trucks = add_truck(trucks)
        # Checking If Any Car Collided With Any Truck
        for t in trucks:
            if t.collide(car):
                car.collision = True
                car.y = t.y + 60
            t.move()
        # Removing Truck And Increasing Score
        for _ in range(truck_on_frame):
            if trucks[0].y > winh :
                trucks.remove(trucks[0])
                if car.collision  : 
                    score -= 1
                    run = False
                score += 1
        # Car Turning and Tilting On Keypress
        keys_pressed = pygame.key.get_pressed()
        car.tilt('|')     # tilting back
        if keys_pressed[pygame.K_LEFT]:
            car.tilt('l')     # tilting left
            car.turn_left()
        elif keys_pressed[pygame.K_RIGHT]:
            car.tilt('r')     # tilting right
            car.turn_right()
        # Final Draw
        draw_window(car,trucks,bg,score)

        if trucks == [] :
            level += 1
            if level == 6:
                print('YOU WON!')
                pygame.quit()
            if level == 3 or level == 5 :
                truck_on_frame += 1
            elif level == 4 :
                truck_on_frame -= 1
            for _ in range(truck_on_frame):
                trucks = add_truck(trucks)
            truck_count = 1
            tl += 1


    print(f'Score : ',score)
    pygame.quit()


if __name__ == '__main__':
    main()
