#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pygame import sprite, Rect
from load import get_image


class Platform(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image, w, h = get_image('platform.png')
        self.rect = Rect(x, y, w, h)
