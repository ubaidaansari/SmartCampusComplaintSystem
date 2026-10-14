import os
import sqlite3
from flask import Flask, render_template, request
from ml_model import predict_category

app = Flask(__name__)

# Database ka correct path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.environ.get("RENDER"):
    DATABASE = "/var/data/complaints.db"
else:
    DATABASE = os.path.join(BASE_DIR, "complaints.db")
# Database create karna
def create_database():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Submitted'
        )
    """)

    connection.commit()
    connection.close()


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Complaint tracking
@app.route("/track", methods=["GET"])
def track_complaint():
    complaint_id = request.args.get("complaint_id", "").strip()

    if not complaint_id.isdigit() or int(complaint_id) < 1:
        return "Please enter a valid Complaint ID.", 400

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    complaint = connection.execute(
        "SELECT * FROM complaints WHERE id = ?",
        (int(complaint_id),)
    ).fetchone()

    connection.close()

    if complaint is None:
        return """
            <h2>Complaint Not Found</h2>
            <p>Please check your Complaint ID and try again.</p>
            <a href="/">Go Back</a>
        """, 404

    return f"""
        <h1>Complaint Tracking Result</h1>
        <p>Complaint ID: {complaint['id']}</p>
        <p>Category: {complaint['category']}</p>
        <p>Location: {complaint['location']}</p>
        <p>Status: <strong>{complaint['status']}</strong></p>
        <a href="/">Go Back</a>
    """


# Admin dashboard
@app.route("/admin")
def admin_dashboard():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    complaints = connection.execute(
        "SELECT * FROM complaints ORDER BY id DESC"
    ).fetchall()

    total = len(complaints)

    submitted = sum(
        1 for c in complaints if c["status"] == "Submitted"
    )

    in_progress = sum(
        1 for c in complaints if c["status"] == "In Progress"
    )

    resolved = sum(
        1 for c in complaints if c["status"] == "Resolved"
    )

    connection.close()

    return render_template(
        "admin.html",
        complaints=complaints,
        total=total,
        submitted=submitted,
        in_progress=in_progress,
        resolved=resolved
    )


# Update complaint status
@app.route("/admin/update/<int:complaint_id>", methods=["POST"])
def update_complaint_status(complaint_id):
    new_status = request.form.get("status", "")

    allowed_statuses = [
        "Submitted",
        "In Progress",
        "Resolved"
    ]

    if new_status not in allowed_statuses:
        return "Invalid status.", 400

    connection = sqlite3.connect(DATABASE)

    cursor = connection.execute(
        "UPDATE complaints SET status = ? WHERE id = ?",
        (new_status, complaint_id)
    )

    connection.commit()
    updated_rows = cursor.rowcount
    connection.close()

    if updated_rows == 0:
        return "Complaint not found.", 404

    return """
        <h2>Complaint Status Updated Successfully!</h2>
        <a href="/admin">Return to Admin Dashboard</a>
    """


# Submit a new complaint
@app.route("/submit", methods=["POST"])
def submit_complaint():
    student_name = request.form.get(
        "student_name", ""
    ).strip()

    category = request.form.get(
        "category", ""
    ).strip()

    location = request.form.get(
        "location", ""
    ).strip()

    description = request.form.get(
        "description", ""
    ).strip()

    # Check all required fields
    if not all([student_name, category, location, description]):
        return "Please fill in all fields.", 400

    # Predict category using the ML model
    category = predict_category(description)

    # Save complaint in database
    connection = sqlite3.connect(DATABASE)

    cursor = connection.execute("""
        INSERT INTO complaints
        (student_name, category, location, description)
        VALUES (?, ?, ?, ?)
    """, (student_name, category, location, description))

    complaint_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return f"""
        <h1>Complaint Submitted Successfully!</h1>
        <p>Your Complaint ID is: <strong>{complaint_id}</strong></p>
        <p>Predicted Category: <strong>{category}</strong></p>
        <p>Status: Submitted</p>
        <a href="/">Submit another complaint</a>
    """


# Start application
if __name__ == "__main__":
    create_database()
    app.run(debug=True)