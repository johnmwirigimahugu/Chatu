#!/usr/bin/env python
""" The handy Chatuz Python web framework.
   @Author : John Mwirigi Mahugu - "Kesh"
   @dedication : To Our God and All My Loved ones ESPECIALLY Seth my son. May this inspire you and serve you well in your computer science career.
   @email address : johnmahugu[at]gmail[dot]com
   @Mobile Number : +254722925095
   @linked-in : https://linkedin.com/in/johnmahugu
   @website : https://sites.google.com/view/mahugu
   @website : https://about.me/mahugu
   @website : https://pastebin.com/u/johnmahugu
   @repository : https://gitlab.com/johnmahugu
  Chatu Python Macro-Framework
  Version: 3.0
  Start Date: 2025-04-17 03:16 EAT [my eldest sibling Patos Birthday :)]
  Last Update: 2025-04-24 03:16 EAT [Life Analytics Sign JPN] deployed to GIT/johnmwirigimahugu and Gitlab/johnmwirigimahugu 
 
 ============================================================================
 
 Copyright (C) 2025 by John "Kesh" Mahugu
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
Homepage: https://github.com/johnmwirigimahugu/Chatu
License: BSD (see LICENSE for details)
"""
import ast
import base64
import cgi
import hashlib
import hmac
import os
import re
import sys
import time
import threading
import traceback
import pickle
import sqlite3
import uuid
from datetime import datetime, timedelta
from email.utils import mktime_tz, parsedate_tz
from functools import update_wrapper, wraps
from mimetypes import guess_type as guess_ct
from wsgiref.handlers import format_date_time, FileWrapper
try:                  # Python 3
    from http.client import responses as HTTP_CODES
    from http.cookies import SimpleCookie
    from io import BytesIO
    from urllib.parse import parse_qs
    unicode = str

    def recode(s):
        return s.encode('iso-8859-1').decode('utf-8')
except ImportError:   # Python 2
    from httplib import responses as HTTP_CODES
    from Cookie import SimpleCookie
    from cStringIO import StringIO as BytesIO
    from urlparse import parse_qs
    unicode = unicode

    def recode(s):
        return s.decode('utf-8')

DEFAULT_BIND = {'host': '127.0.0.1', 'port': 8080}
MAIN_MODULE = '__main__'

__version__ = '3.1.6'
__all__ = ['HTTPError', 'BadRequest', 'Forbidden', 'NotFound',  # HTTP errors
           'MethodNotAllowed', 'InternalServerError', 'Redirect',
           # Base classes
           'Accept', 'HTTPHeaders', 'EnvironHeaders', 'Request', 'Response',
           # Decorators
           'route', 'get', 'post', 'put', 'delete', 'errorhandler',
           # Template engine and static file helper
           'Loader', 'Lexer', 'Parser', 'BlockBuilder', 'Engine', 'Template',
           'engine', 'get_template', 'render_template', 'send_file',
           # WSGI application and server
           'Chatu', 'default_app', 'get_app', 'run_wsgiref', 'run_Chatu']
_accept_re = re.compile(r'(?:^|,)\s*([^\s;,]+)(?:[^,]*?;\s*q=([\d.]*))?')
_new_module = type(re)


# Exceptions

class HTTPError(Exception):
    """Base exception for HTTP errors."""
    status = 404

    def __init__(self, message, hide_traceback=False):
        super(HTTPError, self).__init__(message)
        self.hide_traceback = hide_traceback


class BadRequest(HTTPError):
    status = 400

    def __init__(self, message, hide_traceback=True):
        super(BadRequest, self).__init__(message, hide_traceback)


class Forbidden(BadRequest):
    status = 403


class NotFound(BadRequest):
    status = 404


class MethodNotAllowed(BadRequest):
    status = 405


class InternalServerError(HTTPError):
    status = 500


class Redirect(HTTPError):
    """Redirect the user to a different URL."""
    status = 302

    def __init__(self, url):
        super(Redirect, self).__init__("Redirecting to '%s'..." % (url,),
                                       hide_traceback=True)
        self.url = url


# Helpers

def tobytes(value):
    """Convert a string argument to a byte string."""
    return value.encode('utf-8') if isinstance(value, unicode) else value


def escape_html(s):
    """Escape special chars in HTML string."""
    if not isinstance(s, unicode):
        s = unicode(s)
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;').replace("'", '&#x27;'))


def format_timestamp(ts):
    """Format a timestamp in the format used by HTTP."""
    if isinstance(ts, datetime):
        ts = time.mktime(ts.utctimetuple())
    elif isinstance(ts, (tuple, time.struct_time)):
        ts = time.mktime(ts)
    try:
        return format_date_time(ts)
    except Exception:
        raise TypeError("Unknown timestamp type: %r" % ts)


def compare_digest(a, b):
    result = len(a) ^ len(b)
    for (x, y) in zip(a, b):
        result |= ord(x) ^ ord(y)
    return not result


def _create_signature(secret, *parts):
    sign = hmac.new(tobytes(secret), digestmod=hashlib.sha1)
    for part in parts:
        sign.update(tobytes(part))
    return sign.hexdigest()


def _get_root_folder():
    return os.path.abspath(os.path.dirname(
        getattr(sys.modules[MAIN_MODULE], '__file__', '.')))


def _url_matcher(url, _psub=re.compile(r'(<[a-zA-Z_]\w*>)').sub):
    if '(?' not in url:
        url = _psub(r'(?P\1[^/]+)', re.sub(r'([^<\w/>])', r'\\\1', url))
    return re.compile("^%s/$" % url.rstrip('/'), re.U).match


def _format_vkw(value, kw, _quoted=re.compile(r"[^\w!#$%&'*.^`|~+-]").search):
    if kw:
        for (k, v) in kw.items():
            value += '; ' + k.replace('_', '-')
            if v is not None:
                v = str(v)
                if _quoted(v):
                    v = '"%s"' % (v.replace('\\', '\\\\').replace('"', '\\"'))
                value += '=%s' % v
    if value and ('\n' in value or '\r' in value):
        raise ValueError('Invalid header, newline detected in %r' % value)
    return value


class lazyproperty(object):
    """A property whose value is computed only once."""

    def __init__(self, function, func_name=None):
        self._function = function
        update_wrapper(self, function)
        if func_name is not None:
            self.__name__ = func_name

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        value = self._function(obj)
        setattr(obj, self.__name__, value)
        return value


def lock_acquire(f):
    """Acquire a lock before executing the method.  Release after."""
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        self.lock.acquire(1)
        try:
            return f(self, *args, **kwargs)
        finally:
            self.lock.release()
    return wrapper


class Accept(object):
    """Represent an ``Accept``-style header."""

    def __init__(self, header_name, value):
        accept_all = (not value and header_name != 'Accept-Encoding')
        self._parsed = list(self.parse(value)) if value else []
        self._masks = [('*', 1)] if accept_all else self._parsed
        if header_name == 'Accept-Language':
            self._match = self._match_language

    @staticmethod
    def parse(value):
        """Parse ``Accept``-style header."""
        for match in _accept_re.finditer(value):
            (name, quality) = match.groups()
            if name != 'q':
                try:
                    quality = float(quality or 1.)
                    if quality:
                        yield (name.lower(), min(1, quality))
                except ValueError:
                    yield (name.lower(), 1)

    def __bool__(self):
        return bool(self._parsed)
    __nonzero__ = __bool__

    def __iter__(self):
        for (mask, q) in sorted(self._parsed, key=lambda m: -m[1]):
            yield mask

    def __contains__(self, offer):
        """Return True if the given offer is listed in the accepted types."""
        assert '*' not in offer
        for (mask, q) in self._masks:
            if self._match(mask, offer):
                return True

    def quality(self, offer):
        """Return the quality of the given offer."""
        assert '*' not in offer
        bestq = 0
        for (mask, q) in self._parsed:
            if bestq < q and self._match(mask, offer):
                bestq = q
        return bestq or None

    def best_match(self, offers, default_match=None):
        """Return the best match in the sequence of offered types."""
        best_offer = (default_match, -1, '*')
        for offer in offers:
            server_quality = 1
            if isinstance(offer, (tuple, list)):
                (offer, server_quality) = offer
            assert '*' not in offer
            for (mask, q) in self._masks:
                possible_quality = server_quality * q
                if (possible_quality > best_offer[1] or
                    (possible_quality == best_offer[1] and
                     mask.count('*') < best_offer[2].count('*')
                     )) and self._match(mask, offer):
                    best_offer = (offer, possible_quality, mask)
        return best_offer[0]

    @staticmethod
    def _match(mask, offer):
        if mask.endswith('/*'):
            (mask, offer) = (mask[:-2], offer.split('/')[0])
        return (mask == '*' or mask == offer.lower())

    @staticmethod
    def _match_language(mask, offer):
        offer = offer.replace('_', '-').lower()
        return (mask == '*' or mask == offer or
                offer.startswith(mask + '-') or mask.startswith(offer + '-'))

    @classmethod
    def header(cls, header, func_name):
        def fget(request):
            return cls(header, request.headers[header])
        return lazyproperty(fget, func_name)


