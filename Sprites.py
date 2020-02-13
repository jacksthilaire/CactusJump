# SPRITES
import settings
import pygame as pg
import random
from random import choice
vector = pg.math.Vector2

bombcheck = False
class Player(pg.sprite.Sprite):

    def __init__(self, game):
        self.game = game
        self.layer = settings.PLAYER_LAYER

        # player image and size creation, movement init
        pg.sprite.Sprite.__init__(self)
        self.image = game.charimage

        # key out black background
        self.image.set_colorkey(settings.BLACK)

        # self rect, pos, vel, acc vectors
        self.rect = self.image.get_rect()
        self.rect.center = (settings.width / 2, settings.height / 2)
        self.pos = vector(settings.width / 2, settings.height / 2)
        self.vel = vector(0, 0)
        self.acc = vector(0, 0)

    def update(self):
        # over-write update method, called from game loop
        # x and y accelerations start at 0, updated on key press
        self.acc = vector(0, settings.PLAYER_GRAVITY)
        keys = pg.key.get_pressed()

        # left and right movement
        if keys[pg.K_LEFT]:
            self.acc.x = -settings.PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = settings.PLAYER_ACC

        # move sprite rect accordingly, apply friction to acc then
        # update the vel and pos from this
        self.acc.x += self.vel.x * settings.PLAYER_FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # wrap around the sides of the screen, if the player leaves the screen
        if self.pos.x > settings.width:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = settings.width

        # this allows the player to land on platforms
        self.rect.midbottom = self.pos

    def jump(self):
        # if the player isn't already in the air or falling, update vertical velocity
        if self.vel.y == 0:
            self.vel.y = -20
            self.game.jump_snd.play()

    def jump_over(self):
        # end the jump early if the space button is let go
        if self.vel.y < -3:
            self.vel.y = -2



class Platform(pg.sprite.Sprite):
    # x/y location, w/h size
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.platforms
        self.layer = settings.PLATFORM_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # possible images and platform sizes
        images = [self.game.spritesheet.get_image(0, 1056, 380, 94),
                  self.game.spritesheet.get_image(0, 960, 380, 94),
                  self.game.spritesheet.get_image(0, 672, 380, 94)]

        sizes = [(100, 20), (50, 20)]

        # set image and make correct size, key out background
        self.image = choice(images)
        self.image = pg.transform.scale(self.image, choice(sizes))
        self.image.set_colorkey(settings.BLACK)

        # rectangle
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # spawn powers
        if random.randrange(100) < settings.POW_RATE:
            Powers(self.game, self)


class Powers(pg.sprite.Sprite):
    # x/y location, w/h size
    def __init__(self, game, plat):
        self.groups = game.all_sprites, game.powers
        self.layer = settings.POW_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)

        # spawn on platform as one of three options
        self.game = game
        self.plat = plat
        self.type = choice(['coin', 'boost', 'bomb'])

        # set image based on type
        if self.type == 'coin':
            self.image = self.game.spritesheet.get_image(244, 1981, 61, 61)
        elif self.type == 'boost':
            self.image = self.game.spritesheet.get_image(852, 1089, 65, 77)
        elif self.type == 'bomb':
            self.image = self.game.bombimage
        else:
            self.image = self.game.spritesheet.get_image(244, 1981, 61, 61)

        self.image.set_colorkey(settings.BLACK)

        # rectangle placement
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()



class Enemies(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = settings.ENEMY_LAYER
        self.groups = game.all_sprites, game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # alternating images, keyed out
        self.image_up = self.game.spritesheet.get_image(421, 1390, 148, 142)
        self.image_up.set_colorkey(settings.BLACK)
        self.image_down = self.game.spritesheet.get_image(534, 913, 142, 148)
        self.image_down.set_colorkey(settings.BLACK)

        self.image_down = pg.transform.scale(self.image_down, (50, 50))
        self.image_up = pg.transform.scale(self.image_up, (50, 50))
        # start with up image
        self.image = self.image_up

        # initialization of position and speed
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-100, settings.width + 100])
        self.vx = random.randrange(3, 4)

        if self.rect.centerx > settings.width:
            self.vx *= -1
        self.rect.y = random.randrange(settings.height / 2)
        self.vy = 0
        self.dy = 0.5

    def update(self):
        # move in x and y axis
        self.rect.x += self.vx
        self.vy += self.dy

        # keep vel constant
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1
        center = self.rect.center

        # switch the images (animation)
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.rect.y += self.vy

        # kill if it leaves the screen
        if self.rect.left > settings.width + 100 or self.rect.right < -100:
            self.kill()


class SpriteSheet:
    # parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # select image from sheet, transform to correct size
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))

        # rescaling
        image = pg.transform.scale(image, ((width // 2) - 10, (height // 2) - 10))
        return image
