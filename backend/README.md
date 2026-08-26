# Kingsastrology Backend

Deterministic backend scaffold for the one-way Kingsastrology product.

## Scope

- Loads only `rules/ch08_*.md` through `rules/ch20_*.md`.
- Ignores Chapters 1-7 by design.
- Treats the filename chapter as canonical for backend scope.
- Surfaces mismatches in legacy rule headers/citations as warnings.
- Does not run AI at runtime.

## Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Useful endpoints:

- `GET /` — redirects to the frontend
- `GET /app` — polished rule review frontend
- `GET /health`
- `GET /rules/scope`
- `GET /rules/chapters`
- `GET /rules/chapters/12`
- `GET /rules?status=draft&classification=strength`
- `GET /rules/by-id/R-12.3`
- `POST /reading/compose`
- `POST /chart/evaluate`
- `POST /reading/from-chart`
- `GET /review` — manual rule review workbench
- `GET /review/rules?chapter=12` — filtered review workbench

The backend currently accepts chart facts that have already been computed by an ephemeris/chart engine. It does not calculate planetary positions yet. Given those facts, `/chart/evaluate` deterministically matches supported rule conditions and `/reading/from-chart` composes a one-way draft reading from the matched rules.

## Manual Rule Review Frontend

Open:

```text
http://127.0.0.1:8000/app
```

Each rule has fields for:

- decision: `Unreviewed`, `Approved`, or `Needs Improvement`
- reviewer
- comments
- improvements

Saved reviews are written to:

```text
backend/data/rule_reviews.json
```

The classic server-rendered fallback remains available at:

```text
http://127.0.0.1:8000/review/rules
```

Example:

```bash
curl -s http://127.0.0.1:8000/chart/evaluate \
  -H 'content-type: application/json' \
  -d '{
    "planets": [
      {"name":"Sun","sign":"Aries","house":1},
      {"name":"Jupiter","sign":"Cancer","house":10}
    ],
    "allow_draft": true,
    "compose": true
  }'
```
