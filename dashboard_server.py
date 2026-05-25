#!/usr/bin/env python3
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from flask import Flask, Response, abort, render_template_string, request, send_from_directory

from auth_core import AuthManager, init_user_from_cli


BASE_DIR = Path(__file__).resolve().parent
SITES_DIR = BASE_DIR / "sites"
STATIC_DASHBOARDS = {
    "alexia": Path("/home/flow/alexia-bot/facturas-repository"),
    "gastos": Path("/home/flow/expenses-bot/gastos-repository"),
}

PROXIES = {
    "gastos": "http://127.0.0.1:8081",
}

app = Flask(__name__)
auth = AuthManager(BASE_DIR, "Enrique")
auth.init_app(app)


SECTIONS = [
    {
        "id": "familia",
        "title": "Finanzas y colegio",
        "summary": "Lo operativo: pagos, comunicados y control diario.",
        "accent": "#12b981",
        "items": [
            {
                "name": "Alexia",
                "description": "Facturas y comunicados del colegio.",
                "url": "/alexia/",
                "repo": "https://github.com/enriqwe/Alexia",
                "accent": "#14b8a6",
            },
            {
                "name": "Control de gastos",
                "description": "Dashboard de movimientos y categorias.",
                "url": "/gastos/",
                "repo": "https://github.com/enriqwe/Gestion-de-Gastos",
                "accent": "#f59e0b",
            },
        ],
    },
    {
        "id": "tools",
        "title": "Tools de trabajo",
        "summary": "Herramientas para crear, organizar y presentar.",
        "accent": "#3b82f6",
        "items": [
            {
                "name": "Editor de Mapas v2",
                "description": "Herramienta visual para crear mapas.",
                "url": "/site/editor-mapas-v2/",
                "repo": "https://github.com/enriqwe/Editor-de-Mapas-v2",
                "accent": "#2563eb",
            },
            {
                "name": "Editor de Mapas",
                "description": "Version anterior del editor de mapas.",
                "url": "/site/editor-mapas/",
                "repo": "https://github.com/enriqwe/Editor-de-Mapas",
                "accent": "#0f766e",
            },
            {
                "name": "Canvas",
                "description": "Canvas infinito para presentaciones.",
                "url": "/site/canvas/",
                "repo": "https://github.com/enriqwe/Canvas",
                "accent": "#be185d",
            },
            {
                "name": "Calendario",
                "description": "Aplicacion de calendario publicada.",
                "url": "/site/calendario/",
                "repo": "https://github.com/enriqwe/Calendario",
                "accent": "#0284c7",
            },
        ],
    },
    {
        "id": "juegos",
        "title": "Juegos",
        "summary": "Aprendizaje y practica visual para entrar directo.",
        "accent": "#ef4444",
        "items": [
            {
                "name": "Mision cuerpo humano",
                "description": "Juego educativo del cuerpo humano.",
                "url": "/site/mision-cuerpo-humano/",
                "repo": "https://github.com/enriqwe/mision-cuerpo-humano",
                "accent": "#dc2626",
            },
            {
                "name": "Juego Frances",
                "description": "Aprende vocabulario de frances.",
                "url": "/site/juego-frances/",
                "repo": "https://github.com/enriqwe/JuegoFrances",
                "accent": "#2563eb",
            },
            {
                "name": "Aprende a escribir",
                "description": "Practica de escritura con ordenador.",
                "url": "/site/aprende-a-escribir/",
                "repo": "https://github.com/enriqwe/aprendeaescribir",
                "accent": "#16a34a",
            },
            {
                "name": "Cosmotablas1",
                "description": "Aprende a multiplicar en el espacio.",
                "url": "https://cosmotablas1.vercel.app",
                "repo": "https://github.com/enriqwe/Cosmotablas1",
                "accent": "#7c3aed",
            },
            {
                "name": "Cosmotablas",
                "description": "Repositorio de Cosmotablas.",
                "url": "https://github.com/enriqwe/Cosmotablas",
                "repo": "https://github.com/enriqwe/Cosmotablas",
                "accent": "#0891b2",
            },
        ],
    },
    {
        "id": "otros",
        "title": "Otros proyectos",
        "summary": "Repositorios publicados o utiles como referencia.",
        "accent": "#64748b",
        "items": [
            {
                "name": "Regulacion",
                "description": "Proyecto publicado en GitHub Pages.",
                "url": "/site/regulacion/",
                "repo": "https://github.com/enriqwe/Regulaci-n",
                "accent": "#64748b",
            },
            {
                "name": "Enriqwe landing",
                "description": "Repositorio de esta landing privada.",
                "url": "https://github.com/enriqwe/enriqwe",
                "repo": "https://github.com/enriqwe/enriqwe",
                "accent": "#475569",
            },
        ],
    },
]

