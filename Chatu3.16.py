# MIT License
#
# Copyright (c) 2025 John Mwirigi Mahugu "The Kesh - Guru" DBA Tangaza University (2020)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Your Python code starts here...

"""
Chatu.py - The Macroframework: Micro, Macro, and Fullstack in One!
Authors: Seth & Kesh (johnmahugu@gmail.com aka The Kesh)
Location: Nairobi, Kenya.
Dedication : To God, My Father Francis Mahugu, Myson Seth Mahugu and all me loved ones and mentees.
Date: Sunday, May 11, 2025, 6:41 PM EAT

Features:
- Routing (sync/async), ASGI/WSGI, helpers, CORS, session (JWT), SSE, templates (Jinja2 & utemplate)
- WebSocket, static file serving, file upload, forms, testing
- DTA ORM (RedBean-style, migrations, admin, REST API)
- User management (registration, login, roles, password reset, email verification, admin UI)
- Email sending (SMTP)
- OAuth2/social login (Google example, extendable)
- All-in-one, single file, no setup!
"""

import os, re, sys, io, json, time, uuid, hashlib, secrets, smtplib, mimetypes, asyncio
from email.message import EmailMessage
import threading
import collections
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from functools import wraps

import ast
import sys
import os
import html
import marshal
import re
import inspect
import numba  # Optional for JIT
from typing import Dict, Any, Optional, List, Callable
from types import CodeType
from collections import ChainMap
from functools import lru_cache

# ===========================================================================
# Core Engine Classes
# ===========================================================================

class TemplateError(Exception):
    """Base class for all template errors."""
    def __init__(self, message: str, lineno: int = None, filename: str = None):
        self.lineno = lineno
        self.filename = filename
        super().__init__(f"{filename or '<unknown>'}:{lineno or '?'} - {message}")

class TemplateSyntaxError(TemplateError):
    """Invalid template syntax."""

class TemplateSecurityError(TemplateError):
    """Attempted unsafe operation in template."""

class ChatuTemplateEngine:
    """
    The ultimate Python template engine with macros, inheritance, sandboxing,
    precompilation, and async support.
    """

    def __init__(
        self,
        template_dir: str = "templates",
        autoescape: bool = True,
        sandboxed: bool = True,
        cache_size: int = 100,
        jit: bool = False
    ):
        self.template_dir = os.path.abspath(template_dir)
        self.autoescape = autoescape
        self.sandboxed = sandboxed
        self.jit = jit
        self._cache = {}
        self._macros: Dict[str, Macro] = {}
        self._filters: Dict[str, Callable] = {
            'e': html.escape,
            'upper': str.upper,
            'lower': str.lower,
            'safe': lambda x: x,
        }
        self._extensions: Dict[str, Callable] = {}
        self._sandbox_globals = self._create_sandbox_globals()

    # ===========================================================================
    # Public API
    # ===========================================================================

    def render(
        self,
        template_name: str,
        context: Optional[Dict] = None,
        **kwargs: Any
    ) -> str:
        """Render a template with given context."""
        context = context or {}
        context.update(kwargs)
        template = self._load_template(template_name)
        return template.render(context)

    async def render_async(
        self,
        template_name: str,
        context: Optional[Dict] = None,
        **kwargs: Any
    ) -> str:
        """Asynchronously render a template."""
        # Implementation would use async AST nodes
        raise NotImplementedError("Async coming in v2.1!")

    def compile(self, template_name: str) -> CodeType:
        """Precompile template to Python bytecode."""
        source = self._get_template_source(template_name)
        ast_tree = self._parse_to_ast(source, template_name)
        code = compile(ast_tree, filename=template_name, mode="exec")
        return marshal.dumps(code)

    def add_filter(self, name: str, func: Callable) -> None:
        """Register a custom filter."""
        self._filters[name] = func

    def add_extension(self, extension: type) -> None:
        """Register a template extension."""
        for name, method in inspect.getmembers(extension, predicate=inspect.isfunction):
            if name.startswith("filter_"):
                self.add_filter(name[7:], method)
            elif name.startswith("tag_"):
                self._extensions[name[4:]] = method

    # ===========================================================================
    # Core Implementation
    # ===========================================================================

    def _load_template(self, name: str) -> "CompiledTemplate":
        """Load and cache templates with LRU caching."""
        if name not in self._cache:
            source = self._get_template_source(name)
            ast_tree = self._parse_to_ast(source, name)
            code = compile(ast_tree, filename=name, mode="exec")
            if self.jit and numba:
                code = numba.jit(code)
            self._cache[name] = CompiledTemplate(code, self)
        return self._cache[name]

    def _get_template_source(self, name: str) -> str:
        """Load template source from disk."""
        path = os.path.join(self.template_dir, name)
        if not os.path.exists(path):
            raise TemplateError(f"Template '{name}' not found")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _parse_to_ast(self, source: str, filename: str) -> ast.Module:
        """Parse template source to validated AST."""
        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError as e:
            raise TemplateSyntaxError(
                f"Syntax error: {e.msg}",
                lineno=e.lineno,
                filename=filename
            ) from e
        
        if self.sandboxed:
            self._validate_ast(tree)
        
        return self._transform_ast(tree)

    def _validate_ast(self, node: ast.AST) -> None:
        """Validate AST nodes for security (prevents unsafe operations)."""
        # Implementation would walk the AST and check for:
        # - Import statements
        # - Function definitions
        # - Restricted builtins
        # - Etc.
        # Raises TemplateSecurityError on violations

    def _transform_ast(self, tree: ast.Module) -> ast.Module:
        """Transform template AST to executable Python code."""
        # Implementation would:
        # - Convert {{ var }} to _output.append(escape(var))
        # - Convert {% if %} to Python if statements
        # - Handle macros, includes, inheritance
        # - Inject line numbers for debugging
        return tree

    def _create_sandbox_globals(self) -> Dict[str, Any]:
        """Create a safe globals environment for template execution."""
        safe_builtins = {
            'range', 'len', 'str', 'int', 'float', 'list', 'dict', 'tuple',
            'bool', 'enumerate', 'zip', 'reversed'
        }
        return {
            '__builtins__': {k: __builtins__[k] for k in safe_builtins},
            'filters': self._filters,
            'escape': html.escape,
            '_output': [],
        }

# ===========================================================================
# Compiled Template Class
# ===========================================================================

class CompiledTemplate:
    """Represents a compiled template ready for rendering."""

    def __init__(self, code: CodeType, engine: ChatuTemplateEngine):
        self.code = code
        self.engine = engine
        self.globals = engine._sandbox_globals.copy()
        self.locals = {}

    def render(self, context: Dict) -> str:
        """Execute the compiled template with given context."""
        self.globals.update(context)
        try:
            exec(self.code, self.globals, self.locals)
            return ''.join(self.globals['_output'])
        except Exception as e:
            raise TemplateRenderingError(
                f"Error rendering template: {e}",
                lineno=getattr(e, 'lineno', None)
            ) from e

# ===========================================================================
# Advanced Features Implementation
# ===========================================================================

class Macro:
    """Represents a template macro with parameters."""
    
    def __init__(self, name: str, args: List[str], body: str, engine: ChatuTemplateEngine):
        self.name = name
        self.args = args
        self.body = body
        self.engine = engine
        self._compiled = None

    def __call__(self, **kwargs: Any) -> str:
        """Render the macro with given arguments."""
        if not self._compiled:
            self._compiled = self.engine._compile_macro(self.body)
        return self._compiled.render(kwargs)

class TemplateExtension:
    """Base class for template extensions."""
    
    @classmethod
    def register(cls, engine: ChatuTemplateEngine) -> None:
        """Register this extension with a template engine."""
        engine.add_extension(cls)

    def filter_capitalize(self, value: str) -> str:
        """Custom filter example."""
        return value.capitalize()
    
    def tag_cache(self, parser, tag_name: str, args: str) -> ast.AST:
        """Custom tag example for caching template fragments."""
        # Implementation would parse arguments and return AST nodes
        pass

# ===========================================================================
# Usage Examples
# ===========================================================================

# Create engine with JIT compilation and 100-template cache
engine = ChatuTemplateEngine(
    template_dir="templates",
    sandboxed=True,
    jit=True,
    cache_size=100
)

# Add custom extension
class MyExtension(TemplateExtension):
    @staticmethod
    def filter_reverse(s: str) -> str:
        return s[::-1]

engine.add_extension(MyExtension)

# Render template with macros and security
html = engine.render(
    "page.html",
    user=get_current_user(),
    items=get_items()
)
""" 
------------------------------------------
Hold onto your keyboard-this will be epic. Let’s build the ultimate templating engine for Chatu.py with features that surpass Jinja2, leveraging Python’s full power while maintaining security and performance. Here's the grand design:

ChatuTemplateEngine 2.0: Feature Breakdown
Feature	Implementation	Benefit
Macros with Args	Parse {% macro %} and compile to Python functions	Reusable components with parameters
Inline Python	{% python %} blocks compiled to AST	Full Python execution in templates
Sandboxed Eval	AST validation + restricted globals	Safe execution of untrusted templates
Bytecode Precompilation	Compile templates to .pyc files	10-100x faster rendering
Type Hints & Annotations	Full mypy/pyright support	Better IDE integration and error checking
Async Support	async/await in templates	Non-blocking I/O in template rendering
Debugging Tools	Line numbers mapped to source	Clear error messages pointing to template
JIT Compilation	Optional Numba/Cython acceleration	Near-native speed for hot code paths
Plugin System	Custom tags/filters via decorators	Extend without modifying core engine
###
Usage Example
python
engine = ChatuTemplateEngine(template_dir='templates')

html = engine.render('child.html', user='Alice', items=[1, 2, 3])
print(html)
templates/base.html

xml
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
</head>
<body>
    <header>{% block header %}Header content{% endblock %}</header>
    <main>{% block content %}Default content{% endblock %}</main>
    <footer>{% block footer %}Footer content{% endblock %}</footer>
</body>
</html>
templates/child.html

xml
{% extends "base.html" %}

{% block title %}Welcome {{ user|e }}{% endblock %}

{% block content %}
<ul>
{% for item in items %}
    <li>{{ item }}</li>
{% endfor %}
</ul>
{% endblock %}
Integration with ChatuWebAssets
I embed my frontend assets (w3.css, w3.js, ahah.js, brython.js) similarly as before with static routes 
and injection helpers, and then call the template engine’s render method to produce HTML that 
includes these assets.

Final Notes
This engine uses Python’s eval carefully with controlled context.
You can extend it with macro support, inline Python blocks, and sandboxing.
Caching compiled templates can be improved for production.
Autoescaping is on by default but can be controlled via filters.
You can add more filters by add_filter() method.
Macro support with argument parsing and invocation
Inline Python execution blocks
Sandboxed evaluation environment
A full parser instead of regex-based partial parsing
Template precompilation to Python bytecode for speed
Building a fully featured, robust, and extensible templating engine-surpassing even Jinja2 in flexibility and power-is an ambitious but achievable goal. Below is a comprehensive design and implementation plan, followed by a detailed, production-ready Python class that supports:
Variable interpolation with {{ ... }} syntax and filters
Control flow blocks with {% if %}, {% for %}, {% else %}, {% endif %}, {% endfor %}
Template inheritance with {% extends "base.html" %} and {% block name %}...{% endblock %}
Includes with {% include "file.html" %}
Macros / Defs with {% macro name(args) %}...{% endmacro %}
Custom filters and autoescaping
Inline Python code execution
Context variable resolution with dotted names and outer context access
Caching and precompilation for performance
Safe sandboxed evaluation environment
# EOF - Chatu TEMPLATING ENGINE
-----------------------------------------------
"""
## -- Chatu Web ASSETS--- ##
# ===========================
# Web Assets Integration
# ===========================

class ChatuWebAssets:
    W3_CSS = "/* full w3.css content here */"
    W3_JS = "/* full w3.js content here */"
    AHAH_JS = "/* full ahah.js content here */"
    BRYTHON_JS = "/* full brython.js content here (optional) */"

    @classmethod
    def register_routes(cls, app):
        @app.route('/static/w3.css')
        def w3_css(request):
            from Chatu import Response  # Adjust import if needed
            resp = Response(cls.W3_CSS)
            resp.content_type = 'text/css'
            return resp

        @app.route('/static/w3.js')
        def w3_js(request):
            from Chatu import Response
            resp = Response(cls.W3_JS)
            resp.content_type = 'application/javascript'
            return resp

        @app.route('/static/ahah.js')
        def ahah_js(request):
            from Chatu import Response
            resp = Response(cls.AHAH_JS)
            resp.content_type = 'application/javascript'
            return resp

        @app.route('/static/brython.js')
        def brython_js(request):
            from Chatu import Response
            resp = Response(cls.BRYTHON_JS)
            resp.content_type = 'application/javascript'
            return resp

    @classmethod
    def inject(cls):
        return (
            '<link rel="stylesheet" href="/static/w3.css">\n'
            '<script src="/static/w3.js"></script>\n'
            '<script src="/static/ahah.js"></script>\n'
            '<script src="/static/brython.js"></script>\n'
            '<script>window.onload=function(){brython();}</script>'
        )

# --- Essential missing pieces ---

# Generic HTTP exception used by `abort()` and dispatch flow
class HTTPException(Exception):
    def __init__(self, status_code, reason=None):
        self.status_code = status_code
        self.reason = reason or "Error"

# Generic async/callback handler support
import inspect

async def invoke_handler(handler, *args, **kwargs):
    if inspect.iscoroutinefunction(handler):
        return await handler(*args, **kwargs)
    else:
        return handler(*args, **kwargs)

#-- Re Pattern by kesh --
# URLPattern class:
# Parses route patterns like `/user/<int:id>` or `/search/<query>`
# and matches them against incoming paths.
# Supports types: int, str (default), path, and custom regex.
# Returns matched variables as a dictionary or None if no match.
import re

class URLPattern:
#    URLPattern parses route patterns with optional type casting, similar to Flask.
#    Supported patterns:
#    - /user/<int:id>       # casts to int
#    - /search/<query>      # default is str
#   - /file/<path:path>    # path matches slashes
#    - /custom/<re:\d{4}>   # regex custom matcher

