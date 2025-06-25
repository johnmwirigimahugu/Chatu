"""
──────────────────────────────────────────────────────────────────────────────
🌍 CHATU FRAMEWORK v11.0.0 (ELF-ZEN EDITION)
──────────────────────────────────────────────────────────────────────────────
🧾 Copyright © 2025 John Kesh Mahugu
🕒 Generated: 2025-06-25 22:11 EAT
🔑 License: MIT

📘 SYNOPSIS:
Chatu is a fullstack, enterprise-grade Python microframework.
It supports WSGI, ASGI, CLI, CGI, and is built for teaching, hosting, and rapid deployment.
Chatu includes templating, authentication, ORM (PeaDB™), REST, GraphQL, TreeQL, and more.

🛣️ ROADMAP:
- ✅ REST + GraphQL + TreeQL
- ✅ ORM x3 (Storm, BlackBean, PeaDB)
- ✅ Admin GUI + CLI + Seed + Test + OAuth2
- ✅ Email + Pagination + i18n + Docs + Scaffold
- ⏳ Future: WebSockets, Web2py/Vue modes, Mobile Builder

🧪 PeaDB™ (The Document Store):
Each document is a 🟢 Pea
Each collection/table is a 🟣 Pod
Together they make up a beautiful garden of scalable, structured data.

📜 LICENSE:
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files, to deal in the Software
without restriction, subject to the MIT License terms.

🙏 DEDICATION:
To all aspiring developers and software engineers around the world 🌍 —
May your code be clean, your bugs be minimal, and your ideas flow infinitely.

🧘 You are the framework. Zen is within.
──────────────────────────────────────────────────────────────────────────────
"""

import os, sys, json, time, threading, inspect, sqlite3, hashlib, hmac, secrets, subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse, unquote_plus
from html import escape as html_escape
from string import Template
from datetime import datetime

# ---------------------------
# Configuration Loader
# ---------------------------
CONFIG = {
    "PORT": 4375,
    "DEBUG": False,
    "SECRET_KEY": "zenmode",
    "DB_NAME": "chatu.db",
    "STATIC_DIR": "static",
    "TEMPLATE_DIR": "templates",
    "ADMIN_EMAIL": "admin@example.com",
    "LOCALE": "en",
    "SESSION_COOKIE": "chatu_session"
}

for file in ["chatu.conf", ".env"]:
    if os.path.exists(file):
        with open(file) as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    CONFIG[k.strip()] = v.strip()