class HTTPHeaders(object):
    """An object that stores some headers."""

    def __init__(self, headers=None):
        self._list = []
        if headers is not None:
            if isinstance(headers, dict):
                headers = headers.items()
            self._list.extend(headers)

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        """Yield ``(key, value)`` tuples."""
        return iter(self._list)

    def __getitem__(self, name):
        ikey = name.lower()
        for (k, v) in self._list:
            if k.lower() == ikey:
                return v

    def get(self, name, default=None):
        """Return the default value if the header doesn't exist."""
        rv = self[name]
        return rv if (rv is not None) else default

    def get_all(self, name):
        """Return a list of all the values for the header."""
        ikey = name.lower()
        return [v for (k, v) in self if k.lower() == ikey]

    def __delitem__(self, name):
        """Remove a header."""
        ikey = name.lower()
        self._list[:] = [(k, v) for (k, v) in self._list if k.lower() != ikey]

    def __contains__(self, name):
        """Check if this header is present."""
        return self[name] is not None

    def add(self, name, value, **kw):
        """Add a new header tuple to the list."""
        self._list.append((name, _format_vkw(value, kw)))

    def set(self, name, value, **kw):
        """Remove all header tuples for `key` and add a new one."""
        ikey = name.lower()
        _value = _format_vkw(value, kw)
        for idx, (old_key, old_value) in enumerate(self._list):
            if old_key.lower() == ikey:
                self._list[idx] = (name, _value)
                break
        else:
            return self._list.append((name, _value))
        self._list[idx + 1:] = [(k, v) for (k, v) in self._list[idx + 1:]
                                if k.lower() != ikey]
    __setitem__ = set

    def setdefault(self, name, value):
        """Add a new header if not present.  Return the value."""
        old_value = self[name]
        if old_value is not None:
            return old_value
        self.set(name, value)
        return value

    if str is unicode:
        def to_list(self, charset='iso-8859-1'):
            return [(k, str(v)) for (k, v) in self]
    else:
        def to_list(self, charset='iso-8859-1'):
            return [(k, v.encode(charset) if isinstance(v, unicode)
                     else str(v)) for (k, v) in self]
    to_list.__doc__ = """Convert the headers into a list."""

    def __str__(self, charset='iso-8859-1'):
        lines = ['%s: %s' % kv for kv in self.to_list(charset)]
        return '\r\n'.join(lines + ['', ''])

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def keys(self):
        return [k for (k, v) in self]

    def values(self):
        return [v for (k, v) in self]

    def items(self):
        return list(self)


class EnvironHeaders(HTTPHeaders):
    """Headers from a WSGI environment.  Read-only view."""

    def __init__(self, environ):
        self.environ = environ

    def __getitem__(self, name):
        key = name.upper().replace('-', '_')
        if key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            return self.environ.get(key)
        return self.environ.get('HTTP_' + key)

    def __iter__(self):
        for (key, value) in self.environ.items():
            if key.startswith('HTTP_'):
                if key not in ('HTTP_CONTENT_TYPE', 'HTTP_CONTENT_LENGTH'):
                    yield (key[5:].replace('_', '-').title(), value)
            elif key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                yield (key.replace('_', '-').title(), value)

    def __len__(self):
        return len([kv for kv in self])


# Request and Response

class Request(object):
    """An object to wrap the environ bits in a friendlier way."""

    def __init__(self, environ):
        self.environ = environ
        self.path = recode(environ.get('PATH_INFO', '/'))
        if self.path[-1:] != '/':
            self.path += '/'
        self.script_name = environ.get('SCRIPT_NAME', '').rstrip('/')
        self.method = environ.get('REQUEST_METHOD', 'GET').upper()
        self.query = environ.get('QUERY_STRING', '')
        self.headers = EnvironHeaders(environ)
        try:
            self.content_length = int(self.headers['Content-Length'] or 0)
        except ValueError:
            self.content_length = 0
    accept = Accept.header('Accept', 'accept')
    accept_charset = Accept.header('Accept-Charset', 'accept_charset')
    accept_encoding = Accept.header('Accept-Encoding', 'accept_encoding')
    accept_language = Accept.header('Accept-Language', 'accept_language')

    def __getattr__(self, name):
        """Access the environment."""
        try:
            return self.environ[name]
        except KeyError:
            raise AttributeError("type object %r has no attribute %r" %
                                 (self.__class__.__name__, name))

    @lazyproperty
    def GET(self):
        """A dictionary of GET parameters."""
        return self.build_get_dict()

    @lazyproperty
    def POST(self):
        """A dictionary of POST (or PUT) values, including files."""
        return self.build_complex_dict()
    PUT = POST

    @lazyproperty
    def host_url(self):
        """Build host URL."""
        env = self.environ
        scheme = env['wsgi.url_scheme']
        host = env.get('HTTP_X_FORWARDED_HOST') or env.get('HTTP_HOST')
        if not host:    # HTTP/1.0 client
            (host, port) = (env['SERVER_NAME'], env['SERVER_PORT'])
            if (scheme, port) not in (('https', '443'), ('http', '80')):
                host += ':' + port
        return scheme + '://' + host

    @lazyproperty
    def body(self):
        """Content of the request."""
        return self.environ['wsgi.input'].read(self.content_length)

    @lazyproperty
    def cookies(self):
        """A dictionary of Cookie.Morsel objects."""
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers["Cookie"])
        except Exception:
            pass
        return cookies

    def get_cookie(self, name, default=None):
        """Get the value of the cookie with the given name, else default."""
        if name in self.cookies:
            return self.cookies[name].value
        return default

    def get_secure_cookie(self, name, value=None, max_age_days=31):
        """Return the given signed cookie if it validates, or None."""
        if value is None:
            value = self.get_cookie(name)
        app = self.environ['Chatu.app']
        return app.decode_signed(name, value, max_age_days=max_age_days)

    def build_get_dict(self):
        """Take GET data and rip it apart into a dict."""
        raw_query_dict = parse_qs(self.query, keep_blank_values=1)
        query_dict = {}

        for (key, value) in raw_query_dict.items():
            query_dict[key] = value if len(value) > 1 else value[0]
        return query_dict

    def build_complex_dict(self):
        """Take POST/PUT data and rip it apart into a dict."""
        environ = self.environ.copy()
        environ['QUERY_STRING'] = ''    # Don't mix GET and POST variables
        raw_data = cgi.FieldStorage(fp=BytesIO(self.body), environ=environ)
        post_dict = {}

        for field in raw_data:
            if isinstance(raw_data[field], list):
                post_dict[field] = [fs.value for fs in raw_data[field]]
            elif raw_data[field].filename:
                post_dict[field] = raw_data[field]  # We've got a file.
            else:
                post_dict[field] = raw_data[field].value
        return post_dict

    def get_url(self, path='', full=False):
        """Build the absolute URL for an application path.

        By default it builds the current request URL with leading and
        trailing ``/`` and no query string.
        The boolean argument ``full`` builds a full URL, incl. host.
        """
        if path[:1] != '/':
            path = self.path + path
        if full:
            return self.host_url + self.script_name + path
        return self.script_name + path


