# -*- coding: utf-8 -*-
# Copyright (C) 2009 Örjan Persson

import httplib
import threading
import urllib


class HttpClient(object):
    def request(self, method, url, *args, **kwargs):
        raise NotImplementedError()

    def encode_params(self, params):
        params = map(self.encode_param, params.iteritems())
        return urllib.urlencode(dict(params))

    def encode_param(self, item):
        key, value = item
        if isinstance(value, bool):
            value = value and 'true' or 'false'
        elif not isinstance(value, basestring):
            value = str(value)
        return (key, value)


class HttpConnection(HttpClient):
    default_port = 80
    schema = 'http'

    def __init__(self, addr, manager=None, *args, **kwargs):
        super(HttpConnection, self).__init__(*args, **kwargs)
        self.addr = addr
        self.__manager = manager

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__manager:
            self.__manager.return_connection(self)


class Httplib_HttpConnection(httplib.HTTPConnection, HttpConnection):
    def __init__(self, addr, manager, *args, **kwargs):
        httplib.HTTPConnection.__init__(self, addr[0], addr[1], *args, **kwargs)
        HttpConnection.__init__(self, addr, manager, *args, **kwargs)


class Httplib_HttpsConnection(httplib.HTTPSConnection, HttpConnection):
    schema = 'https'
    def __init__(self, addr, manager, *args, **kwargs):
        httplib.HTTPSConnection.__init__(self, addr[0], addr[1], *args, **kwargs)
        HttpConnection.__init__(self, addr, manager, *args, **kwargs)


class HttpConnectionManager(HttpClient):
    schemas = {'http': Httplib_HttpConnection,
               'https': Httplib_HttpsConnection}

    def __init__(self, schemas=None, *args, **kwargs):
        super(HttpConnectionManager, self).__init__(*args, **kwargs)
        self.__connections = {}
        self.__connections_lock = threading.Lock()

        if schemas:
            self.schemas = schemas

    def get_connection(self, schema, addr, *args, **kwargs):
        schema_cls = self.schemas[schema]
        addr = self.__cleanup_addr(addr, schema_cls.default_port)

        with self.__connections_lock:
            conns = self.__connections.setdefault((schema, addr), [])

            if not conns:
                try:
                    conns.append(schema_cls(addr, self, *args, **kwargs))
                except KeyError:
                    raise AttributeError('Unsupported url schema: %s' % (schema,))

            return conns.pop()

    def return_connection(self, conn):
        addr = self.__cleanup_addr(conn.addr)
        with self.__connections_lock:
            self.__connections[(conn.schema, addr)].append(conn)

    def request(self, method, url, params=None, *args, **kwargs):
        schema, addr, path = self.__split_url(url)

        if params:
            path += '?' + self.encode_params(params)

        with self.get_connection(schema, addr) as conn:
            conn.request(method, path, *args, **kwargs)
            response = conn.getresponse()
            data = response.read()

        return data

    def __cleanup_addr(self, addr, default_port=None):
        if isinstance(addr, basestring):
            addr = addr.split(':', 1)
        if len(addr) != 2:
            addr = (addr[0], default_port)
        return addr

    def __split_url(self, url):
        """Split url into parts

        @rtype:  (str, str, str)
        @return: a tuple with (schema, addr, path)
        """
        schema, rest = url.split(':', 1)
        addr, path = urllib.splithost(rest)
        return (schema, addr, path)
