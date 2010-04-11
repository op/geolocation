# -*- coding: utf-8 -*-
# Copyright (C) 2009 Örjan Persson

import copy
try:
    import json
except ImportError:
    import simplejson as json

import geolocation
import geolocation.abstract as abstract


class CodecError(StandardError):
    """Base exception class for codec errors"""
    pass


class UnknownCodec(CodecError):
    """Failed to find any codec for the given format"""
    pass


class Codec(object):
    """Abstract codec"""

    formats = []
    """List of formats this codec supports"""

    def __init__(self, variant):
        """Create a variant of the codec"""
        if variant not in self.formats:
            raise CodecError('%r not supported by %r (supported: %s)' % \
                             (variant, self, ', '.join(self.formats)))
        self.variant = variant

    def decode(self, data):
        """Decode data"""
        raise NotImplementedError()

    def encode(self, data):
        """Encode data"""
        raise NotImplementedError()


class CodecFactory(abstract.Factory):
    @classmethod
    def register(cls, codec, formats=None):
        if formats is None:
            formats = codec.formats
        elif not isinstance(formats, (list, tuple, set)):
            formats = [formats]

        for fmt in formats:
            super(CodecFactory, cls).register(fmt, codec)

    @classmethod
    def create(cls, variant, *args, **kwargs):
        try:
            codec = super(CodecFactory, cls).create(variant, variant, *args, **kwargs)
        except abstract.UnknownVariant:
            return UnknownCodec('Failed to find a codec to handle "%s" (available: %s)' % \
                                (variant, ', '.join(cls.creatables())))

        return codec


class GeolocationDecodeError(CodecError, geolocation.GeolocationError):
    pass


class GeolocationCodec(Codec):
    pass


class GeolocationCodecs(CodecFactory):
    """Geolocation Codecs

    >>> json = '{"foo": ["bar", false, 1.3]}'
    >>> data = {u'foo': [u'bar', False, 1.3]}

    >>> codec = GeolocationCodec.create('json')
    >>> codec.decode(json) == data
    True
    >>> codec.encode(data) == json
    True
    """
    pass

class GeolocationJsonCodec(GeolocationCodec):
    formats = ['json']

    def decode(self, data):
        return json.loads(data)

    def encode(self, data):
        return json.dumps(data)


def setup(codecs, registry=None):
    if not registry:
        registry = GeolocationCodecs()

    if isinstance(codecs, type(registry)):
        return copy(codecs)

    if isinstance(codecs, dict):
        for variant, codec in codecs.iteritems():
            registry.register(codec, [variant])
    else:
        for codec in codecs:
            registry.register(codec)

    return registry

setup([GeolocationJsonCodec], GeolocationCodecs)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