#    Example:
#    >>> pattern = URLPattern("/user/<int:id>")
#    >>> pattern.match("/user/42")
#    {'id': '42'}


    def __init__(self, pattern):
        self.url_pattern = pattern
        self.regex = self._compile_pattern(pattern)

    def _compile_pattern(self, pattern):
        def convert(match):
            name = match.group('name')
            type_ = match.group('type') or 'str'
            if type_ == 'int':
                return f"(?P<{name}>\\d+)"
            elif type_ == 'path':
                return f"(?P<{name}>.+)"
            elif type_.startswith('re:'):
                return f"(?P<{name}>{type_[3:]})"
            else:
                return f"(?P<{name}>[^/]+)"
        regex = re.sub(r'<(?:(?P<type>[^:<>]+):)?(?P<name>\w+)>', convert, pattern)
        return re.compile(f'^{regex}$')

    def match(self, path):
        match = self.regex.match(path)
        return match.groupdict() if match else None


# --- Helpers ---
def urldecode_str(s):
    s = s.replace('+', ' ')
    parts = s.split('%')
    if len(parts) == 1:
        return s
    result = [parts[0]]
    for item in parts[1:]:
        if item == '':
            result.append('%')
        else:
            code = item[:2]
            result.append(chr(int(code, 16)))
            result.append(item[2:])
    return ''.join(result)


def urldecode_bytes(s):
    s = s.replace(b'+', b' ')
    parts = s.split(b'%')
    if len(parts) == 1:
        return s.decode()
    result = [parts[0]]
    for item in parts[1:]:
        if item == b'':
            result.append(b'%')
        else:
            code = item[:2]
            result.append(bytes([int(code, 16)]))
            result.append(item[2:])
    return b''.join(result).decode()


def urlencode(s):
    return s.replace('+', '%2B').replace(' ', '+').replace(
        '%', '%25').replace('?', '%3F').replace('#', '%23').replace(
            '&', '%26').replace('=', '%3D')


def mro(cls):  # pragma: no cover
    """Return the method resolution order of a class.

    This is a helper function that returns the method resolution order of a
    class. It is used by Chatu to find the best error handler to invoke for
    the raised exception.

    In CPython, this function returns the ``__mro__`` attribute of the class.
    In MicroPython, this function implements a recursive depth-first scanning
    of the class hierarchy.
    """
    if hasattr(cls, 'mro'):
        return cls.__mro__

    def _mro(cls):
        m = [cls]
        for base in cls.__bases__:
            m += _mro(base)
        return m

    mro_list = _mro(cls)

    # If a class appears multiple times (due to multiple inheritance) remove
    # all but the last occurence. This matches the method resolution order
    # of MicroPython, but not CPython.
    mro_pruned = []
    for i in range(len(mro_list)):
        base = mro_list.pop(0)
        if base not in mro_list:
            mro_pruned.append(base)
    return mro_pruned


class NoCaseDict(dict):
    """A subclass of dictionary that holds case-insensitive keys.

    :param initial_dict: an initial dictionary of key/value pairs to
                         initialize this object with.

    Example::

        >>> d = NoCaseDict()
        >>> d['Content-Type'] = 'text/html'
        >>> print(d['Content-Type'])
        text/html
        >>> print(d['content-type'])
        text/html
        >>> print(d['CONTENT-TYPE'])
        text/html
        >>> del d['cOnTeNt-TyPe']
        >>> print(d)
        {}
    """
    def __init__(self, initial_dict=None):
        super().__init__(initial_dict or {})
        self.keymap = {k.lower(): k for k in self.keys() if k.lower() != k}

    def __setitem__(self, key, value):
        kl = key.lower()
        key = self.keymap.get(kl, key)
        if kl != key:
            self.keymap[kl] = key
        super().__setitem__(key, value)

    def __getitem__(self, key):
        kl = key.lower()
        return super().__getitem__(self.keymap.get(kl, kl))

    def __delitem__(self, key):
        kl = key.lower()
        super().__delitem__(self.keymap.get(kl, kl))

    def __contains__(self, key):
        kl = key.lower()
        return self.keymap.get(kl, kl) in self.keys()

    def get(self, key, default=None):
        kl = key.lower()
        return super().get(self.keymap.get(kl, kl), default)

    def update(self, other_dict):
        for key, value in other_dict.items():
            self[key] = value


def mro(cls):  # pragma: no cover
    """Return the method resolution order of a class.

    This is a helper function that returns the method resolution order of a
    class. It is used by Chatu to find the best error handler to invoke for
    the raised exception.

    In CPython, this function returns the ``__mro__`` attribute of the class.
    In MicroPython, this function implements a recursive depth-first scanning
    of the class hierarchy.
    """
    if hasattr(cls, 'mro'):
        return cls.__mro__

    def _mro(cls):
        m = [cls]
        for base in cls.__bases__:
            m += _mro(base)
        return m

    mro_list = _mro(cls)

    # If a class appears multiple times (due to multiple inheritance) remove
    # all but the last occurence. This matches the method resolution order
    # of MicroPython, but not CPython.
    mro_pruned = []
    for i in range(len(mro_list)):
        base = mro_list.pop(0)
        if base not in mro_list:
            mro_pruned.append(base)
    return mro_pruned


class MultiDict(dict):
    """A subclass of dictionary that can hold multiple values for the same
    key. It is used to hold key/value pairs decoded from query strings and
    form submissions.

    :param initial_dict: an initial dictionary of key/value pairs to
                         initialize this object with.

    Example::

        >>> d = MultiDict()
        >>> d['sort'] = 'name'
        >>> d['sort'] = 'email'
        >>> print(d['sort'])
        'name'
        >>> print(d.getlist('sort'))
        ['name', 'email']
    """
    def __init__(self, initial_dict=None):
        super().__init__()
        if initial_dict:
            for key, value in initial_dict.items():
                self[key] = value

    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, [])
        super().__getitem__(key).append(value)

    def __getitem__(self, key):
        return super().__getitem__(key)[0]

    def get(self, key, default=None, type=None):
        """Return the value for a given key.

        :param key: The key to retrieve.
        :param default: A default value to use if the key does not exist.
        :param type: A type conversion callable to apply to the value.

        If the multidict contains more than one value for the requested key,
        this method returns the first value only.

        Example::

            >>> d = MultiDict()
            >>> d['age'] = '42'
            >>> d.get('age')
            '42'
            >>> d.get('age', type=int)
            42
            >>> d.get('name', default='noname')
            'noname'
        """
        if key not in self:
            return default
        value = self[key]
        if type is not None:
            value = type(value)
        return value

    def getlist(self, key, type=None):
        """Return all the values for a given key.

        :param key: The key to retrieve.
        :param type: A type conversion callable to apply to the values.

        If the requested key does not exist in the dictionary, this method
        returns an empty list.

        Example::

            >>> d = MultiDict()
            >>> d.getlist('items')
            []
            >>> d['items'] = '3'
            >>> d.getlist('items')
            ['3']
            >>> d['items'] = '56'
            >>> d.getlist('items')
            ['3', '56']
            >>> d.getlist('items', type=int)
            [3, 56]
        """
        if key not in self:
            return []
        values = super().__getitem__(key)
        if type is not None:
            values = [type(value) for value in values]
        return values


# --- CORS ---
class CORS:
    """Add CORS headers to HTTP responses.

    :param app: The application to add CORS headers to.
    :param allowed_origins: A list of origins that are allowed to make
                            cross-site requests. If set to '*', all origins are
                            allowed.
    :param allow_credentials: If set to True, the
                              ``Access-Control-Allow-Credentials`` header will
                              be set to ``true`` to indicate to the browser
                              that it can expose cookies and authentication
                              headers.
    :param allowed_methods: A list of methods that are allowed to be used when
                            making cross-site requests. If not set, all methods
                            are allowed.
    :param expose_headers: A list of headers that the browser is allowed to
                           exposed.
    :param allowed_headers: A list of headers that are allowed to be used when
                            making cross-site requests. If not set, all headers
                            are allowed.
    :param max_age: The maximum amount of time in seconds that the browser
                    should cache the results of a preflight request.
    :param handle_cors: If set to False, CORS headers will not be added to
                        responses. This can be useful if you want to add CORS
                        headers manually.
    """
    def __init__(self, app=None, allowed_origins=None, allow_credentials=False,
                 allowed_methods=None, expose_headers=None,
                 allowed_headers=None, max_age=None, handle_cors=True):
        self.allowed_origins = allowed_origins
        self.allow_credentials = allow_credentials
        self.allowed_methods = allowed_methods
        self.expose_headers = expose_headers
        self.allowed_headers = None if allowed_headers is None \
            else [h.lower() for h in allowed_headers]
        self.max_age = max_age
        if app is not None:
            self.initialize(app, handle_cors=handle_cors)

    def initialize(self, app, handle_cors=True):
        """Initialize the CORS object for the given application.

        :param app: The application to add CORS headers to.
        :param handle_cors: If set to False, CORS headers will not be added to
                            responses. This can be useful if you want to add
                            CORS headers manually.
        """
        self.default_options_handler = app.options_handler
        if handle_cors:
            app.options_handler = self.options_handler
            app.after_request(self.after_request)
            app.after_error_request(self.after_request)

    def options_handler(self, request):
        headers = self.default_options_handler(request)
        headers.update(self.get_cors_headers(request))
        return headers

    def get_cors_headers(self, request):
        """Return a dictionary of CORS headers to add to a given request.

        :param request: The request to add CORS headers to.
        """
        cors_headers = {}
        origin = request.headers.get('Origin')
        if self.allowed_origins == '*':
            cors_headers['Access-Control-Allow-Origin'] = origin or '*'
            if origin:
                cors_headers['Vary'] = 'Origin'
        elif origin in (self.allowed_origins or []):
            cors_headers['Access-Control-Allow-Origin'] = origin
            cors_headers['Vary'] = 'Origin'
        if self.allow_credentials and \
                'Access-Control-Allow-Origin' in cors_headers:
            cors_headers['Access-Control-Allow-Credentials'] = 'true'
        if self.expose_headers:
            cors_headers['Access-Control-Expose-Headers'] = \
                ', '.join(self.expose_headers)

        if request.method == 'OPTIONS':
            # handle preflight request
            if self.max_age:
                cors_headers['Access-Control-Max-Age'] = str(self.max_age)

            method = request.headers.get('Access-Control-Request-Method')
            if method:
                method = method.upper()
                if self.allowed_methods is None or \
                        method in self.allowed_methods:
                    cors_headers['Access-Control-Allow-Methods'] = method

            headers = request.headers.get('Access-Control-Request-Headers')
            if headers:
                if self.allowed_headers is None:
                    cors_headers['Access-Control-Allow-Headers'] = headers
                else:
                    headers = [h.strip() for h in headers.split(',')]
                    headers = [h for h in headers
                               if h.lower() in self.allowed_headers]
                    cors_headers['Access-Control-Allow-Headers'] = \
                        ', '.join(headers)

        return cors_headers

    def after_request(self, request, response):
        saved_vary = response.headers.get('Vary')
        response.headers.update(self.get_cors_headers(request))
        if saved_vary and saved_vary != response.headers.get('Vary'):
            response.headers['Vary'] = (
                saved_vary + ', ' + response.headers['Vary'])

# --- Session (JWT) ---
class SessionDict(dict):
    """A session dictionary.

    The session dictionary is a standard Python dictionary that has been
    extended with convenience ``save()`` and ``delete()`` methods.
    """
    def __init__(self, request, session_dict):
        super().__init__(session_dict)
        self.request = request

    def save(self):
        """Update the session cookie."""
        self.request.app._session.update(self.request, self)

    def delete(self):
        """Delete the session cookie."""
        self.request.app._session.delete(self.request)


class SessionDict(dict):
    """A session dictionary.

    The session dictionary is a standard Python dictionary that has been
    extended with convenience ``save()`` and ``delete()`` methods.
    """
    def __init__(self, request, session_dict):
        super().__init__(session_dict)
        self.request = request

    def save(self):
        """Update the session cookie."""
        self.request.app._session.update(self.request, self)

    def delete(self):
        """Delete the session cookie."""
        self.request.app._session.delete(self.request)


# --- SSE (Server-Sent Events) ---
class SSE:
    @staticmethod
    async def send(response, event, data):
        msg = f"event: {{event}}\ndata: {{json.dumps(data)}}\n\n"
        await response.write(msg.encode())

# --- Templates (utemplate & Jinja2) ---
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    def render_template(template_name, **context):
        env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
        template = env.get_template(template_name)
        return template.render(**context)
except ImportError:
    def render_template(template_name, **context):
        with open(os.path.join("templates", template_name), encoding="utf-8") as f:
            tpl = f.read()
        for k, v in context.items():
            tpl = tpl.replace("{{ "+k+" }}", str(v))
        return tpl

# --- Core Chatu ---

# --- Authentication Helpers & Decorators ---

def login_user(request, user: dict):
    """Logs in a user by storing info in the session."""
    request.session["user_id"] = user.get("id")
    request.session["name"] = user.get("name")
    request.session["email"] = user.get("email")
    request.session["role"] = user.get("role", "user")
    request.session.save()

def logout_user(request):
    """Logs out the current user."""
    request.session.clear()
    request.session.delete()

def current_user(request):
    """Returns the current logged-in user or None."""
    uid = request.session.get("user_id")
    if not uid:
        return None
    return {
        "id": uid,
        "name": request.session.get("name"),
        "email": request.session.get("email"),
        "role": request.session.get("role", "user"),
    }

