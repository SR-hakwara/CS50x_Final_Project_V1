from .database import db
from datetime import datetime, timedelta


class Project:
    @staticmethod
    def create_table():
        """
        Creates the 'projects' table if it doesn't exist.
        The table includes columns for project details, status, priority, and foreign key to users.
        """
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER,
                user_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                detailed_description TEXT,
                start_date DATE DEFAULT CURRENT_DATE,
                deadline DATE,
                status TEXT CHECK(status IN ('to do', 'in progress', 'done', 'blocked')) DEFAULT 'to do',
                priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
                PRIMARY KEY (id, user_id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )

    @staticmethod
    def create(title, description, user_id, **kwargs):
        """
        Creates a new project for the specified user.
        Generates a new project ID by finding the maximum ID for the user and incrementing it by 1.
        Formats date to '%Y-%m-%d' if provided.
        """
        next_id = db.execute(
            """
            SELECT COALESCE(MAX(id), 0) + 1 
            FROM projects WHERE user_id = ?
            """,
            user_id,
        )[0]["COALESCE(MAX(id), 0) + 1"]

        # Format dates to "%Y-%m-%d" if provided
        start_date = kwargs.get("start_date")
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")

        deadline = kwargs.get("deadline")
        if deadline:
            deadline = datetime.strptime(deadline, "%Y-%m-%d").strftime("%Y-%m-%d")

        return db.execute(
            """
            INSERT INTO projects (id, title, description, user_id, detailed_description, 
                                start_date, deadline, status, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            next_id,
            title,
            description,
            user_id,
            kwargs.get("detailed_description", ""),
            start_date,
            deadline,
            kwargs.get("status", "to do"),
            kwargs.get("priority", "medium"),
        )

    @staticmethod
    def _parse_dates(project):
        """
        Ensures project dates are in "%Y-%m-%d" format for consistency.
        """
        if "start_date" in project and project["start_date"]:
            project["start_date"] = datetime.strptime(
                project["start_date"], "%Y-%m-%d"
            ).strftime("%Y-%m-%d")
        if "deadline" in project and project["deadline"]:
            project["deadline"] = datetime.strptime(
                project["deadline"], "%Y-%m-%d"
            ).strftime("%Y-%m-%d")
        return project

    @staticmethod
    def update(project_id, user_id, **kwargs):
        """
        Updates a project with the provided fields.
        Formats date to "%Y-%m-%d" if provided.
        Dynamically constructs the SET clause based on the provided kwargs.
        """
        if not kwargs:
            raise ValueError("No fields provided to update.")

        # Format dates to "%Y-%m-%d" if provided
        if "start_date" in kwargs and kwargs["start_date"]:
            kwargs["start_date"] = datetime.strptime(
                kwargs["start_date"], "%Y-%m-%d"
            ).strftime("%Y-%m-%d")
        if "deadline" in kwargs and kwargs["deadline"]:
            kwargs["deadline"] = datetime.strptime(
                kwargs["deadline"], "%Y-%m-%d"
            ).strftime("%Y-%m-%d")

        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [project_id, user_id]

        db.execute(
            f"""
            UPDATE projects 
            SET {set_clause}
            WHERE id = ? AND user_id = ?
            """,
            *values,
        )

    @staticmethod
    def get(project_id, user_id):
        """
        Retrieves a project by its ID and user ID.
        Returns a list of projects (typically one project).
        """
        projects = db.execute(
            """
            SELECT * FROM projects 
            WHERE id = ? AND user_id = ?
            """,
            project_id,
            user_id,
        )

        return [Project._parse_dates(project) for project in projects]

    @staticmethod
    def get_all(user_id):
        """
        Retrieves all projects for the specified user.
        """
        projects = db.execute("SELECT * FROM projects WHERE user_id = ?", user_id)
        return [Project._parse_dates(project) for project in projects]

    @staticmethod
    def get_active_projects(user_id):
        """
        Retrieves active projects (with status 'in progress') for the specified user.
        Includes a count of active tasks (tasks with status 'in progress' or 'blocked').
        """
        return db.execute(
            """
            SELECT p.*, COUNT(t.id) as active_tasks
            FROM projects p
            JOIN tasks t ON p.id = t.project_id 
            AND t.status IN ('in progress', 'blocked')
            WHERE p.user_id = ? AND p.status = 'in progress'
            GROUP BY p.id
            """,
            user_id,
        )

    @staticmethod
    def get_recent(user_id):
        """
        Retrieves projects from the last 7 days with status 'to do' for the specified user.
        """
        seven_days_ago = datetime.now() - timedelta(days=7)
        projects = db.execute(
            "SELECT * FROM projects WHERE user_id = ? AND status = 'to do' AND start_date >= ?",
            (user_id, seven_days_ago.strftime('%Y-%m-%d'))
        )
        return [Project._parse_dates(project) for project in projects]

    @staticmethod
    def delete(project_id, user_id):
        """
        Deletes a project by its ID and user ID.
        """
        db.execute(
            "DELETE FROM projects WHERE id = ? AND user_id = ?", project_id, user_id
        )