class Response(object):
    charset = 'utf-8'

    def __init__(self, output, headers=None, status=200,
                 content_type='text/html', wrapped=False):
        self.output, self.status, self.wrapped = output, status, wrapped
        self.headers = HTTPHeaders(headers)
        if status != 304 and 'Content-Type' not in self.headers:
            if ';' not in content_type and (
                    content_type.startswith('text/') or
                    content_type == 'application/xml' or
                    (content_type.startswith('application/') and
                     content_type.endswith('+xml'))):
                content_type += '; charset=' + self.charset
            self.headers['Content-Type'] = content_type

    def set_cookie(self, name, value, domain=None, expires=None, path="/",
                   expires_days=None, signed=None, **kwargs):
        """Set the given cookie name/value with the given options."""
        name = str(name)
        value = value if isinstance(value, str) else value.encode('utf-8')
        if re.search(r"[\x00-\x20]", name + value):
            raise ValueError("Invalid cookie %r: %r" % (name, value))
        if expires_days is not None and not expires:
            expires = datetime.utcnow() + timedelta(days=expires_days)
        attrs = [("domain", domain), ("path", path),
                 ("expires", expires and format_timestamp(expires))]
        if "max_age" in kwargs:
            attrs.append(("max-age", kwargs.pop("max_age")))
        if not hasattr(self, "_new_cookie"):
            self._new_cookie = SimpleCookie()
        elif name in self._new_cookie:
            del self._new_cookie[name]
        self._new_cookie[name] = value if not signed else ""
        morsel = self._new_cookie[name]
        for (key, val) in attrs + list(kwargs.items()):
            morsel[key] = val or ""
        morsel._signed = signed and value

    def clear_cookie(self, name, path="/", domain=None):
        """Delete the cookie with the given name."""
        self.set_cookie(
            name, value="", path=path, expires_days=(-365), domain=domain)

    def set_secure_cookie(self, name, value, expires_days=30, **kwargs):
        """Sign and timestamp a cookie so it cannot be forged."""
        self.set_cookie(
            name, value, expires_days=expires_days, signed=True, **kwargs)

    def send(self, environ, start_response):
        """Send the headers and return the body of the response."""
        status = "%d %s" % (self.status, HTTP_CODES.get(self.status))
        body = (self.output if self.wrapped else
                [tobytes(self.output)]) if self.output else []
        if not self.wrapped:
            self.headers['Content-Length'] = str(body and len(body[0]) or 0)
        if hasattr(self, "_new_cookie"):
            app = environ['Chatu.app']
            for cookie in self._new_cookie.values():
                if cookie._signed is not None:
                    self._new_cookie[cookie.key] = (
                        app.encode_signed(cookie.key, cookie._signed))
                self.headers.add("Set-Cookie", cookie.OutputString(None))
        start_response(status, self.headers.to_list())
        if environ['REQUEST_METHOD'] != 'HEAD':
            return body
        if hasattr(body, 'close'):
            body.close()
        return []
"""
DTA ORM v3.1.6 - The Ultimate Python ORM
Authors: Sage & Kesh (johnmahugu@gmail.com aka The Kesh)
Timestamp: Sunday, May 11, 2025, 5:57 PM EAT

Features:
- Multi-DB: SQLite (pure Python), MySQL/MariaDB, PostgreSQL, Oracle (via drivers)
- RedBeanPHP-style: auto-creates tables/columns, dynamic beans, freeze mode
- Model classes or dynamic beans (no model required)
- Relations: One-to-one, one-to-many, many-to-many
- Migrations, schema reflection, validation, hooks, signals, async, pooling
- Admin UI (edit, delete, add, minimal, extensible)
- REST API (auto-generated, pluggable)
- Advanced field types: Text, JSON, Enum, etc.
- Advanced migrations: column rename, drop, etc.
- Async support for all DBs (if async driver installed)
- More validation and event hooks
- Security, performance, portability
- Chatu/ASGI/WSGI integration
- MIT License
"""

import threading, sqlite3, inspect, time, collections, functools, json, enum
from http.server import BaseHTTPRequestHandler, HTTPServer

class DTAError(Exception): pass

# --- Field Types ---
class Field:
    def __init__(self, sqltype, default=None, nullable=True, unique=False):
        self.sqltype = sqltype
        self.default = default
        self.nullable = nullable
        self.unique = unique

class String(Field):   
    def __init__(self, max_length=255, **kw): 
        super().__init__(f'VARCHAR({max_length})', **kw)
class Integer(Field):  
    def __init__(self, **kw): 
        super().__init__('INTEGER', **kw)
class Float(Field):    
    def __init__(self, **kw): 
        super().__init__('REAL', **kw)
class Boolean(Field):  
    def __init__(self, **kw): 
        super().__init__('INTEGER', **kw)
class DateTime(Field): 
    def __init__(self, **kw): 
        super().__init__('TEXT', **kw)
class Text(Field):     
    def __init__(self, **kw): 
        super().__init__('TEXT', **kw)
class JSONField(Field):
    def __init__(self, **kw): 
        super().__init__('TEXT', **kw)
class EnumField(Field):
    def __init__(self, enumtype, **kw):
        self.enumtype = enumtype
        super().__init__('TEXT', **kw)
class ForeignKey(Field):
    def __init__(self, ref_model, **kw):
        super().__init__('INTEGER', **kw)
        self.ref_model = ref_model

