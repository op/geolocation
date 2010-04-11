#!/usr/bin/env python
# -*- coding: utf-8 -*-

import geolocation
import geolocation.providers.google as google

# alternative 1
geocodes = geolocation.GeolocationFinder('google')
print geocodes.get_by_address('Borgmästargatan, Stockholm').locations[0].position

# alternative 2
geocodes = google.GoogleGeocodes()
print geocodes.get_by_position(latitude=59.3145477, longitude=18.0864521).locations[0].position
