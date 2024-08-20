from flask import Flask, render_template, request, url_for, send_from_directory, redirect
import os

from werkzeug.utils import secure_filename
import logging
from score import score_ECG, score_Clinical, score_Metabolites

from functions import process_csv2, process_csv1, process_xlsx1, process_xlsx2, generate_score_plot

# Initialize the Flask application
app = Flask(__name__)

# Configuration of the application
UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded files
PLOT1_FOLDER = 'static/plots1'  # Folder to store the first set of plots
PLOT2_FOLDER = 'static/plots2'  # Folder to store the second set of plots
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}  # Allowed file extensions for upload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PLOT1_FOLDER'] = PLOT1_FOLDER
app.config['PLOT2_FOLDER'] = PLOT2_FOLDER

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create the upload and plot directories if they do not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PLOT1_FOLDER, exist_ok=True)
os.makedirs(PLOT2_FOLDER, exist_ok=True)

# Function to check if a file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/exemple2')
def exemple2():
    return render_template('exemple2.html')

@app.route('/exemple3')
def exemple3():
    return render_template('exemple3.html')

@app.route('/data_formats')
def data_formats():
    return render_template('data_formats.html')

@app.route('/tutorials')
def tutorials():
    return render_template('tutorials.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')



# Route for the homepage
@app.route('/index')
def index():
    return render_template('E_strain.html')

@app.route('/maestria')
def maestria():
    return render_template('maestria.html')

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No files selected'
    files = request.files.getlist('file')  # Get list of uploaded files
    orientation = request.form.get('orientation')  # Get form data for orientation

    # Filter the uploaded files to get only CSV files
    csv_files = [f for f in files if f and allowed_file(f.filename) and f.filename.lower().endswith('.csv')]
    xlsx_files = [f for f in files if f and allowed_file(f.filename) and f.filename.lower().endswith('.xlsx')]

    if not (csv_files or xlsx_files):
        return 'No valid .csv or .xlsx files selected.'

    plot_paths = []

    # Process each CSV file
    for file in csv_files:
        filename = secure_filename(file.filename)  # Secure the filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)  # Save the file to the upload folder

        # Process the CSV file based on the selected orientation
        if orientation == 'rows':
            plot_paths, d = process_csv1(filepath, app.config['PLOT1_FOLDER'])
            if d:
                return redirect(url_for('error'))
        else:
            plot_paths, d = process_csv2(filepath, app.config['PLOT1_FOLDER'])
            if d:
                return redirect(url_for('error'))

    # Process each XLSX file
    for file in xlsx_files:
        filename = secure_filename(file.filename)  # Secure the filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)  # Save the file to the upload folder

        # Process the XLSX file based on the selected orientation
        if orientation == 'rows':
            plot_paths, d = process_xlsx1(filepath, app.config['PLOT1_FOLDER'])
            if d:
                return redirect(url_for('error'))
        else:
            plot_paths, d = process_xlsx2(filepath, app.config['PLOT1_FOLDER'])
            if d:
                return redirect(url_for('error'))

    return render_template('plot.html', plot_paths=plot_paths)

@app.route('/submit-answers', methods=['POST'])
def submit_answers():
    # Get form data
    m0_laesv_3d = float(request.form['question1'])
    m0_lved_3d = float(request.form['question2'])
    m0_la_tot_emf = float(request.form['question3'])
    m0_la_strain_conduit = float(request.form['question4'])

    GLYC = float(request.form['question5'])
    Urea = float(request.form['question6'])

    Arginine = float(request.form['question7'])
    Met_MetSufoxide = float(request.form['question8'])
    Kynurenine = float(request.form['question9'])

    data = [m0_laesv_3d, m0_lved_3d, m0_la_tot_emf, m0_la_strain_conduit, GLYC, Urea, Arginine, Met_MetSufoxide, Kynurenine]

    plot_paths = []
    scores = []

    # Calculate scores based on form data
    if all(val != 0 for val in data[:4]):
        score1 = score_ECG(data[0], data[1], data[2], data[3])
        plot_paths.append(generate_score_plot(score1, 1, "Graph Score ECG", app.config['PLOT2_FOLDER']))
        scores.append(score1)

    if all(val != 0 for val in data[4:6]):
        score2 = score_Clinical(data[4], data[5])
        plot_paths.append(generate_score_plot(score2, 2, "Graph Score Clinical", app.config['PLOT2_FOLDER']))
        scores.append(score2)

    if all(val != 0 for val in data[6:9]):
        score3 = score_Metabolites(data[6], data[7], data[8])
        plot_paths.append(generate_score_plot(score3, 3, "Graph Score Metabolites", app.config['PLOT2_FOLDER']))
        scores.append(score3)

    if scores:
        total_score = sum(scores)
        plot_paths.append(generate_score_plot(total_score, 4, "Graph Combined Score", app.config['PLOT2_FOLDER']))

    return redirect(url_for('display_graph', plot_paths=plot_paths))

@app.route('/display-graph')
def display_graph():
    plot_paths = request.args.getlist('plot_paths')
    return render_template('display_graph.html', plot_paths=plot_paths)

@app.route('/error')
def error():
    return render_template('ERROR.html')

@app.route('/static/<path:filename>')
def download_file(filename):
    return send_from_directory('static', filename, as_attachment=True)

@app.route('/uploads/<path:filename>')
def download_file2(filename):
    return send_from_directory('uploads', filename, as_attachment=True, mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True)









