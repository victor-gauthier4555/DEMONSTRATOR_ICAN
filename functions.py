import logging
import pandas as pd
from flask import redirect, url_for
from score import score_ECG, score_Clinical, score_Metabolites
import matplotlib.pyplot as plt
import numpy as np
import os
import plotly.graph_objects as go



def read_csv_with_encoding(filepath):
    encodings = ['utf-8', 'latin1', 'iso-8859-1']
    delimiters = [',', ';', '\t']

    for encoding in encodings:
        for delimiter in delimiters:
            try:
                df = pd.read_csv(filepath, encoding=encoding, delimiter=delimiter)
                if df.shape[1] > 1:  # Check if the DataFrame has more than one column
                    return df
            except UnicodeDecodeError:
                continue
    logging.warning(f"Impossible to read the file {filepath} with encoding and specified delimiters.")
    return redirect(url_for('error'))





# Function to process CSV file when orientation is 'rows'
def process_csv1(filepath, plot_folder):
    df = read_csv_with_encoding(filepath)
    d = False
    if df is None:
        d = True
        return [], d

    # Define the variables needed for scoring
    keywords = ['M0_LVESV_3D', 'M0_LVED_3D', 'M0_LA_tot_EmF', 'M0_LA_strain_conduit', 'GLYC', 'Urea', 'Arginine',
                'Met_MetSufoxide', 'Kynurenine']

    # Check if the first cell is numeric (indicates incorrect orientation)
    if isinstance(df.iloc[0, 0], (int, float)):
        d = True
        return [], d

    # Add missing keywords to the DataFrame
    missing_vars = {key: [0] * (len(df.columns) - 1) for key in keywords if key not in df.iloc[:, 0].values}
    for key, values in missing_vars.items():
        df.loc[len(df)] = [key] + values

    # Define the index column
    Index = df.columns[0]

    # Filter and sort the DataFrame based on the keywords
    df2 = df[df[Index].isin(keywords)].sort_values(Index).reset_index(drop=True)
    plot_paths = []
    patient_names = df2.columns[1:]

    for i, patient_name in enumerate(patient_names, start=1):
        data = df2.iloc[:, i]

        if np.isnan(data[0]):  # Skip columns without valid data
            logging.warning(f"Colonne {i} ({patient_name}) vide ou ne contenant pas de données valides.")
            continue

        data = data.fillna(0)  # Fill NaN values with zero
        plot_individual_paths = []
        scores = []

        type_of_score = [0, 0, 0]



        # Calculate scores based on data
        if all(val != 0 for val in data[:4]):
            score1 = score_ECG(data[0], data[1], data[2], data[3])
            scores.append(score1)
            type_of_score[0] = 1

        if all(val != 0 for val in data[4:6]):
            score2 = score_Clinical(data[4], data[5])
            scores.append(score2)
            type_of_score[1] = 1

        if all(val != 0 for val in data[6:9]):
            score3 = score_Metabolites(data[6], data[7], data[8])
            scores.append(score3)
            type_of_score[2] = 1

        if scores:
            total_score = sum(scores)
            plot_individual_paths.append(generate_score_plot(total_score, f"{patient_name}_4", "Graph Combined Score", plot_folder, type_of_score))

        plot_paths.append({
            'patient_name': i,
            'plots': plot_individual_paths
        })

    if (len(plot_individual_paths)==0):
        d= True
        return [], d

    return plot_paths, d

# Function to process CSV file when orientation is 'columns'
def process_csv2(filepath, plot_folder):
    df = read_csv_with_encoding(filepath)
    d = False
    if df is None:
        d = True
        return [], d

    # Define the variables needed for scoring
    keywords = ['M0_LVESV_3D', 'M0_LVED_3D', 'M0_LA_tot_EmF', 'M0_LA_strain_conduit', 'GLYC', 'Urea', 'Arginine',
                'Met_MetSufoxide', 'Kynurenine']

    # Check if the first cell is not numeric (indicates incorrect orientation)
    """if not isinstance(df.iloc[0, 0], (int, float)):
        print(isinstance(df.iloc[0, 0], (int, float)))
        d = True
        return [], d"""

    # Add missing keywords as columns to the DataFrame
    for key in keywords:
        if key not in df.columns:
            df[key] = [0] * len(df)

    df = df[keywords]  # Filter the DataFrame to include only the keywords
    patient_names = range(len(df))  # Create a list of patient indices
    plot_paths = []

    for i, patient_name in enumerate(patient_names, start=1):
        data = df.iloc[i - 1]

        """if np.isnan(data):  # Skip rows without valid data
            logging.warning(f"Colonne {i} ({patient_name}) vide ou ne contenant pas de données valides.")
            continue"""

        data = data.fillna(0)  # Fill NaN values with zero
        plot_individual_paths = []
        scores = []

        type_of_score=[0,0,0]



        # Calculate scores based on data
        if all(val != 0 for val in data[:4]):
            score1 = score_ECG(data[0], data[1], data[2], data[3])
            scores.append(score1)
            type_of_score[0] = 1


        if all(val != 0 for val in data[4:6]):
            score2 = score_Clinical(data[4], data[5])
            scores.append(score2)
            type_of_score[1] = 1

        if all(val != 0 for val in data[6:9]):
            score3 = score_Metabolites(data[6], data[7], data[8])
            scores.append(score3)
            type_of_score[2] = 1


        score_type=type_of_score[0]*4+type_of_score[1]*2+type_of_score[2]

        if scores:
            total_score = sum(scores)
            plot_individual_paths.append(generate_score_plot(total_score, f"{patient_name}_4", "Graph Combined Score", plot_folder,score_type))

        plot_paths.append({
            'patient_name': i,
            'plots': plot_individual_paths
        })

    if (len(plot_individual_paths)==0):
        d= True
        return [], d





    return plot_paths, d