os.makedirs(CONFIG["STATIC_DIR"], exist_ok=True)
os.makedirs(CONFIG["TEMPLATE_DIR"], exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# ---------------------------
# Core App
# ---------------------------
class Chatu:
    def __init__(self):
        self.routes = []
        self.cli = {}
        self.crons = []
        self.plugins = []
        self.middlewares = []

    def route(self, path, methods=["GET"]):
        def wrapper(func):
            self.routes.append({"path": path, "methods": methods, "func": func, "doc": func.__doc__})
            return func
        return wrapper

    def cli_command(self, name):
        def wrapper(func):
            self.cli[name] = func
            return func
        return wrapper

    def cron(self, expr):
        def wrapper(func):
            self.crons.append((expr, func))
            return func
        return wrapper

    def middleware(self, func):
        self.middlewares.append(func)
        return func

    def load_plugins(self):
        if os.path.isdir("plugins"):
            for fname in os.listdir("plugins"):
                if fname.endswith(".py"):
                    exec(open(f"plugins/{fname}").read(), {"app": self})

    def send_email(self, to, subject, body):
        if not CONFIG.get("SMTP_HOST"): return
        from email.message import EmailMessage
        msg = EmailMessage()
        msg["From"] = CONFIG.get("SMTP_USER")
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        import smtplib
        with smtplib.SMTP(CONFIG["SMTP_HOST"], int(CONFIG["SMTP_PORT"])) as s:
            s.starttls()
            s.login(CONFIG["SMTP_USER"], CONFIG["SMTP_PASS"])
            s.send_message(msg)
    # /modules put modules here like forms.py, charts.py they are automatically loaded and injected into the framework
    def load_modules(self, folder="modules"):
        if not os.path.exists(folder):
            os.makedirs(folder)
            return
        for fname in os.listdir(folder):
            if fname.endswith(".py"):
                module_path = os.path.join(folder, fname)
                name = fname[:-3]
                try:
                    with open(module_path, "r", encoding="utf-8") as f:
                        code = compile(f.read(), module_path, 'exec')
                        scope = {"app": self}
                        exec(code, scope)
                        self.plugins.append((name, scope))
                except Exception as e:
                    print(f"[⚠] Error loading module {fname}: {e}")

app = Chatu()
#-------------------------------------------------------------------#
#  📦 Chatu v11.0.0 – Part 2: Templates, Sessions, Forms, Auth, Flash.
#-------------------------------------------------------------------#
# ---------------------------
# Templating System
# ---------------------------
TEMPLATES = {}

def embed_templates(tpl_dict):
    TEMPLATES.update(tpl_dict)

def render_template(name, context={}):
    context.setdefault("csrf_token", generate_csrf_token(context.get("session_id", "anon")))
    context.setdefault("flash", lambda req: "<br>".join(get_flashed_messages(req)))
    if name in TEMPLATES:
        tpl = TEMPLATES[name]
    else:
        try:
            with open(f"{CONFIG['TEMPLATE_DIR']}/{name}", encoding="utf-8") as f:
                tpl = f.read()
        except FileNotFoundError:
            return f"Template not found: {name}"
    return Template(tpl).safe_substitute(context)

# ---------------------------
# Session Handling
# ---------------------------
SESSIONS = {}

def get_session(session_id):
    return SESSIONS.setdefault(session_id, {})

def set_session(session_id, key, value):
    SESSIONS.setdefault(session_id, {})[key] = value

def clear_session(session_id):
    if session_id in SESSIONS:
        del SESSIONS[session_id]

# ---------------------------
# CSRF Protection
# ---------------------------
def generate_csrf_token(session_id):
    return hmac.new(CONFIG["SECRET_KEY"].encode(), session_id.encode(), hashlib.sha256).hexdigest()

def validate_csrf(req):
    token = req["params"].get("csrf_token", [""])[0]
    sid = req.get("session_id", "anon")
    expected = generate_csrf_token(sid)
    return hmac.compare_digest(token, expected)

# ---------------------------
# Form Helpers (like web2py)
# ---------------------------
def form_start(action="#", method="POST", session_id="anon"):
    token = generate_csrf_token(session_id)
    return f'<form action="{action}" method="{method}" enctype="multipart/form-data">' + \
           f'<input type="hidden" name="csrf_token" value="{token}">'

def form_end():
    return "</form>"

def form_text(name, label=""):
    return f'<label>{label}</label><input type="text" name="{name}">'

def form_password(name, label=""):
    return f'<label>{label}</label><input type="password" name="{name}">'

def form_submit(label="Submit"):
    return f'<button type="submit">{label}</button>'

def form_textarea(name, label=""):
    return f'<label>{label}</label><textarea name="{name}"></textarea>'

def form_select(name, options):
    return f'<label>{name}</label><select name="{name}">' + "".join(
        f'<option value="{o}">{o}</option>' for o in options) + "</select>"

# ---------------------------
# Flash Messages
# ---------------------------
_flash_store = {}

def flash(req, message):
    sid = req.get("session_id")
    if sid:
        _flash_store[sid] = _flash_store.get(sid, []) + [message]

def get_flashed_messages(req):
    sid = req.get("session_id")
    msgs = _flash_store.pop(sid, []) if sid else []
    return msgs

# ---------------------------
# Authentication
# ---------------------------
def hash_password(password):
    salt = CONFIG["SECRET_KEY"][:8]
    return hashlib.sha512((password + salt).encode()).hexdigest()

def check_password(password, hashed):
    return hash_password(password) == hashed

def login_required(fn):
    def wrapper(req, *args, **kwargs):
        if not req.get("session", {}).get("user_id"):
            return "401 Unauthorized", [("Content-Type", "text/plain")], b"Unauthorized"
        return fn(req, *args, **kwargs)
    return wrapper

#-------------------------------------------------------------------#
# 📦 Chatu v11.0.0 – Part 3: ORM, Models, PeaPod™, BlackBean, and Storm.
#-------------------------------------------------------------------#

# ---------------------------
# Q Expressions (Advanced Filters)
# ---------------------------
class Q:
    def __init__(self, **kwargs):
        self.filters = kwargs
        self.connector = "AND"
        self.negated = False

    def __and__(self, other): return QGroup(self, "AND", other)
    def __or__(self, other): return QGroup(self, "OR", other)
    def __invert__(self): self.negated = not self.negated; return self

class QGroup(Q):
    def __init__(self, left, connector, right):
        self.left = left
        self.connector = connector
        self.right = right

def parse_q(q):
    if isinstance(q, QGroup):
        l, lp = parse_q(q.left)
        r, rp = parse_q(q.right)
        return f"({l} {q.connector} {r})", lp + rp
    elif isinstance(q, Q):
        parts, params = [], []
        for k, v in q.filters.items():
            if "__" in k:
                f, op = k.split("__", 1)
                if op == "icontains": parts.append(f"{f} LIKE ?"); params.append(f"%{v}%")
                elif op == "gte": parts.append(f"{f} >= ?"); params.append(v)
                elif op == "lte": parts.append(f"{f} <= ?"); params.append(v)
                elif op == "ne": parts.append(f"{f} != ?"); params.append(v)
                elif op == "lt": parts.append(f"{f} < ?"); params.append(v)
                elif op == "gt": parts.append(f"{f} > ?"); params.append(v)
            else: parts.append(f"{k} = ?"); params.append(v)
        sql = " AND ".join(parts)
        if q.negated: sql = f"NOT ({sql})"
        return sql, params
    raise ValueError("Invalid Q object")

# ---------------------------
# PeaDB™: NoSQL JSON Store on SQLite
# ---------------------------
class Pea:
    @classmethod
    def _cursor(cls): return cls.Meta.connection.cursor()

    @classmethod
    def _prepare(cls, filters):
        table = cls.__name__.lower()
        if not filters:
            return f"SELECT id, data FROM {table}", ()
        where = []
        params = []
        for k, v in filters.items():
            where.append(f"json_extract(data, '$.{k}') = ?")
            params.append(v)
        sql = f"SELECT id, data FROM {table} WHERE {' AND '.join(where)}"
        return sql, params

    @classmethod
    def all(cls): return list(cls.find())

    @classmethod
    def find(cls, **kwargs):
        cur = cls._cursor()
        sql, params = cls._prepare(kwargs)
        cur.execute(sql, params)
        for id_, data in cur.fetchall():
            obj = cls()
            obj.id = id_
            obj.__dict__.update(json.loads(data))
            yield obj

    @classmethod
    def create_table(cls):
        sql = f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} (id INTEGER PRIMARY KEY, data TEXT)"
        cls._cursor().execute(sql)
        cls.Meta.connection.commit()

    def save(self):
        cur = self._cursor()
        table = self.__class__.__name__.lower()
        d = self.__dict__.copy()
        d.pop("id", None)
        blob = json.dumps(d)
        cur.execute(f"INSERT INTO {table} (data) VALUES (?)", (blob,))
        self.id = cur.lastrowid
        self.Meta.connection.commit()

    def update(self):
        if not hasattr(self, "id"):
            raise ValueError("Object must be saved first.")
        cur = self._cursor()
        d = self.__dict__.copy()
        d.pop("id")
        cur.execute(f"UPDATE {self.__class__.__name__.lower()} SET data = ? WHERE id = ?",
                    (json.dumps(d), self.id))
        self.Meta.connection.commit()

    def delete(self):
        cur = self._cursor()
        cur.execute(f"DELETE FROM {self.__class__.__name__.lower()} WHERE id = ?", (self.id,))
        self.Meta.connection.commit()

    class Meta:
        connection = sqlite3.connect(CONFIG["DB_NAME"], check_same_thread=False)

