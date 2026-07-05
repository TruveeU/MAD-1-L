import csv
import matplotlib.pyplot as plt
from flask import Flask, render_template, request

app = Flask(__name__)

CSV_FILE = 'data.csv'

def read_csv():
    """Read the CSV file and return a list of dictionaries.
    Expected columns: 'Student id', 'Course id', 'Marks'
    """
    rows = []
    with open(CSV_FILE, newline='') as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            cleaned = {
                'Student id': row['Student id'].strip(),
                'Course id': row['Course id'].strip(),
                'Marks': int(row['Marks'].strip())
            }
            rows.append(cleaned)
    return rows

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        id_type = request.form.get('ID')
        id_value = request.form.get('id_value')
        if not id_type or not id_value:
            return render_template('error.html')
        try:
            id_int = int(id_value)
        except ValueError:
            return render_template('error.html')
        data = read_csv()
        if id_type == 'student_id':
            return student_data(data, id_int)
        elif id_type == 'course_id':
            return course_data(data, id_int)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

def student_data(rows, sid):
    courses = [r for r in rows if r['Student id'] == str(sid)]
    if not courses:
        return render_template('error.html')
    total = sum(r['Marks'] for r in courses)
    return render_template('student_data.html', courses=courses, total=total)

def course_data(rows, cid):
    marks = [r['Marks'] for r in rows if r['Course id'] == str(cid)]
    if not marks:
        return render_template('error.html')
    avg = sum(marks) / len(marks)
    max_marks = max(marks)
    export_plot(marks)
    return render_template('course_data.html', avg=avg, max_marks=max_marks)

def export_plot(marks_list):
    lower = (min(marks_list) // 10) * 10
    plt.figure(figsize=(10, 6))
    plt.hist(marks_list, bins=range(lower, 101, 1), edgecolor='black')
    plt.xlim(lower, 100)
    plt.xlabel('Marks')
    plt.ylabel('Frequency')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig('./static/bar-chart.png', dpi=300, bbox_inches='tight')
    plt.close()

@app.route('/compare')
def compare():
    rows1 = read_csv()
    rows2 = []
    with open('data (1).csv', newline='') as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            rows2.append({
                'Student id': row['Student id'].strip(),
                'Course id': row['Course id'].strip(),
                'Marks': int(row['Marks'].strip())
            })
    set1 = { (r['Student id'], r['Course id'], r['Marks']) for r in rows1 }
    set2 = { (r['Student id'], r['Course id'], r['Marks']) for r in rows2 }
    only1 = set1 - set2
    only2 = set2 - set1
    diffs = []
    for sid, cid, m in only1:
        diffs.append({'Student id': sid, 'Course id': cid, 'Marks': m, '_merge': 'left_only'})
    for sid, cid, m in only2:
        diffs.append({'Student id': sid, 'Course id': cid, 'Marks': m, '_merge': 'right_only'})
    if not diffs:
        return render_template('identical.html')
    return render_template('diff.html', differences=diffs)

if __name__ == '__main__':
    app.run(debug=False, port=5000)
