# Project and Task Management Web Application

#### Video Demo: [URL HERE](https://youtu.be/6N83oWLCxk0)
#### Description: A web application for managing projects and tasks, built with Flask, Tailwind CSS, and DaisyUI.

## Overview

This web application is designed to help users manage their projects and tasks efficiently. It provides a user-friendly interface for creating, viewing, updating, and deleting projects and tasks. The application is built using **Flask** for the backend, **Tailwind CSS** for styling, and **DaisyUI** for pre-designed components.

The application follows the **MVC (Model-View-Controller)** architecture, ensuring a clean separation of concerns. Data is stored in an **SQLite** database, making it lightweight and easy to deploy.

## Features
![image](https://github.com/user-attachments/assets/df14a717-a5ae-4fe0-a914-93b3f26da632)

### Project Management
- **Create Projects**: Add new projects with details like title, description, deadline, status, and priority.
- **View Projects**: View a list of all projects or detailed information about a specific project.
- **edit Projects**: Modify project details.
- **Delete Projects**: Remove projects, ensuring that linked tasks are updated accordingly.

### Task Management
- **Create Tasks**: Add new tasks with details like title, description, deadline, status, and priority.
- **View Tasks**: View a list of all tasks or detailed information about a specific task.
- **Update Tasks**: Modify task details, including linking or unlinking them from projects.
- **Delete Tasks**: Remove tasks, ensuring that they're removed from any linked projects.

### User Authentication
- **Register**: Create a new account with a username, email, and password.
- **Login**: Log in to access your projects and tasks.
- **Profile**: Update your profile information, including username, email, and password.

### Dashboard
- **Overview**: View a summary of active projects, ongoing tasks, completed tasks, and upcoming deadlines.
- **Statistics**: Track progress with statistics like the percentage of tasks completed this week.

## File Structure

- `app.py`: The main Flask application file.
- `app.db`: the database.
- `helpers.py`: helpers function (only one for now).
- `README.md`: this file.
- `requirements.txt`: Lists the Python dependencies.
- `models/`: Contains the database models.
  - `__init__.py`: Mark the directory as a Python package, enabling to import modules from it. Initialize db tables.
  - `database.py`: Handles database initialization and connection.
  - `user.py`: Defines the `User` model.
  - `project.py`: Defines the `Project` model.
  - `task.py`: Defines the `Task` model.
- `templates/`: Contains the HTML templates.
  - `layout.html`: The base template for the application.
  - `index.html`: The home page with the dashboard.
  - `projects.html`: Displays a list of projects.
  - `add_project.html`: Form for adding a new project.
  - `edit_project.html`: Form for editing an existing project.
  - `project.html`: Displays detailed information about a project.
  - `tasks.html`: Displays a list of tasks.
  - `add_task.html`: Form for adding a new task.
  - `edit_task.html`: Form for editing an existing task.
  - `task.html`: Displays detailed information about a task.
  - `login.html`: The login page.
  - `register.html`: The registration page.
  - `profile.html`: The user profile page.
  - `calendar.html`: displays a tasks calendar deadline.
- `static/`: Contains static files like CSS and JavaScript.
  - `css/`: Custom CSS files.
  - `js/`: JavaScript files.
  - `img/`: Image files.

## Design Choices and Justifications

### Flask
Flask was chosen for its simplicity and flexibility. 
It allows for rapid development while providing the necessary tools to build a robust web application.

### Tailwind CSS and DaisyUI
Tailwind CSS was selected for its utility-first approach, making it easy to create custom designs without writing a lot of CSS. 
DaisyUI complements Tailwind by providing pre-designed components, speeding up the development process.

### SQLite
SQLite was chosen as the database because it is lightweight, easy to set up, and sufficient for the scale of this application. 
It also integrates seamlessly with Flask.

### MVC Architecture
The application follows the MVC architecture to ensure a clear separation of concerns. 
This makes the codebase more maintainable and easier to extend in the future.

## Libraries Used

- **Flask**: Web framework for Python.
- **Flask-Session**: Manages user sessions.
- **SQLite3**: Lightweight database for data storage.
- **Tailwind CSS**: Utility-first CSS framework. (Node.js was used to install and use it)
- **DaisyUI**: Component library for Tailwind CSS. (Node.js was used to install and use it)
- **CS50**: Provides a simple interface for interacting with the SQLite database.

## Usage Example

### Launching the Application

Navigate to the project directory:

```
cd project
```
Install the dependencies:

```
pip install -r requirements.txt
```
Run the application:

```
python app.py (or flask run)
```
Open your browser and navigate to http://localhost:5000.

## Project and Task Management Workflow
### 1. Register and Log In

   - Register a new account or log in with existing credentials.

### 2. Dashboard

   - View an overview of your active projects, ongoing tasks, and upcoming deadlines.

### 3. Manage Projects

   - **Add a Project**: Fill out the form to create a new project.
   
   - **View Projects**: See a list of all your projects or view detailed information about a specific project.
   
   - **Edit a Project**: Update project details or add/remove linked tasks.
   
   - **Delete a Project**: Remove a project and its linked tasks.

### 4. Manage Tasks

   - **Add a Task**: Fill out the form to create a new task.
   
   - **View Tasks**: See a list of all your tasks or view detailed information about a specific task.
   
   - **Edit a Task**: Update task details or link/unlink it from a project.
   
   - **Delete a Task**: Remove a task and update any linked projects.

### 5. Profile

- Update your profile information, including username, email, and password.

## Error Handling

The application includes robust error handling to ensure a smooth user experience. For example:

- **Invalid Dates**: Deadlines must be in the future and in the correct format (YYYY-MM-DD).

- **Duplicate Entries**: Usernames and emails must be unique.

- **Missing Fields**: Required fields must be filled out when creating or updating projects and tasks.

## Conclusion

This project demonstrates the core principles of web development using Flask, Tailwind CSS, and DaisyUI.
It provides a practical and functional solution for managing projects and tasks, with a clean and maintainable codebase.
The application is designed to be easily extensible, allowing for future enhancements such as integrating a more advanced database or adding additional features.

