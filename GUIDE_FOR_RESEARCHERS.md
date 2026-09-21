# Preparing an oTree project for the BEER Lab server

**Audience:** researchers, students and collaborators who want their oTree
experiment hosted by the BEER Lab (Tecnológico de Monterrey).
**Version:** 2026-09-17. Questions: lab.economia@servicios.tec.mx

This document is self-contained. Follow it and your project will run on the
lab server without changes. Everything else (servers, HTTPS, database,
backups, domain names) is handled by the lab.

---

## 1. What the lab gives you

| You get | Details |
|---|---|
| A public address | `https://<name>.beer-lab.org` (you choose `<name>`, see §5.2) |
| HTTPS, no port numbers | Participants just open the link; works on phones |
| A Postgres database | Your data persists across restarts and code updates |
| The standard oTree admin | `https://<name>.beer-lab.org` → admin login, Rooms, session creation, data export |
| Nightly backups | Kept by the lab; you still export your own data (§7) |
| Updates | Send a new commit; the lab rebuilds your game (a few seconds of downtime) |

You do **not** need Heroku, Docker, a server, or a domain. You do **not**
write any deployment files (no `Dockerfile`, `Procfile`, `runtime.txt`, or
`docker-compose.yml`). If those files exist in your repo from Heroku they
are ignored.

---

## 2. What the server runs

- **Python 3.11.** Test with Python 3.11 locally; 3.12 or 3.13 features may
  not exist on the server.
- **oTree:** whatever version your `requirements.txt` asks for (§3.2).
  The unpinned spec `otree>=5.11.0` installs **oTree 6** today.
- **Linux (Debian) container.** File and path names are case-sensitive:
  `templates/MyPage.html` and `templates/mypage.html` are different files.
  A project that works on Windows can fail here because of this.
- **One process per game**, fine for classroom or lab sessions of up to a few
  hundred simultaneous participants.
- **Postgres** through the `DATABASE_URL` environment variable, which the
  server sets. Never set it yourself.
- **Time zone** `America/Monterrey` for logs; oTree stores timestamps in UTC as
  usual.
- The container's filesystem is **discarded on every update**. Anything your
  code writes to disk (CSV files, pickles, images) disappears. Store data in
  oTree fields, or ask the lab if you truly need files.

---

## 3. Repository layout and required files

Your project must be a **git repository whose root is the oTree project
folder**, exactly what `otree startproject` creates:

```
my_experiment/                 <- git root == oTree project root
├── settings.py                <- required
├── requirements.txt           <- required
├── .gitignore                 <- required (§3.4)
├── README.md                  <- recommended (§3.5)
├── _static/                   <- images, css, js (optional)
├── _templates/                <- global templates (optional)
├── _rooms/                    <- participant-label files if you use Rooms (optional)
├── app_one/
│   ├── __init__.py
│   └── *.html
└── app_two/
    └── ...
```

Do **not** nest the project inside another folder (`repo/otree/settings.py`
will be rejected). One repo = one oTree project = one subdomain. A project can
contain many apps and many session configs.

### 3.1 `settings.py` rules

```python
from os import environ

SESSION_CONFIGS = [
    dict(
        name='my_task',
        display_name="Tarea: Repartir Pesos",   # participant-neutral name (see §5.3)
        app_sequence=['app_one', 'app_two'],
        num_demo_participants=4,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="",
)

LANGUAGE_CODE = 'es'
REAL_WORLD_CURRENCY_CODE = 'MXN'
USE_POINTS = True

ROOMS = [
    dict(name='sala1', display_name='Sala 1'),
    dict(name='sala2', display_name='Sala 2'),
]

# --- Required exactly like this. The server injects the values. ---
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
SECRET_KEY = environ.get('OTREE_SECRET_KEY')
# AUTH_LEVEL is also set by the server (STUDY). Do not hard-code it.

# --- Any other secret or per-deployment value: read it from the environment
#     and list the variable name in your README (§3.5). ---
FACILITATOR_PIN = environ.get('OTREE_FACILITATOR_PIN', '0000')

INSTALLED_APPS = ['otree']
```

