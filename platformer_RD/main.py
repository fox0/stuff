#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
from pygame import *

from camera import Camera
from player import Player
from blocks import Platform
from load import get_image

DISPLAY = WIN_WIDTH, WIN_HEIGHT = 800, 640  # ширина и высота создаваемого окна


def load_level(entities):
    with open('level.txt') as f:
        level = f.readlines()

    platforms = list()  # то, во что мы будем врезаться или опираться
    x, y = 0, 0  # координаты
    _, _, w, h = Platform(x, y).rect
    for row in level:  # вся строка
        for col in row:        # каждый символ
            if col == "*":
                pf = Platform(x, y)
                entities.add(pf)
                platforms.append(pf)
            x += w  # блоки платформы ставятся на ширине блоков
        y += h     # то же самое и с высотой
        x = 0

    total_level_width = len(level[0]) * w  # Высчитываем фактическую ширину уровня
    total_level_height = len(level) * h    # и высоту
    return platforms, total_level_width, total_level_height


def main():
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption('test v0.0.1')
    bg, _, _ = get_image('640_winter_lab_by_kooner_cz.png')
    
    entities = pygame.sprite.Group()  # Все объекты
    hero = Player(0, 50)
    entities.add(hero)
    platforms, total_level_width, total_level_height = load_level(entities)
    camera = Camera(WIN_WIDTH, WIN_HEIGHT, total_level_width, total_level_height)

    timer = pygame.time.Clock()
    keys = {
        K_UP: False,
        K_DOWN: False,
        K_LEFT: False,
        K_RIGHT: False,
        K_SPACE: False,
    }
    while True:
        timer.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT:
                return
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    return
                keys[e.key] = True
            if e.type == KEYUP:
                keys[e.key] = False

        hero.update(keys, platforms)  # передвижение
        camera.update(hero)           # центризируем камеру относительно персонажа

        screen.blit(bg, (0, 0))       # каждую итерацию необходимо всё перерисовывать
        for e in entities:
            screen.blit(e.image, camera.apply(e))
        pygame.display.update()     # обновление и вывод всех изменений на экран


if __name__ == "__main__":
    main()
