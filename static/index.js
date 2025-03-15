import { Calendar } from 'https://cdn.jsdelivr.net/npm/@fullcalendar/core@6.1.15/+esm';
import interactionPlugin from 'https://cdn.jsdelivr.net/npm/@fullcalendar/interaction@6.1.15/+esm';
import dayGridPlugin from 'https://cdn.jsdelivr.net/npm/@fullcalendar/daygrid@6.1.15/+esm';
import timeGridPlugin from 'https://cdn.jsdelivr.net/npm/@fullcalendar/timegrid@6.1.15/+esm';
import listPlugin from 'https://cdn.jsdelivr.net/npm/@fullcalendar/list@6.1.15/+esm';

document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
	console.log(document.getElementById('events-data').textContent);
    var events = JSON.parse(document.getElementById('events-data').textContent);

    var calendar = new Calendar(calendarEl, {
        plugins: [interactionPlugin, dayGridPlugin, timeGridPlugin, listPlugin],
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        initialDate: new Date().toISOString().split("T")[0],
        navLinks: true,
        editable: true,
        dayMaxEvents: true,
        events: events
    });

    calendar.render();

	document.getElementById("event-form").addEventListener("submit", async function (event) {
        event.preventDefault();

        let eventName = document.getElementById("event-name").value;
        let dueDate = document.getElementById("due-date").value;
        let description = document.getElementById("description").value;

        if (eventName && dueDate) {
            let newEvent = {
                title: eventName,
                start: dueDate,
                description: description
            };

            try {
                let response = await fetch('/add-event', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newEvent)
                });

                let data = await response.json();
                if (data.success) {
                    calendar.addEvent(newEvent);
                    document.getElementById("event-form").reset();
                    alert("Event added successfully!");
                } else {
                    alert("Failed to add event.");
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Server error. Try again.");
            }
        }
    });

});
