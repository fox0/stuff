#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pygame import *
from animation import Animation, COLOR_KEY


MAX_SPEED_X = 10
MAX_SPEED_Y = 5

JUMP_POWER = 10
MOVE_SPEED = 3
FLY_POWER = 1

TRENIE = 1
TRENIE_FLY = 0.3
GRAVITY = 0.25

WIDTH = 80   # TODO 94 = 14 + 66 + 14
HEIGHT = 80  # !

# спрайты
ANIMATION = {
    'stay_right': ['0_2.png'],

    # 'right': ['1_12.png', '1_13.png', '1_14.png', '1_15.png', '1_16.png', '1_17.png'],
    # 'right': ['2_12.png', '2_13.png', '2_14.png', '2_15.png', '2_16.png', '2_17.png'],
    'right': ['3_12.png', '3_13.png', '3_14.png', '3_15.png', '3_16.png', '3_17.png'],

    # 'jump_right': ['4_12.png', '4_13.png', '4_14.png', '4_15.png', '4_16.png', '4_17.png'],  # летит вертикально
    'jump_right': ['5_12.png', '5_13.png', '5_14.png', '5_15.png', '5_16.png', '5_17.png'],  # парит
    'fly_right': ['6_12.png', '6_13.png', '6_14.png', '6_15.png', '6_16.png', '6_17.png'],  # летит горизонтально
}


class Player(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.startX = x  # Начальная позиция Х, пригодится когда будем переигрывать уровень
        self.startY = y
        self.speed_x = 0    # скорость перемещения. 0 - стоять на месте
        self.speed_y = 0    # скорость вертикального перемещения
        self.is_fly = True
        self.id_left = False

        self.image = Surface((WIDTH, HEIGHT))
        self.image.fill(Color(COLOR_KEY))
        self.rect = Rect(x, y, WIDTH, HEIGHT)  # прямоугольный объект
        self.image.set_colorkey(Color(COLOR_KEY))  # делаем фон прозрачным  # !!! какой-то костыль

        self.animation = dict()
        for key, val in ANIMATION.items():
            self.animation[key] = Animation(self.image, val)
            if 'right' in key:
                key = key.replace('right', 'left')
                self.animation[key] = Animation(self.image, val, xbool=True)

    def update(self, keys, platforms):
        jump = keys[K_SPACE]
        up = keys[K_UP]
        down = keys[K_DOWN]
        left = keys[K_LEFT]
        right = keys[K_RIGHT]

        if jump:
            if not self.is_fly:
                self.speed_y -= JUMP_POWER

        if up:
            self.speed_y -= FLY_POWER

        if down:
            self.speed_y += FLY_POWER

        if left:
            self.speed_x -= MOVE_SPEED

        if right:
            self.speed_x += MOVE_SPEED

        if self.is_fly:
            if self.speed_x > 0:
                self.speed_x -= TRENIE_FLY
            if self.speed_x < 0:
                self.speed_x += TRENIE_FLY
        else:
            if self.speed_x > 0:
                self.speed_x -= TRENIE
            if self.speed_x < 0:
                self.speed_x += TRENIE

        self.speed_y += GRAVITY

        # self.speed_y = min(self.speed_y, MAX_SPEED)  # вниз без ограничений
        self.speed_y = max(self.speed_y, -MAX_SPEED_Y)   # вверх
        self.speed_x = min(self.speed_x, MAX_SPEED_X)    # вправо
        self.speed_x = max(self.speed_x, -MAX_SPEED_X)   # влево

        # print 'speed: %s\t%s' % (self.speed_x, self.speed_y)

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.is_fly:
            animation = 'jump_left' if self.id_left else 'jump_right'
        else:
            animation = 'stay_left' if self.id_left else 'stay_right'

        if left:
            self.id_left = True
            animation = 'fly_left' if self.is_fly else 'left'

        if right:
            self.id_left = False
            animation = 'fly_right' if self.is_fly else 'right'

        self.animation[animation].update()  # перерисовываем спрайт

        self.is_fly = True
        for p in platforms:
            if sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком
                # print '%s\t%s' % (self.rect.bottom, p.rect.top)
                if self.speed_y > 0:
                    self.is_fly = False
                    self.speed_y = 0
                    self.rect.bottom = p.rect.top + 1  # запрещаем проваливаться сквозь пол
                else:
                    self.speed_y = 0  # bug


                #
                # if xvel > 0:                       # если движется вправо
                #     self.rect.right = p.rect.left  # то не движется вправо
                #
                # if xvel < 0:                       # если движется влево
                #     self.rect.left = p.rect.right  # то не движется влево
                #
                # if yvel > 0:                       # если падает вниз
                #     self.rect.bottom = p.rect.top  # то не падает вниз
                #     self.is_fly = False
                #     self.speed_y = 0                  # и энергия падения пропадает
                #
                # if yvel < 0:                       # если движется вверх
                #     self.rect.top = p.rect.bottom  # то не движется вверх
                #     self.speed_y = 0                  # и энергия прыжка пропадает

        self.rect.x = max(0, self.rect.x)   # левая граница экрана
        self.rect.y = max(0, self.rect.y)   # верхняя граница экрана
