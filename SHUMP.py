import pygame
import random
from os import path

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'sound')

# Settings for a new window
WIDTH = 480
HEIGHT = 600
FPS = 50  # Frames per second: Decides how fast our game will run

# Define Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Initialise Pygame and create window
pygame.init()  # Initialises pygame
pygame.mixer.init()  # Mixer handles all the sound effects in your game
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Creation of a new window
pygame.display.set_caption("shmup")
clock = pygame.time.Clock()  # Defining variable to keep track of time and
# makes sure we are going at the correct fps

#font for the score
font_name= pygame.font.match_font('arial bold')

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    surf.blit(text_surface, text_rect)

def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT =10
    fill = (pct/3) * BAR_LENGTH # 3 because we are considering 3 shields
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill,BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 1)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)




class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 3 # player has 3 shields , when the third time mob hits the player it is destroyed
        self.shoot_delay = 250 #after 250ms bullet will be fired
        self.last_shot = pygame.time.get_ticks() #keeps track of last shot
        self.lives = 3
        self.hidden = False #if player has lives this hide the player once it dies
        self.hide_timer = pygame.time.get_ticks()#how long we stay hidden

    def update(self):
        #if its time to unhide
        if self.hidden and pygame.time.get_ticks() - self.hide_timer  > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        self.speedx = 0
        keystate = pygame.key.get_pressed()  #gives the in built list of keys
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5
        if keystate[pygame.K_SPACE]:#as long as the spacebar is pressed bullets are fired
            self.shoot()
        self.rect.x += self.speedx
        # so that sprite doesnot move out of given width
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0


    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()

    def hide(self):
        #hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

class  Mob(pygame.sprite.Sprite):  #sprite as movable enemies
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(WHITE)
       # self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy() #making a copy of the image coz if we use transform.rotate
        # then due to continuous rotation on a regular interval distorts the appearance of meteor
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)#sprite will always be within the width
        self.rect.y = random.randrange(-100 ,-40)
        self.speedy = random.randrange(1 ,8)
        self.speedx = random.randrange(-10,10)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8) #how fast our sprite is rotating
        self.last_update = pygame.time.get_ticks() #ticks=tick of clock.how many ticks have been since the game is started
        #tells when we rotated the meteor last time


    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed ) % 360  #to have different rotation after certain instance
            # we don't want to have our rotation keep getting bigger n bigger n hence %360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image =new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10


    def update(self):
        self.rect.y += self.speedy
        #kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            center = self.rect.center
            self.image = explosion_anim[self.size][0]
            self.rect = self.image.get_rect()
            self.rect.center = center
            self.kill()

def show_start_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "SHMUP!", 64, WIDTH / 2,HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22, WIDTH / 2,HEIGHT / 2 )
    draw_text(screen, "Press any key to begin", 18,WIDTH / 2,HEIGHT * 3 / 4)
    #draw_text(screen, "Score", 50, WIDTH / 2, HEIGHT / 2)

    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "GAME OVER!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "SCORE :  " + str(score), 50, WIDTH / 2, HEIGHT / 2)
    #draw_text(screen, "Press any key to play again", 18, WIDTH / 2, HEIGHT * 3 / 4)

    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


#loop all game graphics
background = pygame.image.load(path.join(img_dir, "starfield2.png")).convert()
#background_rect1 = pygame.transform.scale(background, (1066, 600))
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "spaceShips_005.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
#meteor_img = pygame.image.load(path.join(img_dir, "spaceMeteors_001.png")).convert()
bullet_img = pygame.image.load(path.join(img_dir, "laserRed.png")).convert()
meteor_images = []
meteor_list = ['spaceMeteors_001.png','meteorBig.png','meteorSmall.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())

#explosion
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
img = pygame.image.load(path.join(img_dir, 'explosion1_0022.png')).convert()
img.set_colorkey(BLACK)
img_lg = pygame.transform.scale(img, (100, 100))
explosion_anim['lg'].append(img_lg)
img_sm = pygame.transform.scale(img, (30, 30))
explosion_anim['sm'].append(img_sm)
#for i in range(3):
    #filename = 'explosion{}.png'.format(i) #takes 3 png file 1 by 1
img = pygame.image.load(path.join(img_dir, 'explosion0.png')).convert()
img.set_colorkey(BLACK)
explosion_anim['player'].append(img)


#Load all the game sounds
shoot_sound = pygame.mixer.Sound(path.join(snd_dir,'Laser_Shoot8.wav'))
expl_sound = pygame.mixer.Sound(path.join(snd_dir,'Explosion16.wav'))
expl1_sound = pygame.mixer.Sound(path.join(snd_dir,'Explosion32.wav'))

pygame.mixer.music.load(path.join(snd_dir, 'Battle.mp3'))
pygame.mixer.music.set_volume(1)



score = 0
#once the music comes to an end the parameter helps to restart it again & music continuous
pygame.mixer.music.play(loops=-1)

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(8):
    newmob()


# Game Loop
show_start_screen()
game_over = False #will show game over screen
running = True
while running:
    # Code of a game can be divided into three parts:
    #if game_over:
     #   show_go_screen()
      #  game_over = False #will not show game over screen


    # 1)Process Input(Events): Clicking of a mouse, Pressing a key
    clock.tick(FPS)  # Makes sure that the program runs at the same speed
    for event in pygame.event.get():  # Records all the events that occur when we are executing
        # the draw or update code block
        # Check for closing window event
        if event.type == pygame.QUIT:
            running = False
        #whenever the space bar is pressed  bullet will be fired
        #elif event.type == pygame.KEYDOWN:
        #    if event.key == pygame.K_SPACE:
        #       player.shoot()

    # 2)Update Game: When something has to change on the screen you have to update the game


    #Update
    all_sprites.update()

    #check to see if a bullet hit a mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 10
        expl_sound.play()
        expl = Explosion(hit.rect.center,'lg')
        all_sprites.add(expl)
        newmob()


    #check to see if mob hit player
    hits = pygame.sprite.spritecollide(player, mobs, True)#Returns a list of mobs that hits the player
    #if we are sheilding our ship for 2/3 times and mob is not destroyed
    # then in every frame(fps) continuously it will hit ship n ship will be destroyed so its true so the player can have 2/3 chances
    #if mob hits the player game ends and it returns a list
    for hit in  hits:
        player.shield -= 1
        expl_sound.play()
        expl = Explosion(hit.rect.center,'sm')
        all_sprites.add(expl)

        newmob()
        if player.shield <= 0:
            expl1_sound.play()
            death_explosion = Explosion(player.rect.center,'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 3
            #running = False

    #if the player died and the explosion has finished playing
    # alive() is in-built funct chceks whether sprite it exists or not in any group
    if  player.lives == 0 and not death_explosion.alive():
        game_over = True
    if game_over:
        show_go_screen()
        game_over = False #will not show game over screen

    # 3)Draw / Render: If your character moves to the right, then you have to draw the
     # character to that many pixels to the right
    screen.fill(BLACK)  # Colors the screen black
    screen.blit(background, background_rect) #copy the pixels of one thing to another
    all_sprites.draw(screen)

    draw_text(screen, str(score), 20, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)


    # Do the flip thingy in the end. After drawing everything, flip the display
    pygame.display.flip()  # Used for basically showing the new drawings to the user.Eg.
    # Imagine a white board that can flip.One side is the display which is
    # visible to the user and the other side is the drawing.Once you finish completing a
    # drawing you flip the board and it,ll be visible to the user while on the other side
    # you'll start creating your other drawing

print("Your score is", score)

pygame.quit()