Rules:

1. `ADMIN_PASSWORD` and `SECRET_KEY` **must** come from `OTREE_ADMIN_PASSWORD`
   and `OTREE_SECRET_KEY`. Never write a real password or key in the file.
   The lab generates strong values per game.
2. Do not set `DATABASE_URL`, `DEBUG`, `OTREE_PRODUCTION` or `AUTH_LEVEL` in
   code; the server controls them.
3. Anything else that changes between your laptop and production (PINs, API
   keys, a survey URL, a payment amount you want to tweak without a new
   commit) goes through `environ.get('OTREE_<NAME>', '<safe default>')`, with
   a **safe** default: a value that cannot be exploited if the lab forgets to
   set it. Prefix custom variables with `OTREE_` so they are easy to spot.
4. No absolute URLs to `localhost`, `127.0.0.1`, `herokuapp.com` or an IP
   address anywhere in Python or templates. Use relative links and oTree's
   URL helpers.
5. `ROOMS` are optional but recommended for classroom and lab sessions: they
   give stable participant links per classroom or seat and record which room a
   participant used.

### 3.2 `requirements.txt`

Keep it short and **pin the oTree version you tested with**:

```
otree==6.0.15
psycopg2-binary
```

- `psycopg2-binary` is required (Postgres driver). Plain `psycopg2` also works
  (the server can compile it) but installs slower.
- Add only what your code imports (`numpy`, `pandas`, …). Every extra package
  makes builds slower and adds ways to break.
- Do **not** list `otree` twice or use the `# oTree-may-overwrite-this-file`
  header (delete those comment lines, otherwise oTree overwrites the file
  when you run `otree zip`).
- If you upgrade oTree later, say so in your commit message: an oTree major
  upgrade usually requires resetting the database (§6.3).

### 3.3 Files that must NOT be in the repo

- Databases: `db.sqlite3` and anything `*.sqlite3`.
- Exports and participant data: `*.csv`, `*.xlsx`, `all_apps_wide*`,
  `PageTimes*`. Data belongs in your analysis folder, not in the deployed app.
- Secrets: real passwords, API keys, `.env` files, notes that contain the
  admin password.
- Caches and build leftovers: `__pycache__/`, `*.pyc`, `staticfiles/`,
  `__temp_migrations/`, `.otreezip`, `*.otreezip`, virtual environments.
- Large binaries: keep `_static/` under ~20 MB total; compress images; no
  videos in the repo (host them elsewhere and link).

### 3.4 `.gitignore` (copy this)

```
db.sqlite3
*.sqlite3
__pycache__/
*.pyc
.otreezip
*.otreezip
staticfiles/
__temp_migrations/
.env
.venv/
venv/
.idea/
.vscode/
*.csv
*.xlsx
```

Remove the `*.csv` line only if your app **reads** a CSV at run time (for
example a table of career descriptions); in that case keep the file small
and mention it in the README.

### 3.5 `README.md` in your repo (template)

```markdown
# <Project title>

Contact: <name, e-mail>. PI: <name>. IRB/ethics approval: <code>.

## Requested subdomain
<name>.beer-lab.org

## Session configs
- `my_task` — main study, ~50 min, 20–40 participants per session, uses Rooms.
- `my_task_demo` — 5-minute demo for facilitators.

## Environment variables (besides OTREE_ADMIN_PASSWORD / OTREE_SECRET_KEY)
- `OTREE_FACILITATOR_PIN` — 4–6 digits the facilitator types to trigger the raffle.

## Run-time data files
- `app_one/careers.csv` — read at start-up; small, no personal data.

## Tested with
Python 3.11.x, oTree 6.0.15, on <date>. `otree test my_task` passes.

## Expected load
Up to 45 simultaneous participants; sessions on <dates>.
```

---

## 4. Test locally before sending anything