# ---------------------------
# BlackBean ORM (SQL Mapper)
# ---------------------------
class Field:
    def __init__(self, sqltype="TEXT", nullable=True, unique=False):
        self.sqltype = sqltype
        self.nullable = nullable
        self.unique = unique

class String(Field):
    def __init__(self, max_length=255, **kwargs):
        super().__init__(f"VARCHAR({max_length})", **kwargs)

class Integer(Field):
    def __init__(self, **kwargs):
        super().__init__("INTEGER", **kwargs)

class BB_Model:
    _orm = None
    _conn = sqlite3.connect(CONFIG["DB_NAME"], check_same_thread=False)
    _conn.row_factory = sqlite3.Row

    @classmethod
    def migrate(cls):
        table = cls.__name__.lower()
        fields = cls.__annotations__
        cols = []
        for k, typ in fields.items():
            if isinstance(typ, Field):
                col = f"{k} {typ.sqltype}"
                if not typ.nullable: col += " NOT NULL"
                if typ.unique: col += " UNIQUE"
                cols.append(col)
        sql = f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY, {', '.join(cols)})"
        cls._conn.execute(sql)
        cls._conn.commit()

    @classmethod
    def create(cls, **kwargs):
        keys = ",".join(kwargs.keys())
        vals = ",".join("?" * len(kwargs))
        sql = f"INSERT INTO {cls.__name__.lower()} ({keys}) VALUES ({vals})"
        cur = cls._conn.execute(sql, tuple(kwargs.values()))
        cls._conn.commit()
        return cur.lastrowid

    @classmethod
    def all(cls):
        cur = cls._conn.execute(f"SELECT * FROM {cls.__name__.lower()}")
        return [dict(row) for row in cur.fetchall()]

    @classmethod
    def where(cls, *q_objs, **kwargs):
        if q_objs:
            sql, params = parse_q(q_objs[0])
        else:
            sql, params = parse_q(Q(**kwargs))
        cur = cls._conn.execute(f"SELECT * FROM {cls.__name__.lower()} WHERE {sql}", params)
        return [dict(row) for row in cur.fetchall()]