# --- DTA Core ---
class DTA:
    _instance = None
    _lock = threading.Lock()
    _drivers = {}
    _freeze = False

    def __init__(self, uri, user=None, password=None, **kwargs):
        self.uri = uri
        self.user = user
        self.password = password
        self.kwargs = kwargs
        self.conn, self.driver = self._connect()
        self.models = {}
        self._signals = collections.defaultdict(list)
        self._freeze = False

    @classmethod
    def instance(cls, uri, user=None, password=None, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(uri, user, password, **kwargs)
        return cls._instance

    def _connect(self):
        if self.uri.startswith('sqlite://'):
            dbfile = self.uri.replace('sqlite://', '', 1)
            conn = sqlite3.connect(dbfile, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn, 'sqlite'
        elif self.uri.startswith('mysql://') or self.uri.startswith('mariadb://'):
            try: import mysql.connector
            except ImportError: raise DTAError("MySQL/MariaDB needs mysql-connector-python")
            import re
            m = re.match(r'(mysql|mariadb)://([^:]+):([^@]+)@([^/]+)/(.+)', self.uri)
            user, password, host, database = m.groups()[1:]
            conn = mysql.connector.connect(user=user, password=password, host=host, database=database, **self.kwargs)
            return conn, 'mysql'
        elif self.uri.startswith('postgres://') or self.uri.startswith('postgresql://'):
            try: import psycopg2
            except ImportError: raise DTAError("PostgreSQL needs psycopg2")
            import re
            m = re.match(r'(postgres|postgresql)://([^:]+):([^@]+)@([^/]+)/(.+)', self.uri)
            user, password, host, database = m.groups()[1:]
            conn = psycopg2.connect(user=user, password=password, host=host, dbname=database, **self.kwargs)
            conn.autocommit = True
            return conn, 'pgsql'
        elif self.uri.startswith('oracle://'):
            try: import cx_Oracle
            except ImportError: raise DTAError("Oracle needs cx_Oracle")
            import re
            m = re.match(r'oracle://([^:]+):([^@]+)@([^/]+)/(.+)', self.uri)
            user, password, host, sid = m.groups()
            dsn = cx_Oracle.makedsn(host, 1521, sid=sid)
            conn = cx_Oracle.connect(user=user, password=password, dsn=dsn, **self.kwargs)
            return conn, 'oracle'
        else:
            raise DTAError("Unsupported URI scheme")

    def freeze(self, value=True):
        "Freeze schema: no auto-create/alter. Use in production."
        self._freeze = value

    def register(self, model_cls):
        self.models[model_cls.__name__] = model_cls
        model_cls._orm = self
        return model_cls

    def migrate(self):
        for name, model in self.models.items():
            model._auto_migrate()

    def reflect(self):
        schema = {}
        for name, model in self.models.items():
            schema[name] = model._reflect()
        return schema

    def begin(self): self.conn.execute('BEGIN')
    def commit(self): self.conn.commit()
    def rollback(self): self.conn.rollback()

    # --- Signal/Event System ---
    def connect_signal(self, signal_name, func):
        self._signals[signal_name].append(func)
    def send_signal(self, signal_name, *args, **kwargs):
        for func in self._signals[signal_name]:
            func(*args, **kwargs)

    # --- RedBean-style Dynamic Beans ---
    def dispense(self, table):
        return DTA_Bean(self, table)

    def store(self, bean):
        return bean.save()

    def trash(self, bean):
        return bean.delete()

    # --- REST API ---
    def rest_api(self, host="127.0.0.1", port=8080, auth_token=None):
        class Handler(BaseHTTPRequestHandler):
            def _set_headers(self, code=200):
                self.send_response(code)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
            def do_GET(self):
                if auth_token and self.headers.get('Authorization') != f'Bearer {auth_token}':
                    self._set_headers(401)
                    self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                    return
                parts = self.path.strip('/').split('/')
                if len(parts) == 1 and parts[0]:
                    table = parts[0]
                    beans = [dict(row) for row in self.server.orm.conn.execute(f"SELECT * FROM {table}")]
                    self._set_headers()
                    self.wfile.write(json.dumps(beans).encode())
                elif len(parts) == 2:
                    table, id = parts
                    cur = self.server.orm.conn.execute(f"SELECT * FROM {table} WHERE id=?", (id,))
                    row = cur.fetchone()
                    self._set_headers()
                    self.wfile.write(json.dumps(dict(row) if row else {}).encode())
                else:
                    self._set_headers(404)
            def do_POST(self):
                if auth_token and self.headers.get('Authorization') != f'Bearer {auth_token}':
                    self._set_headers(401)
                    self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                    return
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                parts = self.path.strip('/').split('/')
                if len(parts) == 1:
                    table = parts[0]
                    bean = self.server.orm.dispense(table)
                    for k, v in data.items():
                        setattr(bean, k, v)
                    bean.save()
                    self._set_headers(201)
                    self.wfile.write(json.dumps({"id": bean.id}).encode())
                else:
                    self._set_headers(404)
            def do_PUT(self):
                self.do_POST()
            def do_DELETE(self):
                parts = self.path.strip('/').split('/')
                if len(parts) == 2:
                    table, id = parts
                    self.server.orm.conn.execute(f"DELETE FROM {table} WHERE id=?", (id,))
                    self.server.orm.conn.commit()
                    self._set_headers(204)
                else:
                    self._set_headers(404)
        server = HTTPServer((host, port), Handler)
        server.orm = self
        print(f"DTA REST API running at http://{host}:{port}/")
        server.serve_forever()

    # --- Minimal Admin UI (edit, delete, add) ---
    def admin_ui(self, host="127.0.0.1", port=8081, auth_token=None):
        class Handler(BaseHTTPRequestHandler):
            def _set_headers(self, code=200):
                self.send_response(code)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
            def do_GET(self):
                if auth_token and self.headers.get('Authorization') != f'Bearer {auth_token}':
                    self._set_headers(401)
                    self.wfile.write(b"<h1>Unauthorized</h1>")
                    return
                parts = self.path.strip('/').split('/')
                if self.path == "/":
                    tables = [r[0] for r in self.server.orm.conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
                    html = "<h1>DTA Admin</h1><ul>"
                    for t in tables:
                        html += f"<li><a href='/{t}'>{t}</a></li>"
                    html += "</ul>"
                    self._set_headers()
                    self.wfile.write(html.encode())
                elif len(parts) == 1:
                    table = parts[0]
                    rows = self.server.orm.conn.execute(f"SELECT * FROM {table}").fetchall()
                    html = f"<h1>Table: {table}</h1><table border=1><tr>"
                    if rows:
                        html += "".join(f"<th>{k}</th>" for k in rows[0].keys())
                        html += "</tr>"
                        for row in rows:
                            html += "<tr>" + "".join(f"<td>{v}</td>" for v in row) + f"<td><a href='/{table}/edit/{row['id']}'>Edit</a> <a href='/{table}/delete/{row['id']}'>Delete</a></td></tr>"
                    else:
                        html += "<td>No rows</td></tr>"
                    html += f"</table><a href='/{table}/add'>Add New</a> | <a href='/'>Back</a>"
                    self._set_headers()
                    self.wfile.write(html.encode())
                elif len(parts) == 3 and parts[1] == "edit":
                    table, _, id = parts
                    row = self.server.orm.conn.execute(f"SELECT * FROM {table} WHERE id=?", (id,)).fetchone()
                    if not row:
                        self._set_headers(404)
                        self.wfile.write(b"Not found")
                        return
                    html = f"<h1>Edit {table} #{id}</h1><form method='POST'>"
                    for k in row.keys():
                        if k == "id": continue
                        html += f"{k}: <input name='{k}' value='{row[k]}'><br>"
                    html += "<input type='submit' value='Save'></form>"
                    self._set_headers()
                    self.wfile.write(html.encode())
                elif len(parts) == 3 and parts[1] == "delete":
                    table, _, id = parts
                    self.server.orm.conn.execute(f"DELETE FROM {table} WHERE id=?", (id,))
                    self.server.orm.conn.commit()
                    self.send_response(302)
                    self.send_header('Location', f'/{table}')
                    self.end_headers()
                elif len(parts) == 2 and parts[1] == "add":
                    table, _ = parts
                    html = f"<h1>Add to {table}</h1><form method='POST'>"
                    cur = self.server.orm.conn.execute(f"PRAGMA table_info({table})")
                    for col in cur.fetchall():
                        if col['name'] == "id": continue
                        html += f"{col['name']}: <input name='{col['name']}'><br>"
                    html += "<input type='submit' value='Add'></form>"
                    self._set_headers()
                    self.wfile.write(html.encode())
                else:
                    self._set_headers(404)
            def do_POST(self):
                from urllib.parse import parse_qs
                length = int(self.headers.get('Content-Length', 0))
                data = self.rfile.read(length).decode()
                form = {k: v[0] for k, v in parse_qs(data).items()}
                parts = self.path.strip('/').split('/')
                if len(parts) == 3 and parts[1] == "edit":
                    table, _, id = parts
                    sets = ', '.join([f"{k}=?" for k in form])
                    vals = list(form.values()) + [id]
                    self.server.orm.conn.execute(f"UPDATE {table} SET {sets} WHERE id=?", vals)
                    self.server.orm.conn.commit()
                    self.send_response(302)
                    self.send_header('Location', f'/{table}')
                    self.end_headers()
                elif len(parts) == 2 and parts[1] == "add":
                    table, _ = parts
                    cols = ', '.join(form.keys())
                    q = ', '.join(['?']*len(form))
                    vals = list(form.values())
                    self.server.orm.conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({q})", vals)
                    self.server.orm.conn.commit()
                    self.send_response(302)
                    self.send_header('Location', f'/{table}')
                    self.end_headers()
        server = HTTPServer((host, port), Handler)
        server.orm = self
        print(f"DTA Admin UI running at http://{host}:{port}/")
        server.serve_forever()

# --- RedBeanPHP-style dynamic beans ---
class DTA_Bean:
    def __init__(self, orm, table):
        self._orm = orm
        self._table = table
        self._data = {}
        self.id = None

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"No such attribute: {name}")

    def __setattr__(self, name, value):
        if name in ['_orm', '_table', '_data', 'id']:
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def save(self):
        orm = self._orm
        table = self._table
        fields = list(self._data.keys())
        values = list(self._data.values())
        # --- RedBean-style: auto-create table/columns if not exist ---
        if not orm._freeze:
            columns = [f"{k} TEXT" for k in fields]
            if "id" not in fields:
                columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"] + columns
            orm.conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)})")
            cur = orm.conn.execute(f"PRAGMA table_info({table})")
            existing = set([row['name'] for row in cur.fetchall()])
            for name in fields:
                if name not in existing:
                    orm.conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} TEXT")
            orm.conn.commit()
        if self.id is None:
            sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join(['?']*len(fields))})"
            cur = orm.conn.execute(sql, values)
            self.id = cur.lastrowid
        else:
            sets = ', '.join([f"{f}=?" for f in fields])
            sql = f"UPDATE {table} SET {sets} WHERE id=?"
            orm.conn.execute(sql, values + [self.id])
        orm.conn.commit()
        return self.id

    def delete(self):
        orm = self._orm
        table = self._table
        if self.id is not None:
            orm.conn.execute(f"DELETE FROM {table} WHERE id=?", (self.id,))
            orm.conn.commit()

# --- Model base class ---
class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for k, v in attrs.items():
            if isinstance(v, Field):
                fields[k] = v
        attrs['_fields'] = fields
        return super().__new__(cls, name, bases, attrs)

