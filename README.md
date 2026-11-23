# DealerOS Reconciliation Assessment

A Django REST API and React/Vite interface for reconciling System A and System B CSV exports.

## Requirements

- Python 3.10+
- Node.js 18+
- npm

## Run Locally

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python manage.py runserver 8000
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal. To compare your own files, upload the System A, System B, and Locations CSVs, then click **Upload & compare**.

## API

- `GET /api/health/` — health check.
- `GET /api/reference-data/` — location reference data.
- `POST /api/compare/` — compares CSV files. Supports optional `system_a`, `system_b`, `locations`, and `org_id` (`ORG-A` or `ORG-B`). Omitted files use the bundled samples.

## Reconciliation Rules

- Reference IDs are normalized by trimming, uppercasing, and removing a leading `REC-`.
- Amounts are compared to two decimal places.
- Records are scoped by organization using location mappings; unknown locations are excluded from scoped comparisons.
- Records are checked by location, date, and amount.
- Multiple System B entries are accepted as a split only when each is labelled as a part and all share the same location and date. Otherwise, they are flagged for review.
- Results include a reason and details. Original CSV files are not modified.

## Tests

```bash
python manage.py test reconcile
```

## Scope and AI Assistance

This assessment focuses on CSV import, reconciliation, organization scoping, and a results table. Uploaded files are processed in memory; authentication, file persistence, pagination, and production security are outside the current scope.

AI tools assisted with implementation and documentation. I reviewed and adapted the work and am responsible for understanding and verifying the final code.