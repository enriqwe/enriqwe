#!/usr/bin/env python3
import os
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from flask import Flask, Response, abort, redirect, render_template_string, request, send_from_directory, session, url_for

from auth_core import AuthManager, init_user_from_cli


BASE_DIR = Path(__file__).resolve().parent
SITES_DIR = BASE_DIR / "sites"
STATIC_DASHBOARDS = {
    "facturas": Path("/home/flow/alexia-bot/facturas-repository"),
    "gastos": Path("/home/flow/expenses-bot/gastos-repository"),
}
COMUNICADOS_FILE = Path("/home/flow/alexia-bot/repository/comunicados.json")

PROXIES = {
    "gastos": "http://127.0.0.1:8081",
}

app = Flask(__name__)
auth = AuthManager(BASE_DIR, "Enrique")
auth.init_app(app)


ADMIN_EMAIL = "enriqwe@gmail.com"
GABI_EMAIL = "emailsdegabi@gmail.com"


SECTIONS = [
    {
        "id": "familia",
        "title": "Finanzas y colegio",
        "summary": "Lo operativo: pagos, comunicados y control diario.",
        "accent": "#12b981",
        "items": [
            {
                "key": "alexia",
                "name": "Comunicados Alexia",
                "description": "Mensajes del colegio con texto completo.",
                "url": "/alexia/",
                "repo": "https://github.com/enriqwe/Alexia",
                "accent": "#14b8a6",
            },
            {
                "key": "facturas-alexia",
                "name": "Facturas Alexia",
                "description": "Dashboard de facturas del colegio con PDFs.",
                "url": "/facturas/",
                "repo": "https://github.com/enriqwe/Alexia",
                "accent": "#0f766e",
            },
            {
                "key": "gastos",
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
                "key": "editor-mapas-v2",
                "name": "Editor de Mapas v2",
                "description": "Herramienta visual para crear mapas.",
                "url": "/site/editor-mapas-v2/",
                "repo": "https://github.com/enriqwe/Editor-de-Mapas-v2",
                "accent": "#2563eb",
            },
            {
                "key": "editor-mapas",
                "name": "Editor de Mapas",
                "description": "Version anterior del editor de mapas.",
                "url": "/site/editor-mapas/",
                "repo": "https://github.com/enriqwe/Editor-de-Mapas",
                "accent": "#0f766e",
            },
            {
                "key": "canvas",
                "name": "Canvas",
                "description": "Canvas infinito para presentaciones.",
                "url": "/site/canvas/",
                "repo": "https://github.com/enriqwe/Canvas",
                "accent": "#be185d",
            },
            {
                "key": "calendario",
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
                "key": "mision-cuerpo-humano",
                "name": "Mision cuerpo humano",
                "description": "Juego educativo del cuerpo humano.",
                "url": "/site/mision-cuerpo-humano/",
                "repo": "https://github.com/enriqwe/mision-cuerpo-humano",
                "accent": "#dc2626",
            },
            {
                "key": "juego-frances",
                "name": "Juego Frances",
                "description": "Aprende vocabulario de frances.",
                "url": "/site/juego-frances/",
                "repo": "https://github.com/enriqwe/JuegoFrances",
                "accent": "#2563eb",
            },
            {
                "key": "aprende-a-escribir",
                "name": "Aprende a escribir",
                "description": "Practica de escritura con ordenador.",
                "url": "/site/aprende-a-escribir/",
                "repo": "https://github.com/enriqwe/aprendeaescribir",
                "accent": "#16a34a",
            },
            {
                "key": "cosmotablas1",
                "name": "Cosmotablas1",
                "description": "Aprende a multiplicar en el espacio.",
                "url": "https://cosmotablas1.vercel.app",
                "repo": "https://github.com/enriqwe/Cosmotablas1",
                "accent": "#7c3aed",
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
                "key": "regulacion",
                "name": "Regulacion",
                "description": "Proyecto publicado en GitHub Pages.",
                "url": "/site/regulacion/",
                "repo": "https://github.com/enriqwe/Regulaci-n",
                "accent": "#64748b",
            },
        ],
    },
]

