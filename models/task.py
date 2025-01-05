from .database import db
from datetime import datetime


class Task:
    VALID_STATUSES = ("to do", "in progress", "done", "blocked")
    VALID_PRIORITIES = ("low", "medium", "high", "urgent")

    @staticmethod
    def create_table() -> None:
        """
        Creates the 'tasks' table if it doesn't exist.
        The table includes columns for task details, status, priority, and foreign keys to users and projects.
        """
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER,
                user_id INTEGER,
                project_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                detailed_description TEXT,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deadline TIMESTAMP,
                status TEXT CHECK(status IN ('to do', 'in progress', 'done', 'blocked')) DEFAULT 'to do',
                priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
                completed_date TIMESTAMP,
                PRIMARY KEY (id, user_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (project_id, user_id) REFERENCES projects(id, user_id)
            )
            """
        )

    @staticmethod
    def validate_status(status: str) -> None:
        """
        Validates that the provided status is one of the valid statuses.
        Raises a ValueError if the status is invalid.
        """
        if status not in Task.VALID_STATUSES:
            raise ValueError(
                f"Invalid status. Must be one of: {', '.join(Task.VALID_STATUSES)}"
            )

    @staticmethod
    def validate_priority(priority: str) -> None:
        """
        Validates that the provided priority is one of the valid priorities.
        Raises a ValueError if the priority is invalid.
        """
        if priority not in Task.VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority. Must be one of: {', '.join(Task.VALID_PRIORITIES)}"
            )

    @staticmethod
    def create(title: str, description: str, user_id: int, **kwargs) -> None:
        """
        Creates a new task for the specified user.
        Generates a new task ID by finding the maximum ID for the user and incrementing it by 1.
        Formats date to '%Y-%m-%d %I:%M:%S %p' if provided.
        """
        if not title or not description or not user_id:
            raise ValueError("Title and description are required")

        if "status" in kwargs:
            Task.validate_status(kwargs["status"])
        if "priority" in kwargs:
            Task.validate_priority(kwargs["priority"])

        # Generate creation_date in AM/PM format
        creation_date = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        deadline = kwargs.get("deadline")
        if deadline:
            deadline = datetime.strptime(deadline, "%Y-%m-%d %I:%M:%S %p").strftime(
                "%Y-%m-%d %I:%M:%S %p"
            )
        completed_date = kwargs.get("completed_date")
        if completed_date:
            completed_date = datetime.strptime(
                completed_date, "%Y-%m-%d %I:%M:%S %p"
            ).strftime("%Y-%m-%d %I:%M:%S %p")

        next_id: int = db.execute(
            """
            SELECT COALESCE(MAX(id), 0) + 1 
            FROM tasks WHERE user_id = ?
            """,
            user_id,
        )[0]["COALESCE(MAX(id), 0) + 1"]

        return db.execute(
            """
            INSERT INTO tasks (id, title, description, user_id, project_id,
                             detailed_description, creation_date, deadline, status, priority, completed_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            next_id,
            title,
            description,
            user_id,
            kwargs.get("project_id", None),
            kwargs.get("detailed_description", ""),
            creation_date,
            deadline,
            kwargs.get("status", "to do"),
            kwargs.get("priority", "medium"),
            completed_date,
        )

    @staticmethod
    def update(task_id: int, user_id: int, **kwargs) -> None:
        """
        Updates a task with the provided fields.
        Automatically sets the completed_date if the status is updated to 'done'.
        Formats date to '%Y-%m-%d %I:%M:%S %p' if provided.
        Dynamically constructs the SET clause based on the provided kwargs.
        """
        if not task_id or not user_id:
            raise ValueError("task_id and user_id are required")

        if "status" in kwargs and kwargs["status"] == "done":
            kwargs["completed_date"] = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

        if "status" in kwargs:
            Task.validate_status(kwargs["status"])
        if "priority" in kwargs:
            Task.validate_priority(kwargs["priority"])
        if "project_id" in kwargs:
            if kwargs["project_id"] == "":
                kwargs["project_id"] = None

        allowed_columns = {
            "project_id",
            "title",
            "description",
            "detailed_description",
            "deadline",
            "status",
            "priority",
            "completed_date",
        }

        update_data = {
            key: value for key, value in kwargs.items() if key in allowed_columns
        }
        if not update_data:
            raise ValueError("No valid columns provided for update")

        set_clause = ", ".join([f"{key} = ?" for key in update_data])
        values = list(update_data.values()) + [task_id, user_id]

        db.execute(
            f"UPDATE tasks SET {set_clause} WHERE id = ? AND user_id = ?", *values
        )

    @staticmethod
    def delete(task_id, user_id):
        """
        Deletes a task by its ID and user ID.
        """
        db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", task_id, user_id)

    @staticmethod
    def _parse_dates(task):
        """
        Ensures task dates are in '%Y-%m-%d %I:%M:%S %p' format for consistency.
        """
        if "creation_date" in task and task["creation_date"]:
            task["creation_date"] = datetime.strptime(
                task["creation_date"], "%Y-%m-%d %I:%M:%S %p"
            )
        if "deadline" in task and task["deadline"]:
            task["deadline"] = datetime.strptime(
                task["deadline"], "%Y-%m-%d %I:%M:%S %p"
            )
        if "completed_date" in task and task["completed_date"]:
            task["completed_date"] = datetime.strptime(
                task["completed_date"], "%Y-%m-%d %I:%M:%S %p"
            )
        return task

    @staticmethod
    def get(user_id: int, **kwargs) -> list:
        """
        Retrieves tasks based on the provided filters.
        """
        if not user_id:
            raise ValueError("user_id is required")

        if "status" in kwargs:
            Task.validate_status(kwargs["status"])
        if "priority" in kwargs:
            Task.validate_priority(kwargs["priority"])

        allowed_columns = {
            "id",
            "project_id",
            "title",
            "description",
            "detailed_description",
            "deadline",
            "status",
            "priority",
            "completed_date",
        }

        get_data = {
            key: value for key, value in kwargs.items() if key in allowed_columns
        }
        if not get_data:
            raise ValueError("No valid columns provided")

        where_clause = " AND " + "AND ".join([f"{key} = ? " for key in get_data])
        values = [user_id] + list(get_data.values())
        tasks = db.execute(
            f"SELECT * From tasks WHERE user_id = ? {where_clause}", *values
        )
        return [Task._parse_dates(task) for task in tasks]

    @staticmethod
    def get_all(user_id):
        """
        Retrieves all tasks for the specified user.
        """
        tasks = db.execute("SELECT * FROM tasks WHERE user_id = ?", user_id)
        return [Task._parse_dates(task) for task in tasks]

    @staticmethod
    def get_by_project(project_id, user_id):
        """
        Retrieves tasks associated with the specified project.
        """
        tasks = db.execute(
            """
            SELECT * FROM tasks 
            WHERE project_id = ? AND user_id = ?
            """,
            project_id,
            user_id,
        )
        return [Task._parse_dates(task) for task in tasks]

    @staticmethod
    def get_in_progress(user_id):
        """
        Retrieves tasks with status 'in progress' for the specified user.
        """
        tasks = db.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND status = 'in progress'", user_id
        )
        return [Task._parse_dates(task) for task in tasks]

    @staticmethod
    def get_done(user_id):
        """
        Retrieves tasks with status 'done' for the specified user.
        """
        tasks = db.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND status = 'done'", user_id
        )
        return [Task._parse_dates(task) for task in tasks]

    @staticmethod
    def get_blocked(user_id):
        """
        Retrieves tasks with status 'blocked' for the specified user.
        """
        tasks = db.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND status = 'blocked'", user_id
        )
        return [Task._parse_dates(task) for task in tasks]

    @staticmethod
    def get_tasks_on_hold(user_id):
        """
        Retrieves tasks with status 'to do' or 'blocked' for the specified user.
        """
        tasks = db.execute(
            """
            SELECT * FROM tasks 
            WHERE user_id = ? AND status IN ('to do', 'blocked')
            ORDER BY deadline ASC
            """,
            user_id,
        )
        return [Task._parse_dates(task) for task in tasks]

    @staticmethod
    def get_completed_this_week(user_id):
        """
        Retrieves tasks completed in the current week for the specified user.
        """
        tasks = db.execute(
            """
            SELECT * FROM tasks 
            WHERE user_id = ? 
            AND status = 'done' 
            AND completed_date IS NOT NULL
            AND strftime('%Y-%W', substr(completed_date, 1, 10)) = strftime('%Y-%W', 'now')
            """,
            user_id,
        )
        return [Task._parse_dates(task) for task in tasks]

    @staticmethod
    def get_upcoming_tasks(user_id, days=7):
        """
        Retrieves tasks with deadlines within the next number of days for the specified user.
        """
        tasks = db.execute(
            """ 
            SELECT * FROM tasks
            WHERE user_id = ?
            AND status != 'done'
            AND status != 'in progress'
            AND deadline BETWEEN date('now') AND date('now', '+' || ? || ' days')
            ORDER BY deadline ASC 
            """,
            user_id,
            days,
        )
        return [Task._parse_dates(task) for task in tasks]

    @staticmethod
    def get_all_unassigned(user_id):
        """
        Retrieves tasks that aren't assigned to any project for the specified user.
        """
        tasks = db.execute(
            "SELECT * FROM tasks WHERE project_id IS NULL AND user_id = ?", user_id
        )
        return [Task._parse_dates(task) for task in tasks]