All commands from the repo root, in a fresh virtual environment with
**Python 3.11**.

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```
(macOS/Linux: `source .venv/bin/activate`)

```bash
pip install -r requirements.txt
```

1. **Development server**, click through every page yourself:
```bash
otree devserver
```
2. **Bots** (write at least a minimal `tests.py`/`PlayerBot` per app; they
   catch broken form fields and page logic):
```bash
otree test my_task
```
3. **Production mode**, which is what the server runs. It disables debug
   pages and catches missing static files and template errors that
   `devserver` hides. Set the same variables the server will set:

Windows PowerShell:
```powershell
$env:OTREE_PRODUCTION='1'; $env:OTREE_AUTH_LEVEL='STUDY'; $env:OTREE_ADMIN_PASSWORD='test'; $env:OTREE_SECRET_KEY='test'; otree prodserver 8000
```
macOS/Linux:
```bash
OTREE_PRODUCTION=1 OTREE_AUTH_LEVEL=STUDY OTREE_ADMIN_PASSWORD=test OTREE_SECRET_KEY=test otree prodserver 8000
```
   Open `http://localhost:8000`, log in as `admin` / `test`, create a session
   from a Room, and play it on **two different browsers** (or one normal and
   one private window) at the same time to check multi-player pages.
4. **Fresh clone test** (catches files you forgot to commit):
```bash
git clone <your repo url> /tmp/fresh && cd /tmp/fresh && pip install -r requirements.txt && otree test my_task
```
5. **Optional, exact server reproduction** with Docker Desktop: see Appendix A.

---

## 5. What to send the lab

### 5.1 The code — send a zip by e-mail

1. Put `settings.py` and `requirements.txt` at the root of the project
   folder (section 2).
2. Zip the folder as **`<subdomain>-v1.zip`**, without `.venv`, `db.sqlite3`,
   `__pycache__`, CSV/XLSX exports or any data. Over 20 MB: share a OneDrive
   link instead of attaching.
3. E-mail it to **lab.economia@servicios.tec.mx**, subject
   `[oTree] <subdomain> v1 — investigación` (or `— docencia` for a classroom
   game), with the details of 5.2–5.4 in the body.
4. The lab deploys it by hand (allow a few working days; say your session
   dates), replies with the URL, and hands over the admin password in person
   or by phone — never by e-mail. If the build fails you get the error and a
   suggested fix; send `<subdomain>-v2.zip`.
5. Every later version is a new zip with the next number. Model changes reset
   the database (section 7).

Start from the lab's template — https://github.com/ecastrom/otree_template (public;
runnable oTree 6 project + design guide) — or, for a classroom game,
from the published dictator game (ask the lab for a copy). The public guides
at https://experiments.beer-lab.org/guia/ (research) and
https://teaching.beer-lab.org/guia/ (teaching) say the same in Spanish.

### 5.2 The subdomain name

Rules for `<name>` in `<name>.beer-lab.org`:

- 3–15 characters, lowercase letters, digits and hyphens only, starts with a
  letter. Examples: `beca`, `precios`, `mercado2`, `encuestas-dei`.
- **Neutral for participants.** The address is visible to them on every page.
  Do not name the treatment, the hypothesis or the construct (`sesgo-genero`,
  `accion-afirmativa`, `confianza`), because it primes answers. Name the
  activity or a project code instead (`decisiones`, `tarea-a`, `proyecto42`).
- Not already in use (the lab will tell you).

### 5.3 Participant-facing text (the lab will check this)

Participants should only see what they need to act. Session config
`display_name`s, page titles and instructions must **not** reveal the
research question, treatment arms, the name of the policy being studied, or
what "the researcher wants". Describe the action ("Repartir fichas"), not the
construct ("Preferencias sociales"). Read every screen as a participant who
is trying to guess the purpose: if you can guess it, rewrite it.

### 5.4 Operational details

- Number of sessions, dates and times, expected simultaneous participants.
- Which session config and which Rooms each session uses.
- Environment variables you need set, with the values sent through a
  **separate channel** (not in the README, not in the repo).
- Who needs the admin password (the lab sends it person-to-person).
- Whether the study is covered by an ethics approval and its code.

---

## 6. After deployment

### 6.1 What you receive

