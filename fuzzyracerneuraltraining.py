import random
import os
import numpy as np
import pygame
import neat
import pickle
import visualize

pygame.init()
pygame.font.init()
winbr,winh = (600,900)
pygame.display.set_caption("Fuzzy Racer")
fonts = pygame.font.SysFont("comicsans", 50)
icon = pygame.image.load('imgs/icon.svg')
pygame.display.set_icon(icon)
win = pygame.display.set_mode((winbr,winh))

car_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","car.png")).convert_alpha(), (70, 100))
truck_img = [pygame.transform.scale(pygame.image.load(os.path.join("imgs","truck.png")).convert_alpha(), (95,125)),pygame.transform.scale(pygame.image.load(os.path.join("imgs","random.png")).convert_alpha(), (95,125)),pygame.transform.scale(pygame.image.load(os.path.join("imgs","big_truck.png")).convert_alpha(), (400,100)),pygame.transform.scale(pygame.image.load(os.path.join("imgs","bus.png")).convert_alpha(), (100,100))]
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","road.png")).convert_alpha(), (winbr,winh))
blast_img = [pygame.transform.scale(pygame.image.load(os.path.join("imgs","blast.png")).convert_alpha(), (75,75)),pygame.transform.scale(pygame.image.load(os.path.join("imgs","blast.png")).convert_alpha(),(150,150))]

fps = 30
gen = 0
delay = (0.5)*winh
bg_vel = 7
truck_vel = 20
level = 1
truck_on_frame = 1
road = (25,winbr - 100)
level_2_lock = True
best_fitness = -1


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
        if dir == 'l' and self.x - self.turn > road[0]:
            self.img = pygame.transform.rotate(car_img,self.tilt_angle)
        elif dir == 'r' and self.x + self.turn < road[1]:
            self.img = pygame.transform.rotate(car_img,-self.tilt_angle)
        elif dir == '|':
            self.img = pygame.transform.rotate(car_img,0)
        
    def turn_left(self):
        if self.x - self.turn > road[0]: 
            self.x = self.x - self.turn

    def turn_right(self):
        if self.x + self.turn < road[1]: 
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
    global level, delay, truck_on_frame, road, level_2_lock
    if level == 1: 
        random_truck = obstacle(random.randint(road[0],road[1]),0)
        if random.randint(0,1):
            random_truck.img = truck_img[1]
    elif level == 2:
        if level_2_lock:
            delay = (1.5)*delay # Increasing Delay In 2nd Level
            level_2_lock = False
        obstacle.vel = 40          # Increasing Velocity In 2nd Level
        random_truck = obstacle(random.randint(road[0],road[1]),0)
        if random.randint(0,1):
            random_truck.img = truck_img[1]
    trucks.append(random_truck)
    return trucks

def draw_window(cars,trucks,bg,score,bf):
    global gen, level, best_fitness
    bg.draw(win)
    for car in cars:
        car.draw(win)
    for tr in trucks:
        tr.draw(win)
    score_label = fonts.render("SCORE : " + str(score),1,(255,255,255))
    win.blit(score_label, (winbr - score_label.get_width() - 15, 10))
    level_label = fonts.render("LEVEL : " + str(level),1,(255,255,255))
    win.blit(level_label, (15, 10))
    gen_label = fonts.render("GEN : " + str(gen-1),1,(255, 165, 0))
    win.blit(gen_label, (10, 50))
    alive_label = fonts.render("ALIVE : " + str(len(cars)),1,(255, 165, 0))
    win.blit(alive_label, (10, 90))
    small_fonts = pygame.font.SysFont('comicsans', 25)
    fitness = np.round(bf,2)
    fitness_label = small_fonts.render(f"fitness for best car : {fitness}" ,1,(255, 165, 0))
    if best_fitness < fitness:
        best_fitness = fitness
    best_fitness_label = small_fonts.render(f"best fitness uptill now : {best_fitness}",1,(255, 165, 0))
    win.blit(best_fitness_label, (winbr - score_label.get_width() - 100, 50))
    win.blit(fitness_label, (winbr - score_label.get_width() - 85, 70))
    pygame.display.update()

