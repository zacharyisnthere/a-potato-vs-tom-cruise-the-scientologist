#!/home/zachary/Documents/Repos/apotatovstomcruisethescientologist/venv/bin/python

import pygame
import random
import sys


# Add the directory to sys.path
sys.path.append('src')


from TextSprite import TextSprite
from Slider import Slider

from SettingsManager import SettingsManager
#from GameController import GameController


# general setup
pygame.init()
pygame.mixer.init()
pygame.joystick.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 640
pygame.display.set_caption('a potato vs tom cruise the scientologist')
screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
clock = pygame.time.Clock()
running = True


#inputs
joysticks = {}
player1_id = 0
dead_zone = 0.25

J_MOVE_x = 0 #left joystick left and right
J_MOVE_y = 1 #left joystick up and down

J_AIM_x = 3 #right joystick left and right
J_AIM_y = 4 #right joystick up and down
J_FIRE = 5 #Right Bumper
J_FIREAXIS = 5 #Right Trigger

J_UP = 1
J_DOWN = 1
J_LEFT = 0
J_RIGHT = 0

b_J_FIREAXIS = False
b_J_UP = False
b_J_DOWN = False
b_J_LEFT = False
b_J_RIGHT = False

J_menu_cooldown = .2

time_since_move_b_J_UP = J_menu_cooldown
time_since_move_b_J_DOWN = J_menu_cooldown
time_since_move_b_J_LEFT = J_menu_cooldown
time_since_move_b_J_RIGHT = J_menu_cooldown

automove_b_J_UP = True
automove_b_J_DOWN = True
automove_b_J_LEFT = True
automove_b_J_RIGHT = True


J_SELECT = 0 #A button

J_PAUSE = 7 #right menu button
J_RESET = 6 #left menu button



UP = pygame.K_w
DOWN = pygame.K_s
LEFT = pygame.K_a
RIGHT = pygame.K_d
FUP = pygame.K_UP
FDOWN = pygame.K_DOWN
FLEFT = pygame.K_LEFT
FRIGHT = pygame.K_RIGHT
FIRE = [FUP, FDOWN, FLEFT, FRIGHT]
PAUSE = [pygame.K_ESCAPE]

AUP = [UP, FUP]
ADOWN = [DOWN, FDOWN]
ALEFT = [LEFT, FLEFT]
ARIGHT = [RIGHT, FRIGHT]
SELECT = [pygame.K_SPACE, pygame.K_RETURN]

RESET = pygame.K_r
RESETHIGHSCORE = pygame.K_p
QUIT = None


#Master References
_SettingsManager = SettingsManager()


#settings
master_volume = _SettingsManager.settings['master_volume']
music_volume = _SettingsManager.settings['music_volume']
sfx_volume = _SettingsManager.settings['sfx_volume']

#acs means accessibility
acs_shoot_while_aiming = False

#global variables
scene = 0 #0 = menu, 1 = game, maybe -1 could be a splash screen or something. 

playing = True
lost = False
paused = False
in_menu = False

frame = 0

start_dic = 10000
dic = start_dic
time_to_spawn = int(start_dic/3333)
first_time_to_spawn = 1.5
tt = time_to_spawn - first_time_to_spawn

highscore = 0
score = 0
time = 0

background = 0 #small numbers are plain colors, like 0 = white 1 = black etc. numbers above 100 are full images
menu_selected = 0

time_since_lost = 0
reload_time = .2
time_since_fired = reload_time
fired_down_key = False
fired_down_joy = False
ffdir = pygame.math.Vector2(0,-1)

code_string = ''
batman = False


#groups
all_sprites = pygame.sprite.Group()
player_sprites = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()
tom_sprites = pygame.sprite.Group()

text_sprites = pygame.sprite.Group()
text_lose_sprites = pygame.sprite.Group()
text_score_sprites = pygame.sprite.Group()
text_header_sprites = pygame.sprite.Group()
text_button_sprites = pygame.sprite.Group()

