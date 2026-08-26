# Kings Astrology iOS

Native SwiftUI companion for the rule-review backend. This first iOS version focuses on the manual review workflow for Brihat Jataka Chapters 8-20:

- Loads `/review/api/rules` from the local FastAPI backend.
- Filters rules by chapter, decision, classification, status, and search text.
- Shows condition, effect, verse source, citations, notes, and warnings.
- Saves reviewer decision, comments, and improvement notes to `/review/api/rules/{rule_id}/review`.

## Run locally

Start the backend first:

```bash
cd backend
PYTHONPATH=. /tmp/kingsastro-backend-venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Build the simulator app:

```bash
xcodebuild \
  -project ios/KingsAstrologyReview/KingsAstrologyReview.xcodeproj \
  -scheme KingsAstrologyReview \
  -configuration Debug \
  -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath ios/build \
  CODE_SIGNING_ALLOWED=NO \
  build
```

The app currently points at `http://127.0.0.1:8000`, which works from the iOS simulator when the backend is running on the same Mac.

## Current scope

This app does not compute charts and does not contain doctrine. It is an API client for the deterministic backend review workflow, in line with the project rule that doctrine and guardrails stay server-side.