FEATURED = [
    ("Alexia", "/alexia/", "Colegio"),
    ("Gastos", "/gastos/", "Finanzas"),
    ("Mapas v2", "/site/editor-mapas-v2/", "Tool"),
    ("Juegos", "#juegos", "Seccion"),
]


LANDING_HTML = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Enrique</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0c111d;
      --panel: #121826;
      --panel-2: #182132;
      --line: #273244;
      --text: #f3f6fb;
      --muted: #9aa7bb;
      --brand: #e8b44f;
      --ok: #12b981;
      --danger: #ef4444;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        linear-gradient(180deg, rgba(232,180,79,.10), transparent 320px),
        linear-gradient(135deg, #0c111d 0%, #141b2a 48%, #0c111d 100%);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 24px clamp(18px, 4vw, 48px);
      border-bottom: 1px solid rgba(148,163,184,.18);
      background: rgba(12,17,29,.86);
      backdrop-filter: blur(18px);
      position: sticky;
      top: 0;
      z-index: 5;
    }
    .brand { display: flex; align-items: center; gap: 14px; min-width: 0; }
    .mark {
      width: 42px;
      height: 42px;
      border-radius: 12px;
      display: grid;
      place-items: center;
      background: var(--brand);
      color: #17120a;
      font-weight: 900;
      font-size: 21px;
    }
    h1 { margin: 0; font-size: clamp(24px, 4vw, 40px); letter-spacing: 0; }
    .subtitle { color: var(--muted); margin-top: 3px; font-size: 14px; }
    .logout {
      border: 1px solid var(--line);
      background: rgba(17,24,39,.8);
      color: var(--text);
      border-radius: 10px;
      padding: 10px 12px;
      font-weight: 700;
      cursor: pointer;
    }
    main { width: min(1220px, calc(100vw - 32px)); margin: 28px auto 54px; }
    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(320px, .78fr);
      gap: 18px;
      align-items: stretch;
      margin-bottom: 18px;
    }
    .summary, .quick, .section {
      border: 1px solid var(--line);
      background: rgba(18,24,38,.86);
      border-radius: 8px;
      box-shadow: 0 18px 50px rgba(0,0,0,.24);
    }
    .summary { padding: clamp(22px, 4vw, 38px); }
    .summary h2 { margin: 0 0 12px; font-size: clamp(28px, 5vw, 58px); line-height: 1.02; letter-spacing: 0; }
    .summary p { margin: 0; color: var(--muted); max-width: 720px; line-height: 1.55; font-size: 16px; }
    .quick { display: grid; align-content: center; gap: 10px; padding: 16px; }
    .quick-title { color: var(--muted); font-size: 13px; font-weight: 800; text-transform: uppercase; }
    .quick a {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      color: var(--text);
      text-decoration: none;
      border: 1px solid var(--line);
      background: rgba(12,17,29,.74);
      border-radius: 8px;
      padding: 14px 15px;
      font-weight: 800;
    }
    .quick a:hover, .card:hover { border-color: rgba(232,180,79,.55); transform: translateY(-1px); }
    .section { margin-top: 18px; padding: 18px; scroll-margin-top: 102px; }
    .section-head {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: end;
      margin-bottom: 14px;
      border-bottom: 1px solid rgba(148,163,184,.14);
      padding-bottom: 14px;
    }
    .section h2 { margin: 0; font-size: clamp(22px, 3vw, 32px); letter-spacing: 0; }
    .section p { margin: 6px 0 0; color: var(--muted); line-height: 1.45; }
    .count {
      flex: 0 0 auto;
      color: var(--text);
      border: 1px solid var(--line);
      border-left: 5px solid var(--section-accent);
      background: rgba(12,17,29,.7);
      border-radius: 8px;
      padding: 8px 10px;
      font-weight: 800;
      font-size: 13px;
    }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 12px; }
    .card {
      min-height: 176px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      border: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(24,33,50,.95), rgba(15,21,34,.94));
      border-radius: 8px;
      padding: 16px;
      text-decoration: none;
      color: var(--text);
      position: relative;
      overflow: hidden;
      transition: border-color .16s ease, transform .16s ease;
    }
    .card::before {
      content: "";
      position: absolute;
      inset: 0 0 auto 0;
      height: 5px;
      background: var(--accent);
    }
    .card h3 { margin: 10px 0 8px; font-size: 20px; letter-spacing: 0; }
    .card p { margin: 0; color: var(--muted); line-height: 1.45; }
    .actions { display: flex; gap: 10px; margin-top: 18px; }
    .button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 38px;
      padding: 9px 11px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 800;
      font-size: 14px;
    }
    .primary { background: var(--accent); color: #07111f; }
    .secondary { border: 1px solid var(--line); color: var(--text); background: rgba(12,17,29,.74); }
    @media (max-width: 760px) {
      header { align-items: flex-start; padding: 16px; }
      .hero { grid-template-columns: 1fr; }
      .section-head { align-items: flex-start; flex-direction: column; }
      .subtitle { font-size: 13px; }
      .logout { padding: 9px 10px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="mark">E</div>
      <div>
        <h1>Enrique</h1>
        <div class="subtitle">Panel privado de accesos</div>
      </div>
    </div>
    <form method="post" action="/logout"><button class="logout" type="submit">Salir</button></form>
  </header>
  <main>
    <section class="hero">
      <div class="summary">
        <h2>Todo a dos clics.</h2>
        <p>Accesos privados a colegio, finanzas, tools y juegos. Las secciones estan pensadas para abrir rapido lo que necesitas sin buscar entre repositorios.</p>
      </div>
      <nav class="quick" aria-label="Accesos principales">
        <div class="quick-title">Accesos rapidos</div>
        {% for name, url, label in featured %}
        <a href="{{ url }}"><span>{{ name }}</span><small>{{ label }} -></small></a>
        {% endfor %}
      </nav>
    </section>
    {% for section in sections %}
    <section class="section" id="{{ section.id }}" style="--section-accent: {{ section.accent }}" aria-labelledby="{{ section.id }}-title">
      <div class="section-head">
        <div>
          <h2 id="{{ section.id }}-title">{{ section.title }}</h2>
          <p>{{ section.summary }}</p>
        </div>
        <div class="count">{{ section["items"]|length }} accesos</div>
      </div>
      <div class="grid">
        {% for app in section["items"] %}
        <article class="card" style="--accent: {{ app.accent }}">
          <div>
            <h3>{{ app.name }}</h3>
            <p>{{ app.description }}</p>
          </div>
          <div class="actions">
            <a class="button primary" href="{{ app.url }}">Abrir</a>
            <a class="button secondary" href="{{ app.repo }}">Repo</a>
          </div>
        </article>
        {% endfor %}
      </div>
    </section>
      {% endfor %}
  </main>
</body>
</html>"""


@app.get("/")
@auth.require_login
def index():
    return render_template_string(LANDING_HTML, sections=SECTIONS, featured=FEATURED)


def safe_site_path(slug: str, path: str):
    root = (SITES_DIR / slug).resolve()
    if not root.is_dir():
        abort(404)
    candidate = (root / path).resolve()
    if root != candidate and root not in candidate.parents:
        abort(404)
    if candidate.is_dir():
        candidate = candidate / "index.html"
    if not candidate.exists():
        candidate = root / "index.html"
    return root, candidate


@app.get("/site/<slug>/")
@app.get("/site/<slug>/<path:path>")
@auth.require_login
def site(slug: str, path: str = "index.html"):
    root, target = safe_site_path(slug, path)
    if target.name.startswith(".") or any(part.startswith(".") for part in target.relative_to(root).parts):
        abort(404)
    return send_from_directory(root, target.relative_to(root))


def serve_static_dashboard(name: str, path: str = "index.html"):
    root = STATIC_DASHBOARDS[name].resolve()
    target = (root / path).resolve()
    if root != target and root not in target.parents:
        abort(404)
    if target.is_dir():
        target = target / "index.html"
    if not target.exists():
        abort(404)
    if target.name.startswith(".") or any(part.startswith(".") for part in target.relative_to(root).parts):
        abort(404)
    return send_from_directory(root, target.relative_to(root))


def proxy_request(base_url: str, path: str = ""):
    query = f"?{request.query_string.decode('utf-8')}" if request.query_string else ""
    url = f"{base_url.rstrip('/')}/{path}{query}"
    data = request.get_data() if request.method not in {"GET", "HEAD"} else None
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length", "connection", "accept-encoding"}
    }
    upstream_request = urllib.request.Request(url, data=data, headers=headers, method=request.method)
    try:
        with urllib.request.urlopen(upstream_request, timeout=30) as upstream:
            body = upstream.read()
            response_headers = [
                (key, value)
                for key, value in upstream.headers.items()
                if key.lower() not in {"connection", "content-length", "transfer-encoding", "content-encoding"}
            ]
            return Response(body, status=upstream.status, headers=response_headers)
    except urllib.error.HTTPError as exc:
        return Response(exc.read(), status=exc.code)
    except urllib.error.URLError:
        return Response("Servicio interno no disponible.", status=502)


@app.get("/alexia/")
@app.get("/alexia/<path:path>")
@auth.require_login
def alexia_dashboard(path: str = "index.html"):
    return serve_static_dashboard("alexia", path or "index.html")


@app.get("/gastos/")
@app.get("/gastos/<path:path>")
@auth.require_login
def gastos_dashboard(path: str = "index.html"):
    return serve_static_dashboard("gastos", path or "index.html")


@app.route("/upload", methods=["POST"])
@auth.require_login
def gastos_upload_proxy():
    return proxy_request(PROXIES["gastos"], "upload")


def main():
    if init_user_from_cli(auth, sys.argv):
        return
    port = int(os.environ.get("PORT", "8090"))
    app.run(host="0.0.0.0", port=port, threaded=True)


if __name__ == "__main__":
    main()