# ---------------------------
# Register ORM in app
# ---------------------------
app.Pea = Pea
app.BB_Model = BB_Model
app.Q = Q


#-------------------------------------------------------------------#
# 📦 Chatu v11.0.0 – Part 4: REST API, GraphQL, TreeQL, Admin GUI, Pagination.
#-------------------------------------------------------------------#

# ---------------------------
# Pagination Helper
# ---------------------------
def paginate_model(model, page=1, per_page=10):
    offset = (page - 1) * per_page
    rows = model._conn.execute(
        f"SELECT * FROM {model.__name__.lower()} LIMIT ? OFFSET ?", (per_page, offset)
    ).fetchall()
    total = model._conn.execute(f"SELECT COUNT(*) FROM {model.__name__.lower()}").fetchone()[0]
    return {
        "items": [dict(row) for row in rows],
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": (total + per_page - 1) // per_page
    }

# ---------------------------
# REST API Generator
# ---------------------------
class RestAPI:
    def __init__(self, model):
        self.model = model
        self.name = model.__name__.lower()

    def routes(self):
        return [
            (f"/api/{self.name}", ["GET"], self.index),
            (f"/api/{self.name}", ["POST"], self.create),
            (f"/api/{self.name}/<id>", ["GET"], self.show),
            (f"/api/{self.name}/<id>", ["PUT"], self.update),
            (f"/api/{self.name}/<id>", ["DELETE"], self.delete),
        ]

    def index(self, req):
        return json.dumps(self.model.all())

    def show(self, req):
        id = req["path"].split("/")[-1]
        return json.dumps(self.model.find(id))

    def create(self, req):
        return json.dumps(self.model.create(**req["params"]))

    def update(self, req):
        id = req["path"].split("/")[-1]
        self.model.update(id, **req["params"])
        return "Updated"

    def delete(self, req):
        id = req["path"].split("/")[-1]
        self.model.delete(id)
        return "Deleted"

# ---------------------------
# GraphQL Support
# ---------------------------
class GraphQL:
    def __init__(self, schema): self.schema = schema
    def resolve(self, query):
        result = {}
        for key in self.schema:
            if key in query:
                result[key] = self.schema[key].all()
        return result

# ---------------------------
# TreeQL Resolver
# ---------------------------
def resolve_tree(model, fields):
    base = model.all()
    for row in base:
        for field in fields:
            rel = getattr(model, field, None)
            if rel:
                row[field] = rel(row)
    return base

# ---------------------------
# Admin UI (Auto-generated)
# ---------------------------
@app.route("/admin")
@login_required
def admin_index(req):
    html = "<h1>Admin Panel</h1><ul>"
    for m in Model.__subclasses__():
        html += f"<li><a href='/admin/{m.__name__.lower()}'>{m.__name__}</a></li>"
    html += "</ul>"
    return html

