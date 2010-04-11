# -*- coding: utf-8 -*-
# Copyright (C) 2009 Örjan Persson

from __future__ import with_statement

import logging

import geolocation.codecs as codecs
import geolocation.http as http

log = logging.getLogger(__name__)


class GeolocationHttpClient(object):
    """Geolocation Http Client

    Keeps a pool of http connections and codecs.
    """

    def __init__(self, client=None, decoders=None):
        super(GeolocationHttpClient, self).__init__()
        self.__client = client or http.HttpConnectionManager()
        self.__decoders = codecs.setup(decoders or codecs.GeolocationCodecs)

    def request(self, method, url, params, codec=None):
        """Retrieve and decode data via HTTP

        Arguments:
            - `method`      -- HTTP method to use
            - `url`         -- HTTP url
            - `params`      -- HTTP parameters as a dict
            - `codec`       -- data decoder (optional)
        """
        data = self.__client.request(method, url, params)
        if self.__decoders.supports(codec):
            codec = self.__decoders.get(codec)
            data = codec.decode(data)

        return data
