# -*- coding: utf-8 -*-
# Copyright (C) 2009 Örjan Persson

from geolocation import abstract
from geolocation import providers

class GeolocationError(StandardError):
    pass


class GeolocationResult(abstract.Dictable):
    def __init__(self, locations):
        self.locations = locations


def GeolocationFinder(provider='google', *args, **kwargs):
    """Create a geolocation finder

    Instantiate a geolocation finder with the given provider used as the
    backend for the data.

        - `provider`        -- name or instance of a provider (defaults to google)

    For complete documentation, see ``provider.GeolocationProvider``.
    """
    return providers.GeolocationProviderManager.create(provider, *args, **kwargs)