def main(genomes, config):
    global gen, delay, level, truck_on_frame, truck_vel, level_2_lock
    gen += 1
    clock = pygame.time.Clock()
    run = True
    score = 0

    cars = []
    nets = []
    ge   = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        cars.append(vehicle(winbr/2 - int(car_img.get_width()/2),winh - 150))
        ge.append(genome)

    trucks = []
    truck_count = 1
    for _ in range(truck_on_frame):
        trucks = add_truck(trucks)
    bg = background(0)

    tl = 0
    truck_on_level = [20,20]           # Number Of Trucks At A Particular Level
    while run:     
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
        # Moving Background
        bg.move()
        # Turning Car
        for car in cars:
            car.tilt('|')
        for x, car in enumerate(cars):  # give each car a fitness of 0.1 for each frame it runs
            ge[x].fitness += 0.1
            input = (car.x, winbr - car.x, trucks[0].x, trucks[0].y, level)
            output = nets[cars.index(car)].activate(input)    
            if output[0] > 0.5:  # we use a sigmoid activation function so result will be between 0 and 1
                car.tilt('l')     
                car.turn_left()
            elif output[0] < 0.5:
                car.tilt('r')
                car.turn_right() 
        # Moving Trucks
        if trucks[len(trucks)-1].y > delay and truck_count < truck_on_level[tl]:
            for _ in range(truck_on_frame):
                truck_count += 1
                trucks = add_truck(trucks)
        # Checking If Any Car Collided With Any Truck
        for t in trucks:
            for car in cars:
                if t.collide(car):
                    ge[cars.index(car)].fitness -= 2    # if the car collides, remove -2 from it's fitness function 
                    car.collision = True
                    car.y = t.y + 60   # adding 10 as collision happens a little before there y positions match
            t.move()
        # Removing Truck And Increasing Score
        for _ in range(truck_on_frame):
            if trucks[0].y > winh:
                trucks.remove(trucks[0])
                car_check = cars.copy()
                for car in car_check:
                    if car.collision:
                        nets.pop(cars.index(car))
                        ge.pop(cars.index(car))
                        cars.pop(cars.index(car))
                score += 1
                for _ in range(len(cars)):  # Increasing the fitness function for every remaining car after every truck passes the window
                    ge[_].fitness += 1
        # Checking The Fitness To Pickle The Model
        if ge != []:
            fit = [_.fitness for _ in ge]
            fit.sort(reverse = True)
            bf = fit[0]
        draw_window(cars,trucks,bg,score,bf)

        if trucks == []:
            level += 1
            truck_count = 1
            tl += 1 
            if level == 3:
                delay = (0.5)*winh
                obstacle.vel = 20
                level = 1
                level_2_lock = True 
                tl = 0
            for _ in range(truck_on_frame):
                trucks = add_truck(trucks)
            for _ in range(len(cars)):
                ge[_].fitness += 5

        if np.round(bf,2) > 10000:      # picling the Neural Network with the threshold fitness function 
            print(nets)
            with open('pickled_net.pkl','wb') as p:
                pickle.dump(nets[0],p)
            visualize.draw_net(config,ge[0],filename = 'Neural_Engine_Net')
            pygame.quit()

        if len(cars) == 0:
            # reintialize all values 
            delay = (0.5)*winh
            obstacle.vel = 20
            level = 1
            level_2_lock = True
            tl = 0 #check if correct
            # truck_on_frame = 1
            return False

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation,config_file)
    p = neat.Population(config)
    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main, 1000)
    print(f'BEST GENOME : {winner}')

if __name__ == '__main__':
    config_file = os.path.join(os.path.dirname(__file__), 'config.txt') 
    run(config_file)
