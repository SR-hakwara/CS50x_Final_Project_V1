document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const events = JSON.parse(document.getElementById('calendar-data').textContent);  // Pass events from Flask

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',  // Default view
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: events,
        eventClick: function(info) {
            // Update modal content
            document.getElementById('modal-title').textContent = info.event.title;
            document.getElementById('modal-description').textContent = `Description: ${info.event.extendedProps.description}\nStatus: ${info.event.extendedProps.status}`;

            // Update links with task ID
            const taskId = info.event.id;  // Ensure we get the task ID from the event data
            document.getElementById('view-task').href = `/task/${taskId}`;
            document.getElementById('edit-task').href = `/edit_task/${taskId}`;
            document.getElementById('delete-task').href = `/delete_task/${taskId}`;

            // Show modal
            document.getElementById('task-modal').checked = true;
        }
    });

    calendar.render();
});