#assets
text_font = pygame.font.SysFont(None, 30)
#bg_img = pygame.image.load('./assets/img/bgimg1.jpg')
#bg_img = pygame.transform.scale(bg_img, (WINDOW_WIDTH*1.25, WINDOW_HEIGHT*1.25))

player_img = './assets/img/potato.png'
enemy_img = './assets/img/tomcruise_sunglasses_0.png'
enemy_hurt_1_img = './assets/img/tomcruise_hurt1.png'
enemy_hurt_2_img = './assets/img/tomcruise_hurt2.png'
enemy_hurt_3_img = './assets/img/tomcruise_hurt3.png'

#audio
music_intro_sfx = './assets/audio/danger_zone.wav'
music_loop_sfx = './assets/audio/danger_zone_loop.wav'

select1_sfx = './assets/audio/select1.wav'
select2_sfx = './assets/audio/select2.wav'
shoot_sfx = './assets/audio/laserShoot.wav'
hit_sfx = './assets/audio/hitHurt.wav'
kill_sfx = './assets/audio/hitHurt.wav'
lose_sfx = './assets/audio/explosion.wav'

class GameController():
    def __init__(self):
        pass

    #quit
    def quit(self):
        _settings = {
            'master_volume': master_volume,
            'music_volume': music_volume,
            'sfx_volume': sfx_volume
        }
        _SettingsManager.save_settings(_settings)

        global running
        running = False

    #scene management
    def change_scene(self, new_scene):
        for i in all_sprites:
            i.kill()
        global scene
        scene = new_scene
        
        global menu_selected
        menu_selected = 0

    #state management
    def lose(self):
        global score
        global highscore
        if int(self.get_highscore()) < score:
            highscore = score
            self.save_highscore(highscore)

        global playing
        global lost
        global paused
        if playing:
            self.stop_music()
            self.play_sound(lose_sfx, 0.5)

        playing = False
        lost = True
        in_menu = True
        paused = False

    def pause(self):
        global paused
        global playing
        paused = True
        playing = False

        self.pause_music()
    
    def unpause(self):
        global paused
        global playing
        paused = False
        playing = True

        self.unpause_music()

        for i in text_header_sprites:
            i.kill()

    def restart_game(self):
        for i in all_sprites:
            i.kill()
        
        global dic
        global score
        global highscore
        global time
        global time_to_spawn
        global playing
        global lost
        global paused

        dic = start_dic
        score = 0
        highscore = int(self.get_highscore())
        time = 0
        time_to_spawn = int(start_dic/3333)
        self.play_music(music_loop_sfx, music_intro_sfx)
        playing = True
        lost = False
        paused = False


    #sound management
    def play_sound(self, audio_clip, volume=1):
        sound = pygame.mixer.Sound(audio_clip)
        sound.play()
        sound.set_volume(volume * master_volume/60 * sfx_volume/60)
        
    def play_music(self, music_loop, music_intro=None, volume=1):
        if music_intro: pygame.mixer.music.load(music_intro, 'wav')
        else: pygame.mixer.music.load(music_loop, 'wav')
        pygame.mixer.music.play()
        pygame.mixer.music.queue(music_loop, 'wav', -1)

        pygame.mixer.music.set_volume(volume * master_volume/60 * music_volume/60)

    def stop_music(self):
        pygame.mixer.music.stop()

    def pause_music(self):
        pygame.mixer.music.pause()
    def unpause_music(self):
        pygame.mixer.music.unpause()<<<<<<<<

    #high score management
    def save_highscore(self, hs):
        f = open('./memory/highscore.mem', 'w')
        f.write(str(hs))
        f.close()

    def get_highscore(self):
        f = open('./memory/highscore.mem', 'r')
        return f.read()


    def return_shoot_sounds(self):        
        shoot_sounds = [
            './assets/audio/batman/batman_pew1.wav',
            './assets/audio/batman/batman_pew2.wav',
            './assets/audio/batman/batman_pew3.wav',
            './assets/audio/batman/batman_pew4.wav',
            './assets/audio/batman/batman_pew5.wav',
            './assets/audio/batman/batman_pew6.wav',
            './assets/audio/batman/batman_pew7.wav',
            './assets/audio/batman/batman_pew8.wav',
            './assets/audio/batman/batman_pew9.wav',
            './assets/audio/batman/batman_pew10.wav',
        ] 
        return shoot_sounds

    def return_hit_sounds(self):        
        hit_sounds = [
            './assets/audio/batman/batman_ugh1.wav',
            './assets/audio/batman/batman_ugh2.wav',
            './assets/audio/batman/batman_ugh3.wav',
            './assets/audio/batman/batman_ugh4.wav',
        ]
        return hit_sounds


