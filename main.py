import pygame as pg
import random
import settings
import Sprites
import os
from os import path
from random import choice

# CACTUS JUMP

# credits
# 2020 - Jack St. Hilaire
# All sounds and music created by Jack St. Hilaire
# cactus character designed by Jack St. Hilaire
# enemy and platform sprites: www.kenney.nl


class Game:
    def __init__(self):

        # game init, sound init, fonts init
        pg.init()
        pg.mixer.init()
        self.font_name = pg.font.match_font(settings.FONT_NAME)

        # keep game running to start
        self.running = True

        # screen, clock, display name
        self.screen = pg.display.set_mode((settings.width, settings.height))
        pg.display.set_caption(settings.title)
        self.clock = pg.time.Clock()

        # load images, scores, etc.
        self.data_load()

    def data_load(self):

        # read high score from file, unless file doesn't exist or the game hasn't been played yet
        with open(settings.HSFILE, 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                # if it doesn't work, set the high score to 0
                self.highscore = 0

        # loading spritesheet and character from image folder
        self.spritesheet = Sprites.SpriteSheet(settings.SPRITESHEET)
        self.charimage = pg.image.load(settings.CHAR_SPRITE)
        self.bombimage = pg.image.load('bombsprite.png')


        # sound directory and game sounds (not music)
        self.jump_snd = pg.mixer.Sound('jump.wav')
        self.coin_snd = pg.mixer.Sound('coinsound.wav')
        self.boost_snd = pg.mixer.Sound('boostsound.wav')
        self.bomb_snd = pg.mixer.Sound('explsound.wav')
        self.death_snd = pg.mixer.Sound('deathsound.wav')

    def new(self):

        # new level, add player, objects, platforms, and enemies to sprites, called on game start
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powers = pg.sprite.Group()
        self.enemies = pg.sprite.Group()

        # reference for the player class, so methods from player can be called, add to sprites
        self.player = Sprites.Player(self)
        self.all_sprites.add(self.player)

        # starting platforms, created from settings
        for platf in settings.PLATFORM_LIST:
            Sprites.Platform(self, *platf)

        # score starts at 0, enemy spawn timer starts at 0
        self.score = 0
        self.enemy_timer = 0

        # load music
        pg.mixer.music.load('Yeti.ogg')

        # run the game
        self.run()

    def run(self):
        # gm loop, runs all game processes after new game is started

        # self.playing will be false when the game ends or user quits
        self.playing = True

        # play music, set volume
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(0.39)

        # game loop
        while self.playing:
            # keep clock going at game FPS, call events update and draw
            self.clock.tick(settings.fps)
            self.events()
            self.update()
            self.draw()

        # fade music after the game loop ends
        pg.mixer.music.fadeout(600)

    def update(self):
        # updates the sprites, checking for key press, applying gravity, game over condition

        # calls the update method of all sprite classes in existence, importantly player
        self.all_sprites.update()

        # enemy spawn, randomized based on desired frequency of enemy spawns
        now = pg.time.get_ticks()
        if now - self.enemy_timer > 10000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.enemy_timer = now
            Sprites.Enemies(self)

        # enemy hit detection, kill player on hit
        enemyhits = pg.sprite.spritecollide(self.player, self.enemies, False)
        if enemyhits:
            self.death_snd.play()
            self.playing = False

        # check for collision with platforms
        hits = pg.sprite.spritecollide(self.player, self.platforms, False)

        if hits:
            # on collision with platform, stop vertical , make sure player is placed on the platform
            if self.player.vel.y > 0:

                if hits[0].rect.right + 15 > self.player.pos.x > hits[0].rect.left - 15:
                    if self.player.pos.y < hits[0].rect.bottom:
                        self.player.pos.y = hits[0].rect.top + 1
                        self.player.vel.y = 0

        # check for collision with objects/powers
        powhits = pg.sprite.spritecollide(self.player, self.powers, True)

        # detect the type of pow, apply effect, play sound
        for pow in powhits:
            if pow.type == 'boost':
                self.player.vel.y = -50
                self.boost_snd.play()
            elif pow.type == 'coin':
                self.score = self.score + 3
                self.coin_snd.play()
            elif pow.type == 'bomb':
                lr = choice(['L', 'R'])
                if lr == 'L':
                    self.player.vel.x = 100
                else:
                    self.player.vel.x = -100
                self.bomb_snd.play()

            else:
                continue

        # move screen if player is close to the top (3/4 for now)
        if self.player.rect.top <= settings.height / 4:
            self.player.pos.y += abs(self.player.vel.y)

            # move all the platforms, and remove them if they leave the screen
            for plat in self.platforms:
                plat.rect.y += abs(self.player.vel.y)

                if plat.rect.top >= settings.height:
                    plat.kill()
                    # players can score points on passing platforms, in addition to picking up coins
                    self.score += 1

            # same for enemies
            for enemy in self.enemies:
                enemy.rect.y += abs(self.player.vel.y)

                if enemy.rect.top >= settings.height:
                    enemy.kill()

        # make new platforms, limit 8 at a time
        while len(self.platforms) < 8:
            # old w vals --> 50, 100
            w = random.randrange(60, 120)
            Sprites.Platform(self, random.randrange(0, settings.width - w), random.randrange(-75, -30))

        # game over condition, when player falls off the bottom of the screen
        if self.player.rect.bottom > settings.height:
            self.death_snd.play()
            self.playing = False

    def events(self):
        # possible user based events to track, quit and jump

        # for all events that pg can find
        for event in pg.event.get():

            # closing window check
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            # jump event check, jump end check when spacebar is let go, or boost event
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()

            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_over()

            # double jump, less effective
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    self.player.vel.y = -15

    def draw(self):
        # draw to screen
        # RENDER: sprites, background, score text
        self.screen.fill(settings.BLUE)
        self.all_sprites.draw(self.screen)
        self.drawText(str(self.score), 30, settings.RED, settings.width / 2, 20)

        # do this only after drawing everything
        pg.display.flip()

    def show_start_screen(self):
        # the start screen
        self.screen.fill(settings.GREEN)
        self.drawText(settings.title, 50, settings.WHITE, settings.width / 2, 50)
        self.drawText("The hardest cactus game of all time", 30, settings.WHITE, settings.width / 2, 130)
        self.drawText("Press a key to play", 40, settings.GREY, settings.width / 2, 250)
        self.drawText("High Score: " + str(self.highscore), 40, settings.GREY, settings.width / 2, 300)
        self.drawText("Jack St. Hilaire, 2020", 30, settings.WHITE, settings.width / 2, 500)
        pg.display.flip()

        # waiting for key press to start
        self.waitKey()

    def show_go_screen(self):
        # game over screen

        self.screen.fill(settings.GREEN)
        self.drawText(settings.title, 50, settings.WHITE, settings.width / 2, 50)
        self.drawText("Press a key to play", 40, settings.WHITE, settings.width / 2, 250)

        # if the high score is beaten, update
        if self.score > self.highscore:
            self.highscore = self.score

            # display the new record and print to file
            self.drawText("New Record: " + str(self.highscore), 40, settings.RED, settings.width / 2, 300)
            with open(settings.HSFILE, 'w') as f:
                f.write(str(self.score))
        else:
            # if no new record, just display previous high score
            self.drawText("High Score: " + str(self.highscore), 40, settings.RED, settings.width / 2, 300)

        pg.display.flip()

        # play again on key press
        self.waitKey()

    def waitKey(self):
        # waits for a key press to start the game on one of the start screens
        waiting = True
        while waiting:
            self.clock.tick(settings.fps)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def drawText(self, text, size, color, x, y):

        # draw text to the screen
        # need to make list of fonts to use different ones   <-----------------
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


# actually create and run the game, title and end screens, quit when done

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
