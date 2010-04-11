# -*- coding: utf-8 -*-
# Copyright (C) 2009 Örjan Persson

import geolocation

from geolocation import client
from geolocation import codecs
from geolocation import orientation
from geolocation import providers


class GoogleGeocodeJsonDecoder(codecs.GeolocationCodecs.get_class('json')):
    def __init__(self, *args, **kwargs):
        super(GoogleGeocodeJsonDecoder, self).__init__(*args, **kwargs)

        # google uses quite similar mapping (what an coincident!)
        self.direction_mapping = {}
        for direction in orientation.Compass.directions:
            self.direction_mapping[direction.replace('_', '')] = direction

    def decode(self, data):
        data = super(GoogleGeocodeJsonDecoder, self).decode(data)

        status = data.get('status')
        if not status or status.lower() != 'ok':
            msg = 'Geocode retrieval failed with status: %s' % (status,)
            raise geolocation.GeolocationError(msg)

        locations = []
        for result in data['results']:
            address = self.parse_address(result['address_components'])
            location, viewport, bounds = self.parse_geometry(result['geometry'])
            locations.append(orientation.Geolocation(address, location, viewport, bounds))

        return geolocation.GeolocationResult(locations)

    def parse_address(self, components):
        parts = []
        for component in components:
            short = component['short_name'].encode('utf-8')
            long = component['long_name'].encode('utf-8')
            types = set(component['types'])

            part = orientation.GeolocationAddressPart(short, long, types)
            parts.append(part)

        return orientation.GeolocationAddress(parts)

    def parse_geometry(self, geometry):
        location = self.parse_location(geometry['location'])
        viewport = self.parse_directions(geometry.get('viewport'))
        bounds = self.parse_directions(geometry.get('bounds'))

        return location, viewport, bounds

    def parse_directions(self, data):
        if not data:
            return None

        directions = {}
        for key, pos in data.iteritems():
            name = self.direction_mapping[key]
            assert name not in directions
            directions[name] = self.parse_location(pos)

        return directions

    def parse_location(self, data):
        return orientation.GeolocationPosition(data['lat'], data['lng'])


class GoogleGeocodesClient(client.GeolocationHttpClient):
    URL = 'http://maps.google.com/maps/api/geocode/%(format)s'
    """Base URL"""

    def __init__(self, url=None, *args, **kwargs):
        super(GoogleGeocodesClient, self).__init__(*args, **kwargs)
        self.__url = url or self.URL

    def request(self, codec=None, **kwargs):
        variant = codec and codec.variant or 'json'
        url = self.__url % {'format': variant}
        return super(GoogleGeocodesClient, self).request('GET', url, kwargs,
                                                         codec=codec or variant)


def create_client(decoders=None, *args, **kwargs):
    if not decoders:
        decoders = [GoogleGeocodeJsonDecoder]

    return GoogleGeocodesClient(decoders=decoders, *args, **kwargs)


class GoogleGeocodes(providers.GeolocationProvider):
    """Converts between addresses and geocodes

    Using the Google Geocoding_ Web Service REST API_ to convert an
    address into geocodes and vice versa.

    Default format use is JSON and will automatically be decoded unless
    format is explicitly specified.

    If you wish to replace the HTTP client used, the decoding part of the
    data etc, you can easily pass your own retriever function in the
    constructor or override the `retrieve()` method.

    .. _API: http://code.google.com/apis/maps/documentation/geocoding
    """
    def __init__(self, decoders=None, *args, **kwargs):
        self.client = create_client(decoders=decoders, *args, **kwargs)

    def get_by_position(self, latitude, longitude, sensor=False, **kwargs):
        """Get address for a location by latitude and longitude

        Retrieves the closes human-readable address by latitude and longitude
        coordinates.

        The default retrieves honors the format argument which either can be
        json, xml or ``None``. If the format is ``None``, the retrieved data
        will be decoded. Note that this could also make it raise Exceptions
        based on the status in the response.

        Arguments:
            - `latitude`    -- latitude coordinate
            - `longitude`   -- longitude coordinate
            - `sensor`      -- wether or not requested via location sensor

        Keyword arguments (optional):
            - `format`      -- json, xml or None
            - `bounds`      -- boudning box of the viewport_
            - `region`      -- region code as ccTLD_
            - `language`    -- response language_

        .. _viewport: http://code.google.com/apis/maps/documentation/geocoding/index.html#Viewports
        .. _ccTLD: http://en.wikipedia.org/wiki/ccTLD
        .. _language: http://code.google.com/apis/maps/faq.html#languagesupport
        """
        latlng = ','.join(map(str, (latitude, longitude)))
        return self.client.request(latlng=latlng, sensor=sensor, **kwargs)

    def get_by_address(self, address, sensor=False, **kwargs):
        return self.client.request(address=address, sensor=sensor, **kwargs)


providers.GeolocationProviderManager.register('google', GoogleGeocodes)
