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

    // Calendar view state
    const HOURS_IN_DAY = 24;
    const MINUTES_PER_HOUR = 60;
    const HOUR_HEIGHT = 48; // pixels per hour
    let currentView = 'week';
    let currentDate = DateTime.now();

    // State management
    let selectedTimezones = new Set();
    let events = [];

    // DOM elements
    const timezoneSelectorDiv = document.getElementById('timezone-selectors');
    const timezoneCalendarsDiv = document.getElementById('timezone-calendars');
    const timeColumnDiv = document.querySelector('.time-column');
    const calendarContentDiv = document.querySelector('.calendar-content');
    const eventForm = document.getElementById('event-form');
    const eventsListDiv = document.getElementById('events-list');
    const eventTimezoneSelect = document.getElementById('event-timezone');
    const todayBtn = document.getElementById('today-btn');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const currentDateDisplay = document.getElementById('current-date');
    const viewButtons = {
        day: document.getElementById('day-view-btn'),
        week: document.getElementById('week-view-btn'),
        month: document.getElementById('month-view-btn')
    };

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
        // Update timezone columns
        const timezoneColumnsDiv = document.getElementById('timezone-columns');
        timezoneColumnsDiv.innerHTML = '';
        
        selectedTimezones.forEach(timezone => {
            const column = document.createElement('div');
            column.className = 'timezone-column';
            
            const header = document.createElement('div');
            header.className = 'timezone-header';
            
            const label = document.createElement('div');
            label.className = 'timezone-label';
            label.textContent = timezone;
            
            const time = document.createElement('div');
            time.className = 'timezone-time';
            time.textContent = DateTime.now().setZone(timezone).toFormat('HH:mm');
            
            header.appendChild(label);
            header.appendChild(time);
            column.appendChild(header);
            timezoneColumnsDiv.appendChild(column);
        });

        // Clear existing content
        timeColumnDiv.innerHTML = '';
        calendarContentDiv.innerHTML = '';
        
        // Generate time labels
        for (let hour = 0; hour < HOURS_IN_DAY; hour++) {
            const timeLabel = document.createElement('div');
            timeLabel.className = 'time-label';
            timeLabel.textContent = DateTime.now().set({ hour }).toFormat('HH:mm');
            timeColumnDiv.appendChild(timeLabel);
        }

        // Add current time indicator
        const now = DateTime.now();
        const currentTimeIndicator = document.createElement('div');
        currentTimeIndicator.className = 'current-time-indicator';
        const minutesSinceMidnight = now.hour * 60 + now.minute;
        const topPosition = (minutesSinceMidnight / MINUTES_PER_HOUR) * HOUR_HEIGHT;
        currentTimeIndicator.style.top = `${topPosition}px`;
        timeColumnDiv.appendChild(currentTimeIndicator);

        // Calculate date range for current view
        const startDate = currentView === 'week' 
            ? currentDate.startOf('week')
            : currentDate.startOf('day');
        
        const daysToShow = currentView === 'week' ? 7 : 1;

        // Create columns for each day
        for (let dayOffset = 0; dayOffset < daysToShow; dayOffset++) {
            const currentColumnDate = startDate.plus({ days: dayOffset });
            const dayColumn = document.createElement('div');
            dayColumn.className = 'day-column';
            
            // Add 'today' class if this column represents today
            if (currentColumnDate.hasSame(DateTime.now(), 'day')) {
                dayColumn.classList.add('today');
            }

            // Create hour cells
            for (let hour = 0; hour < HOURS_IN_DAY; hour++) {
                const hourCell = document.createElement('div');
                hourCell.className = 'hour-cell';
                hourCell.dataset.date = currentColumnDate.toISO();
                hourCell.dataset.hour = hour;

                // Show times in all selected timezones
                const timeDiv = document.createElement('div');
                timeDiv.className = 'timezone-times';
                
                selectedTimezones.forEach(timezone => {
                    const time = currentColumnDate
                        .set({ hour })
                        .setZone(timezone);
                    
                    const timeSpan = document.createElement('span');
                    timeSpan.className = 'timezone-time';
                    timeSpan.textContent = `${timezone}: ${time.toFormat('HH:mm')}`;
                    timeDiv.appendChild(timeSpan);
                });

                hourCell.appendChild(timeDiv);
                dayColumn.appendChild(hourCell);
            }

            calendarContentDiv.appendChild(dayColumn);
        }

        // Update events display
        displayEvents();
    }

    // Display events on the calendar
    function displayEvents() {
        // Clear existing event elements
        document.querySelectorAll('.event-display').forEach(el => el.remove());

        events.forEach(event => {
            const startDate = DateTime.fromISO(event.start_datetime);
            const endDate = DateTime.fromISO(event.end_datetime);
            
            // Find the corresponding column
            const dayColumn = Array.from(calendarContentDiv.children)
                .find(col => {
                    const cellDate = DateTime.fromISO(col.querySelector('.hour-cell').dataset.date);
                    return cellDate.hasSame(startDate, 'day');
                });

            if (dayColumn) {
                const startMinutes = startDate.hour * 60 + startDate.minute;
                const endMinutes = endDate.hour * 60 + endDate.minute;
                const duration = endMinutes - startMinutes;
                
                const eventElement = document.createElement('div');
                eventElement.className = 'event-display';
                eventElement.style.top = `${(startMinutes / MINUTES_PER_HOUR) * HOUR_HEIGHT}px`;
                eventElement.style.height = `${(duration / MINUTES_PER_HOUR) * HOUR_HEIGHT}px`;
                eventElement.style.backgroundColor = event.color || '#1a73e8';
                
                // Create timezone times string
                const timeStrings = Array.from(selectedTimezones).map(tz => {
                    const tzStart = startDate.setZone(tz);
                    const tzEnd = endDate.setZone(tz);
                    return `${tz}: ${tzStart.toFormat('HH:mm')} - ${tzEnd.toFormat('HH:mm')}`;
                }).join('\n');

                eventElement.innerHTML = `
                    <div class="event-title">${event.title}</div>
                    <div class="event-time">${timeStrings}</div>
                    ${event.description ? `<div class="event-description">${event.description}</div>` : ''}
                `;

                dayColumn.appendChild(eventElement);
            }
        });
    }

    // Event handlers
    async function handleEventSubmit(e) {
        e.preventDefault();
        
        const title = document.getElementById('event-title').value;
        const startDate = document.getElementById('event-start-date').value;
        const startTime = document.getElementById('event-start-time').value;
        const endDate = document.getElementById('event-end-date').value;
        const endTime = document.getElementById('event-end-time').value;
        const timezone = document.getElementById('event-timezone').value;
        const description = document.getElementById('event-description').value;
        const color = document.getElementById('event-color').value;
        
        const event = {
            title,
            start_datetime: `${startDate}T${startTime}`,
            end_datetime: `${endDate}T${endTime}`,
            timezone,
            description,
            color
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

    // Calendar view functions
    function generateTimeLabels() {
        timeColumnDiv.innerHTML = '';
        for (let hour = 0; hour < HOURS_IN_DAY; hour++) {
            const timeLabel = document.createElement('div');
            timeLabel.className = 'time-label';
            timeLabel.textContent = `${hour.toString().padStart(2, '0')}:00`;
            timeLabel.style.height = `${HOUR_HEIGHT}px`;
            timeColumnDiv.appendChild(timeLabel);
        }
    }

    function generateCalendarGrid() {
        calendarContentDiv.innerHTML = '';
        const daysToShow = currentView === 'week' ? 7 : 1;
        
        // Create grid cells for each day and hour
        for (let day = 0; day < daysToShow; day++) {
            const dayColumn = document.createElement('div');
            dayColumn.className = 'day-column';
            dayColumn.style.height = `${HOURS_IN_DAY * HOUR_HEIGHT}px`;
            
            // Create hour cells within the day
            for (let hour = 0; hour < HOURS_IN_DAY; hour++) {
                const hourCell = document.createElement('div');
                hourCell.className = 'hour-cell';
                hourCell.style.height = `${HOUR_HEIGHT}px`;
                dayColumn.appendChild(hourCell);
            }
            
            calendarContentDiv.appendChild(dayColumn);
        }
    }

    function updateCurrentDateDisplay() {
        const format = currentView === 'month' ? 'MMMM yyyy' : 'MMMM d, yyyy';
        currentDateDisplay.textContent = currentDate.toFormat(format);
    }

    function switchView(view) {
        currentView = view;
        Object.keys(viewButtons).forEach(key => {
            viewButtons[key].classList.toggle('active', key === view);
        });
        updateCalendarView();
    }

    function updateCalendarView() {
        updateCurrentDateDisplay();
        generateTimeLabels();
        generateCalendarGrid();
        // Populate events after grid is generated
        populateEvents();
    }

    function navigateCalendar(direction) {
        const units = {
            day: { days: 1 },
            week: { weeks: 1 },
            month: { months: 1 }
        };
        currentDate = currentDate.plus(units[currentView]).multiply(direction);
        updateCalendarView();
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
        
        // Set up navigation handlers
        todayBtn.addEventListener('click', () => {
            currentDate = DateTime.now();
            updateCalendarView();
        });
        
        prevBtn.addEventListener('click', () => navigateCalendar(-1));
        nextBtn.addEventListener('click', () => navigateCalendar(1));
        
        // Set up view switching handlers
        Object.entries(viewButtons).forEach(([view, button]) => {
            button.addEventListener('click', () => switchView(view));
        });
        
        // Load existing events
        loadEvents();
        
        // Initial calendar setup
        updateCalendarView();
        
        // Update timezone times periodically
        function updateTimezoneTimes() {
            const timezoneColumns = document.querySelectorAll('.timezone-column');
            timezoneColumns.forEach(column => {
                const timeElement = column.querySelector('.timezone-time');
                const timezone = column.querySelector('.timezone-label').textContent;
                timeElement.textContent = DateTime.now().setZone(timezone).toFormat('HH:mm');
            });
        }

        // Update times every minute
        setInterval(() => {
            updateTimezoneTimes();
            if (currentView !== 'month') {
                updateCalendarView();
            }
        }, 60000); // Update every minute

        // Initial time update
        updateTimezoneTimes();
    }

    // Start the application
    initialize();
});