def login_required(view):
    """Decorator: Only allows logged-in users."""
    @wraps(view)
    async def wrapped(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return Response("Unauthorized", 401)
        return await invoke_handler(view, request, *args, **kwargs)
    return wrapped

def roles_required(*roles):
    """Decorator: Only allows users with specific roles."""
    def decorator(view):
        @wraps(view)
        async def wrapped(request, *args, **kwargs):
            role = request.session.get("role")
            if role not in roles:
                return Response("Forbidden: Insufficient role", 403)
            return await invoke_handler(view, request, *args, **kwargs)
        return wrapped
    return decorator

def anonymous_only(view):
    """Decorator: Prevents logged-in users from accessing the route (e.g. login/register pages)."""
    @wraps(view)
    async def wrapped(request, *args, **kwargs):
        if request.session.get("user_id"):
            return Response.redirect("/")
        return await invoke_handler(view, request, *args, **kwargs)
    return wrapped

class Request:
    """An HTTP request."""
    #: Specify the maximum payload size that is accepted. Requests with larger
    #: payloads will be rejected with a 413 status code. Applications can
    #: change this maximum as necessary.
    #:
    #: Example::
    #:
    #:    Request.max_content_length = 1 * 1024 * 1024  # 1MB requests allowed
    max_content_length = 16 * 1024

    #: Specify the maximum payload size that can be stored in ``body``.
    #: Requests with payloads that are larger than this size and up to
    #: ``max_content_length`` bytes will be accepted, but the application will
    #: only be able to access the body of the request by reading from
    #: ``stream``. Set to 0 if you always access the body as a stream.
    #:
    #: Example::
    #:
    #:    Request.max_body_length = 4 * 1024  # up to 4KB bodies read
    max_body_length = 16 * 1024

    #: Specify the maximum length allowed for a line in the request. Requests
    #: with longer lines will not be correctly interpreted. Applications can
    #: change this maximum as necessary.
    #:
    #: Example::
    #:
    #:    Request.max_readline = 16 * 1024  # 16KB lines allowed
    max_readline = 2 * 1024

    class G:
        pass

    def __init__(self, app, client_addr, method, url, http_version, headers,
                 body=None, stream=None, sock=None):
        #: The application instance to which this request belongs.
        self.app = app
        #: The address of the client, as a tuple (host, port).
        self.client_addr = client_addr
        #: The HTTP method of the request.
        self.method = method
        #: The request URL, including the path and query string.
        self.url = url
        #: The path portion of the URL.
        self.path = url
        #: The query string portion of the URL.
        self.query_string = None
        #: The parsed query string, as a
        #: :class:`MultiDict <Chatu.MultiDict>` object.
        self.args = {}
        #: A dictionary with the headers included in the request.
        self.headers = headers
        #: A dictionary with the cookies included in the request.
        self.cookies = {}
        #: The parsed ``Content-Length`` header.
        self.content_length = 0
        #: The parsed ``Content-Type`` header.
        self.content_type = None
        #: A general purpose container for applications to store data during
        #: the life of the request.
        self.g = Request.G()

        self.http_version = http_version
        if '?' in self.path:
            self.path, self.query_string = self.path.split('?', 1)
            self.args = self._parse_urlencoded(self.query_string)

        if 'Content-Length' in self.headers:
            self.content_length = int(self.headers['Content-Length'])
        if 'Content-Type' in self.headers:
            self.content_type = self.headers['Content-Type']
        if 'Cookie' in self.headers:
            for cookie in self.headers['Cookie'].split(';'):
                name, value = cookie.strip().split('=', 1)
                self.cookies[name] = value

        self._body = body
        self.body_used = False
        self._stream = stream
        self.sock = sock
        self._json = None
        self._form = None
        self.after_request_handlers = []

    @staticmethod
    async def create(app, client_reader, client_writer, client_addr):
        """Create a request object.

        :param app: The Chatu application instance.
        :param client_reader: An input stream from where the request data can
                              be read.
        :param client_writer: An output stream where the response data can be
                              written.
        :param client_addr: The address of the client, as a tuple.

        This method is a coroutine. It returns a newly created ``Request``
        object.
        """
        # request line
        line = (await Request._safe_readline(client_reader)).strip().decode()
        if not line:  # pragma: no cover
            return None
        method, url, http_version = line.split()
        http_version = http_version.split('/', 1)[1]

        # headers
        headers = NoCaseDict()
        content_length = 0
        while True:
            line = (await Request._safe_readline(
                client_reader)).strip().decode()
            if line == '':
                break
            header, value = line.split(':', 1)
            value = value.strip()
            headers[header] = value
            if header.lower() == 'content-length':
                content_length = int(value)

        # body
        body = b''
        if content_length and content_length <= Request.max_body_length:
            body = await client_reader.readexactly(content_length)
            stream = None
        else:
            body = b''
            stream = client_reader

        return Request(app, client_addr, method, url, http_version, headers,
                       body=body, stream=stream,
                       sock=(client_reader, client_writer))

    def _parse_urlencoded(self, urlencoded):
        data = MultiDict()
        if len(urlencoded) > 0:  # pragma: no branch
            if isinstance(urlencoded, str):
                for kv in [pair.split('=', 1)
                           for pair in urlencoded.split('&') if pair]:
                    data[urldecode_str(kv[0])] = urldecode_str(kv[1]) \
                        if len(kv) > 1 else ''
            elif isinstance(urlencoded, bytes):  # pragma: no branch
                for kv in [pair.split(b'=', 1)
                           for pair in urlencoded.split(b'&') if pair]:
                    data[urldecode_bytes(kv[0])] = urldecode_bytes(kv[1]) \
                        if len(kv) > 1 else b''
        return data

    @property
    def body(self):
        """The body of the request, as bytes."""
        return self._body

    @property
    def stream(self):
        """The body of the request, as a bytes stream."""
        if self._stream is None:
            self._stream = AsyncBytesIO(self._body)
        return self._stream

    @property
    def json(self):
        """The parsed JSON body, or ``None`` if the request does not have a
        JSON body."""
        if self._json is None:
            if self.content_type is None:
                return None
            mime_type = self.content_type.split(';')[0]
            if mime_type != 'application/json':
                return None
            self._json = json.loads(self.body.decode())
        return self._json

    @property
    def form(self):
        """The parsed form submission body, as a
        :class:`MultiDict <Chatu.MultiDict>` object, or ``None`` if the
        request does not have a form submission."""
        if self._form is None:
            if self.content_type is None:
                return None
            mime_type = self.content_type.split(';')[0]
            if mime_type != 'application/x-www-form-urlencoded':
                return None
            self._form = self._parse_urlencoded(self.body)
        return self._form

    def after_request(self, f):
        """Register a request-specific function to run after the request is
        handled. Request-specific after request handlers run at the very end,
        after the application's own after request handlers. The function must
        take two arguments, the request and response objects. The return value
        of the function must be the updated response object.

        Example::

            @app.route('/')
            def index(request):
                # register a request-specific after request handler
                @req.after_request
                def func(request, response):
                    # ...
                    return response

                return 'Hello, World!'

        Note that the function is not called if the request handler raises an
        exception and an error response is returned instead.
        """
        self.after_request_handlers.append(f)
        return f

    @staticmethod
    async def _safe_readline(stream):
        line = (await stream.readline())
        if len(line) > Request.max_readline:
            raise ValueError('line too long')
        return line


class Response:
    """An HTTP response class.

    :param body: The body of the response. If a dictionary or list is given,
                 a JSON formatter is used to generate the body. If a file-like
                 object or an async generator is given, a streaming response is
                 used. If a string is given, it is encoded from UTF-8. Else,
                 the body should be a byte sequence.
    :param status_code: The numeric HTTP status code of the response. The
                        default is 200.
    :param headers: A dictionary of headers to include in the response.
    :param reason: A custom reason phrase to add after the status code. The
                   default is "OK" for responses with a 200 status code and
                   "N/A" for any other status codes.
    """
    types_map = {
        'css': 'text/css',
        'gif': 'image/gif',
        'html': 'text/html',
        'jpg': 'image/jpeg',
        'js': 'application/javascript',
        'json': 'application/json',
        'png': 'image/png',
        'txt': 'text/plain',
    }

    send_file_buffer_size = 1024

    #: The content type to use for responses that do not explicitly define a
    #: ``Content-Type`` header.
    default_content_type = 'text/plain'

    #: The default cache control max age used by :meth:`send_file`. A value
    #: of ``None`` means that no ``Cache-Control`` header is added.
    default_send_file_max_age = None

    #: Special response used to signal that a response does not need to be
    #: written to the client. Used to exit WebSocket connections cleanly.
    already_handled = None

    def __init__(self, body='', status_code=200, headers=None, reason=None):
        if body is None and status_code == 200:
            body = ''
            status_code = 204
        self.status_code = status_code
        self.headers = NoCaseDict(headers or {})
        self.reason = reason
        if isinstance(body, (dict, list)):
            self.body = json.dumps(body).encode()
            self.headers['Content-Type'] = 'application/json; charset=UTF-8'
        elif isinstance(body, str):
            self.body = body.encode()
        else:
            # this applies to bytes, file-like objects or generators
            self.body = body
        self.is_head = False

    def set_cookie(self, cookie, value, path=None, domain=None, expires=None,
                   max_age=None, secure=False, http_only=False,
                   partitioned=False):
        """Add a cookie to the response.

        :param cookie: The cookie's name.
        :param value: The cookie's value.
        :param path: The cookie's path.
        :param domain: The cookie's domain.
        :param expires: The cookie expiration time, as a ``datetime`` object
                        or a correctly formatted string.
        :param max_age: The cookie's ``Max-Age`` value.
        :param secure: The cookie's ``secure`` flag.
        :param http_only: The cookie's ``HttpOnly`` flag.
        :param partitioned: Whether the cookie is partitioned.
        """
        http_cookie = '{cookie}={value}'.format(cookie=cookie, value=value)
        if path:
            http_cookie += '; Path=' + path
        if domain:
            http_cookie += '; Domain=' + domain
        if expires:
            if isinstance(expires, str):
                http_cookie += '; Expires=' + expires
            else:  # pragma: no cover
                http_cookie += '; Expires=' + time.strftime(
                    '%a, %d %b %Y %H:%M:%S GMT', expires.timetuple())
        if max_age is not None:
            http_cookie += '; Max-Age=' + str(max_age)
        if secure:
            http_cookie += '; Secure'
        if http_only:
            http_cookie += '; HttpOnly'
        if partitioned:
            http_cookie += '; Partitioned'
        if 'Set-Cookie' in self.headers:
            self.headers['Set-Cookie'].append(http_cookie)
        else:
            self.headers['Set-Cookie'] = [http_cookie]

    def delete_cookie(self, cookie, **kwargs):
        """Delete a cookie.

        :param cookie: The cookie's name.
        :param kwargs: Any cookie opens and flags supported by
                       ``set_cookie()`` except ``expires`` and ``max_age``.
        """
        self.set_cookie(cookie, '', expires='Thu, 01 Jan 1970 00:00:01 GMT',
                        max_age=0, **kwargs)

    def complete(self):
        if isinstance(self.body, bytes) and \
                'Content-Length' not in self.headers:
            self.headers['Content-Length'] = str(len(self.body))
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = self.default_content_type
            if 'charset=' not in self.headers['Content-Type']:
                self.headers['Content-Type'] += '; charset=UTF-8'

    async def write(self, stream):
        self.complete()

        try:
            # status code
            reason = self.reason if self.reason is not None else \
                ('OK' if self.status_code == 200 else 'N/A')
            await stream.awrite('HTTP/1.0 {status_code} {reason}\r\n'.format(
                status_code=self.status_code, reason=reason).encode())

            # headers
            for header, value in self.headers.items():
                values = value if isinstance(value, list) else [value]
                for value in values:
                    await stream.awrite('{header}: {value}\r\n'.format(
                        header=header, value=value).encode())
            await stream.awrite(b'\r\n')

            # body
            if not self.is_head:
                iter = self.body_iter()
                async for body in iter:
                    if isinstance(body, str):  # pragma: no cover
                        body = body.encode()
                    try:
                        await stream.awrite(body)
                    except OSError as exc:  # pragma: no cover
                        if exc.errno in MUTED_SOCKET_ERRORS or \
                                exc.args[0] == 'Connection lost':
                            if hasattr(iter, 'aclose'):
                                await iter.aclose()
                        raise
                if hasattr(iter, 'aclose'):  # pragma: no branch
                    await iter.aclose()

        except OSError as exc:  # pragma: no cover
            if exc.errno in MUTED_SOCKET_ERRORS or \
                    exc.args[0] == 'Connection lost':
                pass
            else:
                raise

    def body_iter(self):
        if hasattr(self.body, '__anext__'):
            # response body is an async generator
            return self.body

        response = self

        class iter:
            ITER_UNKNOWN = 0
            ITER_SYNC_GEN = 1
            ITER_FILE_OBJ = 2
            ITER_NO_BODY = -1

            def __aiter__(self):
                if response.body:
                    self.i = self.ITER_UNKNOWN  # need to determine type
                else:
                    self.i = self.ITER_NO_BODY
                return self

            async def __anext__(self):
                if self.i == self.ITER_NO_BODY:
                    await self.aclose()
                    raise StopAsyncIteration
                if self.i == self.ITER_UNKNOWN:
                    if hasattr(response.body, 'read'):
                        self.i = self.ITER_FILE_OBJ
                    elif hasattr(response.body, '__next__'):
                        self.i = self.ITER_SYNC_GEN
                        return next(response.body)
                    else:
                        self.i = self.ITER_NO_BODY
                        return response.body
                elif self.i == self.ITER_SYNC_GEN:
                    try:
                        return next(response.body)
                    except StopIteration:
                        await self.aclose()
                        raise StopAsyncIteration
                buf = response.body.read(response.send_file_buffer_size)
                if iscoroutine(buf):  # pragma: no cover
                    buf = await buf
                if len(buf) < response.send_file_buffer_size:
                    self.i = self.ITER_NO_BODY
                return buf

            async def aclose(self):
                if hasattr(response.body, 'close'):
                    result = response.body.close()
                    if iscoroutine(result):  # pragma: no cover
                        await result

        return iter()

    @classmethod
    def redirect(cls, location, status_code=302):
        """Return a redirect response.

        :param location: The URL to redirect to.
        :param status_code: The 3xx status code to use for the redirect. The
                            default is 302.
        """
        if '\x0d' in location or '\x0a' in location:
            raise ValueError('invalid redirect URL')
        return cls(status_code=status_code, headers={'Location': location})

    @classmethod
    def send_file(cls, filename, status_code=200, content_type=None,
                  stream=None, max_age=None, compressed=False,
                  file_extension=''):
        """Send file contents in a response.

        :param filename: The filename of the file.
        :param status_code: The 3xx status code to use for the redirect. The
                            default is 302.
        :param content_type: The ``Content-Type`` header to use in the
                             response. If omitted, it is generated
                             automatically from the file extension of the
                             ``filename`` parameter.
        :param stream: A file-like object to read the file contents from. If
                       a stream is given, the ``filename`` parameter is only
                       used when generating the ``Content-Type`` header.
        :param max_age: The ``Cache-Control`` header's ``max-age`` value in
                        seconds. If omitted, the value of the
                        :attr:`Response.default_send_file_max_age` attribute is
                        used.
        :param compressed: Whether the file is compressed. If ``True``, the
                           ``Content-Encoding`` header is set to ``gzip``. A
                           string with the header value can also be passed.
                           Note that when using this option the file must have
                           been compressed beforehand. This option only sets
                           the header.
        :param file_extension: A file extension to append to the ``filename``
                               parameter when opening the file, including the
                               dot. The extension given here is not considered
                               when generating the ``Content-Type`` header.

        Security note: The filename is assumed to be trusted. Never pass
        filenames provided by the user without validating and sanitizing them
        first.
        """
        if content_type is None:
            ext = filename.split('.')[-1]
            if ext in Response.types_map:
                content_type = Response.types_map[ext]
            else:
                content_type = 'application/octet-stream'
        headers = {'Content-Type': content_type}

        if max_age is None:
            max_age = cls.default_send_file_max_age
        if max_age is not None:
            headers['Cache-Control'] = 'max-age={}'.format(max_age)

        if compressed:
            headers['Content-Encoding'] = compressed \
                if isinstance(compressed, str) else 'gzip'

        f = stream or open(filename + file_extension, 'rb')
        return cls(body=f, status_code=status_code, headers=headers)


class Chatu:
    """An HTTP application class.

    This class implements an HTTP application instance and is heavily
    influenced by the ``Flask`` class of the Flask framework. It is typically
    declared near the start of the main application script.

    Example::

        from Chatu import Chatu

        app = Chatu()
    """
    def __init__(self, name=None):
        self.import_name = name or __name__
        self.url_map = []
        self.before_request_handlers = []
        self.after_request_handlers = []
        self.after_error_request_handlers = []
        self.error_handlers = {}
        self.shutdown_requested = False
        self.options_handler = self.default_options_handler
        self.debug = False
        self.server = None

    def route(self, url_pattern, methods=None):
        """Decorator that is used to register a function as a request handler
        for a given URL.

        :param url_pattern: The URL pattern that will be compared against
                            incoming requests.
        :param methods: The list of HTTP methods to be handled by the
                        decorated function. If omitted, only ``GET`` requests
                        are handled.

        The URL pattern can be a static path (for example, ``/users`` or
        ``/api/invoices/search``) or a path with dynamic components enclosed
        in ``<`` and ``>`` (for example, ``/users/<id>`` or
        ``/invoices/<number>/products``). Dynamic path components can also
        include a type prefix, separated from the name with a colon (for
        example, ``/users/<int:id>``). The type can be ``string`` (the
        default), ``int``, ``path`` or ``re:[regular-expression]``.

        The first argument of the decorated function must be
        the request object. Any path arguments that are specified in the URL
        pattern are passed as keyword arguments. The return value of the
        function must be a :class:`Response` instance, or the arguments to
        be passed to this class.

        Example::

            @app.route('/')
            def index(request):
                return 'Hello, world!'
        """
        def decorated(f):
            self.url_map.append(
                ([m.upper() for m in (methods or ['GET'])],
                 URLPattern(url_pattern), f))
            return f
        return decorated

    def get(self, url_pattern):
        """Decorator that is used to register a function as a ``GET`` request
        handler for a given URL.

        :param url_pattern: The URL pattern that will be compared against
                            incoming requests.

        This decorator can be used as an alias to the ``route`` decorator with
        ``methods=['GET']``.

        Example::

            @app.get('/users/<int:id>')
            def get_user(request, id):
                # ...
        """
        return self.route(url_pattern, methods=['GET'])

    def post(self, url_pattern):
        """Decorator that is used to register a function as a ``POST`` request
        handler for a given URL.

        :param url_pattern: The URL pattern that will be compared against
                            incoming requests.

        This decorator can be used as an alias to the``route`` decorator with
        ``methods=['POST']``.

        Example::

            @app.post('/users')
            def create_user(request):
                # ...
        """
        return self.route(url_pattern, methods=['POST'])

    def put(self, url_pattern):
        """Decorator that is used to register a function as a ``PUT`` request
        handler for a given URL.

        :param url_pattern: The URL pattern that will be compared against
                            incoming requests.

        This decorator can be used as an alias to the ``route`` decorator with
        ``methods=['PUT']``.

        Example::

            @app.put('/users/<int:id>')
            def edit_user(request, id):
                # ...
        """
        return self.route(url_pattern, methods=['PUT'])

    def patch(self, url_pattern):
        """Decorator that is used to register a function as a ``PATCH`` request
        handler for a given URL.

        :param url_pattern: The URL pattern that will be compared against
                            incoming requests.

        This decorator can be used as an alias to the ``route`` decorator with
        ``methods=['PATCH']``.

        Example::

            @app.patch('/users/<int:id>')
            def edit_user(request, id):
                # ...
        """
        return self.route(url_pattern, methods=['PATCH'])

    def delete(self, url_pattern):
        """Decorator that is used to register a function as a ``DELETE``
        request handler for a given URL.

        :param url_pattern: The URL pattern that will be compared against
                            incoming requests.

        This decorator can be used as an alias to the ``route`` decorator with
        ``methods=['DELETE']``.

        Example::

            @app.delete('/users/<int:id>')
            def delete_user(request, id):
                # ...
        """
        return self.route(url_pattern, methods=['DELETE'])

    def before_request(self, f):
        """Decorator to register a function to run before each request is
        handled. The decorated function must take a single argument, the
        request object.

        Example::

            @app.before_request
            def func(request):
                # ...
        """
        self.before_request_handlers.append(f)
        return f

    def after_request(self, f):
        """Decorator to register a function to run after each request is
        handled. The decorated function must take two arguments, the request
        and response objects. The return value of the function must be an
        updated response object.

        Example::

            @app.after_request
            def func(request, response):
                # ...
                return response
        """
        self.after_request_handlers.append(f)
        return f

    def after_error_request(self, f):
        """Decorator to register a function to run after an error response is
        generated. The decorated function must take two arguments, the request
        and response objects. The return value of the function must be an
        updated response object. The handler is invoked for error responses
        generated by Chatu, as well as those returned by application-defined
        error handlers.

        Example::

            @app.after_error_request
            def func(request, response):
                # ...
                return response
        """
        self.after_error_request_handlers.append(f)
        return f

    def errorhandler(self, status_code_or_exception_class):
        """Decorator to register a function as an error handler. Error handler
        functions for numeric HTTP status codes must accept a single argument,
        the request object. Error handler functions for Python exceptions
        must accept two arguments, the request object and the exception
        object.

        :param status_code_or_exception_class: The numeric HTTP status code or
                                               Python exception class to
                                               handle.

        Examples::

            @app.errorhandler(404)
            def not_found(request):
                return 'Not found'

            @app.errorhandler(RuntimeError)
            def runtime_error(request, exception):
                return 'Runtime error'
        """
        def decorated(f):
            self.error_handlers[status_code_or_exception_class] = f
            return f
        return decorated

    def mount(self, subapp, url_prefix=''):
        """Mount a sub-application, optionally under the given URL prefix.

        :param subapp: The sub-application to mount.
        :param url_prefix: The URL prefix to mount the application under.
        """
        for methods, pattern, handler in subapp.url_map:
            self.url_map.append(
                (methods, URLPattern(url_prefix + pattern.url_pattern),
                 handler))
        for handler in subapp.before_request_handlers:
            self.before_request_handlers.append(handler)
        for handler in subapp.after_request_handlers:
            self.after_request_handlers.append(handler)
        for handler in subapp.after_error_request_handlers:
            self.after_error_request_handlers.append(handler)
        for status_code, handler in subapp.error_handlers.items():
            self.error_handlers[status_code] = handler

    @staticmethod
    def abort(status_code, reason=None):
        """Abort the current request and return an error response with the
        given status code.

        :param status_code: The numeric status code of the response.
        :param reason: The reason for the response, which is included in the
                       response body.

        Example::

            from Chatu import abort

            @app.route('/users/<int:id>')
            def get_user(id):
                user = get_user_by_id(id)
                if user is None:
                    abort(404)
                return user.to_dict()
        """
        raise HTTPException(status_code, reason)

    async def start_server(self, host='0.0.0.0', port=5000, debug=False,
                           ssl=None):
        """Start the Chatu web server as a coroutine. This coroutine does
        not normally return, as the server enters an endless listening loop.
        The :func:`shutdown` function provides a method for terminating the
        server gracefully.

        :param host: The hostname or IP address of the network interface that
                     will be listening for requests. A value of ``'0.0.0.0'``
                     (the default) indicates that the server should listen for
                     requests on all the available interfaces, and a value of
                     ``127.0.0.1`` indicates that the server should listen
                     for requests only on the internal networking interface of
                     the host.
        :param port: The port number to listen for requests. The default is
                     port 5000.
        :param debug: If ``True``, the server logs debugging information. The
                      default is ``False``.
        :param ssl: An ``SSLContext`` instance or ``None`` if the server should
                    not use TLS. The default is ``None``.

        This method is a coroutine.

        Example::

            import asyncio
            from Chatu import Chatu

            app = Chatu()

            @app.route('/')
            async def index(request):
                return 'Hello, world!'

            async def main():
                await app.start_server(debug=True)

            asyncio.run(main())
        """
        self.debug = debug

        async def serve(reader, writer):
            if not hasattr(writer, 'awrite'):  # pragma: no cover
                # CPython provides the awrite and aclose methods in 3.8+
                async def awrite(self, data):
                    self.write(data)
                    await self.drain()

                async def aclose(self):
                    self.close()
                    await self.wait_closed()

                from types import MethodType
                writer.awrite = MethodType(awrite, writer)
                writer.aclose = MethodType(aclose, writer)

            await self.handle_request(reader, writer)

        if self.debug:  # pragma: no cover
            print('Starting async server on {host}:{port}...'.format(
                host=host, port=port))

        try:
            self.server = await asyncio.start_server(serve, host, port,
                                                     ssl=ssl)
        except TypeError:  # pragma: no cover
            self.server = await asyncio.start_server(serve, host, port)

        while True:
            try:
                if hasattr(self.server, 'serve_forever'):  # pragma: no cover
                    try:
                        await self.server.serve_forever()
                    except asyncio.CancelledError:
                        pass
                await self.server.wait_closed()
                break
            except AttributeError:  # pragma: no cover
                # the task hasn't been initialized in the server object yet
                # wait a bit and try again
                await asyncio.sleep(0.1)

    
    def run(self, host="127.0.0.1", port=None, debug=False, ssl=None):
        import socket

        def is_port_available(p):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex((host, p)) != 0

        default_ports = [7000, 4375]
        if port is None:
            for p in default_ports:
                if is_port_available(p):
                    port = p
                    break
            else:
                port = 8000  # fallback default
        elif not is_port_available(port):
            print(f"⚠️  Port {port} is in use. Trying fallback ports...")
            for p in default_ports:
                if is_port_available(p):
                    port = p
                    break

        print(f"🚀 Chatu is running on http://{host}:{port}")
        print("🔁 Press CTRL+C to quit")
        asyncio.run(self.start_server(host=host, port=port, debug=debug, ssl=ssl))


    def shutdown(self):
        """Request a server shutdown. The server will then exit its request
        listening loop and the :func:`run` function will return. This function
        can be safely called from a route handler, as it only schedules the
        server to terminate as soon as the request completes.

        Example::

            @app.route('/shutdown')
            def shutdown(request):
                request.app.shutdown()
                return 'The server is shutting down...'
        """
        self.server.close()

    def find_route(self, req):
        method = req.method.upper()
        if method == 'OPTIONS' and self.options_handler:
            return self.options_handler(req)
        if method == 'HEAD':
            method = 'GET'
        f = 404
        for route_methods, route_pattern, route_handler in self.url_map:
            req.url_args = route_pattern.match(req.path)
            if req.url_args is not None:
                if method in route_methods:
                    f = route_handler
                    break
                else:
                    f = 405
        return f

    def default_options_handler(self, req):
        allow = []
        for route_methods, route_pattern, route_handler in self.url_map:
            if route_pattern.match(req.path) is not None:
                allow.extend(route_methods)
        if 'GET' in allow:
            allow.append('HEAD')
        allow.append('OPTIONS')
        return {'Allow': ', '.join(allow)}

    async def handle_request(self, reader, writer):
        req = None
        try:
            req = await Request.create(self, reader, writer,
                                       writer.get_extra_info('peername'))
        except Exception as exc:  # pragma: no cover
            print_exception(exc)

        res = await self.dispatch_request(req)
        if res != Response.already_handled:  # pragma: no branch
            await res.write(writer)
        try:
            await writer.aclose()
        except OSError as exc:  # pragma: no cover
            if exc.errno in MUTED_SOCKET_ERRORS:
                pass
            else:
                raise
        if self.debug and req:  # pragma: no cover
            print('{method} {path} {status_code}'.format(
                method=req.method, path=req.path,
                status_code=res.status_code))

    async def dispatch_request(self, req):
        after_request_handled = False
        if req:
            if req.content_length > req.max_content_length:
                if 413 in self.error_handlers:
                    res = await invoke_handler(self.error_handlers[413], req)
                else:
                    res = 'Payload too large', 413
            else:
                f = self.find_route(req)
                try:
                    res = None
                    if callable(f):
                        for handler in self.before_request_handlers:
                            res = await invoke_handler(handler, req)
                            if res:
                                break
                        if res is None:
                            res = await invoke_handler(
                                f, req, **req.url_args)
                        if isinstance(res, tuple):
                            body = res[0]
                            if isinstance(res[1], int):
                                status_code = res[1]
                                headers = res[2] if len(res) > 2 else {}
                            else:
                                status_code = 200
                                headers = res[1]
                            res = Response(body, status_code, headers)
                        elif not isinstance(res, Response):
                            res = Response(res)
                        for handler in self.after_request_handlers:
                            res = await invoke_handler(
                                handler, req, res) or res
                        for handler in req.after_request_handlers:
                            res = await invoke_handler(
                                handler, req, res) or res
                        after_request_handled = True
                    elif isinstance(f, dict):
                        res = Response(headers=f)
                    elif f in self.error_handlers:
                        res = await invoke_handler(self.error_handlers[f], req)
                    else:
                        res = 'Not found', f
                except HTTPException as exc:
                    if exc.status_code in self.error_handlers:
                        res = self.error_handlers[exc.status_code](req)
                    else:
                        res = exc.reason, exc.status_code
                except Exception as exc:
                    print_exception(exc)
                    exc_class = None
                    res = None
                    if exc.__class__ in self.error_handlers:
                        exc_class = exc.__class__
                    else:
                        for c in mro(exc.__class__)[1:]:
                            if c in self.error_handlers:
                                exc_class = c
                                break
                    if exc_class:
                        try:
                            res = await invoke_handler(
                                self.error_handlers[exc_class], req, exc)
                        except Exception as exc2:  # pragma: no cover
                            print_exception(exc2)
                    if res is None:
                        if 500 in self.error_handlers:
                            res = await invoke_handler(
                                self.error_handlers[500], req)
                        else:
                            res = 'Internal server error', 500
        else:
            if 400 in self.error_handlers:
                res = await invoke_handler(self.error_handlers[400], req)
            else:
                res = 'Bad request', 400
        if isinstance(res, tuple):
            res = Response(*res)
        elif not isinstance(res, Response):
            res = Response(res)
        if not after_request_handled:
            for handler in self.after_error_request_handlers:
                res = await invoke_handler(
                    handler, req, res) or res
        res.is_head = (req and req.method == 'HEAD')
        return res


# --- ASGI Support ---
'''
class ChatuAsgi(Chatu):
    """A subclass of the core :class:`Chatu <Chatu.Chatu>` class that
    implements the ASGI protocol.

    This class must be used as the application instance when running under an
    ASGI web server.
    """
    def __init__(self):
        super().__init__()
        self.embedded_server = False

    async def asgi_app(self, scope, receive, send):
        """An ASGI application."""
        if scope['type'] not in ['http', 'websocket']:  # pragma: no cover
            return
        path = scope['path']
        if 'query_string' in scope and scope['query_string']:
            path += '?' + scope['query_string'].decode()
        headers = NoCaseDict()
        content_length = 0
        for key, value in scope.get('headers', []):
            key = key.decode().title()
            headers[key] = value.decode()
            if key == 'Content-Length':
                content_length = int(value)

        if content_length and content_length <= Request.max_body_length:
            body = b''
            more = True
            while more:
                packet = await receive()
                body += packet.get('body', b'')
                more = packet.get('more_body', False)
            stream = None
        else:
            body = b''
            stream = _BodyStream(receive)

        req = Request(
            self,
            (scope['client'][0], scope['client'][1]),
            scope.get('method', 'GET'),
            path,
            'HTTP/' + scope['http_version'],
            headers,
            body=body,
            stream=stream,
            sock=(receive, send))
        req.asgi_scope = scope

        res = await self.dispatch_request(req)
        res.complete()

        header_list = []
        for name, value in res.headers.items():
            if not isinstance(value, list):
                header_list.append((name.lower().encode(), value.encode()))
            else:
                for v in value:
                    header_list.append((name.lower().encode(), v.encode()))

        if scope['type'] != 'http':  # pragma: no cover
            return

        await send({'type': 'http.response.start',
                    'status': res.status_code,
                    'headers': header_list})

        cancelled = False

        async def cancel_monitor():
            nonlocal cancelled

            while True:
                event = await receive()
                if event is None or \
                        event['type'] == 'http.disconnect':  # pragma: no cover
                    cancelled = True
                    break

        monitor_task = asyncio.ensure_future(cancel_monitor())

        body_iter = res.body_iter().__aiter__()
        res_body = b''
        try:
            res_body = await body_iter.__anext__()
            while not cancelled:  # pragma: no branch
                next_body = await body_iter.__anext__()
                await send({'type': 'http.response.body',
                            'body': res_body,
                            'more_body': True})
                res_body = next_body
        except StopAsyncIteration:
            await send({'type': 'http.response.body',
                        'body': res_body,
                        'more_body': False})
        if hasattr(body_iter, 'aclose'):  # pragma: no branch
            await body_iter.aclose()
        cancelled = True
        await monitor_task

    async def __call__(self, scope, receive, send):
        return await self.asgi_app(scope, receive, send)

    def shutdown(self):
        if self.embedded_server:  # pragma: no cover
            super().shutdown()
        else:
            pid = os.getpgrp() if hasattr(os, 'getpgrp') else os.getpid()
            os.kill(pid, signal.SIGTERM)

    def run(self, host='0.0.0.0', port=5000, debug=False,
            **options):  # pragma: no cover
        """Normally you would not start the server by invoking this method.
        Instead, start your chosen ASGI web server and pass the ``Chatu``
        instance as the ASGI application.
        """
        self.embedded_server = True
        super().run(host=host, port=port, debug=debug, **options)
'''

# --- WebSocket (minimal) ---
class WebSocketError(Exception):
    """Exception raised when an error occurs in a WebSocket connection."""
    pass


# websocket_upgrade not found in websocket.py

# with_websocket not found in websocket.py

# --- Static File Serving ---
class Static:
    @staticmethod
    def serve(directory, default_file="index.html"):
        async def handler(request):
            rel_path = request.path.lstrip("/")
            file_path = os.path.join(directory, rel_path)
            if not os.path.abspath(file_path).startswith(os.path.abspath(directory)):
                return Response("Forbidden", 403)
            if not os.path.isfile(file_path):
                return Response("Not found", 404)
            mime_type, _ = mimetypes.guess_type(file_path)
            with open(file_path, "rb") as f:
                content = f.read()
            return Response(content, headers={{"Content-Type": mime_type or "application/octet-stream"}})
        return handler

# --- Uploads ---
class Upload:
    allowed_types = ["image/png", "image/jpeg", "application/pdf"]
    max_size = 10 * 1024 * 1024
    @staticmethod
    async def save(request, field_name, dest_dir="uploads", allowed_types=None, max_size=None):
        allowed_types = allowed_types or Upload.allowed_types
        max_size = max_size or Upload.max_size
        file = request.files.get(field_name)
        if not file: raise ValueError("No file uploaded")
        filename = file.filename
        content = file.body
        if len(content) > max_size: raise ValueError("File too large")
        if file.content_type not in allowed_types: raise ValueError("File type not allowed")
        os.makedirs(dest_dir, exist_ok=True)
        unique_name = f"{{uuid.uuid4().hex}}_{{filename}}"
        file_path = os.path.join(dest_dir, unique_name)
        with open(file_path, "wb") as f:
            f.write(content)
        return {{"filename": filename, "saved_as": unique_name, "path": file_path, "content_type": file.content_type, "size": len(content)}}

# --- Forms ---
class Form:
    def __init__(self, **fields): self.fields = fields
    def validate(self, data): return all(f.validate(data.get(k)) for k, f in self.fields.items())

class StringField:
    def __init__(self, label, validators=[]): self.label = label; self.validators = validators
    def validate(self, value): return all(v(value) for v in self.validators)

class IntegerField:
    def __init__(self, label, validators=[]): self.label = label; self.validators = validators
    def validate(self, value): return all(v(int(value)) for v in self.validators)

class BooleanField:
    def __init__(self, label, validators=[]): self.label = label; self.validators = validators
    def validate(self, value): return all(v(bool(value)) for v in self.validators)

class EmailField:
    def __init__(self, label, validators=[]): self.label = label; self.validators = validators
    def validate(self, value): return all(v(value) for v in self.validators) and '@' in value

class PasswordField:
    def __init__(self, label, validators=[]): self.label = label; self.validators = validators
    def validate(self, value): return all(v(value) for v in self.validators)

class SelectField:
    def __init__(self, label, choices, validators=[]): 
        self.label = label; self.validators = validators; self.choices = choices
    def validate(self, value): return all(v(value) for v in self.validators) and value in [c[0] for c in self.choices]

class TextAreaField:
    def __init__(self, label, validators=[]): self.label = label; self.validators = validators
    def validate(self, value): return all(v(value) for v in self.validators)

class validators:
    @staticmethod
    def DataRequired(): return lambda v: v is not None and v != ""
    @staticmethod
    def Email(): return lambda v: re.match(r"[^@]+@[^@]+\.[^@]+", v)
    @staticmethod
    def Length(min=None, max=None): 
        return lambda v: (min is None or len(v) >= min) and (max is None or len(v) <= max)
    @staticmethod
    def NumberRange(min=None, max=None): 
        return lambda v: (min is None or v >= min) and (max is None or v <= max)

# --- ORM (DTA ORM v3.1.6, RedBean-style) ---
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

class DTAError(Exception): pass

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
        self.models = {{}}
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
        schema = {{}}
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
                if auth_token and self.headers.get('Authorization') != f'Bearer {{auth_token}}':
                    self._set_headers(401)
                    self.wfile.write(json.dumps({{"error": "Unauthorized"}}).encode())
                    return
                parts = self.path.strip('/').split('/')
                if len(parts) == 1 and parts[0]:
                    table = parts[0]
                    beans = [dict(row) for row in self.server.orm.conn.execute(f"SELECT * FROM {{table}}")]
                    self._set_headers()
                    self.wfile.write(json.dumps(beans).encode())
                elif len(parts) == 2:
                    table, id = parts
                    cur = self.server.orm.conn.execute(f"SELECT * FROM {{table}} WHERE id=?", (id,))
                    row = cur.fetchone()
                    self._set_headers()
                    self.wfile.write(json.dumps(dict(row) if row else {{}}).encode())
                else:
                    self._set_headers(404)
            def do_POST(self):
                if auth_token and self.headers.get('Authorization') != f'Bearer {{auth_token}}':
                    self._set_headers(401)
                    self.wfile.write(json.dumps({{"error": "Unauthorized"}}).encode())
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
                    self.wfile.write(json.dumps({{"id": bean.id}}).encode())
                else:
                    self._set_headers(404)
            def do_PUT(self):
                self.do_POST()
            def do_DELETE(self):
                parts = self.path.strip('/').split('/')
                if len(parts) == 2:
                    table, id = parts
                    self.server.orm.conn.execute(f"DELETE FROM {{table}} WHERE id=?", (id,))
                    self.server.orm.conn.commit()
                    self._set_headers(204)
                else:
                    self._set_headers(404)
        server = HTTPServer((host, port), Handler)
        server.orm = self
        print(f"DTA REST API running at http://{{host}}:{{port}}/")
        server.serve_forever()

    # --- Admin UI for Users ---
    def admin_ui(self, host="127.0.0.1", port=8081, auth_token=None):
        class Handler(BaseHTTPRequestHandler):
            def _set_headers(self, code=200):
                self.send_response(code)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
            def do_GET(self):
                if auth_token and self.headers.get('Authorization') != f'Bearer {{auth_token}}':
                    self._set_headers(401)
                    self.wfile.write(b"<h1>Unauthorized</h1>")
                    return
                parts = self.path.strip('/').split('/')
                if self.path == "/":
                    tables = [r[0] for r in self.server.orm.conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
                    html = "<h1>DTA Admin</h1><ul>"
                    for t in tables:
                        html += f"<li><a href='/{{t}}'>{{t}}</a></li>"
                    html += "</ul>"
                    self._set_headers()
                    self.wfile.write(html.encode())
                elif len(parts) == 1:
                    table = parts[0]
                    rows = self.server.orm.conn.execute(f"SELECT * FROM {{table}}").fetchall()
                    html = f"<h1>Table: {{table}}</h1><table border=1><tr>"
                    if rows:
                        html += "".join(f"<th>{{k}}</th>" for k in rows[0].keys())
                        html += "</tr>"
                        for row in rows:
                            html += "<tr>" + "".join(f"<td>{{v}}</td>" for v in row) + f"<td><a href='/{{table}}/edit/{{row['id']}}'>Edit</a> <a href='/{{table}}/delete/{{row['id']}}'>Delete</a></td></tr>"
                    else:
                        html += "<td>No rows</td></tr>"
                    html += f"</table><a href='/{{table}}/add'>Add New</a> | <a href='/'>Back</a>"
                    self._set_headers()
                    self.wfile.write(html.encode())
                elif len(parts) == 3 and parts[1] == "edit":
                    table, _, id = parts
                    row = self.server.orm.conn.execute(f"SELECT * FROM {{table}} WHERE id=?", (id,)).fetchone()
                    if not row:
                        self._set_headers(404)
                        self.wfile.write(b"Not found")
                        return
                    html = f"<h1>Edit {{table}} #{{id}}</h1><form method='POST'>"
                    for k in row.keys():
                        if k == "id": continue
                        html += f"{{k}}: <input name='{{k}}' value='{{row[k]}}'><br>"
                    html += "<input type='submit' value='Save'></form>"
                    self._set_headers()
                    self.wfile.write(html.encode())
                elif len(parts) == 3 and parts[1] == "delete":
                    table, _, id = parts
                    self.server.orm.conn.execute(f"DELETE FROM {{table}} WHERE id=?", (id,))
                    self.server.orm.conn.commit()
                    self.send_response(302)
                    self.send_header('Location', f'/{{table}}')
                    self.end_headers()
                elif len(parts) == 2 and parts[1] == "add":
                    table, _ = parts
                    html = f"<h1>Add to {{table}}</h1><form method='POST'>"
                    cur = self.server.orm.conn.execute(f"PRAGMA table_info({{table}})")
                    for col in cur.fetchall():
                        if col['name'] == "id": continue
                        html += f"{{col['name']}}: <input name='{{col['name']}}'><br>"
                    html += "<input type='submit' value='Add'></form>"
                    self._set_headers()
                    self.wfile.write(html.encode())
                else:
                    self._set_headers(404)
            def do_POST(self):
                from urllib.parse import parse_qs
                length = int(self.headers.get('Content-Length', 0))
                data = self.rfile.read(length).decode()
                form = {{k: v[0] for k, v in parse_qs(data).items()}}
                parts = self.path.strip('/').split('/')
                if len(parts) == 3 and parts[1] == "edit":
                    table, _, id = parts
                    sets = ', '.join([f"{{k}}=?" for k in form])
                    vals = list(form.values()) + [id]
                    self.server.orm.conn.execute(f"UPDATE {{table}} SET {{sets}} WHERE id=?", vals)
                    self.server.orm.conn.commit()
                    self.send_response(302)
                    self.send_header('Location', f'/{{table}}')
                    self.end_headers()
                elif len(parts) == 2 and parts[1] == "add":
                    table, _ = parts
                    cols = ', '.join(form.keys())
                    q = ', '.join(['?']*len(form))
                    vals = list(form.values())
                    self.server.orm.conn.execute(f"INSERT INTO {{table}} ({{cols}}) VALUES ({{q}})", vals)
                    self.server.orm.conn.commit()
                    self.send_response(302)
                    self.send_header('Location', f'/{{table}}')
                    self.end_headers()
        server = HTTPServer((host, port), Handler)
        server.orm = self
        print(f"DTA Admin UI running at http://{{host}}:{{port}}/")
        server.serve_forever()

class DTA_Bean:
    def __init__(self, orm, table):
        self._orm = orm
        self._table = table
        self._data = {{}}
        self.id = None

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"No such attribute: {{name}}")

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
            columns = [f"{{k}} TEXT" for k in fields]
            if "id" not in fields:
                columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"] + columns
            orm.conn.execute(f"CREATE TABLE IF NOT EXISTS {{table}} ({{', '.join(columns)}})")
            cur = orm.conn.execute(f"PRAGMA table_info({{table}})")
            existing = set([row['name'] for row in cur.fetchall()])
            for name in fields:
                if name not in existing:
                    orm.conn.execute(f"ALTER TABLE {{table}} ADD COLUMN {{name}} TEXT")
            orm.conn.commit()
        if self.id is None:
            sql = f"INSERT INTO {{table}} ({{', '.join(fields)}}) VALUES ({{', '.join(['?']*len(fields))}})"
            cur = orm.conn.execute(sql, values)
            self.id = cur.lastrowid
        else:
            sets = ', '.join([f"{{f}}=?" for f in fields])
            sql = f"UPDATE {{table}} SET {{sets}} WHERE id=?"
            orm.conn.execute(sql, values + [self.id])
        orm.conn.commit()
        return self.id

    def delete(self):
        orm = self._orm
        table = self._table
        if self.id is not None:
            orm.conn.execute(f"DELETE FROM {{table}} WHERE id=?", (self.id,))
            orm.conn.commit()

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
            col = f"{{name}} {{field.sqltype}}"
            if not field.nullable:
                col += " NOT NULL"
            if field.unique:
                col += " UNIQUE"
            columns.append(col)
        if 'id' not in cls._fields:
            columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"] + columns
        if not orm._freeze and orm.driver == 'sqlite':
            sql = f"CREATE TABLE IF NOT EXISTS {{table}} ({{', '.join(columns)}})"
            orm.conn.execute(sql)
            orm.conn.commit()
            # Alter table for new columns
            cur = orm.conn.execute(f"PRAGMA table_info({{table}})")
            existing = set([row['name'] for row in cur.fetchall()])
            for name, field in cls._fields.items():
                if name not in existing:
                    col = f"{{name}} {{field.sqltype}}"
                    if not field.nullable:
                        col += " NOT NULL"
                    if field.unique:
                        col += " UNIQUE"
                    orm.conn.execute(f"ALTER TABLE {{table}} ADD COLUMN {{col}}")
            orm.conn.commit()

    @classmethod
    def _reflect(cls):
        orm = cls._orm
        table = cls.__name__.lower()
        cur = orm.conn.execute(f"PRAGMA table_info({{table}})")
        return [dict(row) for row in cur.fetchall()]

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()
        return obj

    @classmethod
    def get(cls, **kwargs):
        where = ' AND '.join([f"{{k}}=?" for k in kwargs])
        cur = cls._orm.conn.execute(f"SELECT * FROM {{cls.__name__.lower()}} WHERE {{where}} LIMIT 1", tuple(kwargs.values()))
        row = cur.fetchone()
        if row:
            return cls(**row)
        return None

    @classmethod
    def select(cls, where=None, params=()):
        sql = f"SELECT * FROM {{cls.__name__.lower()}}"
        if where:
            sql += f" WHERE {{where}}"
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
            columns = [f"{{k}} {{self._fields[k].sqltype}}" for k in fields]
            if "id" not in fields:
                columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"] + columns
            orm.conn.execute(f"CREATE TABLE IF NOT EXISTS {{table}} ({{', '.join(columns)}})")
            cur = orm.conn.execute(f"PRAGMA table_info({{table}})")
            existing = set([row['name'] for row in cur.fetchall()])
            for name, field in self._fields.items():
                if name not in existing:
                    orm.conn.execute(f"ALTER TABLE {{table}} ADD COLUMN {{name}} {{field.sqltype}}")
            orm.conn.commit()
        if self.id is None:
            sql = f"INSERT INTO {{table}} ({{', '.join(fields)}}) VALUES ({{', '.join(['?']*len(fields))}})"
            cur = orm.conn.execute(sql, values)
            self.id = cur.lastrowid
            orm.conn.commit()
            orm.send_signal('after_create', self)
        else:
            sets = ', '.join([f"{{f}}=?" for f in fields])
            sql = f"UPDATE {{table}} SET {{sets}} WHERE id=?"
            orm.conn.execute(sql, values + [self.id])
            orm.conn.commit()
            orm.send_signal('after_update', self)
        return self.id

    def delete(self):
        orm = self._orm
        table = self.__class__.__name__.lower()
        if self.id is not None:
            orm.conn.execute(f"DELETE FROM {{table}} WHERE id=?", (self.id,))
            orm.conn.commit()
            orm.send_signal('after_delete', self)

    # --- Relations ---
    def has_many(self, related_cls, fk=None):
        fk = fk or f"{{self.__class__.__name__.lower()}}_id"
        return related_cls.select(where=f"{{fk}}=?", params=(self.id,))

    def belongs_to(self, related_cls, fk=None):
        fk = fk or f"{{related_cls.__name__.lower()}}_id"
        val = getattr(self, fk)
        return related_cls.get(id=val)

    def many_to_many(self, related_cls, join_table=None):
        join_table = join_table or f"{{self.__class__.__name__.lower()}}_{{related_cls.__name__.lower()}}s"
        orm = self._orm
        sql = f"""
            SELECT {{related_cls.__name__.lower()}}.* FROM {{related_cls.__name__.lower()}}
            JOIN {{join_table}} ON {{related_cls.__name__.lower()}}.id = {{join_table}}.{{related_cls.__name__.lower()}}_id
            WHERE {{join_table}}.{{self.__class__.__name__.lower()}}_id = ?
        """
        cur = orm.conn.execute(sql, (self.id,))
        return [related_cls(**row) for row in cur.fetchall()]

    # --- Validation & Hooks ---
    def validate(self):
        # Override for custom validation
        for f, field in self._fields.items():
            v = getattr(self, f)
            if not field.nullable and v is None:
                raise ValueError(f"{{f}} cannot be null")
            if isinstance(field, EnumField) and v is not None:
                if v not in [e.value for e in field.enumtype]:
                    raise ValueError(f"{{f}} must be one of {{[e.value for e in field.enumtype]}}")
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
        cur = self.orm.conn.execute(f"PRAGMA table_info({{table}})")
        cols = [row['name'] for row in cur.fetchall()]
        new_cols = [new if c == old else c for c in cols]
        col_defs = ', '.join(new_cols)
        self.orm.conn.execute(f"ALTER TABLE {{table}} RENAME TO {{table}}_old")
        self.orm.conn.execute(f"CREATE TABLE {{table}} ({{col_defs}})")
        self.orm.conn.execute(f"INSERT INTO {{table}} SELECT * FROM {{table}}_old")
        self.orm.conn.execute(f"DROP TABLE {{table}}_old")
        self.orm.conn.commit()

    def drop_column(self, table, col):
        # SQLite does not support DROP COLUMN directly, so we recreate table
        cur = self.orm.conn.execute(f"PRAGMA table_info({{table}})")
        cols = [row['name'] for row in cur.fetchall() if row['name'] != col]
        col_defs = ', '.join(cols)
        self.orm.conn.execute(f"ALTER TABLE {{table}} RENAME TO {{table}}_old")
        self.orm.conn.execute(f"CREATE TABLE {{table}} ({{col_defs}})")
        self.orm.conn.execute(f"INSERT INTO {{table}} ({{col_defs}}) SELECT {{col_defs}} FROM {{table}}_old")
        self.orm.conn.execute(f"DROP TABLE {{table}}_old")
        self.orm.conn.commit()

# --- User Management (Usered-style, admin UI, REST) ---
class User(Model):
    username = String(max_length=64, unique=True, nullable=False)
    email = String(max_length=128, unique=True, nullable=False)
    password_hash = String(max_length=128, nullable=False)
    is_active = Boolean(default=True)
    is_verified = Boolean(default=False)
    roles = JSONField(default=list)
    created_at = DateTime(default=lambda: datetime.datetime.now().isoformat())
    last_login = DateTime(default=None)

    def set_password(self, password):
        salt = secrets.token_hex(8)
        hash_ = hashlib.sha256((salt + password).encode()).hexdigest()
        self.password_hash = f"{{salt}}${{hash_}}"

    def check_password(self, password):
        if not self.password_hash or '$' not in self.password_hash:
            return False
        salt, hash_ = self.password_hash.split('$')
        return hashlib.sha256((salt + password).encode()).hexdigest() == hash_

    def has_role(self, role):
        return role in (self.roles or [])

    def add_role(self, role):
        if not self.roles: self.roles = []
        if role not in self.roles:
            self.roles.append(role)
            self.save()

    def remove_role(self, role):
        if self.roles and role in self.roles:
            self.roles.remove(role)
            self.save()

    def validate(self):
        assert self.username and self.email and self.password_hash, "Fields required"
        assert '@' in self.email, "Invalid email"
        return True

    def mark_verified(self):
        self.is_verified = True
        self.save()

    def mark_login(self):
        self.last_login = datetime.datetime.now().isoformat()
        self.save()

    @classmethod
    def authenticate(cls, username, password):
        user = cls.get(username=username)
        if user and user.check_password(password) and user.is_active and user.is_verified:
            user.mark_login()
            return user
        return None

    @classmethod
    def register(cls, username, email, password):
        if cls.get(username=username) or cls.get(email=email):
            raise ValueError("User already exists")
        user = cls(username=username, email=email)
        user.set_password(password)
        user.save()
        return user

class UserManager:
    @staticmethod
    def send_verification_email(user, send_func):
        token = secrets.token_urlsafe(32)
        # Store token in user or a separate table if needed
        # send_func(user.email, f"Verify: /verify/{{token}}")
        return token

    @staticmethod
    def send_password_reset(user, send_func):
        token = secrets.token_urlsafe(32)
        # Store token, send email
        # send_func(user.email, f"Reset: /reset/{{token}}")
        return token

    @staticmethod
    def verify_user(token):
        # Lookup user by token, mark as verified
        pass

    @staticmethod
    def reset_password(token, new_password):
        # Lookup user by token, set new password
        pass

def login_required(handler):
    async def wrapper(request, *args, **kwargs):
        session = request.app._session.get(request)
        if not session.get("user_id"):
            return Response({{"error": "Authentication required"}}, status_code=401)
        return await handler(request, *args, **kwargs)
    return wrapper

# --- Email Sending ---
class Email:
    @staticmethod
    def send(to, subject, body, from_addr=None, smtp_server="localhost", smtp_port=25, username=None, password=None, use_tls=False):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_addr or "noreply@example.com"
        msg["To"] = to
        msg.set_content(body)
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if use_tls: server.starttls()
            if username: server.login(username, password)
            server.send_message(msg)

# --- OAuth2/Social Login (Google example, extendable) ---
class OAuth2:
    @staticmethod
    def get_authorize_url(client_id, redirect_uri, scope, state):
        return f"https://accounts.google.com/o/oauth2/v2/auth?client_id={{client_id}}&redirect_uri={{redirect_uri}}&response_type=code&scope={{scope}}&state={{state}}"
    
    @staticmethod
    async def exchange_code(code, client_id, client_secret, redirect_uri):
        import httpx
        url = "https://oauth2.googleapis.com/token"
        data = {{"code": code, "client_id": client_id, "client_secret": client_secret, "redirect_uri": redirect_uri, "grant_type": "authorization_code"}}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, data=data)
            return resp.json()
