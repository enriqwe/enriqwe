# Enrique

Landing privada para acceder a las webs publicadas en los repositorios de `enriqwe`.

## Ejecutar

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python dashboard_server.py init-user enriqwe@gmail.com 'CAMBIA_ESTA_CONTRASENA'
./start_dashboard.sh 8090
```

La aplicacion incluye:

- login con usuario y contrasena;
- roles de usuario y administrador;
- permisos por web para mostrar u ocultar accesos;
- usuario inicial configurable con `init-user`;
- recuperacion o alta inicial mediante enlace enviado por email;
- landing visual con accesos a Alexia, Gestion de Gastos y el resto de webs publicadas;
- despliegue local de webs estaticas bajo `/site/...` para no depender de GitHub Pages.

La parte de login necesita servidor Python. GitHub Pages solo sirve HTML estatico y no puede validar contrasenas ni enviar emails por si mismo.

## Actualizar webs estaticas

```bash
./deploy_sites.py
```

El script clona o actualiza los repos publicados y copia una version servible en `sites/`. Esa carpeta no se sube a GitHub.
