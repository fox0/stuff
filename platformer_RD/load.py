#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import join
import pygame


PREFIX_DATA = 'data'

CACHE = dict()


def get_image(name):
    global CACHE
    if name not in CACHE:
        image = load_image(name)
        rect = image.get_rect()
        CACHE[name] = image, rect.w, rect.h  # а нужна ли?
    return CACHE[name]


def load_image(name):
    fullname = join(PREFIX_DATA, name)
    image = pygame.image.load(fullname)
    if not image.get_alpha():
        image = image.convert()
    else:
        image = image.convert_alpha()
    return image