#Game Controller Master Reference
_GameController = GameController()



#Object Classes
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale(pygame.image.load(player_img).convert_alpha(), (60,45))
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        
        self.pos = pygame.math.Vector2(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        self.dir = pygame.math.Vector2()

        self.speed = 300



    def check_partial_match_keys(self, keylist, list1):
        for item1 in list1:
            if keylist[item1]:
                return True
        return False

    def fire(self, dir):
        bullet = Bullet(self.pos, dir, [bullet_sprites, all_sprites])

    def update(self, dt):
        #player movement
        keys = pygame.key.get_pressed()
        recent_keys = pygame.key.get_just_pressed()

        if self.rect.left <= 0: self.dir.x = abs(self.dir.x)
        if self.rect.right >= WINDOW_WIDTH: self.dir.x = -abs(self.dir.x)
        if self.rect.top <= 0: self.dir.y = abs(self.dir.y)
        if self.rect.bottom >= WINDOW_WIDTH: self.dir.y = -abs(self.dir.y)

        if playing:
            self.pos += self.dir * self.speed * dt
            self.rect.center = self.pos
                


#!!!!!Create a class for scene management, use that instead of DEFs because I think they don't work for some reason.<<<<<<<<

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, dir, groups):
        super().__init__(groups)
        self.image = pygame.Surface((5,5))
        self.rect = self.image.get_frect()
        if background == 0: self.image.fill('black')
        if background == 1: self.image.fill('white')

        self.pos = pygame.math.Vector2(pos)
        self.dir = pygame.math.Vector2(dir)
        self.rect.center = self.pos

        self.speed = 500

        sfx = shoot_sfx
        if batman: sfx = _GameController.return_shoot_sounds()[random.randint(0,9)]
        _GameController.play_sound(sfx, 0.2)

    
    def delete(self):
        self.kill()


    def update(self, dt):

        #movement     
        global playing   
        if playing:
            self.pos += self.dir * self.speed * dt
            self.rect.center = self.pos

        if self.pos.x < 0 or self.pos.x > WINDOW_WIDTH or self.pos.y < 0 or self.pos.y > WINDOW_HEIGHT:
            self.delete()