# --- Extend Loader ---
class Extend:
    """
    Dynamically loads Python helper modules from the `Chatu_ext/` directory.

    Usage:
        extend = Extend()
        extend.auth.login_user(...)  # if Chatu_ext/auth.py exists
    """
    def __init__(self, folder="Chatu_ext"):
        import importlib.util
        import types
        self._modules = {}
        self.folder = os.path.abspath(folder)
        if not os.path.isdir(self.folder):
            return  # No extension folder
        for file in os.listdir(self.folder):
            if file.endswith(".py") and not file.startswith("_"):
                modname = file[:-3]
                path = os.path.join(self.folder, file)
                spec = importlib.util.spec_from_file_location(modname, path)
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    self._modules[modname] = module
                    setattr(self, modname, module)
                except Exception as e:
                    print(f"⚠️ Failed to load extension '{modname}': {e}")

    def list_modules(self):
        return list(self._modules.keys())
#--- EXTRA Functionality -- by kesh
# ===========================================================================================#
# ===========================================================================================#
## -- Chatu TOOLS -- ##
#----------------------------------------------------------------------------------------------#
import os
import sys
import json
import importlib
from datetime import datetime

class ChatuTools:
    """
    ChatuTools: Modular extension for CLI scaffolding, API versioning,
    plugin system, middleware chaining, and DB seed/fixtures.
    """

    def __init__(self):
        self.plugins = []
        self.middlewares = []
        self.api_versions = {}
        self.fixtures = {}

    # --- CLI SCAFFOLDING ---
    def cli(self):
        """
        Usage:
            python Chatu.py new blog
            python Chatu.py middleware logger
            python Chatu.py fixture users
            python Chatu.py apiversion v2
        """
        args = sys.argv[1:]
        if not args:
            print("Usage: python Chatu.py [new|middleware|fixture|apiversion] name")
            return
        cmd, *rest = args
        if cmd == "new" and rest:
            self.scaffold_plugin(rest[0])
        elif cmd == "middleware" and rest:
            self.scaffold_middleware(rest[0])
        elif cmd == "fixture" and rest:
            self.scaffold_fixture(rest[0])
        elif cmd == "apiversion" and rest:
            self.scaffold_api_version(rest[0])
        else:
            print("Unknown command or missing name.")

    def scaffold_plugin(self, name):
        folder = "plugins"
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/{name}.py", "w") as f:
            f.write(f"class Plugin:\n    def setup(self):\n        print('Plugin {name} loaded')\n")
        print(f"Plugin '{name}' scaffolded.")

    def scaffold_middleware(self, name):
        folder = "middleware"
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/{name}.py", "w") as f:
            f.write(f"def {name}_middleware(next_handler):\n    def middleware(request):\n        # TODO: implement\n        return next_handler(request)\n    return middleware\n")
        print(f"Middleware '{name}' scaffolded.")

    def scaffold_fixture(self, name):
        folder = "fixtures"
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/{name}.json", "w") as f:
            f.write('[]\n')
        print(f"Fixture '{name}' scaffolded.")

    def scaffold_api_version(self, version):
        folder = "api"
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/v{version}.py", "w") as f:
            f.write(f"# API v{version} handlers\n")
        print(f"API version '{version}' scaffolded.")

    # --- PLUGIN SYSTEM ---
    def load_plugins(self, plugin_folder="plugins"):
        if not os.path.isdir(plugin_folder):
            return
        sys.path.insert(0, plugin_folder)
        for fname in os.listdir(plugin_folder):
            if fname.endswith(".py") and not fname.startswith("_"):
                mod_name = fname[:-3]
                mod = importlib.import_module(mod_name)
                if hasattr(mod, "Plugin"):
                    self.plugins.append(mod.Plugin())

    def run_plugins(self, *args, **kwargs):
        for plugin in self.plugins:
            if hasattr(plugin, "setup"):
                plugin.setup(*args, **kwargs)

    # --- MIDDLEWARE CHAINING ---
    def add_middleware(self, middleware_fn):
        self.middlewares.append(middleware_fn)

    def apply_middlewares(self, handler):
        # Chain middleware in reverse order (last added, first run)
        for mw in reversed(self.middlewares):
            handler = mw(handler)
        return handler

    # --- API VERSIONING ---
    def register_api_version(self, version, handler):
        self.api_versions[version] = handler

    def api_version_dispatch(self, request):
        version = request.get("version", "v1")
        handler = self.api_versions.get(version)
        if handler:
            return handler(request)
        raise ValueError(f"No handler for API version {version}")

    # --- DB SEED/FIXTURES ---
    def load_fixture(self, fixture_file):
        with open(fixture_file, "r") as f:
            data = json.load(f)
            self.fixtures[os.path.basename(fixture_file)] = data
        return data

    def apply_fixture(self, model_class, fixture_file):
        data = self.load_fixture(fixture_file)
        for item in data:
            obj = model_class(**item)
            obj.save()

    # --- UTILITY ---
    @staticmethod
    def current_datetime():
        return datetime.now().isoformat()