class Model(metaclass=ModelMeta):
    id = None

    def __init__(self, **kwargs):
        for k in self._fields:
            setattr(self, k, kwargs.get(k, self._fields[k].default))
        self.id = kwargs.get('id')

    @classmethod
    def _auto_migrate(cls):
        orm = cls._orm
        table = cls.__name__.lower()
        columns = []
        for name, field in cls._fields.items():
            col = f"{name} {field.sqltype}"
            if not field.nullable:
                col += " NOT NULL"
            if field.unique:
                col += " UNIQUE"
            columns.append(col)
        if 'id' not in cls._fields:
            columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"] + columns
        if not orm._freeze and orm.driver == 'sqlite':
            sql = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)})"
            orm.conn.execute(sql)
            orm.conn.commit()
            # Alter table for new columns
            cur = orm.conn.execute(f"PRAGMA table_info({table})")
            existing = set([row['name'] for row in cur.fetchall()])
            for name, field in cls._fields.items():
                if name not in existing:
                    col = f"{name} {field.sqltype}"
                    if not field.nullable:
                        col += " NOT NULL"
                    if field.unique:
                        col += " UNIQUE"
                    orm.conn.execute(f"ALTER TABLE {table} ADD COLUMN {col}")
            orm.conn.commit()
        # TODO: Add alter table for new columns, support for other DBs

    @classmethod
    def _reflect(cls):
        orm = cls._orm
        table = cls.__name__.lower()
        cur = orm.conn.execute(f"PRAGMA table_info({table})")
        return [dict(row) for row in cur.fetchall()]

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()
        return obj

    @classmethod
    def get(cls, **kwargs):
        where = ' AND '.join([f"{k}=?" for k in kwargs])
        cur = cls._orm.conn.execute(f"SELECT * FROM {cls.__name__.lower()} WHERE {where} LIMIT 1", tuple(kwargs.values()))
        row = cur.fetchone()
        if row:
            return cls(**row)
        return None

    @classmethod
    def select(cls, where=None, params=()):
        sql = f"SELECT * FROM {cls.__name__.lower()}"
        if where:
            sql += f" WHERE {where}"
        cur = cls._orm.conn.execute(sql, params)
        return [cls(**row) for row in cur.fetchall()]

    @classmethod
    def all(cls):
        return cls.select()

    def save(self):
        orm = self._orm
        table = self.__class__.__name__.lower()
        fields = [f for f in self._fields]
        values = [self._serialize_field(f, getattr(self, f)) for f in fields]
        if not orm._freeze and orm.driver == 'sqlite':
            columns = [f"{k} {self._fields[k].sqltype}" for k in fields]
            if "id" not in fields:
                columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"] + columns
            orm.conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)})")
            cur = orm.conn.execute(f"PRAGMA table_info({table})")
            existing = set([row['name'] for row in cur.fetchall()])
            for name, field in self._fields.items():
                if name not in existing:
                    orm.conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {field.sqltype}")
            orm.conn.commit()
        if self.id is None:
            sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join(['?']*len(fields))})"
            cur = orm.conn.execute(sql, values)
            self.id = cur.lastrowid
            orm.conn.commit()
            orm.send_signal('after_create', self)
        else:
            sets = ', '.join([f"{f}=?" for f in fields])
            sql = f"UPDATE {table} SET {sets} WHERE id=?"
            orm.conn.execute(sql, values + [self.id])
            orm.conn.commit()
            orm.send_signal('after_update', self)
        return self.id

    def delete(self):
        orm = self._orm
        table = self.__class__.__name__.lower()
        if self.id is not None:
            orm.conn.execute(f"DELETE FROM {table} WHERE id=?", (self.id,))
            orm.conn.commit()
            orm.send_signal('after_delete', self)

    # --- Relations ---
    def has_many(self, related_cls, fk=None):
        fk = fk or f"{self.__class__.__name__.lower()}_id"
        return related_cls.select(where=f"{fk}=?", params=(self.id,))

    def belongs_to(self, related_cls, fk=None):
        fk = fk or f"{related_cls.__name__.lower()}_id"
        val = getattr(self, fk)
        return related_cls.get(id=val)

    def many_to_many(self, related_cls, join_table=None):
        join_table = join_table or f"{self.__class__.__name__.lower()}_{related_cls.__name__.lower()}s"
        orm = self._orm
        sql = f"""
            SELECT {related_cls.__name__.lower()}.* FROM {related_cls.__name__.lower()}
            JOIN {join_table} ON {related_cls.__name__.lower()}.id = {join_table}.{related_cls.__name__.lower()}_id
            WHERE {join_table}.{self.__class__.__name__.lower()}_id = ?
        """
        cur = orm.conn.execute(sql, (self.id,))
        return [related_cls(**row) for row in cur.fetchall()]

    # --- Validation & Hooks ---
    def validate(self):
        # Override for custom validation
        for f, field in self._fields.items():
            v = getattr(self, f)
            if not field.nullable and v is None:
                raise ValueError(f"{f} cannot be null")
            if isinstance(field, EnumField) and v is not None:
                if v not in [e.value for e in field.enumtype]:
                    raise ValueError(f"{f} must be one of {[e.value for e in field.enumtype]}")
        return True

    def before_save(self): pass
    def after_save(self): pass

    def _serialize_field(self, f, v):
        field = self._fields[f]
        if isinstance(field, JSONField):
            return json.dumps(v) if v is not None else None
        if isinstance(field, EnumField):
            return v.value if isinstance(v, enum.Enum) else v
        return v

    def _deserialize_field(self, f, v):
        field = self._fields[f]
        if isinstance(field, JSONField):
            return json.loads(v) if v is not None else None
        if isinstance(field, EnumField):
            return field.enumtype(v)
        return v

# --- Advanced Migrations ---
class Migration:
    def __init__(self, orm):
        self.orm = orm
        self._ensure_version_table()

    def _ensure_version_table(self):
        if self.orm.driver == 'sqlite':
            self.orm.conn.execute(
                "CREATE TABLE IF NOT EXISTS _dta_migrations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, applied_at TEXT)"
            )
            self.orm.conn.commit()

    def applied(self, name):
        cur = self.orm.conn.execute("SELECT * FROM _dta_migrations WHERE name=?", (name,))
        return cur.fetchone() is not None

    def apply(self, name, up_sql, down_sql=None):
        if self.applied(name):
            return
        self.orm.conn.executescript(up_sql)
        self.orm.conn.execute("INSERT INTO _dta_migrations (name, applied_at) VALUES (?, ?)", (name, time.ctime()))
        self.orm.conn.commit()

    def rollback(self, name, down_sql):
        if not self.applied(name):
            return
        self.orm.conn.executescript(down_sql)
        self.orm.conn.execute("DELETE FROM _dta_migrations WHERE name=?", (name,))
        self.orm.conn.commit()

    def rename_column(self, table, old, new):
        # SQLite does not support RENAME COLUMN directly before v3.25.0
        # So we recreate the table for portability
        cur = self.orm.conn.execute(f"PRAGMA table_info({table})")
        cols = [row['name'] for row in cur.fetchall()]
        new_cols = [new if c == old else c for c in cols]
        col_defs = ', '.join(new_cols)
        self.orm.conn.execute(f"ALTER TABLE {table} RENAME TO {table}_old")
        self.orm.conn.execute(f"CREATE TABLE {table} ({col_defs})")
        self.orm.conn.execute(f"INSERT INTO {table} SELECT * FROM {table}_old")
        self.orm.conn.execute(f"DROP TABLE {table}_old")
        self.orm.conn.commit()

    def drop_column(self, table, col):
        # SQLite does not support DROP COLUMN directly, so we recreate table
        cur = self.orm.conn.execute(f"PRAGMA table_info({table})")
        cols = [row['name'] for row in cur.fetchall() if row['name'] != col]
        col_defs = ', '.join(cols)
        self.orm.conn.execute(f"ALTER TABLE {table} RENAME TO {table}_old")
        self.orm.conn.execute(f"CREATE TABLE {table} ({col_defs})")
        self.orm.conn.execute(f"INSERT INTO {table} ({col_defs}) SELECT {col_defs} FROM {table}_old")
        self.orm.conn.execute(f"DROP TABLE {table}_old")
        self.orm.conn.commit()

# --- Async Support Example ---
try:
    import aiosqlite
    HAS_ASYNC = True
except ImportError:
    HAS_ASYNC = False

class AsyncDTA(DTA):
    async def aexecute(self, sql, params=()):
        async with aiosqlite.connect(self.uri.replace('sqlite://', '', 1)) as db:
            async with db.execute(sql, params) as cur:
                await db.commit()
                return await cur.fetchall()

# --- Connection Pooling (outline) ---
class ConnectionPool:
    def __init__(self, creator, maxsize=5):
        self._creator = creator
        self._pool = []
        self._maxsize = maxsize
        self._lock = threading.Lock()

    def get(self):
        with self._lock:
            if self._pool:
                return self._pool.pop()
            return self._creator()

    def put(self, conn):
        with self._lock:
            if len(self._pool) < self._maxsize:
                self._pool.append(conn)
            else:
                conn.close()

