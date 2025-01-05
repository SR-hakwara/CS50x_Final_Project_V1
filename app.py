from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for, get_flashed_messages,
)
from flask_session import Session
import re  # For email validation

from datetime import datetime
from models import User, Project, Task, init_db
from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
init_db()


@app.after_request
def after_request(response):
    """
    Ensure responses aren't cached.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.
    """
    if request.method == "POST":
        # Retrieve form data
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")
        confirmation = request.form.get("confirm_password")

        # Basic validations
        if not username:
            flash("Username is required.", "error")
            return render_template("register.html", username=username, email=email)
        if not email:
            flash("Email is required.", "error")
            return render_template("register.html", username=username, email=email)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format.", "error")
            return render_template("register.html", username=username, email=email)
        if not password:
            flash("Password is required.", "error")
            return render_template("register.html", username=username, email=email)
        if password != confirmation:
            flash("Passwords do not match.", "error")
            return render_template("register.html", username=username, email=email)
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template("register.html", username=username, email=email)

        # Check if the username or email already exists
        if User.get_by_username(username):
            flash("Username is already taken.", "error")
            return render_template("register.html", username=username, email=email)
        if User.get_by_email(email):
            flash("This email is already used.", "error")
            return render_template("register.html", username=username, email=email)

        # Insert the user into the database
        try:
            User.create(username, email, password)
            flash("Account created successfully! Please log in.", "success")
            return render_template("login.html")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return render_template("register.html", username=username, email=email)

    # Render the registration page
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log in an existing user.
    """
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Must provide username", "error")
            return render_template("login.html")

        elif not password:
            flash("Must provide password", "error")
            return render_template("login.html")

        rows = User.get_by_username(username)

        if len(rows) != 1 or not User.check_password(rows[0]["hash"], password):
            flash("Invalid username and/or password", "error")
            print("invalid usernam mdp")
            return render_template("login.html")

        session["user_id"] = rows[0]["id"]
        session["user_name"] = rows[0]["username"]
        session["user_email"] = rows[0]["email"]

        return redirect("/")

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """
    Update the user's profile information.
    """
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Basic validations
        if not username:
            flash("Username is required.", "error")
            return render_template("profile.html", username=username, email=email)
        if not email:
            flash("Email is required.", "error")
            return render_template("profile.html", username=username, email=email)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format.", "error")
            return render_template("profile.html", username=username, email=email)

        # Check if another user already takes the username or email
        existing_user = User.get_by_username(username)
        if existing_user and existing_user[0]["id"] != session["user_id"]:
            flash("Username is already taken.", "error")
            return render_template("profile.html", username=username, email=email)

        existing_email = User.get_by_email(email)
        if existing_email and existing_email[0]["id"] != session["user_id"]:
            flash("This email is already used.", "error")
            return render_template("profile.html", username=username, email=email)

        # Password validation only if the password is provided
        if password:
            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return render_template("profile.html", username=username, email=email)
        else:
            password = None

        # Update the user
        User.update(session["user_id"], username, email, password)

        # Update session data
        if session["user_name"] != username:
            session["user_name"] = username
            flash("Profile username updated successfully!", "success")
        elif session["user_email"] != email:
            session["user_email"] = email
            flash("Profile email updated successfully!", "success")
        elif password is not None:
            flash("Password updated successfully!", "success")
        else:
            flash("No changes to save ", "success")

        return redirect(url_for("profile"))

    return render_template("profile.html")


@app.route("/logout")
def logout():
    """
    Log user out.
    """
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
@login_required
def index():
    """
    Display the dashboard with active projects, ongoing tasks, and statistics.
    """
    user_id = session["user_id"]

    active_projects = Project.get_active_projects(user_id)
    ongoing_tasks = Task.get_tasks_on_hold(user_id)

    completed_this_week_tasks = Task.get_completed_this_week(user_id)
    completed_this_week_count = len(completed_this_week_tasks)

    all_tasks = Task.get_all(user_id)
    all_tasks_count = len(all_tasks)

    done_tasks = Task.get_done(user_id)
    done_tasks_count = len(done_tasks)

    denominator = all_tasks_count - done_tasks_count + completed_this_week_count
    if denominator == 0:
        completed_this_week = 0  # Default value
    else:
        completed_this_week = round(
            (completed_this_week_count / denominator) * 100,
            1,
        )

    upcoming_tasks = Task.get_upcoming_tasks(user_id)
    in_progress_task = Task.get(user_id, status="in progress")

    return render_template(
        "index.html",
        active_projects=active_projects,
        ongoing_tasks=ongoing_tasks,
        completed_this_week=completed_this_week,
        upcoming_tasks=upcoming_tasks,
        in_progress_task=in_progress_task,
    )


@app.route("/projects")
@login_required
def projects():
    """
    Display all projects for the user.
    """
    user_id = session["user_id"]
    projects = Project.get_all(user_id)
    return render_template("projects.html", projects=projects)


@app.route("/add_project", methods=["GET", "POST"])
@login_required
def add_project():
    """
    Add a new project.
    """
    if request.method == "POST":
        # Get form data
        title = request.form.get("title").strip()
        description = request.form.get("description", "").strip()
        detailed_description = request.form.get("detailed_description", "").strip()
        deadline = request.form.get("deadline")
        status = request.form.get("status", "to do")
        priority = request.form.get("priority", "medium")
        user_id = session["user_id"]

        # Validate form data
        if not title:
            flash("Project title is required.", "error")
            return render_template("add_project.html")

        try:
            # Create a project using the Project model
            Project.create(
                title=title,
                description=description,
                user_id=user_id,
                detailed_description=detailed_description,
                deadline=deadline,
                status=status,
                priority=priority,
            )
            flash("Project added successfully!", "success")
            return redirect("/projects")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return render_template("add_project.html")

    # GET request – show the added project form
    return render_template("add_project.html")


@app.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    """
    Edit an existing project.
    """
    # Get the project
    project = Project.get(project_id, session["user_id"])
    if not project:
        flash("Project not found.", "error")
        return redirect("/projects")

    if request.method == "POST":
        # Get form data
        title = request.form.get("title").strip()
        description = request.form.get("description", "").strip()
        detailed_description = request.form.get("detailed_description", "").strip()
        deadline = request.form.get("deadline")
        status = request.form.get("status", "to do")
        priority = request.form.get("priority", "medium")

        # Validate form data
        if not title:
            flash("Project title is required.", "error")
            return render_template("edit_project.html", project=project)

        try:
            # Update the project using the Project model
            Project.update(
                project_id=project_id,
                user_id=session["user_id"],
                title=title,
                description=description,
                detailed_description=detailed_description,
                deadline=deadline,
                status=status,
                priority=priority,
            )
            flash("Project updated successfully!", "success")
            return redirect("/projects")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return render_template("edit_project.html", project=project)

    # GET request – show the edit project form
    return render_template("edit_project.html", project=project[0])


@app.route("/delete_project/<int:project_id>")
@login_required
def delete_project(project_id):
    """
    Delete a project.
    """
    try:
        # Delete a project using the Project model
        task_to_update = Task.get(user_id=session["user_id"], project_id=project_id)

        for task in task_to_update:
            Task.update(task["id"], user_id=session["user_id"], project_id=None)

        Project.delete(project_id, session["user_id"])
        flash("Project deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {e}", "error")

    return redirect("/projects")


@app.route("/project/<int:project_id>")
@login_required
def project(project_id):
    """
    Display details of a specific project and its linked tasks.
    """
    # Get the project details
    project = Project.get(project_id, session["user_id"])

    if not project:
        flash("Project not found.", "error")
        return redirect("/projects")

    # Get all tasks linked to the project
    linked_tasks = {
        "to_do_tasks": Task.get(
            session.get("user_id"), project_id=project_id, status="to do"
        ),
        "in_progress_tasks": Task.get(
            session.get("user_id"), project_id=project_id, status="in progress"
        ),
        "done_tasks": Task.get(
            session.get("user_id"), project_id=project_id, status="done"
        ),
        "blocked_tasks": Task.get(
            session.get("user_id"), project_id=project_id, status="blocked"
        ),
    }
    return render_template(
        "project.html", project=project[0], linked_tasks=linked_tasks
    )


@app.route("/tasks")
@login_required
def tasks():
    """
    Display all tasks for the user, categorized by status.
    """
    to_do_tasks = Task.get(session.get("user_id"), status="to do")
    in_progress_tasks = Task.get(session.get("user_id"), status="in progress")
    done_tasks = Task.get(session.get("user_id"), status="done")
    blocked_tasks = Task.get(session.get("user_id"), status="blocked")

    return render_template(
        "tasks.html",
        to_do_tasks=to_do_tasks,
        in_progress_tasks=in_progress_tasks,
        done_tasks=done_tasks,
        blocked_tasks=blocked_tasks,
    )


@app.route("/task/<int:task_id>")
@login_required
def task(task_id):
    """
    Display details of a specific task.
    """
    # Get the task details
    task = Task.get(session["user_id"], id=task_id)
    if not task:
        flash("Task not found.", "error")
        return redirect("/tasks")

    # Get the linked project if it exists
    project = None
    if task[0].get("project_id"):
        project = Project.get(task[0]["project_id"], session["user_id"])

    return render_template(
        "task.html", task=task[0], project=project[0] if project else None
    )


@app.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():
    """
    Add a new task.
    """
    # Store the previous page in the session
    if request.method == "GET" and request.referrer:
        session["previous_page"] = request.referrer

    if request.method == "POST":
        # Get form data
        title = request.form.get("title").strip()
        description = request.form.get("description", "").strip()
        deadline = request.form.get("deadline")
        status = "to do"  # Default status for new tasks
        project_id = request.form.get("project_id")
        if not project_id:
            project_id = None
        if deadline:
            deadline = datetime.strptime(
                request.form.get("deadline"), "%Y-%m-%dT%H:%M"
            ).strftime("%Y-%m-%d %I:%M:%S %p")
        # Validate form data
        if not title:
            flash("Task title is required.", "error")
            return render_template("add_task.html")

        try:
            # Create a task using the Task model
            Task.create(
                title=title,
                description=description,
                user_id=session["user_id"],
                deadline=deadline,
                status=status,
                project_id=project_id,
            )
            flash("Task added successfully!", "success")
            return redirect(session.pop("previous_page", "/tasks"))
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return render_template("add_task.html")

    # GET request – show the add task form
    projects_ = Project.get_all(session["user_id"])
    return render_template("add_task.html", projects=projects_)


@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    """
    Edit an existing task.
    """
    # Store the previous page in the session
    if request.method == "GET" and request.referrer:
        session["previous_page"] = request.referrer
    # Get the task
    tasks = Task.get(session["user_id"], id=task_id)
    if not tasks:
        flash("Task not found.", "error")
        return redirect(request.referrer or "/tasks")

    # Extract the first task from the list
    task = tasks[0]

    if request.method == "POST":
        # Get form data
        title = request.form.get("title").strip()
        description = request.form.get("description", "").strip()
        detailed_description = request.form.get("detailed_description", "").strip()
        deadline = request.form.get("deadline")
        status = request.form.get("status")
        project_id = request.form.get("project_id")
        priority = request.form.get("priority")

        # Validate form data
        if not title:
            flash("Task title is required.", "error")
            return render_template("edit_task.html", task=task)

        try:
            if deadline:
                deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M").strftime(
                    "%Y-%m-%d %I:%M:%S %p"
                )
            # Update a task using the Task model
            Task.update(
                task_id=task_id,
                user_id=session["user_id"],
                title=title,
                project_id=project_id,
                description=description,
                detailed_description=detailed_description,
                priority=priority,
                deadline=deadline,
                status=status,
            )
            flash("Task updated successfully!", "success")
            return redirect(session.pop("previous_page", "/tasks"))
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return render_template("edit_task.html", task=task)

    # GET request – show the add task form
    projects_ = Project.get_all(session["user_id"])
    return render_template("edit_task.html", task=task, projects=projects_)


@app.route("/delete_task/<int:task_id>")
@login_required
def delete_task(task_id):
    """
    Delete a task.
    """
    try:
        # Delete a task using the Task model
        Task.delete(task_id, session["user_id"])
        flash("Task deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {e}", "error")

    return redirect(request.referrer or "/tasks")


@app.route("/update_task_status/<int:task_id>/<status>")
@login_required
def update_task_status(task_id, status):
    """
    Update the status of a task.
    Valid statuses are 'to do', 'in progress', and 'done'.
    """
    # Validate status
    valid_statuses = ["to do", "in progress", "done"]
    if status not in valid_statuses:
        flash("Invalid status.", "error")
        return redirect("/tasks")

    try:
        # Update task status using the Task model
        Task.update(task_id, session["user_id"], status=status)
        flash("Task status updated successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {e}", "error")

    return redirect(request.referrer or "/tasks")


@app.route("/calendar")
@login_required
def calendar():
    """
    Display the calendar view for tasks with status 'to do' or 'in progress' and their deadlines.
    """
    user_id = session["user_id"]

    # Get tasks with 'to do' or 'in progress' status
    tasks = Task.get(user_id, status="to do") + Task.get(user_id, status="in progress")

    # Format tasks for FullCalendar.js
    events = []
    for task in tasks:
        if task.get("deadline"):
            events.append({
                "id": task["id"],
                "title": task["title"],
                "start": task["deadline"].isoformat(),  # Convert datetime to ISO format. Use deadline as event date
                "description": task.get("description", ""),
                "status": task["status"],
            })

    return render_template("calendar.html", events=events)


if __name__ == "__main__":
    app.run(debug=True)
