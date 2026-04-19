from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

# ----------------------------
# Configuration & helpers
# ----------------------------

# Path to the JSON data file (stored in the project root)
DATA_FILE = os.path.join(os.path.dirname(__file__), 'courses.json')

# Allowed statuses
ALLOWED_STATUSES = {"Not Started", "In Progress", "Completed"}

app = Flask(__name__)

def _ensure_data_file():
    """
    Ensure the data file exists. If not, create it with an empty list [].
    This satisfies the requirement to auto-create the file if missing.
    """
    try:
        if not os.path.exists(DATA_FILE):
            # Create the file and initialize with an empty list
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
    except Exception as e:
        # In a startup phase, failing to create the file is critical
        raise IOError(f"Failed to create data file: {e}")

def _load_courses():
    """
    Load and return the list of courses from the JSON file.
    If the file is empty or invalid, return an empty list.
    """
    _ensure_data_file()
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
    except json.JSONDecodeError:
        # Corrupted JSON; reset to empty list to keep app running
        return []
    except Exception as e:
        raise IOError(f"Failed to read data file: {e}")

def _save_courses(courses):
    """
    Persist the given list of courses to the JSON file.
    """
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(courses, f, indent=2)
    except Exception as e:
        raise IOError(f"Failed to write data file: {e}")

def _get_next_id(courses):
    """
    Compute the next course ID as max(existing IDs) + 1, or 1 if none exist.
    """
    if not courses:
        return 1
    return max(course.get('id', 0) for course in courses) + 1

def _utc_now_iso():
    """
    Return current UTC time in ISO 8601 format, e.g. 2024-08-01T12:34:56Z
    """
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def _validate_date(date_str):
    """
    Validate that date_str has format YYYY-MM-DD.
    Returns True if valid, raises ValueError if invalid.
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        raise ValueError("target_date must be in YYYY-MM-DD format")

def _find_course_by_id(courses, course_id):
    """
    Helper to locate a course by its ID. Returns the course dict or None.
    """
    for c in courses:
        if c.get('id') == course_id:
            return c
    return None

# ----------------------------
# CRUD operations (data layer)
# ----------------------------

def get_all_courses():
    return _load_courses()

def get_course_by_id(course_id):
    courses = _load_courses()
    return _find_course_by_id(courses, course_id)

def add_course(course_dict):
    """
    course_dict should contain: name, description, target_date, status
    Adds id and created_at automatically.
    Returns the created course dict.
    """
    courses = _load_courses()
    new_id = _get_next_id(courses)
    course = course_dict.copy()
    course['id'] = new_id
    course['created_at'] = _utc_now_iso()
    courses.append(course)
    _save_courses(courses)
    return course

def update_course(course_id, update_dict):
    """
    Update fields of the course with given ID using update_dict.
    Returns the updated course or None if not found.
    """
    courses = _load_courses()
    course = _find_course_by_id(courses, course_id)
    if not course:
        return None

    # Do not allow updating id or created_at via this function
    allowed_updates = {'name', 'description', 'target_date', 'status'}
    for key, value in update_dict.items():
        if key in allowed_updates:
            course[key] = value
    _save_courses(courses)
    return course

def delete_course(course_id):
    """
    Delete the course with the given ID. Returns True if deleted, False if not found.
    """
    courses = _load_courses()
    new_courses = [c for c in courses if c.get('id') != course_id]
    if len(new_courses) == len(courses):
        return False  # Not found
    _save_courses(new_courses)
    return True

# ----------------------------
# API endpoints
# ----------------------------

@app.route('/api/courses', methods=['POST'])
def api_create_course():
    """
    POST /api/courses
    Create a new course. Required fields: name, description, target_date, status.
    Automatically generates id and created_at.
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        data = None

    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # Validate required fields
    required_fields = ['name', 'description', 'target_date', 'status']
    missing = [f for f in required_fields if f not in data or not data.get(f)]
    if missing:
        return jsonify({'error': f"Missing required field(s): {', '.join(missing)}"}), 400

    # Validate status
    status = data['status']
    if status not in ALLOWED_STATUSES:
        return jsonify({'error': f"Invalid status. Allowed values: {', '.join(ALLOWED_STATUSES)}"}), 400

    # Validate date format
    target_date = data['target_date']
    try:
        _validate_date(target_date)
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400

    # Build the course object (without id/created_at yet)
    course_input = {
        'name': data['name'],
        'description': data['description'],
        'target_date': target_date,
        'status': status
    }

    try:
        created = add_course(course_input)
        return jsonify(created), 201
    except Exception as e:
        return jsonify({'error': 'Failed to write data file', 'detail': str(e)}), 500

@app.route('/api/courses', methods=['GET'])
@app.route('/api/courses/', methods=['GET'])
def api_get_courses():
    """
    GET /api/courses  -> Get all courses
    GET /api/courses?id=<id> -> Get a specific course by id
    """
    # If an id is provided as a query parameter, return that specific course
    course_id_param = request.args.get('id')
    if course_id_param:
        try:
            course_id = int(course_id_param)
        except ValueError:
            return jsonify({'error': 'id parameter must be an integer'}), 400

        course = get_course_by_id(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        return jsonify(course)

    # Otherwise, return all courses
    try:
        courses = get_all_courses()
        return jsonify(courses)
    except Exception as e:
        return jsonify({'error': 'Failed to read data file', 'detail': str(e)}), 500

@app.route('/api/courses', methods=['PUT'])
def api_update_course():
    """
    PUT /api/courses
    Update an existing course. Requires id in JSON body and at least one field to update.
    Supported fields to update: name, description, target_date, status
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        data = None

    if not data or 'id' not in data:
        return jsonify({'error': 'Missing required field: id'}), 400

    course_id = data['id']

    # Build update payload
    update_payload = {}
    if 'name' in data:
        update_payload['name'] = data['name']
    if 'description' in data:
        update_payload['description'] = data['description']
    if 'target_date' in data:
        try:
            _validate_date(data['target_date'])
            update_payload['target_date'] = data['target_date']
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
    if 'status' in data:
        if data['status'] not in ALLOWED_STATUSES:
            return jsonify({'error': f"Invalid status. Allowed values: {', '.join(ALLOWED_STATUSES)}"}), 400
        update_payload['status'] = data['status']

    if not update_payload:
        return jsonify({'error': 'No valid fields provided to update'}), 400

    try:
        updated = update_course(course_id, update_payload)
        if not updated:
            return jsonify({'error': 'Course not found'}), 404
        return jsonify(updated)
    except Exception as e:
        return jsonify({'error': 'Failed to write data file', 'detail': str(e)}), 500

@app.route('/api/courses', methods=['DELETE'])
def api_delete_course():
    """
    DELETE /api/courses
    Delete a course by id. Requires JSON body with id field.
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        data = None

    if not data or 'id' not in data:
        return jsonify({'error': 'Missing required field: id'}), 400

    course_id = data['id']

    try:
        ok = delete_course(course_id)
        if not ok:
            return jsonify({'error': 'Course not found'}), 404
        return jsonify({'message': 'Course deleted', 'id': course_id})
    except Exception as e:
        return jsonify({'error': 'Failed to write data file', 'detail': str(e)}), 500

# Optional health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

# ----------------------------
# Run the app
# ----------------------------
if __name__ == '__main__':
    # Ensure the data file exists before starting
    try:
        _ensure_data_file()
    except Exception as init_err:
        print(f"Initialization error: {init_err}")
        # Exit if we cannot create the data file
        raise SystemExit(1)

    app.run(debug=True)