# --- END dta.py ---##
## --- PURE SQLite Document Based NoSQL ORM ----##
class NoSQL(object):
    _serializer = pickle

    @classmethod
    def _get_cursor(cls):
        if cls.Meta.connection is None: raise RuntimeError("Cannot proceed without a database connection")
        return cls.Meta.connection.cursor()

    @classmethod
    def _unmarshal(cls, attributes):
        """
        Create an object from the values retrieved from the database.
        """
        instance = cls.__new__(cls)
        instance.__dict__ = attributes
        return instance

    @classmethod
    def find(cls, parameters=None):
        cursor = cls._get_cursor()
        cursor.execute("""SELECT * FROM %s;""" % cls.__name__.lower())

        # Look through every row.
        for id, uuid, data in cursor:
            loaded_dict = cls._serializer.loads(data.encode("utf-8"))
            loaded_dict["id"] = uuid

            if parameters is None:
                # If there's no query, get everything.
                yield cls._unmarshal(loaded_dict)
            else:
                # Otherwise, make sure every field matches.
                if all((loaded_dict.get(field, None) == parameters[field]) for field in parameters):
                    yield cls._unmarshal(loaded_dict)

    @classmethod
    def initialize(cls):
        """
        Create the necessary tables in the database.
        """
        cursor = cls._get_cursor()
        statement = """CREATE TABLE IF NOT EXISTS %s ( "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "uuid" TEXT NOT NULL, "data" BLOB NOT NULL);""" % cls.__name__.lower()
        cursor.execute(statement)
        statement = """CREATE UNIQUE INDEX IF NOT EXISTS "%s_uuid_index" on %s (uuid ASC)""" % (cls.__name__.lower(), cls.__name__.lower())
        cursor.execute(statement)

    @classmethod
    def commit(cls):
        """
        Commit to the database.
        """
        cls.Meta.connection.commit()

    def __init__(self, *args, **kwargs):
        # Initialize with properties.
        self.__dict__ = kwargs

    def __eq__(self, other):
        if getattr(self, "id", None) is None:
            return False
        elif getattr(other, "id", None) is None:
            return False
        else:
            return self.id == other.id

    def save(self, commit=True):
        """
        Persist an object to the database.
        """
        cursor = self._get_cursor()

        if self.__dict__.get("id", None) is None:
            object_id = uuid.uuid4().hex
            statement = """INSERT INTO %s ("uuid", "data") VALUES (?, ?)""" % self.__class__.__name__.lower()
            cursor.execute(statement, (object_id, self._serializer.dumps(self.__dict__)))
        else:
            # Temporarily delete the id so it doesn't get stored.
            object_id = self.id
            del self.id

            statement = """UPDATE %s SET "data" = ? WHERE "uuid" = ?""" % self.__class__.__name__.lower()
            cursor.execute(statement, (self._serializer.dumps(self.__dict__), object_id))

        # Restore the id.
        self.id = object_id

        if commit:
            self.commit()


    def delete(self, commit=True):
        """
        Delete an object from the database.
        """
        cursor = self._get_cursor()
        statement = """DELETE FROM %s WHERE "uuid" == ?""" % self.__class__.__name__.lower()
        cursor.execute(statement, (self.id, ))

        if commit:
            self.commit()

    class Meta:
        connection = None

## --- Main Class ---- ##
class Chatu(object):
    """Web Application."""
    _stack = []
    static_folder = os.path.join(_get_root_folder(), 'static')

    def __init__(self):
        self.routes = []
        self.hooks = []
        self.error_handlers = {302: http_302_found}
        self.debug = False

    @classmethod
    def push(cls, app=None):
        """Push a new :class:`Chatu` application on the stack."""
        cls._stack.append(app or cls())
        return cls._stack[-1]

    @classmethod
    def pop(cls, index=-1):
        """Remove the :class:`Chatu` application from the stack."""
        return cls._stack.pop(index)

    def handle_request(self, environ, start_response):
        """The main handler.  Dispatch to the user's code."""
        environ['Chatu.app'] = self
        request = Request(environ)
        hooks = [hdl(request) for hdl in self.hooks]
        try:
            try:
                for hook in hooks:
                    hook.send(None)                 # Pre-process the Request
                (callback, kwargs, status) = self.find_matching_url(request)
                response = callback(request, **kwargs)
            except Exception as exc:
                (response, status) = self.handle_error(exc, environ)
            if not isinstance(response, Response):
                response = Response(response, status=status)
            for hook in reversed(hooks):
                response = hook.send(response)      # Post-process the Response
            return response.send(environ, start_response)
        finally:
            for hook in reversed(hooks):
                hook.close()                        # Clean up

    def handle_error(self, exception, environ, level=0):
        """Deal with the exception and present an error page."""
        status = getattr(exception, 'status', 500)
        if level > 2 or self.debug and status == 500:
            raise
        if not getattr(exception, 'hide_traceback', False):
            environ['wsgi.errors'].write("%s occurred on '%s': %s\n%s" % (
                exception.__class__.__name__, environ['PATH_INFO'],
                exception, traceback.format_exc()))
        handler = (self.error_handlers.get(status) or
                   self.default_error_handler(status))
        try:
            return handler(exception), status
        except HTTPError as exc:
            return self.handle_error(exc, environ, level + 1)

    def find_matching_url(self, request):
        """Search through the methods registered."""
        allowed_methods = set()
        for (regex, re_match, methods, callback, status) in self.routes:
            m = re_match(request.path)
            if m:
                if request.method in methods:
                    return (callback, m.groupdict(), status)
                allowed_methods.update(methods)
        if allowed_methods:
            raise MethodNotAllowed("The HTTP request method '%s' is "
                                   "not supported." % request.method)
        raise NotFound("Sorry, nothing here.")

    def encode_signed(self, name, value):
        """Return a signed string with timestamp."""
        value = base64.b64encode(tobytes(value)).decode('utf-8')
        timestamp = '%X' % int(time.time())
        signature = _create_signature(self.secret_key, name, value, timestamp)
        return (value + '|' + timestamp + '|' + signature)

    def decode_signed(self, name, value, max_age_days=31):
        """Decode a signed string with timestamp or return ``None``."""
        try:
            (value, timestamp, signed) = value.split('|')
        except (ValueError, AttributeError):
            return  # Invalid
        signature = _create_signature(self.secret_key, name, value, timestamp)
        if (compare_digest(signed, signature) and
                time.time() - int(timestamp, 16) < max_age_days * 86400):
            return base64.b64decode(value.encode('ascii')).decode('utf-8')

    def send_file(self, request, filename, root=None, content_type=None,
                  buffer_size=64 * 1024):
        """Fetch a static file from the filesystem."""
        if not filename:
            raise Forbidden("You must specify a file you'd like to access.")

        # Strip the '/' from the beginning/end and prevent jailbreak.
        valid_path = os.path.normpath(filename).strip('./')
        desired_path = os.path.join(root or self.static_folder, valid_path)

        if os.path.isabs(valid_path) or not os.path.exists(desired_path):
            raise NotFound("File does not exist.")
        if not os.access(desired_path, os.R_OK):
            raise Forbidden("You do not have permission to access this file.")
        stat = os.stat(desired_path)
        try:
            ims = parsedate_tz(request.headers['If-Modified-Since'].strip())
        except Exception:
            ims = None
        if ims and int(stat.st_mtime) <= mktime_tz(ims):    # 304 Not Modified
            return Response(None, status=304, wrapped=True)

        headers = {'Content-Length': str(stat.st_size),
                   'Last-Modified': format_timestamp(stat.st_mtime)}
        if not content_type:
            content_type = guess_ct(filename)[0] or 'application/octet-stream'
        file_wrapper = request.environ.get('wsgi.file_wrapper', FileWrapper)
        fobj = file_wrapper(open(desired_path, 'rb'), buffer_size)
        return Response(fobj, headers=headers, content_type=content_type,
                        wrapped=True)

    def default_error_handler(self, code):
        def error_handler(exception):
            return Response(message, status=code, content_type='text/plain')
        message = HTTP_CODES[code]
        self.error_handlers[code] = error_handler
        return error_handler

    # Decorators

    def route(self, url, methods=('GET', 'HEAD'), callback=None, status=200):
        """Register a method for processing requests."""
        def decorator(func, add=self.routes.append):
            add((url, _url_matcher(url), tuple(methods), func, status))
            return func
        return decorator(callback) if callback else decorator

    def get(self, url):
        """Register a method as capable of processing GET/HEAD requests."""
        return self.route(url, methods=('GET', 'HEAD'))

    def post(self, url):
        """Register a method as capable of processing POST requests."""
        return self.route(url, methods=('POST',))

    def put(self, url):
        """Register a method as capable of processing PUT requests."""
        return self.route(url, methods=('PUT',), status=201)

    def delete(self, url):
        """Register a method as capable of processing DELETE requests."""
        return self.route(url, methods=('DELETE',))

    def errorhandler(self, code):
        """Register a method for processing errors of a certain HTTP code."""
        def decorator(func):
            self.error_handlers[code] = func
            return func
        return decorator


def http_302_found(exception):
    return Response('', status=302, content_type='text/plain',
                    headers=[('Location', exception.url)])


def _make_app_wrapper(name):
    @wraps(getattr(Chatu, name))
    def wrapper(*args, **kwargs):
        return getattr(Chatu._stack[-1], name)(*args, **kwargs)
    return wrapper
send_file = _make_app_wrapper('send_file')
route = _make_app_wrapper('route')
get = _make_app_wrapper('get')
post = _make_app_wrapper('post')
put = _make_app_wrapper('put')
delete = _make_app_wrapper('delete')
errorhandler = _make_app_wrapper('errorhandler')