- Your address `https://<name>.beer-lab.org` and the admin password.
- A listing on `https://experiments.beer-lab.org` (the lab's directory of
  active games; neutral title only).

### 6.2 Running sessions

1. Log in at `https://<name>.beer-lab.org` (user `admin`).
2. Go to **Rooms**, open your room, create the session there. Participants use
   the room link (`https://<name>.beer-lab.org/room/<room>`), which you can
   print, project or send by e-mail.
3. Monitor progress in the admin; export data at the end (§7).

Do **not** ask the lab to deploy a code change during or right before a
session: a deploy restarts the game and drops participants who are mid-page
for a few seconds; a model change wipes the database (§6.3).

### 6.3 Updating your code

- **Copy, text and logic changes** (no new or changed model fields): send the
  new commit/tag. The lab rebuilds; data is kept.
- **Model changes** (new fields, renamed fields, changed types, a new app in
  the sequence, an oTree major upgrade): oTree has no migrations, so the
  database must be **reset and all sessions deleted**. Export first (§7),
  then ask for a deploy "with database reset". Plan model changes between
  waves, never between sessions of the same wave.

### 6.4 When the study ends

Tell the lab. The game is taken offline, the final export is handed to you,
and the database is deleted after the retention period agreed with the PI.

---

## 7. Your data

- Export from the admin: **Data → All apps wide** (one row per participant)
  plus each app's table and **PageTimes**. Do this after **every** session,
  not only at the end.
- Exports contain whatever your apps store, including any personal data you
  collected. Store them according to your ethics protocol. The lab's backups
  are for disaster recovery, not a substitute for your exports.
- The lab never opens or analyses your data.

---

## 8. Common problems and how to avoid them

| Symptom on the server | Cause | Fix |
|---|---|---|
| Build fails on `pip install` | Package not on PyPI, typo, or a package needing a compiler that is not installed | Use `psycopg2-binary`; remove unused packages; pin versions that have wheels |
| Page says "TemplateNotFound" although it works on your PC | Case mismatch in a file name (Windows ignores case, Linux does not) | Match the exact case in `template_name` and `{% include %}` |
| Static image missing | File not committed, or path uses backslashes / wrong case | `{{ static 'app/pic.png' }}` and check `git status` |
| Link goes to `localhost` or `herokuapp.com` | Hard-coded URL | Use relative URLs and oTree helpers |
| Participants see the demo page or session list | `AUTH_LEVEL` set in code | Remove it; the server sets `STUDY` |
| Works once, then "database out of date" | Model changed without a reset | Ask for deploy with reset (after exporting) |
| Values reset after an update | Code writes to files on disk | Store in oTree fields / `participant.vars` / `session.vars` |
| Login rejected | Wrong password or you edited `ADMIN_PASSWORD` in code | Keep the `environ.get` line; ask the lab for the password |

---

## 9. Pre-submission checklist

- [ ] Git root is the oTree project root; `settings.py` and
      `requirements.txt` at top level.
- [ ] `requirements.txt` pins `otree==<version tested>` and includes
      `psycopg2-binary`.
- [ ] `ADMIN_PASSWORD` / `SECRET_KEY` read from `OTREE_ADMIN_PASSWORD` /
      `OTREE_SECRET_KEY`; no secrets in the repo.
- [ ] No `DATABASE_URL`, `DEBUG`, `AUTH_LEVEL` in `settings.py`.
- [ ] Custom settings use `environ.get('OTREE_…', safe_default)` and are
      listed in the README.
- [ ] `.gitignore` in place; no `db.sqlite3`, exports, caches or data files
      committed.
- [ ] Tested with Python 3.11: `otree devserver`, `otree test <config>`,
      `otree prodserver` with `OTREE_PRODUCTION=1`, and a fresh clone.
- [ ] Multi-player pages tested with two browsers simultaneously.
- [ ] Participant-facing text and the subdomain name are neutral (§5.3).
- [ ] README with contact, ethics code, session configs, rooms, variables,
      expected load and dates.