FEATURED = [
    {"key": "alexia", "name": "Alexia", "url": "/alexia/", "label": "Colegio"},
    {"key": "facturas-alexia", "name": "Facturas", "url": "/facturas/", "label": "Colegio"},
    {"key": "gastos", "name": "Gastos", "url": "/gastos/", "label": "Finanzas"},
    {"key": "editor-mapas-v2", "name": "Mapas v2", "url": "/site/editor-mapas-v2/", "label": "Tool"},
    {"key": "juegos", "name": "Juegos", "url": "#juegos", "label": "Seccion"},
]


SITE_ACCESS = {
    "aprende-a-escribir": "aprende-a-escribir",
    "calendario": "calendario",
    "canvas": "canvas",
    "editor-mapas": "editor-mapas",
    "editor-mapas-v2": "editor-mapas-v2",
    "juego-frances": "juego-frances",
    "mision-cuerpo-humano": "mision-cuerpo-humano",
    "regulacion": "regulacion",
}


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
      --glow: rgba(232,180,79,.24);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at 18% 0%, rgba(232,180,79,.16), transparent 28%),
        radial-gradient(circle at 88% 12%, rgba(18,185,129,.12), transparent 24%),
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
    .top-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }
    .admin-link {
      border: 1px solid var(--line);
      background: rgba(17,24,39,.8);
      color: var(--text);
      border-radius: 10px;
      padding: 10px 12px;
      font-weight: 700;
      text-decoration: none;
    }
    .user-chip { color: var(--muted); font-size: 13px; }
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
      background: linear-gradient(180deg, rgba(24,33,50,.9), rgba(18,24,38,.84));
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
    .quick a:hover, .card:hover { border-color: rgba(232,180,79,.55); transform: translateY(-2px); }
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
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; }
    .card {
      min-height: 184px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      border: 1px solid var(--line);
      background:
        radial-gradient(circle at 88% 0%, color-mix(in srgb, var(--accent) 24%, transparent), transparent 34%),
        linear-gradient(180deg, rgba(24,33,50,.96), rgba(15,21,34,.94));
      border-radius: 8px;
      padding: 16px;
      text-decoration: none;
      color: var(--text);
      position: relative;
      overflow: hidden;
      transition: border-color .16s ease, transform .16s ease, box-shadow .16s ease;
    }
    .card::before {
      content: "";
      position: absolute;
      inset: 0 0 auto 0;
      height: 5px;
      background: var(--accent);
    }
    .card:hover { box-shadow: 0 20px 60px color-mix(in srgb, var(--accent) 16%, rgba(0,0,0,.25)); }
    .card-top { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-top: 6px; }
    .app-mark {
      width: 46px;
      height: 46px;
      border-radius: 8px;
      display: grid;
      place-items: center;
      background: var(--accent);
      color: #07111f;
      font-size: 21px;
      font-weight: 950;
      box-shadow: 0 10px 26px color-mix(in srgb, var(--accent) 22%, transparent);
    }
    .arrow {
      width: 38px;
      height: 38px;
      border-radius: 999px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(255,255,255,.16);
      background: rgba(12,17,29,.58);
      color: var(--text);
      font-weight: 950;
    }
    .card h3 { margin: 16px 0 8px; font-size: 21px; letter-spacing: 0; }
    .card p { margin: 0; color: var(--muted); line-height: 1.45; }
    .open-label { color: var(--text); font-weight: 850; margin-top: 18px; font-size: 14px; }
    .empty {
      border: 1px solid var(--line);
      background: rgba(18,24,38,.86);
      border-radius: 8px;
      padding: 22px;
      color: var(--muted);
    }
    @media (max-width: 760px) {
      header { align-items: flex-start; padding: 16px; }
      .hero { grid-template-columns: 1fr; }
      .section-head { align-items: flex-start; flex-direction: column; }
      .subtitle { font-size: 13px; }
      .top-actions { justify-content: flex-start; width: 100%; }
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
    <div class="top-actions">
      <span class="user-chip">{{ current_user }}</span>
      {% if is_admin %}<a class="admin-link" href="/permissions">Permisos</a>{% endif %}
      <form method="post" action="/logout"><button class="logout" type="submit">Salir</button></form>
    </div>
  </header>
  <main>
    <section class="hero">
      <div class="summary">
        <h2>Todo a dos clics.</h2>
        <p>Accesos privados a colegio, finanzas, tools y juegos. Las secciones estan pensadas para abrir rapido lo que necesitas sin buscar entre repositorios.</p>
      </div>
      <nav class="quick" aria-label="Accesos principales">
        <div class="quick-title">Accesos rapidos</div>
        {% for item in featured %}
        <a href="{{ item.url }}"><span>{{ item.name }}</span><small>{{ item.label }} -></small></a>
        {% endfor %}
      </nav>
    </section>
    {% if not sections %}
    <div class="empty">Tu usuario no tiene webs asignadas todavía.</div>
    {% endif %}
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
        <a class="card" href="{{ app.url }}" style="--accent: {{ app.accent }}" aria-label="Abrir {{ app.name }}">
          <div>
            <div class="card-top">
              <div class="app-mark">{{ app.name[:1] }}</div>
              <div class="arrow">-></div>
            </div>
            <h3>{{ app.name }}</h3>
            <p>{{ app.description }}</p>
          </div>
          <div class="open-label">Abrir</div>
        </a>
        {% endfor %}
      </div>
    </section>
      {% endfor %}
  </main>
</body>
</html>"""


PERMISSIONS_HTML = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Permisos · Enrique</title>
  <style>
    :root { color-scheme: dark; --bg:#0c111d; --panel:#121826; --line:#273244; --text:#f3f6fb; --muted:#9aa7bb; --brand:#e8b44f; --ok:#12b981; }
    * { box-sizing: border-box; }
    body { margin:0; min-height:100vh; background:linear-gradient(135deg,#0c111d,#141b2a 52%,#0c111d); color:var(--text); font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif; }
    header { display:flex; justify-content:space-between; align-items:center; gap:14px; padding:22px clamp(16px,4vw,44px); background:rgba(12,17,29,.88); border-bottom:1px solid rgba(148,163,184,.18); position:sticky; top:0; z-index:5; }
    h1 { margin:0; font-size:clamp(24px,4vw,38px); letter-spacing:0; }
    a { color:var(--text); }
    main { width:min(1180px,calc(100vw - 32px)); margin:26px auto 54px; }
    .back { border:1px solid var(--line); border-radius:10px; padding:10px 12px; text-decoration:none; background:rgba(18,24,38,.86); font-weight:800; }
    .panel { border:1px solid var(--line); background:rgba(18,24,38,.88); border-radius:8px; padding:18px; margin-top:16px; }
    .user-head { display:flex; justify-content:space-between; align-items:start; gap:16px; border-bottom:1px solid rgba(148,163,184,.16); padding-bottom:14px; margin-bottom:14px; }
    .controls { display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
    .email { font-size:20px; font-weight:850; }
    .role { color:var(--muted); margin-top:4px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:10px; }
    label { display:flex; align-items:center; gap:10px; border:1px solid var(--line); background:rgba(12,17,29,.72); border-radius:8px; padding:12px; min-height:48px; }
    input[type=checkbox] { width:18px; height:18px; accent-color:var(--ok); }
    button { border:0; border-radius:10px; padding:11px 14px; background:var(--brand); color:#17120a; font-weight:900; cursor:pointer; }
    button.secondary { border:1px solid var(--line); background:rgba(12,17,29,.72); color:var(--text); }
    .disabled { opacity:.64; }
    .note { color:var(--muted); line-height:1.5; }
    @media(max-width:760px){ header{align-items:flex-start; flex-direction:column;} .user-head{flex-direction:column;} }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Gestion de permisos</h1>
      <div class="note">Solo visible para administradores.</div>
    </div>
    <a class="back" href="/">Volver</a>
  </header>
  <main>
    {% for user in users %}
    <form class="panel" method="post">
      <input type="hidden" name="email" value="{{ user.email }}">
      <div class="user-head">
        <div>
          <div class="email">{{ user.email }}</div>
          <div class="role">{{ "Administrador" if user.role == "admin" else "Usuario" }}</div>
        </div>
        {% if user.role != "admin" %}
        <div class="controls">
          <button class="secondary" type="button" data-action="all">Marcar todo</button>
          <button class="secondary" type="button" data-action="none">Quitar todo</button>
          <button type="submit">Guardar permisos</button>
        </div>
        {% endif %}
      </div>
      {% if user.role == "admin" %}
      <div class="note">Los administradores tienen acceso completo y son los unicos que ven esta seccion.</div>
      {% else %}
      <div class="grid">
        {% for access in access_list %}
        <label>
          <input type="checkbox" name="access_key" value="{{ access.key }}" {% if access.key in permissions.get(user.email, []) %}checked{% endif %}>
          <span>{{ access.name }}</span>
        </label>
        {% endfor %}
      </div>
      {% endif %}
    </form>
    {% endfor %}
  </main>
  <script>
    document.querySelectorAll("button[data-action]").forEach((button) => {
      button.addEventListener("click", () => {
        const checked = button.dataset.action === "all";
        button.closest("form").querySelectorAll("input[type=checkbox]").forEach((input) => {
          input.checked = checked;
        });
      });
    });
  </script>
</body>
</html>"""


COMUNICADOS_HTML = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Comunicados Alexia</title>
  <style>
    :root { color-scheme: dark; --bg:#0c111d; --panel:#121826; --line:#273244; --text:#f3f6fb; --muted:#9aa7bb; --brand:#e8b44f; --ok:#12b981; }
    * { box-sizing: border-box; }
    body { margin:0; min-height:100vh; background:linear-gradient(135deg,#0c111d,#141b2a 52%,#0c111d); color:var(--text); font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif; }
    header { display:flex; justify-content:space-between; align-items:start; gap:16px; padding:22px clamp(16px,4vw,44px); background:rgba(12,17,29,.88); border-bottom:1px solid rgba(148,163,184,.18); position:sticky; top:0; z-index:5; }
    h1 { margin:0; font-size:clamp(24px,4vw,38px); letter-spacing:0; }
    main { width:min(1240px,calc(100vw - 32px)); margin:24px auto 54px; }
    a { color:var(--text); }
    .back { border:1px solid var(--line); border-radius:10px; padding:10px 12px; text-decoration:none; background:rgba(18,24,38,.86); font-weight:800; white-space:nowrap; }
    .note { color:var(--muted); line-height:1.45; margin-top:6px; }
    .toolbar { display:grid; grid-template-columns:minmax(0,1fr) 190px 170px; gap:10px; margin-bottom:14px; }
    input, select { width:100%; border:1px solid var(--line); background:rgba(12,17,29,.78); color:var(--text); border-radius:10px; padding:11px 12px; }
    .list { display:grid; gap:12px; }
    details { border:1px solid var(--line); background:rgba(18,24,38,.88); border-radius:8px; padding:14px; }
    summary { cursor:pointer; list-style:none; }
    summary::-webkit-details-marker { display:none; }
    .row { display:grid; grid-template-columns:120px minmax(0,1fr) 160px; gap:14px; align-items:start; }
    .date, .from, .flag { color:var(--muted); font-size:13px; }
    .title { font-weight:850; font-size:18px; line-height:1.25; }
    .body { white-space:pre-wrap; color:#dce6fb; line-height:1.5; border-top:1px solid rgba(148,163,184,.16); margin-top:13px; padding-top:13px; }
    .chips { display:flex; flex-wrap:wrap; gap:6px; margin-top:10px; }
    .chip { border:1px solid var(--line); background:rgba(12,17,29,.78); color:var(--muted); border-radius:999px; padding:4px 8px; font-size:12px; }
    @media(max-width:780px){ header{flex-direction:column;} .toolbar{grid-template-columns:1fr;} .row{grid-template-columns:1fr;} }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Comunicados Alexia</h1>
      <div class="note">{{ comunicados|length }} comunicados indexados · actualizado {{ updated_at }}</div>
    </div>
    <a class="back" href="/">Volver</a>
  </header>
  <main>
    <div class="toolbar">
      <input id="q" placeholder="Buscar por titulo, texto, remitente...">
      <select id="flag">
        <option value="">Todos</option>
        <option value="action">Requieren accion</option>
        <option value="calendar">Calendario</option>
        <option value="review">Pendientes de revisar</option>
      </select>
      <select id="sender">
        <option value="">Todos los remitentes</option>
        {% for sender in senders %}<option value="{{ sender }}">{{ sender }}</option>{% endfor %}
      </select>
    </div>
    <section class="list" id="list">
      {% for item in comunicados %}
      <details data-text="{{ (item.title ~ ' ' ~ item.from ~ ' ' ~ item.detailText)|lower|e }}" data-sender="{{ item.from|e }}" data-action="{{ item.flags.requiresAction }}" data-calendar="{{ item.flags.calendar }}" data-review="{{ item.flags.needsHumanReview }}">
        <summary>
          <div class="row">
            <div class="date">{{ item.dateIso or item.dateText }}</div>
            <div>
              <div class="title">{{ item.title }}</div>
              <div class="from">{{ item.from }}</div>
            </div>
            <div class="flag">{{ item.source }}</div>
          </div>
        </summary>
        <div class="chips">
          {% if item.flags.requiresAction %}<span class="chip">Accion</span>{% endif %}
          {% if item.flags.calendar %}<span class="chip">Calendario</span>{% endif %}
          {% if item.flags.needsHumanReview %}<span class="chip">Revisar</span>{% endif %}
          {% for tag in item.flags.tags %}<span class="chip">{{ tag }}</span>{% endfor %}
        </div>
        <div class="body">{{ item.detailText }}</div>
      </details>
      {% endfor %}
    </section>
  </main>
  <script>
    const q = document.getElementById("q");
    const flag = document.getElementById("flag");
    const sender = document.getElementById("sender");
    const rows = [...document.querySelectorAll("details")];
    function applyFilters() {
      const query = q.value.trim().toLowerCase();
      const selectedFlag = flag.value;
      const selectedSender = sender.value;
      rows.forEach((row) => {
        const okQuery = !query || row.dataset.text.includes(query);
        const okSender = !selectedSender || row.dataset.sender === selectedSender;
        let okFlag = true;
        if (selectedFlag === "action") okFlag = row.dataset.action === "True";
        if (selectedFlag === "calendar") okFlag = row.dataset.calendar === "True";
        if (selectedFlag === "review") okFlag = row.dataset.review === "True";
        row.style.display = okQuery && okSender && okFlag ? "" : "none";
      });
    }
    [q, flag, sender].forEach((el) => el.addEventListener("input", applyFilters));
  </script>
</body>
</html>"""


def all_access_items() -> list[dict]:
    items = []
    for section in SECTIONS:
        items.extend(section["items"])
    return items


def allowed(access_key: str, permissions: set[str]) -> bool:
    return "*" in permissions or access_key in permissions


def visible_sections(email: str) -> list[dict]:
    permissions = auth.permissions_for(email)
    sections = []
    for section in SECTIONS:
        items = [item for item in section["items"] if allowed(item["key"], permissions)]
        if items:
            copy = dict(section)
            copy["items"] = items
            sections.append(copy)
    return sections


def visible_featured(email: str, sections: list[dict]) -> list[dict]:
    permissions = auth.permissions_for(email)
    visible_section_ids = {section["id"] for section in sections}
    items = []
    for item in FEATURED:
        if item["key"] == "juegos":
            if "juegos" in visible_section_ids:
                items.append(item)
        elif allowed(item["key"], permissions):
            items.append(item)
    return items


def require_access(access_key: str):
    if not allowed(access_key, auth.permissions_for(session.get("user_email"))):
        abort(403)


def ensure_seed_users() -> None:
    admin = auth.user(ADMIN_EMAIL)
    if not admin:
        return
    auth.ensure_user_with_password_hash(GABI_EMAIL, admin["password_hash"], role="user", confirmed=True)
    all_keys = [item["key"] for item in all_access_items() if item["key"] != "enriqwe-landing"]
    gabi_permissions = auth.permissions_for(GABI_EMAIL)
    if not gabi_permissions:
        auth.set_permissions(GABI_EMAIL, all_keys)
    else:
        missing_default_keys = {"facturas-alexia"} - gabi_permissions
        if missing_default_keys:
            auth.set_permissions(GABI_EMAIL, sorted(gabi_permissions | missing_default_keys))


ensure_seed_users()


@app.get("/")
@auth.require_login
def index():
    current_user = session.get("user_email")
    sections = visible_sections(current_user)
    return render_template_string(
        LANDING_HTML,
        sections=sections,
        featured=visible_featured(current_user, sections),
        current_user=current_user,
        is_admin=auth.is_admin(current_user),
    )


@app.get("/permissions")
@auth.require_admin
def permissions():
    return render_template_string(
        PERMISSIONS_HTML,
        users=auth.users(),
        access_list=all_access_items(),
        permissions=auth.all_permissions(),
    )


@app.post("/permissions")
@auth.require_admin
def update_permissions():
    email = request.form.get("email")
    user = auth.user(email)
    if not user or user["role"] == "admin":
        return redirect(url_for("permissions"))
    auth.set_permissions(email, request.form.getlist("access_key"))
    return redirect(url_for("permissions"))


def comunicados_data():
    if not COMUNICADOS_FILE.exists():
        return {"updatedAt": "sin datos", "comunicados": []}
    data = json.loads(COMUNICADOS_FILE.read_text(encoding="utf-8"))
    data.setdefault("comunicados", [])
    for item in data["comunicados"]:
        item.setdefault("flags", {})
        item["flags"].setdefault("requiresAction", False)
        item["flags"].setdefault("calendar", False)
        item["flags"].setdefault("needsHumanReview", False)
        item["flags"].setdefault("tags", [])
        item.setdefault("title", "")
        item.setdefault("from", "")
        item.setdefault("detailText", "")
        item.setdefault("dateIso", "")
        item.setdefault("dateText", "")
        item.setdefault("source", "alexia")
    data["comunicados"].sort(key=lambda item: item.get("dateIso") or item.get("dateText") or "", reverse=True)
    return data


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
    access_key = SITE_ACCESS.get(slug)
    if not access_key:
        abort(404)
    require_access(access_key)
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
@auth.require_login
def alexia_comunicados():
    require_access("alexia")
    data = comunicados_data()
    senders = sorted({item.get("from", "") for item in data["comunicados"] if item.get("from")})
    return render_template_string(
        COMUNICADOS_HTML,
        comunicados=data["comunicados"],
        updated_at=data.get("updatedAt", "sin datos"),
        senders=senders,
    )


@app.get("/facturas/")
@app.get("/facturas/<path:path>")
@auth.require_login
def facturas_dashboard(path: str = "index.html"):
    require_access("facturas-alexia")
    return serve_static_dashboard("facturas", path or "index.html")


@app.get("/alexia/facturas/")
@app.get("/alexia/facturas/<path:path>")
@auth.require_login
def alexia_facturas_alias(path: str = ""):
    require_access("facturas-alexia")
    return redirect(f"/facturas/{path}")


@app.get("/alexia/pdf/<path:path>")
@auth.require_login
def alexia_pdf_legacy(path: str):
    require_access("facturas-alexia")
    return serve_static_dashboard("facturas", f"pdf/{path}")


@app.get("/gastos/")
@app.get("/gastos/<path:path>")
@auth.require_login
def gastos_dashboard(path: str = "index.html"):
    require_access("gastos")
    return serve_static_dashboard("gastos", path or "index.html")


@app.route("/upload", methods=["POST"])
@auth.require_login
def gastos_upload_proxy():
    require_access("gastos")
    return proxy_request(PROXIES["gastos"], "upload")


def main():
    if init_user_from_cli(auth, sys.argv):
        return
    port = int(os.environ.get("PORT", "8090"))
    app.run(host="0.0.0.0", port=port, threaded=True)


if __name__ == "__main__":
    main()