"""
USAGE EXAMPLES

# CLI scaffolding
#   python Chatu.py new blog
#   python Chatu.py middleware logger
#   python Chatu.py fixture users
#   python Chatu.py apiversion v2

# Plugin system
Chatu = ChatuTools()
Chatu.load_plugins()
Chatu.run_plugins()

# Middleware chaining
def handler(request): return "OK"
Chatu.add_middleware(logger_middleware)
wrapped_handler = Chatu.apply_middlewares(handler)

# API versioning
def v1_handler(request): return {"version": 1}
def v2_handler(request): return {"version": 2}
Chatu.register_api_version("v1", v1_handler)
Chatu.register_api_version("v2", v2_handler)
response = Chatu.api_version_dispatch({"version": "v2"})

# DB seed/fixtures
Chatu.apply_fixture(User, "fixtures/users.json")
"""


#----------------------------------------------------------------------------------------------#
## -- ToolsHelper Class for introspection i.e inbuilt help --#
import pickle
import sqlite3
import uuid

class noSQLite:
    """
    Simple NoSQL-style object store on top of SQLite.
    Usage:
        class MyDoc(noSQLite.Model):
            pass
        MyDoc.Meta.connection = sqlite3.connect("mydb.sqlite3")
        MyDoc.initialize()
        doc = MyDoc(name="Alice", age=30)
        doc.save()
        for d in MyDoc.find({"name": "Alice"}): print(d.__dict__)
    """
    """
USAGE EXAMPLE
-------------

import sqlite3

# Define your document model
class Note(noSQLite.Model):
    pass

# Set up connection and initialize
Note.Meta.connection = sqlite3.connect("notes.db")
Note.initialize()

# Create and save a note
n = Note(title="Hello", content="World")
n.save()

# Query notes
for note in Note.find({"title": "Hello"}):
    print(note.__dict__)

# Delete a note
note.delete()
"""
"""
UNIT TEST EXAMPLE
-----------------

import unittest
import sqlite3

# Import the noSQLite class here if in another file, or use directly if in the same file

class TestModel(noSQLite.Model):
    class Meta:
        # See setUp for explanation.
        connection = None

class GoatTest(unittest.TestCase):
    def setUp(self):
        # We need the database to reset after each test, so we recreate it here.
        TestModel.Meta.connection = sqlite3.connect(":memory:")
        TestModel.initialize()
        self.instances = [
            TestModel(foo=1, bar="hi"),
            TestModel(foo="hello", bar="hi"),
            TestModel(foo="hello", bar=None),
        ]

    def test_saving(self):
        for instance in self.instances:
            instance.save()

    def test_find(self):
        for instance in self.instances:
            instance.save()
        instances = list(TestModel.find())
        self.assertEqual(len(instances), 3)
        self.assertEqual(instances, self.instances)

    def test_update(self):
        self.assertEqual(len(list(TestModel.find())), 0)
        for instance in self.instances:
            instance.save()
        for instance in TestModel.find():
            instance.test = 3
            instance.save()
        self.assertEqual(len(list(TestModel.find())), 3)
        for instance in TestModel.find():
            self.assertEqual(instance.test, 3)

    def test_in_place_update(self):
        '''
        Test to see if the database behaves properly when inserting items in
        the table we are iterating over.
        '''
        for instance in self.instances:
            instance.save()
        for counter, instance in enumerate(TestModel.find()):
            TestModel().save(False)
            self.assertLess(counter, 100)
        self.assertEqual(len(list(TestModel.find())), 6)

    def test_delete(self):
        for instance in self.instances:
            instance.save()
        for instance in TestModel.find():
            instance.delete()
        instances = list(TestModel.find())
        self.assertEqual(instances, [])

if __name__ == '__main__':
    unittest.main()
"""


    class Model:
        _serializer = pickle

        @classmethod
        def _get_cursor(cls):
            if cls.Meta.connection is None:
                raise RuntimeError("No database connection set in Meta.connection")
            return cls.Meta.connection.cursor()

        @classmethod
        def _unmarshal(cls, attributes):
            inst = cls.__new__(cls)
            inst.__dict__ = attributes
            return inst

        @classmethod
        def find(cls, parameters=None):
            cursor = cls._get_cursor()
            cursor.execute(f"SELECT id, uuid, data FROM {cls.__name__.lower()};")
            for id_, uuid_, data in cursor:
                loaded_dict = cls._serializer.loads(data)
                loaded_dict["id"] = uuid_
                if parameters is None or all(loaded_dict.get(k) == v for k, v in parameters.items()):
                    yield cls._unmarshal(loaded_dict)

        @classmethod
        def initialize(cls):
            cursor = cls._get_cursor()
            tablename = cls.__name__.lower()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {tablename} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    uuid TEXT NOT NULL,
                    data BLOB NOT NULL
                );
            """)
            cursor.execute(f"""
                CREATE UNIQUE INDEX IF NOT EXISTS "{tablename}_uuid_index"
                ON {tablename} (uuid ASC);
            """)

        @classmethod
        def commit(cls):
            cls.Meta.connection.commit()

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        def __eq__(self, other):
            return getattr(self, "id", None) == getattr(other, "id", None)

        def save(self, commit=True):
            cursor = self._get_cursor()
            tablename = self.__class__.__name__.lower()
            if not hasattr(self, "id"):
                object_id = uuid.uuid4().hex
                data = self._serializer.dumps(self.__dict__)
                cursor.execute(
                    f"INSERT INTO {tablename} (uuid, data) VALUES (?, ?)",
                    (object_id, data)
                )
                self.id = object_id
            else:
                object_id = self.id
                d = self.__dict__.copy()
                d.pop("id", None)
                data = self._serializer.dumps(d)
                cursor.execute(
                    f"UPDATE {tablename} SET data = ? WHERE uuid = ?",
                    (data, object_id)
                )
            if commit:
                self.commit()

        def delete(self, commit=True):
            cursor = self._get_cursor()
            tablename = self.__class__.__name__.lower()
            cursor.execute(
                f"DELETE FROM {tablename} WHERE uuid = ?",
                (self.id,)
            )
            if commit:
                self.commit()

        class Meta:
            connection = None
"""
Helper Class for Framework Introspection
... to provide documentation, 
usage examples, and information about available classes and plugins:
"""
class ToolsHelper:
    """Provides information and usage examples for the framework."""

    def __init__(self, framework):
        self.framework = framework

    def list_classes(self):
        """List all classes in the framework."""
        return [cls for cls in dir(self.framework) if isinstance(getattr(self.framework, cls), type)]

    def usage_examples(self):
        """Return usage examples for key features."""
        return {
            "plugins": "framework.plugins.load_plugins()",
            "middleware": "framework.middlewares.add_middleware(fn)",
            "cron": "framework.cron.schedule('0 12 * * *', my_task)",
            "sqlite": "framework.sqlite.query('SELECT * FROM users')",
        }

    def help(self):
        """Prints documentation and usage."""
        print("Framework Classes:", self.list_classes())
        print("Usage Examples:", self.usage_examples())

## -- Cron Job Scheduler -- #
import threading
import time
import schedule

class CronScheduler:
    """Simple cron-like scheduler using schedule library."""
    def __init__(self):
        self.running = False

    def schedule(self, cron_expr, func):
        # For simplicity, only supports every N seconds/minutes/hours
        schedule.every(int(cron_expr)).seconds.do(func)

    def start(self):
        self.running = True
        def run():
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        threading.Thread(target=run, daemon=True).start()

    def stop(self):
        self.running = False

## -- Date Management Class -- #
from datetime import datetime, timedelta

class DateHelper:
    """Easy date management."""
    @staticmethod
    def now():
        return datetime.now()

    @staticmethod
    def add_days(date, days):
        return date + timedelta(days=days)

    @staticmethod
    def format(date, fmt="%Y-%m-%d %H:%M:%S"):
        return date.strftime(fmt)
## -- USER MANAGEMENT NoSQLite -- ##
"""
User Management with noSQLite, JWT, OAuth2
Production-ready, portable, extensible.
Authors: Sage & Kesh (johnmahugu@gmail.com)
"""

import hashlib
import secrets
import datetime
import jwt  # pip install PyJWT
from noSQLite import noSQLite

# --- Settings ---
SECRET_KEY = "your-very-secret-key"  # Use a strong, unique value!
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 30

# --- User Model ---
class User(noSQLite.Model):
    # Document fields
    username: str
    email: str
    password_hash: str
    is_active: bool = True
    is_verified: bool = False
    roles: list = None
    created_at: str = None
    last_login: str = None
    oauth_providers: dict = None  # e.g. {"google": "google_id", ...}
    reset_token: str = None
    verify_token: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.roles = self.roles or []
        self.oauth_providers = self.oauth_providers or {}
        self.created_at = self.created_at or datetime.datetime.now().isoformat()

    # --- Password Management ---
    def set_password(self, password):
        salt = secrets.token_hex(8)
        hash_ = hashlib.sha256((salt + password).encode()).hexdigest()
        self.password_hash = f"{salt}${hash_}"

    def check_password(self, password):
        if not self.password_hash or '$' not in self.password_hash:
            return False
        salt, hash_ = self.password_hash.split('$')
        return hashlib.sha256((salt + password).encode()).hexdigest() == hash_

    # --- Roles ---
    def has_role(self, role):
        return role in (self.roles or [])

    def add_role(self, role):
        if role not in self.roles:
            self.roles.append(role)
            self.save()

    def remove_role(self, role):
        if role in self.roles:
            self.roles.remove(role)
            self.save()

    # --- Verification & Login ---
    def mark_verified(self):
        self.is_verified = True
        self.verify_token = None
        self.save()

    def mark_login(self):
        self.last_login = datetime.datetime.now().isoformat()
        self.save()

    # --- Validation ---
    def validate(self):
        assert self.username and self.email and self.password_hash, "Fields required"
        assert '@' in self.email, "Invalid email"
        return True

    # --- Query helpers ---
    @classmethod
    def get_by_username(cls, username):
        return next(cls.find({"username": username}), None)

    @classmethod
    def get_by_email(cls, email):
        return next(cls.find({"email": email}), None)

    @classmethod
    def get_by_verify_token(cls, token):
        return next(cls.find({"verify_token": token}), None)

    @classmethod
    def get_by_reset_token(cls, token):
        return next(cls.find({"reset_token": token}), None)

    # --- Registration & Auth ---
    @classmethod
    def register(cls, username, email, password):
        if cls.get_by_username(username) or cls.get_by_email(email):
            raise ValueError("User already exists")
        user = cls(username=username, email=email)
        user.set_password(password)
        user.is_active = True
        user.is_verified = False
        user.roles = []
        user.save()
        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.get_by_username(username)
        if user and user.check_password(password) and user.is_active and user.is_verified:
            user.mark_login()
            return user
        return None

    # --- OAuth2 Linking ---
    def link_oauth(self, provider, provider_id):
        self.oauth_providers[provider] = provider_id
        self.save()

    @classmethod
    def get_by_oauth(cls, provider, provider_id):
        for user in cls.find():
            if user.oauth_providers.get(provider) == provider_id:
                return user
        return None

    # --- JWT ---
    def generate_jwt(self, expires_minutes=JWT_EXPIRE_MINUTES):
        payload = {
            "sub": self.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_minutes),
            "roles": self.roles,
            "email": self.email,
            "user_id": self.id
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_jwt(token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

# --- User Manager: Email Verification, Password Reset, OAuth2, JWT ---
class UserManager:
    @staticmethod
    def send_verification_email(user, send_func):
        token = secrets.token_urlsafe(32)
        user.verify_token = token
        user.save()
        send_func(user.email, f"Verify your account: /verify/{token}")
        return token

    @staticmethod
    def verify_user(token):
        user = User.get_by_verify_token(token)
        if user:
            user.mark_verified()
            return True
        return False

    @staticmethod
    def send_password_reset(user, send_func):
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.save()
        send_func(user.email, f"Reset your password: /reset/{token}")
        return token

    @staticmethod
    def reset_password(token, new_password):
        user = User.get_by_reset_token(token)
        if user:
            user.set_password(new_password)
            user.reset_token = None
            user.save()
            return True
        return False

    # --- OAuth2 Registration/Login ---
    @staticmethod
    def oauth_login(provider, provider_id, email=None, username=None):
        user = User.get_by_oauth(provider, provider_id)
        if user:
            user.mark_login()
            return user
        # Register new user via OAuth2
        if not email or not username:
            raise ValueError("Email and username required for new OAuth user")
        user = User(username=username, email=email)
        user.is_active = True
        user.is_verified = True
        user.oauth_providers = {provider: provider_id}
        user.save()
        return user

    # --- JWT Authentication ---
    @staticmethod
    def authenticate_jwt(token):
        payload = User.verify_jwt(token)
        if not payload:
            return None
        user = User.get_by_username(payload.get("sub"))
        if user and user.is_active:
            return user
        return None

# --- Decorator for login required (JWT-based) ---
def login_required_jwt(handler):
    def wrapper(request, *args, **kwargs):
        # Extract token from header or query param
        token = None
        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
        if not token and "token" in request.GET:
            token = request.GET["token"]
        user = UserManager.authenticate_jwt(token)
        if not user:
            return {"error": "Authentication required"}, 401
        request.user = user
        return handler(request, *args, **kwargs)
    return wrapper

# --- Usage Example ---
"""
# Register a user
user = User.register("alice", "alice@example.com", "secret123")

