#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pygame.rect import Rect


class Camera(object):
    def __init__(self, win_width, win_height, width, height):
        self.win_width = win_width
        self.win_height = win_height
        self.state = Rect(0, 0, width, height)

    def camera_func(self, camera, target_rect):
        l, t, _, _ = target_rect
        l, t = -l+self.win_width / 2, -t+self.win_height / 2
        l = min(0, l)                              # Не движемся дальше левой границы
        l = max(self.win_width-camera.width, l)    # Не движемся дальше правой границы
        t = min(0, t)                              # Не движемся дальше верхней границы
        t = max(self.win_height-camera.height, t)  # Не движемся дальше нижней границы
        return Rect(l, t, camera.width, camera.height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)