class Tom(pygame.sprite.Sprite):
    def __init__(self, size, target, groups):
        super().__init__(groups)
        self.size = size
        self.height_mod = (100 + random.randint(-50, 50)) / 100

        self.image_display = pygame.image.load(enemy_img)
        self.image = pygame.transform.scale(self.image_display, (self.size,self.size*self.height_mod)).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        self.target = target
        self.dir = pygame.math.Vector2(1,1)
        self.speed = dic/self.size
        
        self.health = 0
        if self.size > 100: self.health = 1
        if self.size > 160: self.health = 2
        if self.size > 240: self.health = 3

        #random side spawning
        buf = 2
        self.spawn_side = random.randint(0,3)
        if self.spawn_side==0: self.pos = pygame.math.Vector2(random.randint(0,WINDOW_WIDTH), 0 - self.rect.width)
        if self.spawn_side==1: self.pos = pygame.math.Vector2(random.randint(0,WINDOW_WIDTH), WINDOW_HEIGHT + self.rect.width)
        if self.spawn_side==2: self.pos = pygame.math.Vector2(0 - self.rect.height, random.randint(0,WINDOW_HEIGHT))
        if self.spawn_side==3: self.pos = pygame.math.Vector2(WINDOW_WIDTH + self.rect.height, random.randint(0,WINDOW_WIDTH))


    def delete(self):
        _GameController.play_sound(kill_sfx, 0.275)
        self.kill()
    

    def hurt(self):
        if self.health > 0:
            sfx = hit_sfx
            if batman: sfx = _GameController.return_hit_sounds()[random.randint(0,3)]
            _GameController.play_sound(sfx, 0.2)
            self.health -= 1
            if self.health == 0: self.image_display = pygame.image.load(enemy_hurt_1_img)
            if self.health == 1: self.image_display = pygame.image.load(enemy_hurt_2_img)
            if self.health == 2: self.image_display = pygame.image.load(enemy_hurt_3_img)
        else: 
            self.delete()


    def update(self, dt):
        self.image = pygame.transform.scale(self.image_display, (self.size,self.size*self.height_mod)).convert_alpha()

        #movement
        self.dir = pygame.math.Vector2(self.pos.x - self.target.x, self.pos.y - self.target.y).normalize()*-1 if self.target!=self.pos else self.dir

        global playing
        if playing:
            self.pos += self.dir * self.speed * dt
            self.rect.center = self.pos

        #collision        
        self.tom_mask = pygame.mask.from_surface(self.image)

        self.tom_mask_image = self.tom_mask.to_surface()
        self.tom_mask_image.fill('black')

        for bullet in bullet_sprites:
            bullet_mask = pygame.mask.from_surface(bullet.image)
            if self.tom_mask.overlap(bullet_mask, (bullet.pos.x - self.rect.x, bullet.pos.y - self.rect.y)): 
                bullet.delete()
                self.hurt()
        
        player_mask = pygame.mask.from_surface(player.image)
        if self.tom_mask.overlap(player_mask, (player.rect.x - self.rect.x, player.rect.y - self.rect.y)):
            _GameController.lose()



#init
highscore = int(_GameController.get_highscore())
player = None

