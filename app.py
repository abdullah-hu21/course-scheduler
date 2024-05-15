import sys
import webbrowser
from threading import Timer
from flask import Flask, jsonify, request, render_template
from bs4 import BeautifulSoup
import requests
import chardet
import itertools

app = Flask(__name__, static_folder='static', template_folder='templates')

# Mapping for Arabic days to English days
day_mapping = {
    'ح': 'Sunday',
    'ن': 'Monday',
    'ث': 'Tuesday',
    'ر': 'Wednesday',
    'خ': 'Thursday'
}

def convert_time(time_str):
    """Convert time from 24-hour format to 12-hour format with AM/PM."""
    start_time, end_time = time_str.split(' - ')
    start_time = int(start_time)
    end_time = int(end_time)
    start_period = "AM" if start_time < 1200 else "PM"
    end_period = "AM" if end_time < 1200 else "PM"
    start_time = f"{start_time // 100}:{start_time % 100:02d} {start_period}"
    end_time = f"{end_time // 100}:{end_time % 100:02d} {end_period}"
    return f"{start_time} - {end_time}"

def fetch_course_data(course_numbers):
    url = "https://ssb-ar.kfu.edu.sa/PROD_ar/ws?p_trm_code=144610&p_col_code=22&p_sex_code=11"
    response = requests.get(url)
    detected_encoding = chardet.detect(response.content)['encoding']
    print(f"Detected encoding: {detected_encoding}")  # Debug statement

    # Decode the content
    content = response.content.decode(detected_encoding)

    # Use BeautifulSoup with lxml parser
    soup = BeautifulSoup(content, 'lxml')

    course_data = []
    rows = soup.find_all('tr', bgcolor='#F1F5FA')
    print("Fetching course data...")  # Debug statement
    for row in rows:
        columns = row.find_all('td')
        if len(columns) >= 13:
            course_number = columns[0].text.strip()
            status = columns[3].text.strip()
            if course_number in course_numbers and status == "متاحه":
                # Print the raw HTML content for debugging
                print(f"Raw HTML content for course number {course_number}: {row.encode('utf-8')}")

                # Print status for debugging
                print(f"Processing course number: {course_number}, Status: {status}")

                # Translate Arabic days to English
                days_arabic = columns[6].text.strip()
                days_english = ', '.join(day_mapping[day] for day in days_arabic if day in day_mapping)

                # Convert time format
                time_english = convert_time(columns[8].text.strip())

                section_data = {
                    'course_number': course_number,
                    'crn': columns[1].text.strip(),
                    'section': columns[2].text.strip(),
                    'status': status,
                    'course_name': columns[4].text.strip(),
                    'hours': columns[5].text.strip(),
                    'days': days_english,
                    'activity': columns[7].text.strip(),
                    'time': time_english,
                    'instructor': columns[9].text.strip(),
                    'prerequisites': columns[10].text.strip(),
                    'colleges': columns[11].text.strip(),
                    'majors': columns[12].text.strip() if len(columns) > 12 else ''
                }
                print(f"Adding section: {section_data}")  # Debug statement
                course_data.append(section_data)

    print(f"Total sections fetched: {len(course_data)}")  # Debug statement
    return course_data

def check_conflict(time1, time2):
    """Check if two time slots conflict."""
    def to_24_hour(time):
        hours, minutes = map(int, time[:-3].split(':'))
        period = time[-2:]
        if period == 'PM' and hours != 12:
            hours += 12
        if period == 'AM' and hours == 12:
            hours = 0
        return hours * 100 + minutes

    start1, end1 = time1.split(' - ')
    start2, end2 = time2.split(' - ')

    start1 = to_24_hour(start1)
    end1 = to_24_hour(end1)
    start2 = to_24_hour(start2)
    end2 = to_24_hour(end2)

    return not (end1 <= start2 or end2 <= start1)

def generate_schedule_combinations(course_data):
    # Group sections by course number
    grouped_data = {}
    for section in course_data:
        course_number = section['course_number']
        if course_number not in grouped_data:
            grouped_data[course_number] = []
        grouped_data[course_number].append(section)

    # Generate all combinations of one section per course
    all_combinations = list(itertools.product(*grouped_data.values()))

    # Filter out combinations with time conflicts
    valid_combinations = []
    for combo in all_combinations:
        conflict = False
        for i in range(len(combo)):
            for j in range(i + 1, len(combo)):
                if combo[i]['days'] == combo[j]['days'] and check_conflict(combo[i]['time'], combo[j]['time']):
                    conflict = True
                    break
            if conflict:
                break
        if not conflict:
            valid_combinations.append(combo)

    return valid_combinations

@app.route('/api/courses', methods=['POST'])
def get_courses():
    data = request.json
    course_numbers = data.get('courseNumbers', [])
    print(f"Received course numbers: {course_numbers}")  # Debug statement
    course_data = fetch_course_data(course_numbers)
    valid_combinations = generate_schedule_combinations(course_data)
    print(f"Valid combinations sent to frontend: {valid_combinations}")  # Debug statement
    return jsonify(valid_combinations)

@app.route('/')
def serve_index():
    return render_template('index.html')

def open_browser():
    chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
    webbrowser.get(chrome_path).open("http://127.0.0.1:5000")

if __name__ == '__main__':
    # Set the default encoding to utf-8
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    
    # Open the browser after a short delay
    Timer(1, open_browser).start()
    
    app.run(debug=True)
