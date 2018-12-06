#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from pygame import Color, transform
from load import get_image


COLOR_KEY = '#333333'


class Animation(object):
    def __init__(self, dest_surface, frames, delay=0.1, xbool=False):
        """
        :param dest_surface:
        :param frames: список с именами файлов
        :param delay: скорость смены кадров
        """
        self.image = dest_surface
        res = list()
        for frame in frames:
            image, _, _ = get_image(frame)
            if xbool:
                image = transform.flip(image, True, False)  # зеркалим
            res.append(image)
        self.frames = res
        self.frame_number = 0
        self.frame_max = len(frames)
        self.start_time = time.time()
        self.delay = delay

    def update(self):
        tek_time = time.time()
        if tek_time - self.start_time > self.delay:
            self.start_time = tek_time
            self.frame_number += 1
            if self.frame_number >= self.frame_max:
                self.frame_number = 0

        self.image.fill(Color(COLOR_KEY))
        self.image.blit(self.frames[self.frame_number], (0, 0))  # перерисовываем всегда!