def process_xlsx1(filepath, plot_folder):
    df = pd.read_excel(filepath)
    d = False
    if df is None:
        d= True
        return [], d

    # Define the variables needed for scoring
    keywords = ['M0_LVESV_3D', 'M0_LVED_3D', 'M0_LA_tot_EmF', 'M0_LA_strain_conduit', 'GLYC', 'Urea', 'Arginine',
                'Met_MetSufoxide', 'Kynurenine']

    # Check if the first cell is numeric (indicates incorrect orientation)
    if isinstance(df.iloc[0, 0], (int, float)):
        d = True
        return [], d

    # Add missing keywords to the DataFrame
    missing_vars = {key: [0] * (len(df.columns) - 1) for key in keywords if key not in df.iloc[:, 0].values}
    for key, values in missing_vars.items():
        df.loc[len(df)] = [key] + values

    # Define the index column
    Index = df.columns[0]

    # Filter and sort the DataFrame based on the keywords
    df2 = df[df[Index].isin(keywords)].sort_values(Index).reset_index(drop=True)
    plot_paths = []
    patient_names = df2.columns[1:]

    for i, patient_name in enumerate(patient_names, start=1):
        data = df2.iloc[:, i]

        if np.isnan(data[0]):  # Skip columns without valid data
            logging.warning(f"Colonne {i} ({patient_name}) vide ou ne contenant pas de données valides.")
            continue

        data = data.fillna(0)  # Fill NaN values with zero
        plot_individual_paths = []
        scores = []

        type_of_score = [0, 0, 0]


        # Calculate scores based on data
        if all(val != 0 for val in data[:4]):
            score1 = score_ECG(data[0], data[1], data[2], data[3])
            scores.append(score1)
            type_of_score[0] = 1

        if all(val != 0 for val in data[4:6]):
            score2 = score_Clinical(data[4], data[5])
            scores.append(score2)
            type_of_score[1] = 1

        if all(val != 0 for val in data[6:9]):
            score3 = score_Metabolites(data[6], data[7], data[8])
            scores.append(score3)
            type_of_score[2] = 1

        if scores:
            total_score = sum(scores)
            plot_individual_paths.append(generate_score_plot(total_score, f"{patient_name}_4", "Graph Combined Score", plot_folder,type_of_score))

        plot_paths.append({
            'patient_name': i,
            'plots': plot_individual_paths
        })

    if (len(plot_individual_paths)==0):
        d= True
        return [], d

    return plot_paths, d



def process_xlsx2(filepath, plot_folder):
    df = pd.read_excel(filepath)
    d = False
    if df is None:
        d = True
        return [], d

    # Define the variables needed for scoring
    keywords = ['M0_LVESV_3D', 'M0_LVED_3D', 'M0_LA_tot_EmF', 'M0_LA_strain_conduit', 'GLYC', 'Urea', 'Arginine',
                'Met_MetSufoxide', 'Kynurenine']

    # Check if the first cell is not numeric (indicates incorrect orientation)
    if not isinstance(df.iloc[0, 0], (int, float)):
        d = True
        return [], d

    # Add missing keywords as columns to the DataFrame
    for key in keywords:
        if key not in df.columns:
            df[key] = [0] * len(df)

    df = df[keywords]  # Filter the DataFrame to include only the keywords
    patient_names = range(len(df))  # Create a list of patient indices
    plot_paths = []

    for i, patient_name in enumerate(patient_names, start=1):
        data = df.iloc[i - 1]

        if np.isnan(data[0]):  # Skip rows without valid data
            logging.warning(f"Colonne {i} ({patient_name}) vide ou ne contenant pas de données valides.")
            continue

        data = data.fillna(0)  # Fill NaN values with zero
        plot_individual_paths = []
        scores = []

        type_of_score = [0, 0, 0]

        # Calculate scores based on data
        if all(val != 0 for val in data[:4]):
            score1 = score_ECG(data[0], data[1], data[2], data[3])
            scores.append(score1)
            type_of_score[0] = 1

        if all(val != 0 for val in data[4:6]):
            score2 = score_Clinical(data[4], data[5])
            scores.append(score2)
            type_of_score[1] = 1

        if all(val != 0 for val in data[6:9]):
            score3 = score_Metabolites(data[6], data[7], data[8])
            scores.append(score3)
            type_of_score[2] = 1

        if scores:
            total_score = sum(scores)
            plot_individual_paths.append(generate_score_plot(total_score, f"{patient_name}_4", "Graph Combined Score", plot_folder))

        plot_paths.append({
            'patient_name': i,
            'plots': plot_individual_paths
        })

    if (len(plot_individual_paths)==0):
        d= True
        return [], d

    return plot_paths, d



