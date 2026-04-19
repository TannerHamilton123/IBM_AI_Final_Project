# CodeCraftHub

A beginner-friendly Flask REST API project for tracking courses you want to learn. Data is stored in a simple JSON file (`courses.json`) instead of a database. No authentication is required. This project focuses on understanding CRUD operations and REST API basics.

---

## 1) Project Overview and Description

CodeCraftHub is a tiny learning platform where developers can keep a list of courses they want to learn. Each course tracks:

- `id` (auto-generated, starting from 1)
- `name` (required)
- `description` (required)
- `target_date` (required, format YYYY-MM-DD)
- `status` (required, one of: `Not Started`, `In Progress`, `Completed`)
- `created_at` (auto-generated timestamp)

All data is stored in a single JSON file named `courses.json`. The app creates this file automatically if it doesn't exist. The API has no authentication, making it straightforward for beginners to learn REST concepts with a real HTTP interface.

---

## 2) Features

- Create, read, update, and delete courses (CRUD)
- JSON file storage (`courses.json`) with simple read/write operations
- Auto-generated IDs starting from 1
- Auto-generated `created_at` timestamp (UTC, ISO-like format)
- Validation:
  - Required fields: `name`, `description`, `target_date`, `status`
  - `target_date` must be in `YYYY-MM-DD` format
  - `status` must be: `Not Started`, `In Progress`, or `Completed`
- Endpoints under `/api/courses`
- Simple health check endpoint (`/health`)
- Automatically creates the data file if missing

---

## 3) Installation Instructions (Step-by-Step)

**Prerequisites:**
- Python 3.8+ (recommended)
- pip (comes with Python)
- Optional: Virtual environment (recommended)

**Steps:**

1. **Create and activate a virtual environment** (optional but recommended)

   macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies**

   Flask is the only runtime dependency:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**

   From the project root, start the server:
   ```bash
   python app.py
   ```

   By default, the API will be available at:
   ```
   http://127.0.0.1:5000/api/courses
   ```

> **Note:** The app will automatically create `courses.json` if it doesn't exist.

---

## 4) How to Run the Application

Start the server:
```bash
python app.py
```

Open in browser or use curl:
```
http://127.0.0.1:5000/api/courses
```

Quick start sequence:
1. Start server in one terminal: `python app.py`
2. Create a course (see API docs below)
3. List courses: `curl -s http://127.0.0.1:5000/api/courses`

---

## 5) API Endpoints Documentation with Examples

**Base URL:** `http://127.0.0.1:5000/api/courses`

> To fetch a single course, use the `id` as a query parameter: `/api/courses?id=<id>`  
> Trailing slash variants (`/api/courses/`) are also supported for GET.

---

### POST /api/courses — Create a new course

**Required fields:** `name`, `description`, `target_date` (YYYY-MM-DD), `status`

Example payload:
```json
{
  "name": "Python Data Classes",
  "description": "Learn Python data classes for clean data modeling.",
  "target_date": "2026-12-31",
  "status": "Not Started"
}
```

curl command:
```bash
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name":"Python Data Classes","description":"Learn Python data classes for clean data modeling.","target_date":"2026-12-31","status":"Not Started"}'
```

Successful response (201 Created):
```json
{
  "id": 1,
  "name": "Python Data Classes",
  "description": "Learn Python data classes for clean data modeling.",
  "target_date": "2026-12-31",
  "status": "Not Started",
  "created_at": "2026-04-19T12:34:56Z"
}
```

---

### GET /api/courses — Get all courses

```bash
curl -s http://127.0.0.1:5000/api/courses
```

Successful response:
```json
[
  {
    "id": 1,
    "name": "Python Data Classes",
    "description": "Learn Python data classes for clean data modeling.",
    "target_date": "2026-12-31",
    "status": "Not Started",
    "created_at": "2026-04-19T12:34:56Z"
  }
]
```

---

### GET /api/courses?id=\<id\> — Get a specific course

```bash
curl -s "http://127.0.0.1:5000/api/courses?id=1"
```