- [ ] Sent: repo URL or zip, subdomain name, variables (separately), session
      schedule, admin-password recipients.

---

## Appendix A — Reproduce the server locally with Docker (optional)

Requires Docker Desktop. Create these two files **outside** your repo (for
example in a sibling folder `lab-test/`), then run `docker compose up --build`
from that folder and open `http://localhost:8000` (admin password `test`).

`lab-test/docker-compose.yml`

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: otree
      POSTGRES_PASSWORD: otree
      POSTGRES_DB: otree
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U otree -d otree"]
      interval: 5s
      retries: 20
  game:
    build:
      context: ../my_experiment          # <- path to your repo
      dockerfile: ../lab-test/Dockerfile # <- relative to the context
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://otree:otree@db:5432/game
      OTREE_ADMIN_PASSWORD: test
      OTREE_SECRET_KEY: test
      OTREE_AUTH_LEVEL: STUDY
    ports:
      - "8000:8000"
```

`lab-test/Dockerfile` — a copy of the lab's image recipe as of 2026-09-18,
minus the container health check (the authoritative version is
`otree/Dockerfile` in the lab's `server-project` repository):

```dockerfile
FROM python:3.11-slim AS build
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

FROM python:3.11-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --uid 10001 --home-dir /app --shell /usr/sbin/nologin otree
COPY --from=build /venv /venv
ENV PATH=/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    OTREE_PRODUCTION=1 \
    FORWARDED_ALLOW_IPS=* \
    PORT=8000

COPY <<'SH' /usr/local/bin/otree-entrypoint
#!/bin/sh
set -eu
python - <<'PY'
import os, sys, time
from urllib.parse import urlsplit
url = os.environ.get('DATABASE_URL', '')
if not url.startswith('postgres'):
    sys.exit('DATABASE_URL must point at Postgres (got %r)' % url)
import psycopg2
u = urlsplit(url)
dbname = u.path.lstrip('/')
admin_url = u._replace(path='/postgres').geturl()
for _ in range(60):
    try:
        conn = psycopg2.connect(admin_url); break
    except psycopg2.OperationalError:
        time.sleep(1)
else:
    sys.exit('database server not reachable')
conn.autocommit = True
cur = conn.cursor()
cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (dbname,))
if cur.fetchone() is None:
    cur.execute('CREATE DATABASE "%s"' % dbname.replace('"', ''))
    print('created database', dbname)
conn.close()
conn = psycopg2.connect(url)
cur = conn.cursor()
cur.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'otree_session'")
empty = cur.fetchone() is None
conn.close()
open('/tmp/otree-db-empty', 'w').write('1' if empty else '0')
PY
# `docker compose run --rm <game> otree resetdb --noinput` (or any other
# command) runs instead of the server, after the database exists.
if [ "$#" -gt 0 ]; then
    exec "$@"
fi
if [ "$(cat /tmp/otree-db-empty)" = 1 ]; then
    echo "empty database: creating the oTree schema"
    otree resetdb --noinput
fi
exec otree prodserver "$PORT"
SH
RUN chmod 755 /usr/local/bin/otree-entrypoint

WORKDIR /app
COPY --chown=otree:otree . .
RUN chown otree:otree /app
USER otree
EXPOSE 8000
ENTRYPOINT ["otree-entrypoint"]
```

If `docker compose up --build` succeeds and you can log in and play a
session, your repository is ready for the lab. To start over with an empty
database: `docker compose down -v`.

---

## Appendix B — Migrating from Heroku

If your project currently runs on Heroku:

1. Nothing in the code has to change except what §3 requires (most Heroku
   projects already read `OTREE_ADMIN_PASSWORD` / `OTREE_SECRET_KEY` from the
   environment). `Procfile`, `runtime.txt`, `app.json` may stay; they are
   ignored.
2. Export your data from the Heroku admin **before** the move; the lab server
   starts with an empty database unless you ask for a database migration
   (possible only if both sides run the same oTree version).
3. Tell participants and facilitators the new address; old
   `*.herokuapp.com` links stop working when you delete the Heroku app.
