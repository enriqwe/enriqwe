#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "sites-src"
PUBLIC_DIR = BASE_DIR / "sites"

STATIC_SITES = {
    "aprende-a-escribir": "aprendeaescribir",
    "calendario": "Calendario",
    "canvas": "Canvas",
    "editor-mapas": "Editor-de-Mapas",
    "editor-mapas-v2": "Editor-de-Mapas-v2",
    "juego-frances": "JuegoFrances",
    "mision-cuerpo-humano": "mision-cuerpo-humano",
    "onevenue-todo": "onevenue-todo",
    "regulacion": "Regulaci-n",
}

REPOS = sorted(set(STATIC_SITES.values()))


def run(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def update_repos() -> None:
    SRC_DIR.mkdir(parents=True, exist_ok=True)
    for repo in REPOS:
        target = SRC_DIR / repo
        if (target / ".git").exists():
            run(["git", "pull", "--ff-only"], cwd=target)
        else:
            run(["git", "clone", f"https://github.com/enriqwe/{repo}.git", str(target)])


def ignore(_dir: str, names: list[str]) -> set[str]:
    blocked = {
        ".git",
        ".github",
        ".DS_Store",
        "node_modules",
        "__pycache__",
        "dist",
        "build",
        ".env",
        ".env.local",
    }
    return {name for name in names if name in blocked}


def publish_static_sites() -> None:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    for slug, repo in STATIC_SITES.items():
        source = SRC_DIR / repo
        destination = PUBLIC_DIR / slug
        if not (source / "index.html").exists():
            raise SystemExit(f"Missing index.html for {repo}")
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination, ignore=ignore)


def main() -> None:
    update_repos()
    publish_static_sites()
    print(f"DEPLOYED {len(STATIC_SITES)} static sites to {PUBLIC_DIR}")


if __name__ == "__main__":
    main()
