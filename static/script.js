document.getElementById('course-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const courseNumbers = [];
    const inputs = document.querySelectorAll('input[name="course-number"]');
    inputs.forEach(input => {
        courseNumbers.push(input.value.trim());
    });

    console.log("Course numbers to send:", courseNumbers); // Debug statement

    const response = await fetch('/api/courses', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ courseNumbers: courseNumbers })
    });

    const schedules = await response.json();
    console.log("Schedules received from backend:", schedules); // Debug statement
    displaySchedules(schedules);
});

function addCourseField() {
    const container = document.getElementById('course-container');
    const inputCount = container.querySelectorAll('input').length;
    const newInput = document.createElement('input');
    newInput.type = 'text';
    newInput.name = 'course-number';
    newInput.id = `course-number-${inputCount + 1}`;
    newInput.required = true;

    const newLabel = document.createElement('label');
    newLabel.htmlFor = newInput.id;
    newLabel.textContent = 'Enter Course Number:';

    container.appendChild(newLabel);
    container.appendChild(newInput);
}

function displaySchedules(schedules) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = ''; // Clear previous results

    schedules.forEach((schedule, idx) => {
        console.log(`Processing schedule ${idx + 1}:`, schedule); // Debug statement
        const table = document.createElement('table');
        const thead = document.createElement('thead');
        const tbody = document.createElement('tbody');

        const headers = ['course_number', 'crn', 'section', 'status', 'course_name', 'hours', 'days', 'activity', 'time', 'instructor', 'prerequisites', 'colleges', 'majors'];
        const headerRow = document.createElement('tr');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header.replace('_', ' ').toUpperCase();
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);

        schedule.forEach(section => {
            console.log("Processing section:", section); // Debug statement
            const row = document.createElement('tr');
            headers.forEach(header => {
                const key = header;
                const td = document.createElement('td');
                td.textContent = section[key] !== undefined ? section[key] : 'N/A'; // Ensure keys match
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });

        table.appendChild(thead);
        table.appendChild(tbody);

        const tableContainer = document.createElement('div');
        tableContainer.classList.add('table-container');
        tableContainer.innerHTML = `<h2>Table ${idx + 1}</h2>`;
        tableContainer.appendChild(table);
        resultsDiv.appendChild(tableContainer);
    });
}