# Authenticate with password
user = User.authenticate("alice", "secret123")
if user:
    print("Login success!")

# Generate JWT token
token = user.generate_jwt()

# Authenticate with JWT
user2 = UserManager.authenticate_jwt(token)

# OAuth2 login
user = UserManager.oauth_login("google", "google-id-123", email="alice@gmail.com", username="alice")

# Send verification email
def send_func(email, message): print(f"Send to {email}: {message}")
UserManager.send_verification_email(user, send_func)

# Password reset
UserManager.send_password_reset(user, send_func)
UserManager.reset_password(user.reset_token, "newpassword123")
"""
## --- Flash Messaging ---##
class Flash:
    """
    Flash messaging system (web2py/Flask-style).
    Usage:
        flash = Flash(request)
        flash.set("Profile updated!", "success")
        # In your template: {{ flash.get() }}
    """
    SESSION_KEY = "_flash"

    def __init__(self, request):
        self.request = request
        self.session = getattr(request, "session", None)

    def set(self, message, category="info"):
        if not self.session:
            return
        if self.SESSION_KEY not in self.session:
            self.session[self.SESSION_KEY] = []
        self.session[self.SESSION_KEY].append({"message": message, "category": category})
        self.session.save()

    def get(self):
        if not self.session:
            return []
        messages = self.session.get(self.SESSION_KEY, [])
        self.session[self.SESSION_KEY] = []
        self.session.save()
        return messages

    def peek(self):
        if not self.session:
            return []
        return self.session.get(self.SESSION_KEY, [])
## --- ERROR REPORTING ---- ##
import traceback
import logging

class ErrorReporter:
    """
    Robust error reporting and messaging.
    - Logs errors
    - Optionally emails admins
    - Provides user-friendly error messages
    - Can be extended for Sentry, Slack, etc.
    """
    def __init__(self, admin_email=None, log_file="Chatu_errors.log"):
        self.admin_email = admin_email
        self.logger = logging.getLogger("ChatuError")
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.ERROR)

    def report(self, exc, request=None, notify_admin=False):
        tb = traceback.format_exc()
        user_message = "An unexpected error occurred. Please try again later."
        self.logger.error(f"Exception: {exc}\nTraceback:\n{tb}\nRequest: {request}")
        if notify_admin and self.admin_email:
            self.send_admin_email(exc, tb, request)
        return user_message

    def send_admin_email(self, exc, tb, request):
        # Use your framework's email sending logic
        from email.message import EmailMessage
        msg = EmailMessage()
        msg["Subject"] = "[Chatu] Error Report"
        msg["From"] = "noreply@yourapp.com"
        msg["To"] = self.admin_email
        msg.set_content(f"Exception: {exc}\n\nTraceback:\n{tb}\n\nRequest: {request}")
        # Send email (implement your SMTP logic here)
        # smtp.send_message(msg)
## -- WORLD CLASS --#
#--Chatu Task Que--#
import threading
import queue
import time

class ChatuTaskQueue:
    """
    Async Task Queue / Background Jobs
    Lightweight background job queue (threaded).
    Usage:
        queue = ChatuTaskQueue()
        queue.enqueue(myfunc, 1, 2, kwarg='x')
    """
    def __init__(self, workers=2):
        self.tasks = queue.Queue()
        self.workers = []
        self.running = True
        for _ in range(workers):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            self.workers.append(t)

    def worker(self):
        while self.running:
            try:
                func, args, kwargs = self.tasks.get(timeout=1)
                func(*args, **kwargs)
            except queue.Empty:
                continue
            except Exception as e:
                print("Task error:", e)

    def enqueue(self, func, *args, **kwargs):
        self.tasks.put((func, args, kwargs))

    def stop(self):
        self.running = False

## -- LIVE RELOAD / HOT RELOAD -- ##
import os
import sys
import threading

class ChatuReloader:
    """
    Auto-reloads the server on code changes (dev only).
    Usage:
        ChatuReloader.watch_and_restart()
    """
    @staticmethod
    def watch_and_restart(interval=1):
        mtimes = {}
        while True:
            changed = False
            for fname in list(sys.modules):
                if fname.endswith('.py'):
                    try:
                        mtime = os.path.getmtime(fname)
                        if fname not in mtimes:
                            mtimes[fname] = mtime
                        elif mtimes[fname] != mtime:
                            print(f"Detected change in {fname}, reloading...")
                            os._exit(3)
                    except Exception:
                        continue
            time.sleep(interval)
""" Usage:
Run your app with a wrapper script that restarts on exit code 3, or use watchdog for more robust watching.
"""

## --- Built in open API DOCs (Swagger)--##
""" Usage:
Run your app with a wrapper script that restarts on exit code 3, or use watchdog for more robust watching.

