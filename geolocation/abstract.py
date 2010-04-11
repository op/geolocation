# -*- coding: utf-8 -*-
# Copyright (C) 2009 Örjan Persson


class Dictable(object):
    def __repr__(self):
        kvs = ['%s=%s' % (k,v) for k, v in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(kvs))


class UnknownVariant(StandardError):
    pass


class Factory(object):
    """Factory

    Holds a registry of a name into a callable which will construct an instance
    of the requested type. The idea is to make it easier to change default
    implementations for certain types.

    Factories can either be iherited from, or you could take a factory as an
    argument in constructors etc.

    >>> factory1 = Factory()
    >>> factory2 = Factory()

    >>> # no call factory (the instance of Factory)
    >>> Factory.register('seitan', int)

    >>> factory1.get('seitan')
    >>> Factory.get('seitan')
    <type 'int'>

    >>> factory1.register('tofu', str)
    >>> Factory.register('tofu', tuple)

    >>> factory1.get('tofu')
    <type 'str'>
    >>> factory2.get('tofu')
    >>> Factory.get('tofu')
    <type 'tuple'>

    >>> class FloatFactory(Factory):
    ...      def __init__(self, *args, **kwargs):
    ...          super(FloatFactory, self).__init__({'float': float},
    ...                                             *args, **kwargs)

    >>> float_f = FloatFactory()
    >>> float_f.get('tofu')
    >>> float_f.get('float')
    <type 'float'>

    >>> Factory.get('float')
    >>> factory1.get('float')
    """
    callables = {}
    __created = {}

    def __init__(self, creatables=None, *args, **kwargs):
        super(Factory, *args, **kwargs)
        if creatables:
            map(self.register, creatables.iterkeys(), creatables.itervalues())

    @classmethod
    def register(cls, key, value):
        assert callable(value)
        # TODO how to we separate class variable from the instance's? metaclass?

        #callables = getattr(cls, 'callables', None)
        #if not callables:
        #    callables = {}
        #    setattr(cls, 'callables', callables)
        #callables[key] = value
        cls.callables[key] = value

    @classmethod
    def supports(cls, key):
        return key in cls.__created or key in cls.callables

    @classmethod
    def get_class(cls, key):
        if isinstance(key, cls.__class__):
            return key
        else:
            c = cls.__created.get(key)
            if c:
                return c.__class__

            #return getattr(cls, 'callables', {}).get(key)
            c = cls.callables.get(key)
            if not c:
                raise UnknownVariant('Unsupported variant %s (available: %s)' % \
                                     (key, ', '.join(cls.callables.keys())))
            return c

    @classmethod
    def creatables(cls):
        #return getattr(cls, 'callables', {}).keys()
        return cls.callables.keys()

    @classmethod
    def create(cls, key, *args, **kwargs):
        return cls.get_class(key)(*args, **kwargs)

    @classmethod
    def get(cls, key, *args, **kwargs):
        instance = cls.__created.get(key)
        if not instance:
            instance = cls.create(key, *args, **kwargs)
            cls.__created[key] = instance
        return instance


if __name__ == '__main__':
    # this currently fails
    import doctest
    doctest.testmod()