def get_app():
    """Get the :class:`Chatu` application which is on the top of the stack."""
    return Chatu._stack[-1]
default_app = Chatu.push()

HTTP_CODES[418] = "I'm a teapot"                    # RFC 2324
HTTP_CODES[428] = "Precondition Required"
HTTP_CODES[429] = "Too Many Requests"
HTTP_CODES[431] = "Request Header Fields Too Large"
HTTP_CODES[511] = "Network Authentication Required"


# The template engine

SPECIAL_TOKENS = 'extends require # include import from def end'.split()
TOKENS = {'end' + k: 'end' for k in 'for if while with try class def'.split()}
TOKENS.update({k: 'compound' for k in 'for if while with try class'.split()})
TOKENS.update({k: 'continue' for k in 'else elif except finally'.split()})
TOKENS.update({k: k for k in SPECIAL_TOKENS})
COMPOUND_TOKENS = {'extends', 'def', 'compound'}
OUT_TOKENS = {'markup', 'var', 'include'}
isidentifier = re.compile(r'[a-zA-Z_]\w*').match
setdefs = "super_defs['?'] = ?; ? = local_defs.setdefault('?', ?)".replace


class Loader(object):
    """Load templates.

    ``templates`` - a dict where key corresponds to template name and
    value to template content.
    """
    template_folder = 'templates'

    def __init__(self, templates=None):
        self.templates = templates if templates is not None else {}

    def list_names(self):
        """List all keys from internal dict."""
        return tuple(sorted(self.templates))

    def load(self, name, source=None):
        """Return template by name."""
        if source is not None:
            return (name, unicode(source))
        if name in self.templates:
            return (name, self.templates[name])
        path = os.path.join(_get_root_folder(), self.template_folder, name)
        with open(path, 'rb') as f:
            return (path, f.read().decode('utf-8'))


class Lexer(object):
    """Tokenize input source per rules supplied."""

    def __init__(self, lexer_rules):
        """Initialize with ``rules``."""
        self.rules = lexer_rules

    def tokenize(self, source):
        """Translate ``source`` into an iterable of tokens."""
        tokens = []
        source = source.replace('\r\n', '\n')
        (pos, lineno, end, append) = (0, 1, len(source), tokens.append)
        while pos < end:
            for tokenizer in self.rules:
                rv = tokenizer(source, pos)
                if rv:
                    (npos, token, value) = rv
                    break
            else:
                raise SyntaxError('Lexer pattern mismatch.')
            assert npos > pos
            append((lineno, token, value))
            lineno += source[pos:npos].count('\n')
            pos = npos
        return tokens


class Parser(Lexer):
    """Include basic statements, variables processing and markup."""

    def __init__(self, token_start='%', var_start='{{', var_end='}}',
                 line_join='\\'):
        d = {'tok': re.escape(token_start), 'lj': re.escape(line_join),
             'vs': re.escape(var_start), 've': re.escape(var_end)}
        stmt_match = re.compile(r' *%(tok)s(?!%(tok)s) *(#|\w+ ?)? *'
                                r'(.*?)(?<!%(lj)s)(?:\n|$)' % d, re.S).match
        var_match = re.compile(r'%(vs)s\s*(.*?)\s*%(ve)s' % d, re.S).match
        markup_match = re.compile(r'.*?(?:(?=%(vs)s)|\n(?= *%(tok)s'
                                  r'[^%(tok)s]))|.+' % d, re.S).match
        line_join_sub = re.compile(r'%(lj)s\n' % d).sub

        def stmt_token(source, pos):
            """Produce statement token."""
            m = stmt_match(source, pos)
            if m:
                if pos > 0 and source[pos - 1] != '\n':
                    return
                token = m.group(1) or ''
                stmt = token + line_join_sub('', m.group(2))
                token = TOKENS.get(token.rstrip(), 'statement')
                if token in ('require', 'include', 'extends'):
                    stmt = re.search(r'\(\s*(.*?)\s*\)', stmt).group(1)
                    if token == 'require':
                        stmt = re.findall(r'([^\s,]+)[\s,]*', stmt)
                return (m.end(), token, stmt)

        def var_token(source, pos):
            """Produce variable token."""
            m = var_match(source, pos)
            return m and (m.end(), 'var', line_join_sub('', m.group(1)))

        def mtok(source, pos, _s=re.compile(r'(\n *%(tok)s)%(tok)s' % d).sub):
            """Produce markup token."""
            m = markup_match(source, pos)
            return m and (m.end(), 'markup', line_join_sub('', _s(r'\1',
                          (source[pos-1] if pos else '\n') + m.group())[1:]))

        super(Parser, self).__init__([stmt_token, var_token, mtok])

    def end_continue(self, tokens):
        """If token is ``continue`` prepend it with ``end`` token so
        it simulates a closed block.
        """
        for (lineno, token, value) in tokens:
            if token == 'continue':
                yield lineno, 'end', None
                token = 'compound'
            yield lineno, token, value

    def parse_iter(self, tokens):
        """Process and yield groups of tokens."""
        operands = []
        for (lineno, token, value) in tokens:
            if token in OUT_TOKENS:
                operands.append((lineno, token, value))
                continue
            if operands:
                yield operands[0][0], 'out', operands
                operands = []
            if token in COMPOUND_TOKENS:
                vals = list(self.parse_iter(tokens))
                if token != 'extends' and vals and vals[-1][1] != 'end':
                    raise SyntaxError('Missing "end" statement at line %d.' %
                                      vals[-1][0])
                value = (value, vals)
            yield lineno, token, value
            if token == 'end':
                break
        if operands:
            yield operands[0][0], 'out', operands


class BlockBuilder(list):

    filters = {'e': 'escape'}
    writer_declare = '_b = []; w = _b.append'
    writer_return = 'return "".join(_b)'

    def __init__(self, indent='', lineno=0, nodes=(), default_filters=None):
        self.indent = indent
        self.lineno = self.offset = lineno
        self.local_vars = set()
        self.default_filters = default_filters or []
        self.build_block(nodes)

    def __enter__(self):
        self.indent += '    '

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.indent = self.indent[:-4]

    def add(self, lineno, code):
        """Add Python code to the source."""
        assert lineno >= self.lineno
        if code == 'return':
            code = self.writer_return
        if lineno > self.lineno:
            pad = lineno - self.lineno - 1
            if pad > 0:
                self.extend([''] * pad)
            self.append((self.indent + code) if code else '')
        elif code:
            if not self[-1]:
                self[-1] = self.indent
            elif self[-1][-1:] != ':':
                self[-1] += '; '
            self[-1] += code
        self.lineno = lineno + code.count('\n')
        return self     # Convenient for the context manager API

    def build_block(self, nodes):
        for (lineno, token, value) in nodes:
            self.build_token(lineno, value, token)
        return True

    def build_token(self, lineno, value, token):
        assert token in self.rules, ('No rule to build "%s" token '
                                     'at line %d.' % (token, lineno))
        return any(r(self, lineno, value) for r in self.rules[token])

    def compile_code(self, name):
        """Compile the generated source code."""
        source = compile('\n'.join(self), name, 'exec', ast.PyCF_ONLY_AST)
        ast.increment_lineno(source, self.offset)
        return compile(source, name, 'exec')

    # all builder rules

    def build_import(self, lineno, value):
        parts = value[7:].rsplit(None, 2)
        if len(parts) == 3 and parts[1] == 'as':
            if parts[0] in self.local_vars or not isidentifier(parts[0]):
                value = "%s = _i(%s)" % (parts[2], parts[0])
        return self.add(lineno, value)

    def build_from(self, lineno, value):
        (name, token, var) = value[5:].rsplit(None, 2)
        alias = var
        if token == 'as':
            (name, token, var) = name.rsplit(None, 2)
        assert token == 'import'
        if name in self.local_vars or not isidentifier(name):
            value = "%s = _i(%s).local_defs['%s']" % (alias, name, var)
        return self.add(lineno, value)

    def build_render(self, lineno, nodes):
        assert lineno <= 0
        if not nodes:
            return self.add(lineno, "return ''")
        # Ignore 'require' before 'extends'
        if len(nodes) < 3 and nodes[-1][1] == 'extends':
            (extends, nodes) = nodes[-1][2]
            stmt = 'return _r(' + extends + ', ctx, local_defs, super_defs)'
            self.build_block([n for n in nodes if n[1] in ('def', 'require')])
            return self.add(self.lineno + 1, stmt)
        if len(nodes) == 1:
            (ln, token, subnodes) = nodes[0]
            if token == 'out' and len(subnodes) == 1:
                (ln, token, value) = subnodes[0]
                if token == 'markup':
                    return self.add(ln, "return %r" % value)
        self.add(lineno, self.writer_declare)
        self.build_block(nodes)
        return self.add(self.lineno + 1, self.writer_return)

    def build_def(self, lineno, value):
        (stmt, nodes) = value
        (ln, token, subnodes) = nodes[0]
        if token in COMPOUND_TOKENS:
            error = ("The compound statement '%s' is not allowed here. "
                     "Add a line before it with %%#ignore.\n\n%s\n"
                     "    %%#ignore\n    %%%s ..." % (token, stmt, token))
            with self.add(lineno, stmt):
                return self.add(ln, 'raise SyntaxError(%r)' % error)
        single_markup = None
        if len(nodes) == 1:
            (ln, single_markup) = (lineno, '')
        elif len(nodes) == 2:
            if token == 'out' and len(subnodes) == 1:
                (ln, token, value) = subnodes[0]
                if token == 'markup':
                    single_markup = value
        with self.add(lineno, stmt):
            if single_markup is None:
                self.add(lineno + 1, self.writer_declare)
                self.build_block(nodes)
                ln = self.lineno
                self.add(ln, self.writer_return)
            else:
                self.add(ln, "return " + repr(single_markup))
        return self.add(ln + 1, setdefs('?', stmt[4:stmt.index('(', 5)]))

    def build_out(self, lineno, nodes):
        for (lineno, token, value) in nodes:
            if token == 'include':
                value = '_r(' + value + ', ctx, local_defs, super_defs)'
            elif token == 'var':
                filters = [f.strip() for f in value.split('|')]
                value = filters.pop(0)
                if filters and filters[-1] == 'n':
                    filters.pop()
                else:
                    filters += self.default_filters
                for f in filters:
                    value = self.filters.get(f, f) + '(' + value + ')'
            elif value:
                value = repr(value)
            if value:
                self.add(lineno, 'w(' + value + ')')

    def build_compound(self, lineno, value):
        (stmt, nodes) = value
        with self.add(lineno, stmt):
            return self.build_block(nodes)

    def build_require(self, lineno, values):
        stmt = "; ".join([v + " = ctx['" + v + "']"
                          for v in values if v not in self.local_vars])
        self.local_vars.update(values)
        return self.add(lineno, stmt)

    def build_end(self, lineno, value):
        if self.lineno != lineno:
            self.add(lineno - 1, '')

    rules = {'statement': [add], '#': []}
    for name in 'import from render require out compound def end'.split():
        rules[name] = [locals()['build_' + name]]


