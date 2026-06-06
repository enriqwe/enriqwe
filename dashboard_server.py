#!/usr/bin/env python3
import os
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from flask import Flask, Response, abort, flash, redirect, render_template_string, request, send_from_directory, session, url_for

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
                "icon": "🔔",
            },
            {
                "key": "facturas-alexia",
                "name": "Facturas Alexia",
                "description": "Dashboard de facturas del colegio con PDFs.",
                "url": "/facturas/",
                "repo": "https://github.com/enriqwe/Alexia",
                "accent": "#0f766e",
                "icon": "🧾",
            },
            {
                "key": "gastos",
                "name": "Control de gastos",
                "description": "Dashboard de movimientos y categorias.",
                "url": "/gastos/",
                "repo": "https://github.com/enriqwe/Gestion-de-Gastos",
                "accent": "#f59e0b",
                "icon": "📊",
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
                "icon": "🗺️",
            },
            {
                "key": "editor-mapas",
                "name": "Editor de Mapas",
                "description": "Version anterior del editor de mapas.",
                "url": "/site/editor-mapas/",
                "repo": "https://github.com/enriqwe/Editor-de-Mapas",
                "accent": "#0f766e",
                "icon": "📍",
            },
            {
                "key": "canvas",
                "name": "Canvas",
                "description": "Canvas infinito para presentaciones.",
                "url": "/site/canvas/",
                "repo": "https://github.com/enriqwe/Canvas",
                "accent": "#be185d",
                "icon": "✏️",
            },
            {
                "key": "calendario",
                "name": "Calendario",
                "description": "Aplicacion de calendario publicada.",
                "url": "/site/calendario/",
                "repo": "https://github.com/enriqwe/Calendario",
                "accent": "#0284c7",
                "icon": "📅",
            },
            {
                "key": "onevenue-todo",
                "name": "OneVenue To-Do",
                "description": "Tablero privado para ordenar y tachar tareas de trabajo.",
                "url": "/site/onevenue-todo/",
                "repo": "https://github.com/enriqwe/onevenue-todo",
                "accent": "#1769e0",
                "icon": "✅",
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
                "icon": "🧠",
            },
            {
                "key": "juego-frances",
                "name": "Juego Frances",
                "description": "Aprende vocabulario de frances.",
                "url": "/site/juego-frances/",
                "repo": "https://github.com/enriqwe/JuegoFrances",
                "accent": "#2563eb",
                "icon": "🇫🇷",
            },
            {
                "key": "aprende-a-escribir",
                "name": "Aprende a escribir",
                "description": "Practica de escritura con ordenador.",
                "url": "/site/aprende-a-escribir/",
                "repo": "https://github.com/enriqwe/aprendeaescribir",
                "accent": "#16a34a",
                "icon": "✍️",
            },
            {
                "key": "cosmotablas1",
                "name": "Cosmotablas1",
                "description": "Aprende a multiplicar en el espacio.",
                "url": "https://cosmotablas1.vercel.app",
                "repo": "https://github.com/enriqwe/Cosmotablas1",
                "accent": "#7c3aed",
                "icon": "🚀",
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
                "icon": "⚙️",
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
    "onevenue-todo": "onevenue-todo",
    "regulacion": "regulacion",
}