def generate_score_plot(score, index, name, plot_folder, score_type):
    print(score)
    print(index)
    print(plot_folder)
    print(score_type)
    """
    Génère un graphique de score avec des éléments améliorés en utilisant Plotly.
    Enregistre le graphique au format PNG.
    """
    texte_score=""
    if(score_type==1):
        texte_score="Score obtained with Metabolites data"
    if (score_type == 2):
        texte_score = "Score obtained with Clinical data"
    if (score_type == 3):
        texte_score = "Score obtained with Clinical and Metabolites data"
    if (score_type == 4):
        texte_score = "Score obtained with ECG data"
    if (score_type == 5):
        texte_score = "Score obtained with ECG and Metabolites data"
    if (score_type == 6):
        texte_score = "Score obtained with ECG and Clinical"
    if (score_type == 7):
        texte_score = "Score obtained with ECG, Clinical and Metabolites data"

    print(texte_score)


    # Création du graphique
    fig = go.Figure()

    # Ajout d'une ligne horizontale passant par le point carré (réduite en longueur)
    fig.add_shape(type="line", x0=-0.1, x1=0.1, y0=score, y1=score,
                  line=dict(color='#3a8b8b', width=2))  # Réduire la longueur de la ligne

    # Ajout de la zone grisée entre y=-1 et y=1
    fig.add_shape(type="rect",
                  x0=-0.2, x1=0.2, y0=-1, y1=1,
                  fillcolor="grey", opacity=0.3, line_width=0)

    # Ajout des lignes de référence
    fig.add_shape(type="line", x0=-0.2, x1=0.2, y0=-1, y1=-1,
                  line=dict(color="#3a8b8b", dash="dash"))
    fig.add_shape(type="line", x0=-0.2, x1=0.2, y0=1, y1=1,
                  line=dict(color="#3a8b8b", dash="dash"))



    # Tracé du score avec un marqueur carré
    fig.add_trace(go.Scatter(x=[0], y=[score],
                             mode='markers',
                             marker=dict(size=15, color='#3a8b8b', symbol='square',  # Change ici 'x' en 'square'
                                         line=dict(width=2, color='black')),  # Personnalisation du contour du carré
                             name=f'Score: {score}'))

    # Annotations pour 'Positive' et 'Negative'
    fig.add_annotation(x=0.05, y=6, text="Positive", showarrow=False, font=dict(color="#3a8b8b", size=12))
    fig.add_annotation(x=0.05, y=-7, text="Negative", showarrow=False, font=dict(color="#3a8b8b", size=12))

    # Ajouter une annotation pour l'index (légende)
    fig.add_annotation(
        x=0.95, y=0.95,  # Position en haut à droite (en coordonnées relatives)
        xref="paper", yref="paper",
        text=f'<b>Score</b>: {score}',  # Texte de l'index (légende)
        showarrow=False,
        bordercolor="#3a8b8b",  # Couleur de la bordure (même que le carré)
        borderwidth=2,  # Largeur de la bordure
        bgcolor="#5b7173",  # Couleur de fond du carré de légende
        font=dict(size=12, color="white"),  # Style du texte
        align="left"  # Alignement du texte
    )

    # Ajouter une annotation pour le texte_score dans le bas du graphique
    fig.add_annotation(
        x=0, y=-9.5,  # Position à l'intérieur du graphique, proche du bas
        xref="x", yref="y",  # Utilisation des axes x et y pour positionner le texte dans la zone de traçage
        text=texte_score,  # Texte du score
        showarrow=False,
        font=dict(size=14, color="#3a8b8b"),  # Style du texte
        align="center"
    )

    # Configuration de l'apparence du graphique, suppression du quadrillage
    fig.update_layout(
                      yaxis=dict(range=[-10, 10], showgrid=False, zeroline=False,
                                 showline=False, showticklabels=False),  # Désactivation des axes y
                      xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, showline=False),
                      # Désactivation du quadrillage x
                      showlegend=False,
                      plot_bgcolor='#e7eee9',  # Fond du graphique
                      paper_bgcolor='#5b7173',
                      margin=dict(l=10, r=10, t=10, b=10))  # Fond général

    # Sauvegarde du graphique au format PNG
    graph_path = os.path.join(plot_folder, f'graph_{index}.png')
    fig.write_image(graph_path, width=700, height=500, scale=3)  # Sauvegarde en PNG

    return f'{os.path.basename(plot_folder)}/graph_{index}.png'