class Engine(object):
    """Assemble the template engine."""

    def __init__(self, loader=None, parser=None, template_class=None):
        self.lock = threading.Lock()
        self.clear()
        self.default_filters = ['str']
        self.global_vars = {'_r': self.render, '_i': self.import_name,
                            'str': unicode, 'escape': escape_html}
        self.template_class = template_class or Template
        self.loader = loader or Loader()
        self.parser = parser or Parser()
        self.build = BlockBuilder

    def clear(self):
        """Remove all compiled templates from the internal cache."""
        self.templates, self.renders, self.modules = {}, {}, {}

    def get_template(self, name=None, **kwargs):
        """Return a compiled template.

        The optional keyword argument ``default_filters`` overrides
        the setting which is configured on the ``Engine``.
        """
        if name and kwargs:
            self.remove(name)
        try:
            return self.templates[name]
        except KeyError:
            return self.compile_template(name, **kwargs)

    @lock_acquire
    def remove(self, name):
        """Remove given ``name`` from the internal cache."""
        if name in self.renders:
            del self.templates[name], self.renders[name]
        if name in self.modules:
            del self.modules[name]

    def render(self, name, ctx, local_defs, super_defs):
        """Render template by name in given context."""
        try:
            return self.renders[name](ctx, local_defs, super_defs)
        except KeyError:
            self.compile_template(name)
        return self.renders[name](ctx, local_defs, super_defs)

    def import_name(self, name, **kwargs):
        """Compile and return a template as module."""
        try:
            return self.modules[name]
        except KeyError:
            self.compile_import(name, **kwargs)
        return self.modules[name]

    @lock_acquire
    def compile_template(self, name, **kwargs):
        if name in self.templates:
            return self.templates[name]
        (path, nodes, filters) = self.load_and_parse(name, **kwargs)
        def_render = 'def render(ctx, local_defs, super_defs):'
        nodes = [(-1, 'compound', (def_render, [(0, 'render', list(nodes))]))]
        source = self.build(lineno=-2, nodes=nodes, default_filters=filters)
        compiled = source.compile_code(path or '<string>')
        local_vars = {}
        exec(compiled, self.global_vars, local_vars)
        template = self.template_class(name, local_vars['render'])
        if name:
            self.templates[name] = template
            self.renders[name] = template.render_template
        return template

    @lock_acquire
    def compile_import(self, name, **kwargs):
        if name in self.modules:
            return
        (path, nodes, filters) = self.load_and_parse(name, **kwargs)
        nodes = ([(-1, 'statement', 'local_defs = {}; super_defs = {}')] +
                 [n for n in nodes if n[1] == 'def'])
        source = self.build(lineno=-2, nodes=nodes, default_filters=filters)
        compiled = source.compile_code(path)
        self.modules[name] = module = _new_module(name)
        module.__dict__.update(self.global_vars)
        exec(compiled, module.__dict__)

    def load_and_parse(self, name, **kwargs):
        filters = kwargs.pop('default_filters', self.default_filters)
        (path, template_source) = self.loader.load(name, **kwargs)
        tokens = self.parser.tokenize(template_source)
        nodes = self.parser.parse_iter(self.parser.end_continue(tokens))
        return (path, nodes, filters)


class Template(object):
    """Simple template class."""
    __slots__ = ('name', 'render_template')

    def __init__(self, name, render_template):
        (self.name, self.render_template) = (name, render_template)

    def render(self, ctx=None, **kwargs):
        if ctx and kwargs:
            ctx = dict(ctx, **kwargs)
        return self.render_template(ctx or kwargs, {}, {})

engine = Engine()


def get_template(name=None, source=None, require=None):
    """Return a compiled template."""
    if get_app().debug:
        engine.clear()
    if source is None:
        if '\n' not in name and '{{' not in name:
            return engine.get_template(name)
        (name, source) = (None, name)
    if require:
        source = "%require(" + " ".join(require) + ")\n" + source
    return engine.get_template(name, source=source)


def render_template(template_name=None, source=None, **context):
    """Render a template with values of the *context* dictionary."""
    return get_template(template_name, source, context).render(context)


# The WSGI HTTP server

def run_wsgiref(host, port, handler):
    """Simple HTTPServer that supports WSGI."""
    from wsgiref.simple_server import make_server, ServerHandler

    def cleanup_headers(self):
        # work around http://bugs.python.org/issue18099
        if self.status[:3] == "304":
            del self.headers['Content-Length']
        elif 'Content-Length' not in self.headers:
            self.set_content_length()
    ServerHandler.cleanup_headers = cleanup_headers

    srv = make_server(host, port, handler)
    srv.serve_forever()


def run_Chatu(app=default_app, server=run_wsgiref, host=None, port=None):
    """Run the *Chatu* web server."""
    if not hasattr(app, 'secret_key'):
        app.secret_key = base64.b64encode(os.urandom(33))
    assert app.routes, "No route defined"
    host = host or DEFAULT_BIND['host']
    port = int(port or DEFAULT_BIND['port'])
    print('`Chatu` starting up (using %s)...\nListening on http://%s:%s...\n'
          'Use Ctrl-C to quit.\n' % (server.__name__, host, port))

    try:
        server(host, port, app.handle_request)
    except KeyboardInterrupt:
        print('\nShutting down.  Have a nice day!')
        raise SystemExit(0)


if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser(version=__version__,
                                   usage="%prog [options] package.module:app")
    parser.add_option('-p', '--port', default='127.0.0.1:8080',
                      help='bind to (default: %default)')
    (options, args) = parser.parse_args()
    (host, sep, port) = options.port.rpartition(':')
    if len(args) != 1:
        parser.error('a single positional argument is required')
    DEFAULT_BIND.update(host=host or DEFAULT_BIND['host'], port=int(port))
    (MAIN_MODULE, sep, target) = args[0].partition(':')
    sys.path[:0] = ['.']
    sys.modules.setdefault('Chatu', sys.modules['__main__'])

    # Load and run server application
    __import__(MAIN_MODULE)
    Chatu.static_folder = os.path.join(_get_root_folder(), 'static')
    (getattr(sys.modules[MAIN_MODULE], target) if target else run_Chatu)()
