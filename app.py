from flask import Flask, render_template, request, url_for, send_from_directory, redirect
import os

from werkzeug.utils import secure_filename
import logging
import psutil  # Pour suivre l'utilisation du CPU
from score import score_ECG, score_Clinical, score_Metabolites
from functions import process_csv2, process_csv1, process_xlsx1, process_xlsx2, generate_score_plot
from prometheus_flask_exporter import PrometheusMetrics

# Initialize the Flask application

app = Flask(__name__)

 # Le serveur de métriques s'exécutera sur le port 8000
metrics = PrometheusMetrics(app)

# Configuration de l'application
UPLOAD_FOLDER = 'uploads'  # Dossier pour stocker les fichiers téléchargés
PLOT1_FOLDER = 'static/plots1'  # Dossier pour stocker le premier ensemble de graphiques
PLOT2_FOLDER = 'static/plots2'  # Dossier pour stocker le second ensemble de graphiques
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}  # Extensions de fichiers autorisées
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PLOT1_FOLDER'] = PLOT1_FOLDER
app.config['PLOT2_FOLDER'] = PLOT2_FOLDER

# Configure le logging
logging.basicConfig(level=logging.INFO)

# Créer les dossiers d'upload et de plots s'ils n'existent pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PLOT1_FOLDER, exist_ok=True)
os.makedirs(PLOT2_FOLDER, exist_ok=True)


# Fonction pour vérifier si un fichier est autorisé
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS






@app.route('/')
def maestria():
    return render_template('maestria.html')


@app.route('/home')
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


# Route pour la page d'accueil
@app.route('/index')
def index():
    return render_template('E_strain.html')


# Route pour gérer l'upload de fichiers
@app.route('/upload', methods=['POST'])
def upload_file():
    use_default_csv = request.form.get('use_default_csv')  # Vérifie si la case est cochée

    files = request.files.getlist('file') if 'file' in request.files else []
    orientation = request.form.get('orientation')  # Récupère l'orientation

    csv_files = [f for f in files if f and allowed_file(f.filename) and f.filename.lower().endswith('.csv')]
    xlsx_files = [f for f in files if f and allowed_file(f.filename) and f.filename.lower().endswith('.xlsx')]

    # Si la case "Use default CSV" est cochée et qu'aucun fichier n'est uploadé
    if use_default_csv and not csv_files and not xlsx_files:
        default_csv_path = os.path.join('static', 'default.csv')  # Chemin du CSV par défaut

        if not os.path.exists(default_csv_path):
            return 'Default CSV file not found.', 400  # Retourne une erreur si le fichier est introuvable

        # Traitement du fichier CSV par défaut
        if orientation == 'columns':
            plot_paths, d = process_csv1(default_csv_path, app.config['PLOT1_FOLDER'])
        else:
            plot_paths, d = process_csv2(default_csv_path, app.config['PLOT1_FOLDER'])

        if d:
            return redirect(url_for('error'))

        return render_template('plot.html', plot_paths=plot_paths)

    # Si aucun fichier n'a été sélectionné et la case n'est pas cochée
    if not (csv_files or xlsx_files):
        return 'No valid .csv or .xlsx files selected.', 400

    plot_paths = []

    # Traite chaque fichier CSV uploadé
    for file in csv_files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if orientation == 'columns':
            plot_paths, d = process_csv1(filepath, app.config['PLOT1_FOLDER'])
            if d:
                return redirect(url_for('error'))
        else:
            plot_paths, d = process_csv2(filepath, app.config['PLOT1_FOLDER'])
            if d:
                return redirect(url_for('error'))

    # Traite chaque fichier XLSX uploadé
    for file in xlsx_files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if orientation == 'columns':
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


    # Récupère les données du formulaire
    m0_laesv_3d = float(request.form['question1'])
    m0_lved_3d = float(request.form['question2'])
    m0_la_tot_emf = float(request.form['question3'])
    m0_la_strain_conduit = float(request.form['question4'])

    GLYC = float(request.form['question5'])
    Urea = float(request.form['question6'])

    Arginine = float(request.form['question7'])
    Met_MetSufoxide = float(request.form['question8'])
    Kynurenine = float(request.form['question9'])

    data = [m0_laesv_3d, m0_lved_3d, m0_la_tot_emf, m0_la_strain_conduit, GLYC, Urea, Arginine, Met_MetSufoxide,
            Kynurenine]

    plot_paths = []
    scores = []

    # Calcul des scores
    if all(val != 0 for val in data[:4]):
        score1 = score_ECG(data[0], data[1], data[2], data[3])
        plot_paths.append(generate_score_plot(score1, 1, "Graph Score ECG", app.config['PLOT2_FOLDER']))
        scores.append(score1)
       # Utilisation du CPU après calcul de score ECG

    if all(val != 0 for val in data[4:6]):
        score2 = score_Clinical(data[4], data[5])
        plot_paths.append(generate_score_plot(score2, 2, "Graph Score Clinical", app.config['PLOT2_FOLDER']))
        scores.append(score2)
     # Utilisation du CPU après calcul de score clinique

    if all(val != 0 for val in data[6:9]):
        score3 = score_Metabolites(data[6], data[7], data[8])
        plot_paths.append(generate_score_plot(score3, 3, "Graph Score Metabolites", app.config['PLOT2_FOLDER']))
        scores.append(score3)
      # Utilisation du CPU après calcul de score métabolites

    if scores:
        total_score = sum(scores)
        plot_paths.append(generate_score_plot(total_score, 4, "Graph Combined Score", app.config['PLOT2_FOLDER']))
          # Utilisation du CPU après calcul du score combiné

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
    app.run(debug=True, host='0.0.0.0', port=5000)










