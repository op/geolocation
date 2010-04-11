# -*- coding: utf-8 -*-
# Copyright (C) 2009 Örjan Persson

from geolocation import abstract
#from geolocation.providers import google

class GeolocationProvider(object):
    """Converts between addresses and geocodes

        >>> gloc = geolocation.Geolocation()
        >>> gloc.get_by_address('Borgmästargatan, Stockholm, Sweden')
        >>> gloc.get_by_position(10, 20)
    """
    def get_by_address(self, address):
        raise NotImplementedError()

    def get_by_position(self, latitude, longitude):
        raise NotImplementedError()


class GeolocationProviderManager(abstract.Factory):
    """Manager for all providers

    Keep track of all providers available. Call the static `register` method
    if you wish to add a custom provider. To instantiate a provider, you can
    call `create` with the name of a previously registered provider.
    """

    @classmethod
    def register(cls, name, provider):
        """Register geolocation provider

        Add a new or override an existing geolocation location provider.

            - `provider`        -- GeolocationProvider
        """
        super(GeolocationProviderManager, cls).register(name, provider)