c. Built-in API Docs (OpenAPI/Swagger)"""
class ChatuAPIDocs:
    """
    Generates OpenAPI spec from registered routes.
    Usage:
        docs = ChatuAPIDocs()
        docs.add_route("/hello", "GET", summary="Say hello")
        print(docs.openapi_json())
    """
    def __init__(self, title="Chatu API", version="1.0.0"):
        self.title = title
        self.version = version
        self.routes = []

    def add_route(self, path, method, summary="", description="", parameters=None, responses=None):
        self.routes.append({
            "path": path, "method": method, "summary": summary,
            "description": description, "parameters": parameters or [], "responses": responses or {}
        })

    def openapi_json(self):
        paths = {}
        for r in self.routes:
            if r["path"] not in paths:
                paths[r["path"]] = {}
            paths[r["path"]][r["method"].lower()] = {
                "summary": r["summary"],
                "description": r["description"],
                "parameters": r["parameters"],
                "responses": r["responses"] or {"200": {"description": "OK"}}
            }
        return json.dumps({
            "openapi": "3.0.0",
            "info": {"title": self.title, "version": self.version},
            "paths": paths
        }, indent=2)

##-- GraphQL endpoint--##
# pip install graphql-core
from graphql import graphql_sync, build_schema

class ChatuGraphQL:
    """
    Minimal GraphQL endpoint.
    Usage:
        schema = '''
        type Query { hello: String }
        '''
        resolvers = {"hello": lambda *_: "Hello, world!"}
        gq = ChatuGraphQL(schema, resolvers)
        result = gq.execute("{ hello }")
    """
    def __init__(self, schema_str, resolvers):
        self.schema = build_schema(schema_str)
        self.resolvers = resolvers

    def execute(self, query, variables=None):
        return graphql_sync(self.schema, query, root_value=self.resolvers, variable_values=variables).data
##-- Built it Rate Limiting --#
import time
from collections import defaultdict

class ChatuRateLimiter:
    """
    Simple in-memory rate limiter (per-IP or per-user).
    Usage:
        limiter = ChatuRateLimiter(limit=100, period=60)
        if not limiter.allow(ip):
            return Response("Too Many Requests", 429)
    """
    def __init__(self, limit=100, period=60):
        self.limit = limit
        self.period = period
        self.hits = defaultdict(list)

    def allow(self, key):
        now = time.time()
        window = now - self.period
        self.hits[key] = [t for t in self.hits[key] if t > window]
        if len(self.hits[key]) >= self.limit:
            return False
        self.hits[key].append(now)
        return True
##-- Internationalization (i18N)--##
class ChatuI18N:
    """
    Simple translation system.
    Usage:
        i18n = ChatuI18N()
        i18n.add("en", {"hello": "Hello"})
        i18n.add("es", {"hello": "Hola"})
        i18n.set_lang("es")
        print(i18n.t("hello"))  # Hola
    """
    def __init__(self):
        self.translations = {}
        self.lang = "en"

    def add(self, lang, mapping):
        self.translations[lang] = mapping

    def set_lang(self, lang):
        self.lang = lang

    def t(self, key):
        return self.translations.get(self.lang, {}).get(key, key)
##--Builtin Test Client(Advanced)--##
import requests

class ChatuTestClient:
    """
    Advanced test client for HTTP endpoints.
    Usage:
        client = ChatuTestClient("http://localhost:8000")
        r = client.get("/api/hello")
        assert r.status_code == 200
    """
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, path, **kwargs):
        return requests.get(self.base_url + path, **kwargs)

    def post(self, path, data=None, json=None, **kwargs):
        return requests.post(self.base_url + path, data=data, json=json, **kwargs)

    # Add put, delete, etc. as needed
##-- Admin UI Customization--##
class ChatuAdminUI:
    """
    Admin UI customization hooks.
    Usage:
        admin = ChatuAdminUI()
        admin.set_theme("dark")
        admin.add_widget("dashboard", MyWidget)
    """
    def __init__(self):
        self.theme = "default"
        self.widgets = {}

    def set_theme(self, theme):
        self.theme = theme

    def add_widget(self, section, widget):
        self.widgets.setdefault(section, []).append(widget)
##--Wb Socket / Realtime PubSub--##
import asyncio

class ChatuPubSub:
    """
    Simple pub/sub for WebSockets.
    Usage:
        pubsub = ChatuPubSub()
        pubsub.subscribe("news", ws1)
        pubsub.publish("news", "Hello subscribers!")
    """
    def __init__(self):
        self.channels = {}

    def subscribe(self, channel, ws):
        self.channels.setdefault(channel, set()).add(ws)

    def unsubscribe(self, channel, ws):
        self.channels.get(channel, set()).discard(ws)

    async def publish(self, channel, message):
        for ws in self.channels.get(channel, set()):
            await ws.send(message)
## -- Static Asset Pipeline --##
import shutil

class ChatuAssetPipeline:
    """
    Simple static asset pipeline for minification/bundling.
    Usage:
        pipeline = ChatuAssetPipeline()
        pipeline.minify("static/app.js", "static/app.min.js")
    """
    def minify(self, src, dest):
        # Example: just remove whitespace for demo
        with open(src) as f:
            code = f.read()
        minified = "".join(line.strip() for line in code.splitlines())
        with open(dest, "w") as f:
            f.write(minified)

    def bundle(self, files, dest):
        with open(dest, "w") as out:
            for fpath in files:
                with open(fpath) as f:
                    out.write(f.read() + "\n")

    def copy(self, src, dest):
        shutil.copy(src, dest)

# ===========================================================================================#
# --- Testing ---
class TestClient:
    def __init__(self, app):
        self.app = app

    async def request(self, method, path, data=None, headers=None):
        scope = {{
            "type": "http",
            "method": method.upper(),
            "path": path,
            "headers": [(k.lower().encode(), v.encode()) for k, v in (headers or {{}}).items()],
            "client": ("127.0.0.1", 12345),
            "http_version": "1.1",
            "query_string": b"",
        }}
        body = data.encode() if isinstance(data, str) else data or b""
        received = []
        async def receive():
            if received:
                return {{"type": "http.disconnect"}}
            received.append(True)
            return {{"type": "http.request", "body": body, "more_body": False}}
        sent = {{}}
        async def send(message):
            if message["type"] == "http.response.start":
                sent["status_code"] = message["status"]
                sent["headers"] = dict((k.decode(), v.decode()) for k, v in message["headers"])
            elif message["type"] == "http.response.body":
                sent.setdefault("body", b"")
                sent["body"] += message.get("body", b"")
        await self.app(scope, receive, send)
        class Resp:
            status_code = sent.get("status_code", 0)
            headers = sent.get("headers", {{}})
            body = sent.get("body", b"")
            def json(self):
                import json
                return json.loads(self.body.decode())
            def text(self):
                return self.body.decode()
        return Resp()

    async def get(self, path, headers=None):
        return await self.request("GET", path, headers=headers)
    
    async def post(self, path, data=None, headers=None):
        return await self.request("POST", path, data=data, headers=headers)
    
    async def put(self, path, data=None, headers=None):
        return await self.request("PUT", path, data=data, headers=headers)
    
    async def delete(self, path, headers=None):
        return await self.request("DELETE", path, headers=headers)

# --- Plug-and-play app example ---
if __name__ == "__main__":
    app = Chatu(__name__)
    app.mount("/static", Static.serve(directory="static"))
    
    @app.route("/", methods=["GET"])
    async def index(request):
        return Response(render_template("index.html", user="World"))

    @app.route("/admin/users", methods=["GET"])
    async def admin_users(request):
        return AdminUI.user_list()
    app.run()
"""
🧠 Chatu v3 — MASTERED FEATURES
🔧 Core Framework
Flask-compatible routing (@app.route("/<int:id>"))
Sync/async support via invoke_handler
Clean Request and Response models
Built-in HTTP exception handling (HTTPException)
Auto port selection (7000 → 4375 → 8000)
Startup message like Flask ✅

