# -*- coding: utf-8 -*-
# Copyright (C) 2009 Örjan Persson

import math

from geolocation import abstract


class Geolocation(abstract.Dictable):
    def __init__(self, address, position, bounds=None, viewport=None):
        self.address = address
        self.position = position
        self.viewport = viewport
        self.bounds = bounds


class GeolocationPosition(abstract.Dictable):
    def __init__(self, lat, long):
        self.lat = lat
        self.long = long


class GeolocationAddress(abstract.Dictable):
    def __init__(self, parts):
        self.parts = parts


class GeolocationAddressPart(abstract.Dictable):
    def __init__(self, short, long, types):
        self.short = short
        self.long = long
        self.type = types


class CardinalDirections(object):
    directions = set()

    @classmethod
    def add_direction(cls, name, degree):
        if degree < 0:
            degree += math.degrees(2*math.pi)
        cls.directions.add(name)
        setattr(cls, name, degree)


class Compass(CardinalDirections):
    pass


__sorted__ = ['north', 'east', 'south', 'west']
for i, d in enumerate(__sorted__):
    degree = math.degrees(i / 2. * math.pi)

    CardinalDirections.add_direction(d, degree)
    Compass.add_direction(d, degree)

    left = __sorted__[i-1]
    right = __sorted__[-1*(i-1)]

    if left != right:
        Compass.add_direction(d + '_' + right, degree + math.degrees((1 / 4.) * math.pi))
        Compass.add_direction(d + '_' + left,  degree - math.degrees((1 / 4.) * math.pi))

del i, d
