document.addEventListener('DOMContentLoaded', function() {
    // Initialize Luxon DateTime
    const DateTime = luxon.DateTime;
    
    // Common timezone options
    const TIMEZONE_OPTIONS = [
        'UTC',
        'America/Los_Angeles',
        'America/New_York',
        'America/Chicago',
        'Europe/London',
        'Europe/Paris',
        'Asia/Tokyo',
        'Asia/Shanghai',
        'Asia/Singapore',
        'Australia/Sydney'
    ];

    // State management
    let selectedTimezones = new Set();
    let events = [];

    // DOM elements
    const timezoneSelectorDiv = document.getElementById('timezone-selectors');
    const timezoneCalendarsDiv = document.getElementById('timezone-calendars');
    const eventForm = document.getElementById('event-form');
    const eventsListDiv = document.getElementById('events-list');
    const eventTimezoneSelect = document.getElementById('event-timezone');

    // Initialize timezone selectors
    function createTimezoneSelector(index) {
        const selectorDiv = document.createElement('div');
        selectorDiv.className = 'timezone-select';
        
        const select = document.createElement('select');
        select.id = `timezone-${index}`;
        
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = `Select Timezone ${index + 1}`;
        select.appendChild(defaultOption);
        
        TIMEZONE_OPTIONS.forEach(tz => {
            const option = document.createElement('option');
            option.value = tz;
            option.textContent = tz;
            select.appendChild(option);
        });

        select.addEventListener('change', () => {
            if (select.value) {
                selectedTimezones.add(select.value);
            }
            updateCalendarViews();
        });

        selectorDiv.appendChild(select);
        return selectorDiv;
    }

    // Initialize event timezone selector
    function initializeEventTimezoneSelector() {
        TIMEZONE_OPTIONS.forEach(tz => {
            const option = document.createElement('option');
            option.value = tz;
            option.textContent = tz;
            eventTimezoneSelect.appendChild(option);
        });
    }

    // Update calendar views for selected timezones
    function updateCalendarViews() {
        timezoneCalendarsDiv.innerHTML = '';
        
        selectedTimezones.forEach(timezone => {
            const calendarDiv = document.createElement('div');
            calendarDiv.className = 'timezone-calendar';
            
            const header = document.createElement('div');
            header.className = 'timezone-header';
            
            const now = DateTime.now().setZone(timezone);
            header.textContent = `${timezone}: ${now.toFormat('yyyy-MM-dd HH:mm:ss')}`;
            
            calendarDiv.appendChild(header);
            timezoneCalendarsDiv.appendChild(calendarDiv);
        });
    }

    // Event handlers
    async function handleEventSubmit(e) {
        e.preventDefault();
        
        const title = document.getElementById('event-title').value;
        const date = document.getElementById('event-date').value;
        const time = document.getElementById('event-time').value;
        const timezone = document.getElementById('event-timezone').value;
        
        const event = {
            title,
            datetime: `${date}T${time}`,
            timezone
        };

        try {
            const response = await fetch('/api/events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(event)
            });

            if (!response.ok) {
                throw new Error('Failed to create event');
            }

            const result = await response.json();
            events.push(result.event);
            updateEventsList();
            eventForm.reset();
        } catch (error) {
            console.error('Error creating event:', error);
            alert('Failed to create event. Please try again.');
        }
    }

    async function loadEvents() {
        try {
            const response = await fetch('/api/events');
            if (!response.ok) {
                throw new Error('Failed to fetch events');
            }
            events = await response.json();
            updateEventsList();
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    function updateEventsList() {
        const listContainer = document.createElement('div');
        
        events.forEach((event, index) => {
            const eventDiv = document.createElement('div');
            eventDiv.className = 'event-item';
            
            const datetime = DateTime.fromISO(event.datetime, { zone: event.timezone });
            
            const titleDiv = document.createElement('div');
            titleDiv.className = 'event-title';
            titleDiv.textContent = event.title;
            
            const timeDiv = document.createElement('div');
            timeDiv.className = 'event-time';
            
            // Show time in all selected timezones
            const times = Array.from(selectedTimezones).map(tz => {
                return `${tz}: ${datetime.setZone(tz).toFormat('yyyy-MM-dd HH:mm')}`;
            }).join('\n');
            
            timeDiv.textContent = times;
            
            const deleteButton = document.createElement('button');
            deleteButton.className = 'event-delete';
            deleteButton.textContent = '×';
            deleteButton.onclick = () => deleteEvent(index);
            
            eventDiv.appendChild(deleteButton);
            eventDiv.appendChild(titleDiv);
            eventDiv.appendChild(timeDiv);
            
            listContainer.appendChild(eventDiv);
        });
        
        eventsListDiv.innerHTML = '<h2>Scheduled Events</h2>';
        eventsListDiv.appendChild(listContainer);
    }

    async function deleteEvent(index) {
        try {
            const response = await fetch(`/api/events/${index}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete event');
            }
            
            events.splice(index, 1);
            updateEventsList();
        } catch (error) {
            console.error('Error deleting event:', error);
            alert('Failed to delete event. Please try again.');
        }
    }

    // Initialize the page
    function initialize() {
        // Create three timezone selectors
        for (let i = 0; i < 3; i++) {
            timezoneSelectorDiv.appendChild(createTimezoneSelector(i));
        }
        
        // Initialize event timezone selector
        initializeEventTimezoneSelector();
        
        // Set up event form handler
        eventForm.addEventListener('submit', handleEventSubmit);
        
        // Load existing events
        loadEvents();
        
        // Update time display periodically
        setInterval(updateCalendarViews, 1000);
    }

    // Start the application
    initialize();
});