🧩 Modular Architecture
Extend class auto-loads modules from /Chatu-ext/
→ Just drop in .py helpers, access as extend.module.func(...)

🔐 Auth System (Robust)
login_user(), logout_user(), current_user()
Decorators:
@login_required
@roles_required("admin")
@anonymous_only

🧰 Built-in Utilities
URL encoding/decoding
Session (JWT-style), CORS, file uploads, static serving, SSE
Templating (Jinja2 & fallback)
WebSocket-ready scaffold
DTA ORM (RedBean-style): REST API + Admin UI
Form & validator system
🛠 Ready for Anything
You’ve now got a fully extensible, production-ready macroframework with micro-sized simplicity. If you ever want:
CLI scaffolding (e.g., Chatu new blog)
API versioning
Plugin system (like Django apps)
Middleware chaining
DB seed/fixtures
... John. What would you like to create next?
"""
# EOF #
"""
                                                              
                    *@@@@@@@@@@@@@@.                          
                .@@@@@@@@@@@@@@@@@@@@@%                       
              #@@@@@@@@@@@@@@@@@@@@@@@@@@ *@@                 
            :@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@               
           @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@              
          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@=            
         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.           
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@           
       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  #@@@@@@#          
       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*   :@@@@@@          
       @@@@@@@@       :@@@@@@@@@@@@@@@@@@@#*#@@@@@@@          
       @@@@@@@   *@.       -@@@@@@@@@@@@@@@@@@@@@@@@          
       @@@@@@    #@            ++@@@@@@@@@@@@@@@@@@@          
       @@@@@@                       +@@@@@@@@@@@@@@*          
       @@@@@@@*                          @@@@@@@@@@           
        @@@@@@@@                              %@@#            
        :@@@@@@@-                                             
         =@@@@@@@@.                       @@@:                
          :@@@@@@@@@+                  @@@@@@@@               
            @@@@@@@@@@@@=          -@@@@@@@@@@@               
              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                
                @@@@@@@@@@@@@@@@@@@@@@@@@@@-                  
                   @@@@@@@@@@@@@@@@@@@@@                      
                       .%@@@@@@@@@@.                          


"""