####MAIN GAME LOOP###
while running:
    dt = clock.tick() / 1000


    # input loop
    #axis
    #keyboard
    if player and playing:
        keys = pygame.key.get_pressed()

        player.dir.x = int(keys[RIGHT]) - int(keys[LEFT])
        player.dir.y = int(keys[DOWN]) - int(keys[UP])
        player.dir = player.dir.normalize() if player.dir else player.dir


        fdir = pygame.math.Vector2()
        fdir.x = int(keys[FRIGHT]) - int(keys[FLEFT])
        fdir.y = int(keys[FDOWN]) - int(keys[FUP])
        fdir = fdir.normalize() if fdir else fdir

        if fdir.magnitude()>0.9:
            if time_since_fired >= reload_time or not fired_down_key:
                time_since_fired = 0
                fired_down_key = True
                player.fire(fdir)
            
            fired_down_key = True
        else:
            fired_down_key = False
            
        time_since_fired += dt
        

    #joysticks        
    if len(joysticks)>0:
        
        b_J_UP = joysticks[player1_id].get_axis(J_UP) > dead_zone
        b_J_DOWN = joysticks[player1_id].get_axis(J_DOWN) < 0-dead_zone
        b_J_LEFT = joysticks[player1_id].get_axis(J_LEFT) < 0-dead_zone
        b_J_RIGHT = joysticks[player1_id].get_axis(J_RIGHT) > dead_zone  

        b_J_FIREAXIS = joysticks[player1_id].get_axis(J_FIREAXIS) > dead_zone


        if in_menu:
            #input calls
            if b_J_UP and automove_b_J_UP:
                time_since_move_b_J_UP = 0
                _GameController.play_sound(select1_sfx, 0.1)
                menu_selected += 1
            if b_J_DOWN and automove_b_J_DOWN:
                time_since_move_b_J_DOWN = 0
                _GameController.play_sound(select1_sfx, 0.1)
                menu_selected -= 1
            
            
            if menu_selected > len(menu_buttons)-1: menu_selected = 0
            if menu_selected < 0: menu_selected = len(menu_buttons)-1 
            
            
            if b_J_LEFT and automove_b_J_LEFT and type(menu_buttons[menu_selected]) == Slider:
                time_since_move_b_J_LEFT = 0
                _GameController.play_sound(select1_sfx, 0.1)

                if scene == -1:
                    if menu_selected == 1:
                        if master_volume > 0: master_volume -= 10
                    if menu_selected == 2:
                        if music_volume > 0: music_volume -= 10
                    if menu_selected == 3:
                        if sfx_volume > 0: sfx_volume -= 10
                        
            if b_J_RIGHT and automove_b_J_RIGHT and type(menu_buttons[menu_selected]) == Slider:
                time_since_move_b_J_RIGHT = 0
                _GameController.play_sound(select1_sfx, 0.1)

                if scene == -1:
                    if menu_selected == 1:
                        if master_volume < 100: master_volume += 10
                    if menu_selected == 2:
                        if music_volume < 100: music_volume += 10
                    if menu_selected == 3:
                        if sfx_volume < 100: sfx_volume += 10

            

            #automove menu cooldowns
            if time_since_move_b_J_UP >= J_menu_cooldown:
                #this is necessary to reset automove
                time_since_move_b_J_UP = 0
                automove_b_J_UP = True
            else:
                automove_b_J_UP = False

            if time_since_move_b_J_DOWN >= J_menu_cooldown:
                time_since_move_b_J_DOWN = 0
                automove_b_J_DOWN = True
            else:
                automove_b_J_DOWN = False

            if time_since_move_b_J_LEFT >= J_menu_cooldown:
                time_since_move_b_J_LEFT = 0
                automove_b_J_LEFT = True
            else:
                automove_b_J_LEFT = False

            if time_since_move_b_J_RIGHT >= J_menu_cooldown:
                time_since_move_b_J_RIGHT = 0
                automove_b_J_RIGHT = True
            else:
                automove_b_J_RIGHT = False


            time_since_move_b_J_UP += dt
            time_since_move_b_J_DOWN += dt
            time_since_move_b_J_LEFT += dt
            time_since_move_b_J_RIGHT += dt

            if not b_J_UP: automove_b_J_UP = True
            if not b_J_DOWN: automove_b_J_DOWN = True
            if not b_J_LEFT: automove_b_J_LEFT = True
            if not b_J_RIGHT: automove_b_J_RIGHT = True



        if player and playing:
            #joystick
            pdir = pygame.math.Vector2(joysticks[player1_id].get_axis(J_MOVE_x), joysticks[player1_id].get_axis(J_MOVE_y))
            player.dir.x = pdir.x if abs(pdir.x)>dead_zone else player.dir.x
            player.dir.y = pdir.y if abs(pdir.y)>dead_zone else player.dir.y

            fdir = pygame.math.Vector2(joysticks[player1_id].get_axis(J_AIM_x), joysticks[player1_id].get_axis(J_AIM_y))
            if abs(fdir.x)<dead_zone: fdir.x = 0
            if abs(fdir.y)<dead_zone: fdir.y = 0
            fdir = fdir.normalize() if fdir else fdir
            ffdir = fdir if fdir.magnitude() > 0.9 else ffdir

            if fired_down_joy and time_since_fired >= reload_time:
                time_since_fired = 0
                player.fire(ffdir)

            if acs_shoot_while_aiming:
                if fdir.magnitude()>0.9:
                    if time_since_fired >= reload_time and not fired_down_joy:
                        time_since_fired = 0
                        player.fire(ffdir)            


    #button
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            _GameController.quit()   

        if event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks[joy.get_instance_id()] = joy
            # print(f"Joystick {joy.get_instance_id()} connencted")
            if len(joysticks) == 1: 
                player1_id = joy.get_instance_id()
                # print(f'player 1 assigned to joy {player1_id}')
        if event.type == pygame.JOYDEVICEREMOVED:
            del joysticks[event.instance_id]
            # print(f"Joystick {event.instance_id} disconnected")


        if len(joysticks)>0:                    

            if player and playing:
                #Fire
                if joysticks[player1_id].get_button(J_FIRE) or b_J_FIREAXIS:
                    if not fired_down_joy:
                        player.fire(ffdir)
                    
                    fired_down_joy = True
                else:
                    fired_down_joy = False
        

        if event.type == pygame.JOYBUTTONDOWN:
            if scene == 1:
                if event.button == J_PAUSE and not lost:
                    if not paused: _GameController.pause()
                    else: _GameController.unpause()


            if event.button == J_SELECT:
                    if scene == -1:
                        #settings menu
                        if menu_selected == 0:
                            _GameController.change_scene(0)
                        if menu_selected == len(menu_buttons)-2:
                            _SettingsManager.reset_settings()

                            master_volume = _SettingsManager.settings['master_volume']
                            music_volume = _SettingsManager.settings['music_volume']
                            sfx_volume = _SettingsManager.settings['sfx_volume']

                        if menu_selected == len(menu_buttons)-1:
                            _GameController.save_highscore(0)

                    elif scene == 0:
                        if menu_selected == 0:
                            _GameController.change_scene(1)
                            _GameController.restart_game()
                        if menu_selected == 1:
                            _GameController.change_scene(-1)
                        if menu_selected == 2:
                            _GameController.quit()

                    elif scene == 1:
                        if lost:
                            #lose menu
                            if menu_selected == 0:
                                _GameController.restart_game()
                            if menu_selected == 1:
                                _GameController.change_scene(0)

                        elif paused:
                            #pause menu
                            if menu_selected == 0:
                                _GameController.unpause()
                            if menu_selected == 1:
                                _GameController.change_scene(0)


                    _GameController.play_sound(select2_sfx, .08)



        #keyboard
        if event.type == pygame.KEYDOWN:
            #secret code handling
            code_string += event.unicode
            if len(code_string) > 6:
                code_string = code_string[1:]     
            if code_string=='batman' and not batman:
                batman = True

                background = 1

                player_img = './assets/img/battedman.png'
                enemy_img = './assets/img/batman_tomcruise.png'
                enemy_hurt_1_img = './assets/img/batman_tomcruise_hurt1.png'
                enemy_hurt_2_img = './assets/img/batman_tomcruise_hurt2.png'
                enemy_hurt_3_img = './assets/img/batman_tomcruise_hurt3.png'

                music_intro_sfx = None
                music_loop_sfx = './assets/audio/batman/batman_loop.wav'

                shoot_sfx = _GameController.return_shoot_sounds()[random.randint(0,9)]
                hit_sfx = _GameController.return_hit_sounds()[random.randint(0,3)]

                select1_sfx = './assets/audio/batman/batman_boop.wav'
                select2_sfx = './assets/audio/batman/batman_gamestart.wav'
                kill_sfx = hit_sfx
                lose_sfx = './assets/audio/batman/batman_bwahbwah.wav'


                if scene == 1:_GameController.restart_game()
                else: _GameController.play_sound('./assets/audio/batman/batman_stinger.wav', .4)



            if scene == 1:
                if event.key in PAUSE and not lost:
                    if not paused: _GameController.pause()
                    else: _GameController.unpause()

            if in_menu:          

                #keyboard       
                if event.key in AUP:
                    _GameController.play_sound(select1_sfx, 0.1)
                    menu_selected -= 1
                if event.key in ADOWN:
                    _GameController.play_sound(select1_sfx, 0.1)
                    menu_selected += 1

                if event.key in ARIGHT and type(menu_buttons[menu_selected]) == Slider:
                    _GameController.play_sound(select1_sfx, 0.1)
                    
                    if scene == -1:
                        if menu_selected == 1:
                            if master_volume < 100: master_volume += 10
                        if menu_selected == 2:
                            if music_volume < 100: music_volume += 10
                        if menu_selected == 3:
                            if sfx_volume < 100: sfx_volume += 10

                if event.key in ALEFT and type(menu_buttons[menu_selected]) == Slider:
                    _GameController.play_sound(select1_sfx, 0.1)
                    
                    if scene == -1:
                        if menu_selected == 1:
                            if master_volume > 0: master_volume -= 10
                        if menu_selected == 2:
                            if music_volume > 0: music_volume -= 10
                        if menu_selected == 3:
                            if sfx_volume > 0: sfx_volume -= 10



                if event.key in SELECT:
                    if scene == -1:
                        #settings menu
                        if menu_selected == 0:
                            _GameController.change_scene(0)
                        if menu_selected == len(menu_buttons)-2:
                            _SettingsManager.reset_settings()

                            master_volume = _SettingsManager.settings['master_volume']
                            music_volume = _SettingsManager.settings['music_volume']
                            sfx_volume = _SettingsManager.settings['sfx_volume']

                        if menu_selected == len(menu_buttons)-1:
                            _GameController.save_highscore(0)

                    elif scene == 0:
                        if menu_selected == 0:
                            _GameController.change_scene(1)
                            _GameController.restart_game()
                        if menu_selected == 1:
                            _GameController.change_scene(-1)
                        if menu_selected == 2:
                            _GameController.quit()

                    elif scene == 1:
                        if lost:
                            #lose menu
                            if menu_selected == 0:
                                _GameController.restart_game()
                            if menu_selected == 1:
                                _GameController.change_scene(0)

                        elif paused:
                            #pause menu
                            if menu_selected == 0:
                                _GameController.unpause()
                            if menu_selected == 1:
                                _GameController.change_scene(0)


                    _GameController.play_sound(select2_sfx, .08)


        if event.type == pygame.KEYDOWN:
            if scene == 1:
                if event.key == RESET:
                    _GameController.restart_game()

                if event.key == RESETHIGHSCORE:
                    highscore = 0
                    _GameController.save_highscore(highscore)

            if event.key == QUIT:
                _GameController.quit()   




    for i in text_sprites:
        i.kill()

    if scene == -1:
        #SETTINGS SCENE

        playing = False
        in_menu = True

        #draw text
        title_text = TextSprite('SETTINGS', (0,0), [text_header_sprites, text_sprites, all_sprites])
        title_text.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 90)

        mainmenu_button = TextSprite('back to main menu', (0,0), [text_header_sprites, text_sprites, all_sprites])
        mainmenu_button.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 0)

        master_volume_slider = Slider('volume', (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 30), [text_sprites, all_sprites], master_volume)
        music_volume_slider = Slider('music volume', (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 60), [text_sprites, all_sprites], music_volume)
        sfx_volume_slider = Slider('sfx volume', (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 90), [text_sprites, all_sprites], sfx_volume)

    
        #Full screen mode

        #Controls?


        reset_settings_button = TextSprite('reset settings', (0,0), [text_sprites, all_sprites])
        reset_settings_button.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 120)

        reset_highscore_button = TextSprite('reset highscore', (0,0), [text_sprites, all_sprites])
        reset_highscore_button.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 150)


        menu_buttons = [mainmenu_button, master_volume_slider, music_volume_slider, sfx_volume_slider, reset_settings_button, reset_highscore_button]
        if menu_selected > len(menu_buttons)-1: menu_selected = 0
        if menu_selected < 0: menu_selected = len(menu_buttons)-1   



    if scene == 0:
        #TITLE SCENE
        
        playing = False
        in_menu = True

        #draw text
        if len(joysticks)==0: instructions_text = TextSprite('use WASD keys to move, arrow keys to shoot.', (WINDOW_WIDTH/2, WINDOW_HEIGHT - 30), [text_header_sprites, text_sprites, all_sprites], 20)
        if len(joysticks)>0: instructions2_text = TextSprite('use left joystick to move, right joystick to aim, and right trigger to fire.', (WINDOW_WIDTH/2, WINDOW_HEIGHT - 30), [text_header_sprites, text_sprites, all_sprites], 20)


        title_text = TextSprite('BATMAN VS TOM CRUISE THE SCIENTOLOGISTS' if batman else 'A POTATO VS TOM CRUISE THE SCIENTOLOGISTS', (0,0), [text_header_sprites, text_sprites, all_sprites], 35)
        title_text.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 90)

        startgame_button = TextSprite('start game', (0,0), [text_header_sprites, text_sprites, all_sprites])
        startgame_button.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 0)

        settings_button = TextSprite('settings', (0,0), [text_header_sprites, text_sprites, all_sprites])
        settings_button.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 30)

        quit_button = TextSprite('quit', (0,0), [text_header_sprites, text_sprites, all_sprites])
        quit_button.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 60)


        menu_buttons = [startgame_button, settings_button, quit_button]

        if menu_selected > len(menu_buttons)-1: menu_selected = 0
        if menu_selected < 0: menu_selected = len(menu_buttons)-1
        



    if scene == 1:

        #spawn Player
        if player_sprites.__len__() == 0:
            player = Player([player_sprites, all_sprites])


        #spawn Toms
        if playing:
            time += dt
            frame += 1

            if tt >= time_to_spawn:
                for i in range(random.randint(1,int(dic-start_dic+2))):
                    tommy = Tom(random.randint(25,300), player.pos, [all_sprites, tom_sprites])
                tt = 0
            else:
                tt += dt
                time_to_spawn = time_to_spawn / dic * 10000
                dic += dt/20 


            #update score
            score = int(time*100)
            if score >= highscore: highscore = score

        for i in text_score_sprites:
            i.delete()

        highscore_text = TextSprite('high score: ' + str(highscore), (10,10), [text_score_sprites, text_sprites, all_sprites], 20)
        highscore_text.rect.topleft = highscore_text.pos
        score_text = TextSprite('score: ' + str(score), (10,10), [text_score_sprites, text_sprites, all_sprites])
        score_text.rect.topleft = score_text.pos + (0, highscore_text.rect.height)


        #update menu state

        if paused:
            #paused
            in_menu = True

            paused_text = TextSprite('PAUSED', (WINDOW_WIDTH/2,(WINDOW_HEIGHT/2)-90), [text_header_sprites, text_sprites, all_sprites])

            resume_button = TextSprite('resume', (0,0), [text_header_sprites, text_sprites, all_sprites])
            resume_button.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 0)

            mainmenu_button = TextSprite('back to main menu', (0,0), [text_header_sprites, text_sprites, all_sprites])
            mainmenu_button.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 30)

            menu_buttons = [resume_button, mainmenu_button]
            if menu_selected > len(menu_buttons)-1: menu_selected = 0
            if menu_selected < 0: menu_selected = len(menu_buttons)-1   


        elif lost:
            #lost
            gameover_text = TextSprite('GAME OVER', (WINDOW_WIDTH/2,(WINDOW_HEIGHT/2)-90), [text_lose_sprites, text_sprites, all_sprites])
            
            if time_since_lost >= 1.2:
                in_menu = True

                restart_button = TextSprite('try again', (0,0), [text_lose_sprites, text_sprites, all_sprites])
                restart_button.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 0)

                mainmenu_button = TextSprite('back to main menu', (0,0), [text_lose_sprites, text_sprites, all_sprites])
                mainmenu_button.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 30)

                menu_buttons = [restart_button, mainmenu_button]
                if menu_selected > len(menu_buttons)-1: menu_selected = 0
                if menu_selected < 0: menu_selected = len(menu_buttons)-1   

            time_since_lost = time_since_lost + dt
        else: 
            #playing
            in_menu = False
            time_since_lost = 0
            




    
    #update objects
    all_sprites.update(dt)

    #background
    if background == 0: screen.fill('white')
    if background == 1: screen.fill('black')
    if background == 100: screen.blit(bg_img, (0, 0))

    #draw render
    if background == 1:
        for t in text_sprites:    
            if hasattr(t, 'change_color') and callable(getattr(t, 'change_color')):
                t.change_color('white')

    all_sprites.draw(screen)
    text_sprites.draw(screen)
    if in_menu: pygame.draw.rect(screen, ('black') if background==0 else ('white'), menu_buttons[menu_selected].rect, 2)


    #update the screen
    pygame.display.update()

pygame.quit()