# DealerOS reconciliation assessment

A Django REST API plus React/Vite interface for reconciling System A and System B CSV exports.

## Requirements
- Python 3.10+
- Node.js 18+
- npm

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver 8000
```
In a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Vite proxies `/api` requests to Django. Open the local Vite URL printed by npm. The API defaults to the supplied CSVs in `data/`. To use alternate files, choose System A, System B, and/or Locations CSV in the UI and click **Upload & compare**.

## API
- `GET /api/health/` — health check.
- `GET /api/reference-data/` — supplied location reference data.
- `POST /api/compare/` — multipart form with optional `system_a`, `system_b`, `locations` CSV files and optional `org_id` (`ORG-A` or `ORG-B`). If a file is omitted, the bundled sample is used.

## Reconciliation behavior
- Reference IDs are trimmed, uppercased, and normalized by removing a leading `REC-` from either system.
- Money is parsed as decimal and compared to two decimal places.
- Rows are scoped by location-to-organization mapping before matching. Unknown locations are excluded from scoped comparisons.
- Exact one-to-one records are checked in this order: location, date, amount, then matched.
- Multiple System B entries are only treated as a valid split when every entry is explicitly labelled as a part and all share location/date; their amounts are summed. Otherwise they are flagged for review as duplicates.
- Results include reason and details. The original CSVs are never modified.

## Tests
```bash
python manage.py test reconcile
```

## Deliberate scope limits
This assessment build focuses on import, deterministic reconciliation, tenant scoping, and a review table. It does not implement authentication, persistence of uploaded files, pagination, Docker, or production deployment. Uploads are processed in memory; configure production security, access controls, upload limits, and secret management before deployment.

## AI assistance disclosure
I used ChatGPT to help interpret the assessment, draft implementation code, and prepare tests and documentation. I reviewed the generated logic and kept the comparison rules explicit, including tenant scoping and split-entry handling. I am responsible for verifying the application, running the tests, and explaining the final code; I will only state that tests passed after I have run them locally.
