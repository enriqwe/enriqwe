#!/usr/bin/env python3
import os
import secrets
import hashlib
import sqlite3
import subprocess
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path

from flask import Flask, flash, redirect, render_template_string, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


ADMIN_EMAILS = {
    email.strip().lower()
    for email in os.environ.get("DASHBOARD_ADMIN_EMAILS", "enriqwe@gmail.com").split(",")
    if email.strip()
}


LOGIN_HTML = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }}</title><style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;padding:34px 18px;background:#07101f;color:#f6fbff;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;overflow-x:hidden}
body:before{content:"";position:fixed;inset:0;background:linear-gradient(180deg,#07101f 0%,#091a38cc 28%,#06101f 100%),url('/static/login-bg.jpg') center bottom/cover no-repeat;z-index:-2}
body:after{content:"";position:fixed;inset:0;background:radial-gradient(circle at 72% 24%,#39d4ff45,transparent 30%),radial-gradient(circle at 22% 80%,#7c3aed3a,transparent 34%),linear-gradient(90deg,#020817d9,#08152a85 46%,#020817e8);z-index:-1}
main{width:min(438px,calc(100vw - 32px));margin-left:auto;margin-right:clamp(0px,8vw,120px);background:linear-gradient(160deg,#111b31e8,#071224d8);border:1px solid #ffffff24;border-radius:26px;padding:30px;box-shadow:0 28px 90px #000b,0 0 0 1px #5eead433 inset;backdrop-filter:blur(18px)}
.login-kicker{display:inline-flex;align-items:center;gap:8px;margin:0 0 14px;padding:7px 10px;border:1px solid #68e8ff3b;border-radius:999px;background:#071a2dbf;color:#a8efff;font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}.login-kicker:before{content:"";width:8px;height:8px;border-radius:50%;background:#22d3ee;box-shadow:0 0 18px #22d3ee}
h1{margin:0 0 8px;font-size:30px;line-height:1.05}p{color:#bfd0e8;line-height:1.5}.msg{padding:11px 13px;border:1px solid #70e0ff3d;background:#06182ccf;border-radius:14px;margin:16px 0;color:#e7f6ff}
form{margin-top:18px}label{display:block;margin:15px 0 7px;color:#d7e7ff;font-size:13px;font-weight:750}input{width:100%;background:#071225d6;color:#f6fbff;border:1px solid #7dd3fc36;border-radius:14px;padding:13px 14px;outline:0;box-shadow:0 1px 0 #ffffff12 inset}input:focus{border-color:#67e8f9;box-shadow:0 0 0 4px #22d3ee20}
button{width:100%;margin-top:18px;background:linear-gradient(135deg,#2dd4bf,#60a5fa);color:#04111f;border:0;border-radius:14px;padding:13px 14px;font-weight:900;cursor:pointer;box-shadow:0 16px 36px #0891b245}button:hover{filter:brightness(1.06)}
a{color:#b7ecff}.links{display:flex;justify-content:space-between;gap:12px;margin-top:18px;font-size:14px}.links a{text-decoration-color:#b7ecff80;text-underline-offset:3px}
@media (max-width:960px){body{place-items:end start;padding:18px 20px 28px;min-height:100svh}body:before{background:linear-gradient(180deg,#07101fe8 0%,#06101f6e 34%,#06101fe8 100%),url('/static/login-bg.jpg') center center/cover no-repeat}body:after{background:linear-gradient(180deg,#020817bf,#06101f99 48%,#020817f2)}main{width:min(350px,100%);margin:0;padding:24px 20px;border-radius:22px;justify-self:start}h1{font-size:24px}}
</style></head><body><main>
<div class="login-kicker">Enrique Hub</div>
<h1>{{ title }}</h1>
{% for message in get_flashed_messages() %}<div class="msg">{{ message }}</div>{% endfor %}
{{ body|safe }}
</main></body></html>"""


class AuthManager:
    def __init__(self, base_dir: Path, app_name: str):
        self.base_dir = base_dir
        self.app_name = app_name
        self.state_dir = Path(os.environ.get("DASHBOARD_AUTH_DIR", base_dir / "state"))
        self.db_path = self.state_dir / "auth.sqlite3"

    def init_app(self, app: Flask) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        app.secret_key = os.environ.get("DASHBOARD_SECRET_KEY") or self._secret_key()
        app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
        self.init_db()

        app.add_url_rule("/login", view_func=self.login, methods=["GET", "POST"])
        app.add_url_rule("/logout", view_func=self.logout, methods=["POST"])
        app.add_url_rule("/request-password", view_func=self.request_password, methods=["GET", "POST"])
        app.add_url_rule("/set-password/<code>", view_func=self.set_password, methods=["GET", "POST"])

    def _secret_key(self) -> str:
        key_path = self.state_dir / "flask-secret"
        if not key_path.exists():
            key_path.write_text(secrets.token_urlsafe(48), encoding="utf-8")
            key_path.chmod(0o600)
        return key_path.read_text(encoding="utf-8").strip()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT,
                    role TEXT NOT NULL DEFAULT 'user',
                    confirmed_at TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS password_links (
                    code_hash TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    used_at TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS permissions (
                    email TEXT NOT NULL,
                    access_key TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY(email, access_key),
                    FOREIGN KEY(email) REFERENCES users(email) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS deleted_users (
                    email TEXT PRIMARY KEY,
                    deleted_at TEXT NOT NULL
                );
                """
            )
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
            if "role" not in columns:
                conn.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
            for email in ADMIN_EMAILS:
                conn.execute("UPDATE users SET role = 'admin' WHERE email = ?", (email,))

    def create_or_update_user(self, email: str, password: str, confirmed: bool = True) -> None:
        now = self.now()
        confirmed_at = now if confirmed else None
        clean_email = self.clean_email(email)
        role = "admin" if clean_email in ADMIN_EMAILS else "user"
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO users(email, password_hash, role, confirmed_at, created_at)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    password_hash=excluded.password_hash,
                    role=CASE WHEN users.role = 'admin' THEN users.role ELSE excluded.role END,
                    confirmed_at=COALESCE(excluded.confirmed_at, users.confirmed_at)
                """,
                (clean_email, generate_password_hash(password), role, confirmed_at, now),
            )
            conn.execute("DELETE FROM deleted_users WHERE email = ?", (clean_email,))

    def require_login(self, view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_email"):
                return redirect(url_for("login", next=request.path))
            return view(*args, **kwargs)

        return wrapped

    def login(self):
        if request.method == "POST":
            email = self.clean_email(request.form.get("email"))
            password = request.form.get("password") or ""
            user = self.user(email)
            if user and user["confirmed_at"] and check_password_hash(user["password_hash"], password):
                session.clear()
                session["user_email"] = email
                session["user_role"] = user["role"]
                return redirect(request.args.get("next") or url_for("index"))
            flash("Usuario o contraseña incorrectos.")
        body = """
        <form method="post">
          <label>Email</label><input name="email" type="email" autocomplete="username" required autofocus>
          <label>Contraseña</label><input name="password" type="password" autocomplete="current-password" required>
          <button type="submit">Entrar</button>
        </form>
        <div class="links"><a href="/request-password">Alta o recuperar contraseña</a></div>
        """
        return self.page("Acceso al dashboard", body)

    def logout(self):
        session.clear()
        return redirect(url_for("login"))

    def request_password(self):
        if request.method == "POST":
            email = self.clean_email(request.form.get("email"))
            if self.can_request_link(email):
                code = self.create_password_link(email)
                self.send_password_email(email, code)
            flash("Si el email está autorizado, recibirás un enlace de confirmación.")
        body = """
        <p>Introduce tu email para recibir un enlace de alta inicial o recuperación de contraseña.</p>
        <form method="post">
          <label>Email</label><input name="email" type="email" autocomplete="email" required autofocus>
          <button type="submit">Enviar email</button>
        </form>
        <div class="links"><a href="/login">Volver al login</a></div>
        """
        return self.page("Alta o recuperación", body)

    def set_password(self, code: str):
        link = self.valid_link(code)
        if not link:
            return self.page("Enlace no válido", "<p>El enlace ha caducado o ya se ha usado.</p><div class='links'><a href='/request-password'>Pedir otro enlace</a></div>"), 400
        if request.method == "POST":
            password = request.form.get("password") or ""
            confirm = request.form.get("confirm") or ""
            if len(password) < 6:
                flash("La contraseña debe tener al menos 6 caracteres.")
            elif password != confirm:
                flash("Las contraseñas no coinciden.")
            else:
                self.create_or_update_user(link["email"], password, confirmed=True)
                self.consume_link(code)
                flash("Contraseña actualizada. Ya puedes entrar.")
                return redirect(url_for("login"))
        body = f"""
        <p>Email confirmado: <strong>{link['email']}</strong></p>
        <form method="post">
          <label>Nueva contraseña</label><input name="password" type="password" autocomplete="new-password" required autofocus>
          <label>Confirmar contraseña</label><input name="confirm" type="password" autocomplete="new-password" required>
          <button type="submit">Guardar contraseña</button>
        </form>
        """
        return self.page("Definir contraseña", body)

    def page(self, title: str, body: str):
        return render_template_string(LOGIN_HTML, title=title, body=body)

    def user(self, email: str):
        with self.connect() as conn:
            return conn.execute("SELECT * FROM users WHERE email = ?", (self.clean_email(email),)).fetchone()

    def users(self):
        with self.connect() as conn:
            return conn.execute("SELECT email, role, confirmed_at, created_at FROM users ORDER BY role, email").fetchall()

    def delete_user(self, email: str) -> bool:
        clean_email = self.clean_email(email)
        user = self.user(clean_email)
        if not user or user["role"] == "admin":
            return False
        with self.connect() as conn:
            conn.execute("DELETE FROM permissions WHERE email = ?", (clean_email,))
            conn.execute("DELETE FROM password_links WHERE email = ?", (clean_email,))
            conn.execute("DELETE FROM users WHERE email = ?", (clean_email,))
            conn.execute(
                "INSERT OR REPLACE INTO deleted_users(email, deleted_at) VALUES(?, ?)",
                (clean_email, self.now()),
            )
        return True

    def was_deleted(self, email: str) -> bool:
        with self.connect() as conn:
            row = conn.execute("SELECT 1 FROM deleted_users WHERE email = ?", (self.clean_email(email),)).fetchone()
        return bool(row)

    def set_user_password(self, email: str, password: str) -> bool:
        clean_email = self.clean_email(email)
        if len(password) < 6:
            return False
        user = self.user(clean_email)
        if not user:
            return False
        with self.connect() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, confirmed_at = COALESCE(confirmed_at, ?) WHERE email = ?",
                (generate_password_hash(password), self.now(), clean_email),
            )
        return True

    def is_admin(self, email: str | None = None) -> bool:
        clean_email = self.clean_email(email)
        user = self.user(clean_email)
        return bool(user and user["role"] == "admin")

    def ensure_user_with_password_hash(self, email: str, password_hash: str, role: str = "user", confirmed: bool = True) -> None:
        clean_email = self.clean_email(email)
        now = self.now()
        confirmed_at = now if confirmed else None
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO users(email, password_hash, role, confirmed_at, created_at)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    password_hash=excluded.password_hash,
                    role=excluded.role,
                    confirmed_at=COALESCE(users.confirmed_at, excluded.confirmed_at)
                """,
                (clean_email, password_hash, role, confirmed_at, now),
            )
            conn.execute("DELETE FROM deleted_users WHERE email = ?", (clean_email,))

    def require_admin(self, view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_email"):
                return redirect(url_for("login", next=request.path))
            if not self.is_admin(session.get("user_email")):
                return self.page("Sin permiso", "<p>No tienes permiso para acceder a esta seccion.</p><div class='links'><a href='/'>Volver</a></div>"), 403
            return view(*args, **kwargs)

        return wrapped

    def set_permissions(self, email: str, access_keys: list[str]) -> None:
        clean_email = self.clean_email(email)
        now = self.now()
        with self.connect() as conn:
            conn.execute("DELETE FROM permissions WHERE email = ?", (clean_email,))
            conn.executemany(
                "INSERT INTO permissions(email, access_key, created_at) VALUES(?, ?, ?)",
                [(clean_email, key, now) for key in sorted(set(access_keys))],
            )

    def permissions_for(self, email: str) -> set[str]:
        user = self.user(email)
        if not user:
            return set()
        if user["role"] == "admin":
            return {"*"}
        with self.connect() as conn:
            return {row["access_key"] for row in conn.execute("SELECT access_key FROM permissions WHERE email = ?", (self.clean_email(email),))}

    def all_permissions(self) -> dict[str, set[str]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT email, access_key FROM permissions").fetchall()
        permissions: dict[str, set[str]] = {}
        for row in rows:
            permissions.setdefault(row["email"], set()).add(row["access_key"])
        return permissions

    def user_count(self) -> int:
        with self.connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM users").fetchone()[0])

    def can_request_link(self, email: str) -> bool:
        if not email:
            return False
        if self.user(email):
            return True
        allowed = {e.strip().lower() for e in os.environ.get("DASHBOARD_ALLOWED_EMAILS", "").split(",") if e.strip()}
        return self.user_count() == 0 or email in allowed

    def create_password_link(self, email: str) -> str:
        code = secrets.token_urlsafe(32)
        now = self.now()
        expires = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO password_links(code_hash, email, expires_at, created_at) VALUES(?, ?, ?, ?)",
                (self.hash_code(code), self.clean_email(email), expires, now),
            )
        return code

    def valid_link(self, code: str):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM password_links WHERE code_hash = ? AND used_at IS NULL",
                (self.hash_code(code),),
            ).fetchone()
        if not row:
            return None
        if datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
            return None
        return row

    def consume_link(self, code: str) -> None:
        with self.connect() as conn:
            conn.execute("UPDATE password_links SET used_at = ? WHERE code_hash = ?", (self.now(), self.hash_code(code)))

    def send_password_email(self, email: str, code: str) -> None:
        base_url = os.environ.get("DASHBOARD_PUBLIC_URL") or request.host_url.rstrip("/")
        link = f"{base_url}/set-password/{code}"
        subject = f"{self.app_name}: enlace de acceso"
        body = f"Confirma este email y define tu contraseña aquí:\n\n{link}\n\nEl enlace caduca en 30 minutos."
        sender = os.environ.get("DASHBOARD_MAIL_COMMAND", "/home/flow/gmail-venv/bin/python /home/flow/gmail_api.py send")
        subprocess.run([*sender.split(), email, subject, body], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @staticmethod
    def clean_email(email) -> str:
        return str(email or "").strip().lower()

    @staticmethod
    def hash_code(code: str) -> str:
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()


def init_user_from_cli(auth: AuthManager, argv: list[str]) -> bool:
    if len(argv) >= 4 and argv[1] == "init-user":
        auth.init_db()
        auth.create_or_update_user(argv[2], argv[3], confirmed=True)
        print(f"USER_INITIALIZED {auth.clean_email(argv[2])}")
        return True
    return False