ICONS = {
    "alexia": '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"></path><path d="M10 21h4"></path>',
    "facturas-alexia": '<path d="M6 3h12v18l-2-1-2 1-2-1-2 1-2-1-2 1V3z"></path><path d="M9 8h6"></path><path d="M9 12h6"></path><path d="M9 16h4"></path>',
    "gastos": '<path d="M4 19V5"></path><path d="M4 19h16"></path><path d="M8 16v-5"></path><path d="M12 16V8"></path><path d="M16 16v-9"></path>',
    "editor-mapas-v2": '<path d="M9 18l-6 3V6l6-3 6 3 6-3v15l-6 3-6-3z"></path><path d="M9 3v15"></path><path d="M15 6v15"></path>',
    "editor-mapas": '<path d="M12 21s7-5 7-11a7 7 0 1 0-14 0c0 6 7 11 7 11z"></path><circle cx="12" cy="10" r="2"></circle>',
    "canvas": '<path d="M4 20h16"></path><path d="M6 18l10-10 2 2L8 20H6v-2z"></path><path d="M14 6l2-2 4 4-2 2"></path>',
    "calendario": '<rect x="4" y="5" width="16" height="15" rx="2"></rect><path d="M8 3v4"></path><path d="M16 3v4"></path><path d="M4 10h16"></path>',
    "onevenue-todo": '<path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>',
    "mision-cuerpo-humano": '<path d="M12 3a4 4 0 0 0-4 4v3a4 4 0 0 0 8 0V7a4 4 0 0 0-4-4z"></path><path d="M6 21v-3a6 6 0 0 1 12 0v3"></path><path d="M9 10h6"></path>',
    "juego-frances": '<path d="M5 5h14v14H5z"></path><path d="M8 9h8"></path><path d="M8 13h5"></path><path d="M15 13l2 3"></path>',
    "aprende-a-escribir": '<path d="M4 20h16"></path><path d="M7 16l8-8 3 3-8 8H7v-3z"></path><path d="M14 7l3 3"></path>',
    "cosmotablas1": '<path d="M12 2c3 2 5 5 5 8 0 5-5 9-5 9s-5-4-5-9c0-3 2-6 5-8z"></path><path d="M9 21h6"></path><circle cx="12" cy="9" r="2"></circle>',
    "regulacion": '<circle cx="12" cy="12" r="3"></circle><path d="M12 2v3"></path><path d="M12 19v3"></path><path d="M2 12h3"></path><path d="M19 12h3"></path><path d="M4.9 4.9l2.1 2.1"></path><path d="M17 17l2.1 2.1"></path><path d="M19.1 4.9 17 7"></path><path d="M7 17l-2.1 2.1"></path>',
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
      --bg: #080c16;
      --panel: rgba(15, 23, 42, .78);
      --panel-2: rgba(24, 33, 50, .76);
      --line: rgba(148, 163, 184, .22);
      --text: #f7fbff;
      --muted: #a9b8ca;
      --brand: #35d4ff;
      --gold: #f3bf55;
      --green: #37e0a3;
      --pink: #ff6fb1;
      --glow: rgba(53, 212, 255, .3);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at 14% 12%, rgba(53,212,255,.2), transparent 25%),
        radial-gradient(circle at 84% 8%, rgba(243,191,85,.16), transparent 24%),
        radial-gradient(circle at 62% 88%, rgba(55,224,163,.14), transparent 28%),
        linear-gradient(135deg, #080c16 0%, #12192a 46%, #090e19 100%);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      overflow-x: hidden;
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px);
      background-size: 52px 52px;
      mask-image: linear-gradient(to bottom, rgba(0,0,0,.55), transparent 80%);
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px clamp(16px, 4vw, 44px);
      border-bottom: 1px solid rgba(148,163,184,.14);
      background: rgba(8,12,22,.78);
      backdrop-filter: blur(18px);
      position: sticky;
      top: 0;
      z-index: 5;
    }
    .brand { display: flex; align-items: center; gap: 14px; min-width: 0; }
    .mark {
      width: 48px;
      height: 48px;
      border-radius: 16px;
      display: grid;
      place-items: center;
      background: linear-gradient(135deg, var(--brand), var(--green));
      color: #07111f;
      font-weight: 900;
      font-size: 22px;
      box-shadow: 0 0 28px rgba(53,212,255,.28);
    }
    h1 { margin: 0; font-size: clamp(23px, 4vw, 36px); letter-spacing: 0; }
    .subtitle { color: var(--muted); margin-top: 3px; font-size: 14px; }
    .logout {
      border: 1px solid var(--line);
      background: rgba(15,23,42,.72);
      color: var(--text);
      border-radius: 14px;
      padding: 10px 12px;
      font-weight: 700;
      cursor: pointer;
    }
    .top-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }
    .admin-link {
      border: 1px solid var(--line);
      background: linear-gradient(135deg, rgba(53,212,255,.14), rgba(243,191,85,.12));
      color: var(--text);
      border-radius: 14px;
      padding: 10px 12px;
      font-weight: 700;
      text-decoration: none;
    }
    .user-chip { color: var(--muted); font-size: 13px; }
    main { width: min(1220px, calc(100vw - 28px)); margin: 14px auto 40px; position: relative; z-index: 1; }
    .section {
      border: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(24,33,50,.74), rgba(12,18,31,.78));
      border-radius: 22px;
      box-shadow: 0 24px 70px rgba(0,0,0,.28);
      backdrop-filter: blur(18px);
    }
    .card:hover { border-color: rgba(53,212,255,.55); transform: translateY(-3px); }
    .section { margin-top: 14px; padding: clamp(14px, 2.4vw, 20px); scroll-margin-top: 100px; }
    .section-head {
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: center;
      margin-bottom: 12px;
      border-bottom: 1px solid rgba(148,163,184,.14);
      padding-bottom: 12px;
    }
    .section h2 { margin: 0; font-size: clamp(21px, 2.6vw, 29px); letter-spacing: 0; }
    .section p { margin: 4px 0 0; color: var(--muted); line-height: 1.35; font-size: 14px; }
    .count {
      flex: 0 0 auto;
      color: var(--text);
      border: 1px solid var(--line);
      border-left: 5px solid var(--section-accent);
      background: rgba(8,12,22,.56);
      border-radius: 999px;
      padding: 7px 10px;
      font-weight: 800;
      font-size: 12px;
    }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 10px; }
    .card {
      min-height: 94px;
      display: flex;
      align-items: center;
      gap: 13px;
      border: 1px solid rgba(148,163,184,.18);
      background:
        radial-gradient(circle at 98% 0%, color-mix(in srgb, var(--accent) 18%, transparent), transparent 28%),
        linear-gradient(180deg, rgba(26,37,58,.92), rgba(10,16,28,.9));
      border-radius: 16px;
      padding: 13px 14px;
      text-decoration: none;
      color: var(--text);
      position: relative;
      overflow: hidden;
      transition: border-color .16s ease, transform .16s ease, box-shadow .16s ease;
    }
    .card:hover { box-shadow: 0 16px 38px color-mix(in srgb, var(--accent) 14%, rgba(0,0,0,.28)); }
    .card-main {
      min-width: 0;
      flex: 1 1 auto;
      position: relative;
      z-index: 1;
    }
    .app-mark {
      flex: 0 0 auto;
      width: 44px;
      height: 44px;
      border-radius: 14px;
      display: grid;
      place-items: center;
      background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 88%, white), var(--accent));
      color: #07111f;
      font-size: 22px;
      font-weight: 900;
      box-shadow: 0 10px 24px color-mix(in srgb, var(--accent) 22%, transparent);
      position: relative;
      z-index: 1;
    }
    .app-mark svg {
      width: 23px;
      height: 23px;
      stroke: currentColor;
      stroke-width: 2.3;
      fill: none;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    .card h3 { margin: 0 0 4px; font-size: 17px; letter-spacing: 0; line-height: 1.18; }
    .card p { margin: 0; color: var(--muted); line-height: 1.3; font-size: 13px; }
    .empty {
      border: 1px solid var(--line);
      background: rgba(18,24,38,.86);
      border-radius: 18px;
      padding: 22px;
      color: var(--muted);
    }
    @media (max-width: 760px) {
      header { align-items: flex-start; flex-direction: column; padding: 14px; position: relative; }
      .brand { width: 100%; }
      .mark { width: 42px; height: 42px; border-radius: 14px; }
      main { width: min(1220px, calc(100vw - 18px)); margin-top: 9px; }
      .section { border-radius: 18px; padding: 13px; margin-top: 10px; }
      .section-head { align-items: flex-start; flex-direction: column; gap: 8px; }
      .subtitle { font-size: 13px; }
      .top-actions { justify-content: flex-start; width: 100%; }
      .logout { padding: 9px 10px; }
      .grid { grid-template-columns: 1fr; }
      .card { min-height: 78px; padding: 11px 12px; gap: 11px; }
      .app-mark { width: 38px; height: 38px; border-radius: 12px; }
      .app-mark svg { width: 20px; height: 20px; }
      .card h3 { font-size: 16px; }
      .card p { font-size: 12px; }
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
          <div class="app-mark">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              {{ app.icon_svg|safe }}
            </svg>
          </div>
          <div class="card-main">
            <h3>{{ app.name }}</h3>
            <p>{{ app.description }}</p>
          </div>
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
    :root { color-scheme: dark; --bg:#0c111d; --panel:#121826; --line:#273244; --text:#f3f6fb; --muted:#9aa7bb; --brand:#e8b44f; --ok:#12b981; --danger:#ef4444; }
    * { box-sizing: border-box; }
    body { margin:0; min-height:100vh; background:linear-gradient(135deg,#0c111d,#141b2a 52%,#0c111d); color:var(--text); font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif; }
    header { display:flex; justify-content:space-between; align-items:center; gap:14px; padding:22px clamp(16px,4vw,44px); background:rgba(12,17,29,.9); border-bottom:1px solid rgba(148,163,184,.18); position:sticky; top:0; z-index:5; backdrop-filter:blur(16px); }
    h1 { margin:0; font-size:clamp(24px,4vw,38px); letter-spacing:0; }
    h2 { margin:0 0 12px; font-size:18px; }
    a { color:var(--text); }
    main { width:min(1040px,calc(100vw - 28px)); margin:20px auto 54px; display:grid; gap:14px; }
    .back { border:1px solid var(--line); border-radius:10px; padding:10px 12px; text-decoration:none; background:rgba(18,24,38,.86); font-weight:800; }
    .panel, details.user { border:1px solid var(--line); background:rgba(18,24,38,.9); border-radius:8px; padding:14px; }
    .create-grid { display:grid; grid-template-columns:minmax(0,1.5fr) minmax(160px,.8fr) auto; gap:10px; align-items:end; }
    label.field { display:grid; gap:6px; color:var(--muted); font-size:13px; }
    input[type=email], input[type=password] { width:100%; border:1px solid var(--line); background:rgba(12,17,29,.72); color:var(--text); border-radius:10px; padding:11px 12px; min-height:42px; }
    button { border:0; border-radius:10px; padding:11px 14px; background:var(--brand); color:#17120a; font-weight:900; cursor:pointer; min-height:42px; }
    button.secondary { border:1px solid var(--line); background:rgba(12,17,29,.72); color:var(--text); }
    button.danger { background:rgba(239,68,68,.16); color:#fecaca; border:1px solid rgba(239,68,68,.42); }
    .note { color:var(--muted); line-height:1.45; }
    .flash { border:1px solid rgba(232,180,79,.35); background:rgba(232,180,79,.12); border-radius:8px; padding:10px 12px; color:#ffe8b7; }
    .list { display:grid; gap:10px; }
    summary { cursor:pointer; list-style:none; display:grid; grid-template-columns:minmax(0,1fr) auto; gap:10px; align-items:center; }
    summary::-webkit-details-marker { display:none; }
    .identity { min-width:0; }
    .email { font-size:17px; font-weight:850; overflow-wrap:anywhere; }
    .meta { color:var(--muted); margin-top:4px; font-size:13px; }
    .count { border:1px solid var(--line); color:#dce6fb; background:rgba(12,17,29,.72); border-radius:999px; padding:6px 10px; font-size:12px; white-space:nowrap; }
    .body { border-top:1px solid rgba(148,163,184,.16); margin-top:13px; padding-top:13px; display:grid; gap:12px; }
    .controls { display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
    .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(210px,1fr)); gap:8px; }
    .perm { display:flex; align-items:center; gap:9px; border:1px solid var(--line); background:rgba(12,17,29,.72); border-radius:8px; padding:10px; min-height:42px; }
    input[type=checkbox] { width:18px; height:18px; accent-color:var(--ok); flex:0 0 auto; }
    .inline-form { display:flex; gap:8px; flex-wrap:wrap; align-items:end; justify-content:flex-end; }
    .inline-form .field { min-width:180px; flex:1 1 220px; }
    .row-actions { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:10px; align-items:end; }
    @media(max-width:760px){
      header{align-items:flex-start; flex-direction:column;}
      .create-grid, .row-actions{grid-template-columns:1fr;}
      summary{grid-template-columns:1fr;}
      .controls,.inline-form{justify-content:stretch;}
      button{width:100%;}
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Gestion de permisos</h1>
      <div class="note">{{ users|length }} usuarios · permisos colapsados por usuario.</div>
    </div>
    <a class="back" href="/">Volver</a>
  </header>
  <main>
    {% for message in get_flashed_messages() %}<div class="flash">{{ message }}</div>{% endfor %}
    <section class="panel">
      <h2>Alta de usuario</h2>
      <form class="create-grid" method="post">
        <input type="hidden" name="operation" value="create">
        <label class="field">Email<input name="email" type="email" autocomplete="email" required></label>
        <label class="field">Contraseña<input name="password" type="password" autocomplete="new-password" minlength="6" required></label>
        <button type="submit">Crear usuario</button>
      </form>
    </section>

    <section class="list">
      {% for user in users %}
      {% set user_permissions = permissions.get(user.email, []) %}
      {% set permission_count = access_list|length if user.role == "admin" else user_permissions|length %}
      <details class="user">
        <summary>
          <div class="identity">
            <div class="email">{{ user.email }}</div>
            <div class="meta">{{ "Administrador" if user.role == "admin" else "Usuario" }} · {{ "acceso completo" if user.role == "admin" else permission_count ~ " de " ~ access_list|length ~ " accesos" }}</div>
          </div>
          <span class="count">{{ permission_count }} permisos</span>
        </summary>
        <div class="body">
          {% if user.role == "admin" %}
          <div class="note">Los administradores tienen acceso completo y son los unicos que ven esta seccion.</div>
          {% else %}
          <form method="post">
            <input type="hidden" name="operation" value="permissions">
            <input type="hidden" name="email" value="{{ user.email }}">
            <div class="controls">
              <button class="secondary" type="button" data-action="all">Marcar todo</button>
              <button class="secondary" type="button" data-action="none">Quitar todo</button>
              <button type="submit">Guardar permisos</button>
            </div>
            <div class="grid">
              {% for access in access_list %}
              <label class="perm">
                <input type="checkbox" name="access_key" value="{{ access.key }}" {% if access.key in user_permissions %}checked{% endif %}>
                <span>{{ access.name }}</span>
              </label>
              {% endfor %}
            </div>
          </form>
          <div class="row-actions">
            <form class="inline-form" method="post">
              <input type="hidden" name="operation" value="password">
              <input type="hidden" name="email" value="{{ user.email }}">
              <label class="field">Nueva contraseña<input name="password" type="password" autocomplete="new-password" minlength="6" required></label>
              <button class="secondary" type="submit">Resetear contraseña</button>
            </form>
            <form method="post" onsubmit="return confirm('¿Eliminar {{ user.email }}?');">
              <input type="hidden" name="operation" value="delete">
              <input type="hidden" name="email" value="{{ user.email }}">
              <button class="danger" type="submit">Eliminar</button>
            </form>
          </div>
          {% endif %}
        </div>
      </details>
      {% endfor %}
    </section>
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
        items = []
        for item in section["items"]:
            if allowed(item["key"], permissions):
                visible_item = dict(item)
                visible_item["icon_svg"] = ICONS.get(item["key"], ICONS["regulacion"])
                items.append(visible_item)
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
    if not admin or auth.was_deleted(GABI_EMAIL):
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
    operation = request.form.get("operation") or "permissions"
    email = request.form.get("email")

    if operation == "create":
        password = request.form.get("password") or ""
        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.")
        elif not email:
            flash("Indica un email.")
        else:
            auth.create_or_update_user(email, password, confirmed=True)
            flash(f"Usuario creado: {auth.clean_email(email)}")
        return redirect(url_for("permissions"))

    user = auth.user(email)
    if not user:
        flash("Usuario no encontrado.")
        return redirect(url_for("permissions"))

    if operation == "password":
        password = request.form.get("password") or ""
        if auth.set_user_password(email, password):
            flash(f"Contraseña actualizada para {auth.clean_email(email)}.")
        else:
            flash("No se pudo actualizar la contraseña. Usa al menos 6 caracteres.")
        return redirect(url_for("permissions"))

    if operation == "delete":
        if auth.clean_email(email) == auth.clean_email(session.get("user_email")):
            flash("No puedes eliminar tu propio usuario desde aqui.")
        elif auth.delete_user(email):
            flash(f"Usuario eliminado: {auth.clean_email(email)}")
        else:
            flash("No se pudo eliminar el usuario.")
        return redirect(url_for("permissions"))

    if user["role"] == "admin":
        flash("Los administradores siempre tienen acceso completo.")
        return redirect(url_for("permissions"))

    auth.set_permissions(email, request.form.getlist("access_key"))
    flash(f"Permisos guardados para {auth.clean_email(email)}.")
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
    headers["X-OpenClaw-User"] = session.get("user_email", "")
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


@app.get("/upload-result")
@auth.require_login
def gastos_upload_result_proxy():
    require_access("gastos")
    return proxy_request(PROXIES["gastos"], "upload-result")


def main():
    if init_user_from_cli(auth, sys.argv):
        return
    port = int(os.environ.get("PORT", "8090"))
    app.run(host="0.0.0.0", port=port, threaded=True)


if __name__ == "__main__":
    main()
