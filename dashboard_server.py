#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from flask import Flask, render_template_string

from auth_core import AuthManager, init_user_from_cli


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
auth = AuthManager(BASE_DIR, "Enrique")
auth.init_app(app)


APPS = [
    {
        "name": "Alexia",
        "description": "Facturas y comunicados del colegio.",
        "url": "https://enriqwe.github.io/Alexia/",
        "repo": "https://github.com/enriqwe/Alexia",
        "accent": "#2dd4bf",
    },
    {
        "name": "Control de gastos",
        "description": "Dashboard de movimientos y categorias.",
        "url": "https://enriqwe.github.io/Gestion-de-Gastos/",
        "repo": "https://github.com/enriqwe/Gestion-de-Gastos",
        "accent": "#f59e0b",
    },
    {
        "name": "Mision cuerpo humano",
        "description": "Juego educativo publicado en GitHub Pages.",
        "url": "https://enriqwe.github.io/mision-cuerpo-humano/",
        "repo": "https://github.com/enriqwe/mision-cuerpo-humano",
        "accent": "#ef4444",
    },
    {
        "name": "Juego Frances",
        "description": "Practica visual de frances.",
        "url": "https://enriqwe.github.io/JuegoFrances/",
        "repo": "https://github.com/enriqwe/JuegoFrances",
        "accent": "#3b82f6",
    },
    {
        "name": "Aprende a escribir",
        "description": "Actividad para practicar escritura.",
        "url": "https://enriqwe.github.io/aprendeaescribir/",
        "repo": "https://github.com/enriqwe/aprendeaescribir",
        "accent": "#22c55e",
    },
    {
        "name": "Editor de Mapas v2",
        "description": "Herramienta visual para crear mapas.",
        "url": "https://enriqwe.github.io/Editor-de-Mapas-v2/",
        "repo": "https://github.com/enriqwe/Editor-de-Mapas-v2",
        "accent": "#a855f7",
    },
    {
        "name": "Editor de Mapas",
        "description": "Version anterior del editor de mapas.",
        "url": "https://enriqwe.github.io/Editor-de-Mapas/",
        "repo": "https://github.com/enriqwe/Editor-de-Mapas",
        "accent": "#8b5cf6",
    },
    {
        "name": "Calendario",
        "description": "Aplicacion de calendario publicada.",
        "url": "https://enriqwe.github.io/Calendario/",
        "repo": "https://github.com/enriqwe/Calendario",
        "accent": "#06b6d4",
    },
    {
        "name": "Canvas",
        "description": "Experimentos y utilidades de canvas.",
        "url": "https://enriqwe.github.io/Canvas/",
        "repo": "https://github.com/enriqwe/Canvas",
        "accent": "#ec4899",
    },
    {
        "name": "Regulacion",
        "description": "Proyecto publicado en GitHub Pages.",
        "url": "https://enriqwe.github.io/Regulaci-n/",
        "repo": "https://github.com/enriqwe/Regulaci-n",
        "accent": "#64748b",
    },
    {
        "name": "Cosmotablas1",
        "description": "Web principal publicada en Vercel.",
        "url": "https://cosmotablas1.vercel.app",
        "repo": "https://github.com/enriqwe/Cosmotablas1",
        "accent": "#14b8a6",
    },
    {
        "name": "Cosmotablas",
        "description": "Repositorio de Cosmotablas.",
        "url": "https://enriqwe.github.io/Cosmotablas/",
        "repo": "https://github.com/enriqwe/Cosmotablas",
        "accent": "#0ea5e9",
    },
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
      --bg: #0b1020;
      --panel: #111827;
      --panel-2: #172033;
      --line: #26324a;
      --text: #eef4ff;
      --muted: #aab7d4;
      --brand: #38bdf8;
      --ok: #2dd4bf;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at 12% 12%, rgba(56,189,248,.18), transparent 28%),
        radial-gradient(circle at 80% 0%, rgba(45,212,191,.16), transparent 24%),
        linear-gradient(135deg, #080c18 0%, #111827 48%, #0b1020 100%);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 24px clamp(18px, 4vw, 48px);
      border-bottom: 1px solid rgba(148,163,184,.16);
      background: rgba(8,12,24,.72);
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
      background: linear-gradient(135deg, var(--brand), var(--ok));
      color: #07111f;
      font-weight: 900;
      font-size: 21px;
    }
    h1 { margin: 0; font-size: clamp(24px, 4vw, 44px); letter-spacing: 0; }
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
    main { width: min(1180px, calc(100vw - 32px)); margin: 34px auto 54px; }
    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(280px, .85fr);
      gap: 18px;
      align-items: stretch;
      margin-bottom: 20px;
    }
    .summary, .quick {
      border: 1px solid var(--line);
      background: rgba(17,24,39,.78);
      border-radius: 8px;
      padding: clamp(18px, 3vw, 28px);
      box-shadow: 0 18px 60px rgba(0,0,0,.28);
    }
    .summary h2 { margin: 0 0 12px; font-size: clamp(28px, 5vw, 58px); line-height: 1.02; letter-spacing: 0; }
    .summary p { margin: 0; color: var(--muted); max-width: 720px; line-height: 1.55; font-size: 16px; }
    .quick { display: grid; align-content: center; gap: 12px; }
    .quick a {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      color: var(--text);
      text-decoration: none;
      border: 1px solid var(--line);
      background: rgba(11,16,32,.78);
      border-radius: 8px;
      padding: 14px 15px;
      font-weight: 800;
    }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(245px, 1fr)); gap: 14px; }
    .card {
      min-height: 190px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      border: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(23,32,51,.9), rgba(17,24,39,.88));
      border-radius: 8px;
      padding: 18px;
      text-decoration: none;
      color: var(--text);
      position: relative;
      overflow: hidden;
    }
    .card::before {
      content: "";
      position: absolute;
      inset: 0 0 auto 0;
      height: 5px;
      background: var(--accent);
    }
    .card h3 { margin: 10px 0 8px; font-size: 21px; letter-spacing: 0; }
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
    .secondary { border: 1px solid var(--line); color: var(--text); background: rgba(11,16,32,.74); }
    @media (max-width: 760px) {
      header { align-items: flex-start; }
      .hero { grid-template-columns: 1fr; }
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
        <h2>Tus webs en un solo sitio.</h2>
        <p>Accede desde aqui a Alexia, control de gastos y todos los proyectos publicados en tus repositorios de GitHub.</p>
      </div>
      <nav class="quick" aria-label="Accesos principales">
        <a href="https://enriqwe.github.io/Alexia/">Alexia <span>-></span></a>
        <a href="https://enriqwe.github.io/Gestion-de-Gastos/">Control de gastos <span>-></span></a>
        <a href="https://github.com/enriqwe">Repositorios <span>-></span></a>
      </nav>
    </section>
    <section class="grid" aria-label="Todas las webs">
      {% for app in apps %}
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
    </section>
  </main>
</body>
</html>"""


@app.get("/")
@auth.require_login
def index():
    return render_template_string(LANDING_HTML, apps=APPS)


def main():
    if init_user_from_cli(auth, sys.argv):
        return
    port = int(os.environ.get("PORT", "8090"))
    app.run(host="0.0.0.0", port=port, threaded=True)


if __name__ == "__main__":
    main()