Successful response:
```json
{
  "id": 1,
  "name": "Python Data Classes",
  "description": "Learn Python data classes for clean data modeling.",
  "target_date": "2026-12-31",
  "status": "Not Started",
  "created_at": "2026-04-19T12:34:56Z"
}
```

If not found: `404` with `{ "error": "Course not found" }`

---

### PUT /api/courses — Update an existing course

**Payload:** include `id` and any fields to update (`name`, `description`, `target_date`, `status`)

Example payload:
```json
{
  "id": 1,
  "status": "In Progress",
  "target_date": "2026-11-15"
}
```

curl command:
```bash
curl -s -X PUT http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"id":1,"status":"In Progress","target_date":"2026-11-15"}'
```

Successful response:
```json
{
  "id": 1,
  "name": "Python Data Classes",
  "description": "Learn Python data classes for clean data modeling.",
  "target_date": "2026-11-15",
  "status": "In Progress",
  "created_at": "2026-04-19T12:34:56Z"
}
```

If not found: `404` with `{ "error": "Course not found" }`

---

### DELETE /api/courses — Delete a course

**Payload:** JSON object with `id`

Example payload:
```json
{ "id": 1 }
```

curl command:
```bash
curl -s -X DELETE http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"id":1}'
```

Successful response:
```json
{ "message": "Course deleted", "id": 1 }
```

If not found: `404` with `{ "error": "Course not found" }`

---

### GET /health — Health check

```bash
curl -s http://127.0.0.1:5000/health
```

Response:
```json
{ "status": "ok" }
```

---

## 6) Testing Instructions

1. Start the server: `python app.py`
2. Use the curl examples above to test each endpoint.

**Suggested sequence for beginners:**

1. `POST` to create the first course
2. `GET` to list all courses
3. `GET` with `?id=1` to fetch the created course
4. `PUT` to update the course
5. `GET` to confirm the update
6. `DELETE` to remove the course
7. `GET` to confirm deletion (should return an empty list)

**Error scenario tests:**

```bash
# Missing required field (name)
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"description":"Missing name","target_date":"2026-12-31","status":"Not Started"}'
# Expected: 400 { "error": "Missing required field(s): name" }

# Invalid status
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","description":"Bad status","target_date":"2026-12-31","status":"Starting"}'
# Expected: 400 { "error": "Invalid status. Allowed values: ..." }

# Invalid date format
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","description":"Bad date","target_date":"12/31/2026","status":"Not Started"}'
# Expected: 400 { "error": "target_date must be in YYYY-MM-DD format" }

# Course not found
curl -s "http://127.0.0.1:5000/api/courses?id=999999"
# Expected: 404 { "error": "Course not found" }
```

---

## 7) Troubleshooting Common Issues

**Server won't start or port in use**
- Ensure no other process is using port 5000.
- Try a different port: `app.run(debug=True, port=5001)` in `app.py`.

**File read/write errors (courses.json)**
- The app will auto-create the file if missing.
- Check that the project directory has write permissions.

**JSON decode errors after editing courses.json manually**
- If you manually edit the file and corrupt the JSON, the app will reset to an empty list.
- To start fresh, delete `courses.json` and let the app recreate it.

**Invalid input errors**
- Missing required fields: `name`, `description`, `target_date`, or `status`
- Invalid date format: `target_date` must be `YYYY-MM-DD`
- Invalid status: allowed values are `Not Started`, `In Progress`, `Completed`

**API returns 404 for a course that exists**
- Double-check the `id` you're using matches the stored course's `id`.
- Ensure you're querying with `id` as a query parameter: `/api/courses?id=1`

---

## 8) Project Structure Explanation

```
CodeCraftHub/
├── app.py           # Flask app with all routes and data handling
├── courses.json     # JSON file that stores all course objects (auto-created if missing)
├── requirements.txt # Lists dependencies (Flask)
└── README.md        # This file
```

**Key ideas:**
- **No database:** data is stored in a single JSON file to keep things simple.
- **Auto-generated IDs:** IDs start from 1 and increment for each new course.
- **Input validation:** ensures required fields and correct formats before saving.
- **Lightweight and educational:** focused on REST API basics without authentication.
