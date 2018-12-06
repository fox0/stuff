# -*- coding: utf-8 -*-


def load_conf(filename):
    with open(filename, 'r') as f:
        return [i.strip() for i in f.read().split('\n') if i and i[0] != '#']


def load_conf_dict(filename):
    result = {}
    for i in load_conf(filename):
        k, v = i.split(' ')
        result[k] = v
    return result