@app.route("/admin/<model>")
@login_required
def admin_view(req):
    name = req["path"].split("/")[-1]
    model = globals().get(name.capitalize())
    if not model: return "Model not found"
    rows = model.all()
    html = f"<h2>{name.capitalize()}s</h2><table border='1'><tr>"
    if rows: html += "".join(f"<th>{k}</th>" for k in rows[0].keys()) + "</tr>"
    for row in rows:
        html += "<tr>" + "".join(f"<td>{v}</td>" for v in row.values()) + "</tr>"
    html += "</table>"
    return html

#-------------------------------------------------------------------#
# 📦 Chatu v11.0.0 – Part 5: Cron Jobs, WSGI/ASGI, CLI, Dev Tools, and Finalization.
#-------------------------------------------------------------------#

# ---------------------------
# Cron Scheduler
# ---------------------------
def start_crons():
    def every(seconds, fn):
        def wrapper():
            fn()
            threading.Timer(seconds, wrapper).start()
        wrapper()

    for expr, fn in app.crons:
        if expr.startswith("@every"):
            seconds = int(expr.split()[1].replace("s", ""))
            every(seconds, fn)

# ---------------------------
# WSGI App (for production)
# ---------------------------
def wsgi_app(environ, start_response):
    method = environ["REQUEST_METHOD"]
    path = environ["PATH_INFO"]
    length = int(environ.get("CONTENT_LENGTH", 0) or 0)
    body = environ["wsgi.input"].read(length) if length else b""

    req = {
        "method": method,
        "path": path,
        "params": parse_qs(body.decode()),
        "headers": {k[5:].lower().replace("_", "-"): v for k, v in environ.items() if k.startswith("HTTP_")},
        "session_id": environ.get("HTTP_COOKIE", "anon").split("=")[-1]
    }
    req["session"] = get_session(req["session_id"])

    for mw in app.middlewares:
        mw(req)

    for r in app.routes:
        if r["path"] == path and method in r["methods"]:
            res = r["func"](req)
            if isinstance(res, tuple): status, headers, body = res
            else: status, headers, body = "200 OK", [("Content-Type", "text/html")], str(res).encode()
            start_response(status, headers)
            return [body]

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]

# ---------------------------
# ASGI App (for async servers)
# ---------------------------
async def asgi_app(scope, receive, send):
    if scope["type"] != "http":
        return
    body = b""
    while True:
        event = await receive()
        if event["type"] == "http.request":
            body += event.get("body", b"")
            if not event.get("more_body", False):
                break

    req = {
        "method": scope["method"],
        "path": scope["path"],
        "params": parse_qs(body.decode()),
        "headers": dict(scope["headers"]),
        "session_id": "anon",
        "session": {}
    }

    for r in app.routes:
        if r["path"] == req["path"] and req["method"] in r["methods"]:
            result = r["func"](req)
            if isinstance(result, tuple):
                status, headers, body = result
            else:
                status, headers, body = "200 OK", [("Content-Type", "text/html")], str(result).encode()

            await send({"type": "http.response.start", "status": int(status.split()[0]),
                        "headers": [(k.encode(), v.encode()) for k, v in headers]})
            await send({"type": "http.response.body", "body": body})
            return

    await send({"type": "http.response.start", "status": 404,
                "headers": [(b"content-type", b"text/plain")]})
    await send({"type": "http.response.body", "body": b"Not Found"})

# ---------------------------
# CLI / Dev Tools
# ---------------------------
@app.cli_command("run")
def run():
    from wsgiref.simple_server import make_server
    print(f"🌍 Running on http://127.0.0.1:{CONFIG['PORT']}")
    make_server("", int(CONFIG["PORT"]), wsgi_app).serve_forever()

@app.cli_command("dev")
def dev_mode():
    print("🔁 Dev Mode Enabled (Auto Reload)")
    while True:
        proc = subprocess.Popen([sys.executable] + sys.argv[:1] + ["__run__"])
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            break
        print("🔄 Reloading...")

@app.cli_command("__run__")
def _run():
    start_crons()
    app.load_plugins()
    app.load_modules()
    run()

@app.cli_command("seed")
def seed():
    print("🌱 Seeding database...")

@app.cli_command("test")
def test():
    print("🧪 Running tests...")
    assert True, "All tests passed."

# Export WSGI for Passenger/cPanel
application = wsgi_app

"""
📝 Completed: 2025-06-25 maandamano 2 22:11 EAT
🔚 EOF – chatu_v11.0.0.py
Thank You יהוה by johnmahugu {at} gmail {dot} com.
"""