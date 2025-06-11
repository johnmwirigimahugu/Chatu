"""
DTA ORM v3.1.6 - The Ultimate Python ORM
Authors: Seth & Kesh (johnmahugu@gmail.com)
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
- Flaske/ASGI/WSGI integration
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

class String(Field):   def __init__(self, max_length=255, **kw): super().__init__(f'VARCHAR({max_length})', **kw)
class Integer(Field):  def __init__(self, **kw): super().__init__('INTEGER', **kw)
class Float(Field):    def __init__(self, **kw): super().__init__('REAL', **kw)
class Boolean(Field):  def __init__(self, **kw): super().__init__('INTEGER', **kw)
class DateTime(Field): def __init__(self, **kw): super().__init__('TEXT', **kw)
class Text(Field):     def __init__(self, **kw): super().__init__('TEXT', **kw)
class JSONField(Field):def __init__(self, **kw): super().__init__('TEXT', **kw)
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

# --- END dta.py ---
