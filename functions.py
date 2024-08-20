import logging
import pandas as pd
from flask import redirect, url_for
from score import score_ECG, score_Clinical, score_Metabolites
import matplotlib.pyplot as plt
import numpy as np
import os



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



        # Calculate scores based on data
        if all(val != 0 for val in data[:4]):
            score1 = score_ECG(data[0], data[1], data[2], data[3])
            plot_individual_paths.append(generate_score_plot(score1, f"{patient_name}_1", "Graph Score ECG", plot_folder))
            scores.append(score1)

        if all(val != 0 for val in data[4:6]):
            score2 = score_Clinical(data[4], data[5])
            plot_individual_paths.append(generate_score_plot(score2, f"{patient_name}_2", "Graph Score Clinical", plot_folder))
            scores.append(score2)

        if all(val != 0 for val in data[6:9]):
            score3 = score_Metabolites(data[6], data[7], data[8])
            plot_individual_paths.append(generate_score_plot(score3, f"{patient_name}_3", "Graph Score Metabolites", plot_folder))
            scores.append(score3)

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



        # Calculate scores based on data
        if all(val != 0 for val in data[:4]):
            score1 = score_ECG(data[0], data[1], data[2], data[3])
            plot_individual_paths.append(generate_score_plot(score1, f"{patient_name}_1", "Graph Score ECG", plot_folder))
            scores.append(score1)

        if all(val != 0 for val in data[4:6]):
            score2 = score_Clinical(data[4], data[5])
            plot_individual_paths.append(generate_score_plot(score2, f"{patient_name}_2", "Graph Score Clinical", plot_folder))
            scores.append(score2)

        if all(val != 0 for val in data[6:9]):
            score3 = score_Metabolites(data[6], data[7], data[8])
            plot_individual_paths.append(generate_score_plot(score3, f"{patient_name}_3", "Graph Score Metabolites", plot_folder))
            scores.append(score3)

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


        # Calculate scores based on data
        if all(val != 0 for val in data[:4]):
            score1 = score_ECG(data[0], data[1], data[2], data[3])
            plot_individual_paths.append(generate_score_plot(score1, f"{patient_name}_1", "Graph Score ECG", plot_folder))
            scores.append(score1)

        if all(val != 0 for val in data[4:6]):
            score2 = score_Clinical(data[4], data[5])
            plot_individual_paths.append(generate_score_plot(score2, f"{patient_name}_2", "Graph Score Clinical", plot_folder))
            scores.append(score2)

        if all(val != 0 for val in data[6:9]):
            score3 = score_Metabolites(data[6], data[7], data[8])
            plot_individual_paths.append(generate_score_plot(score3, f"{patient_name}_3", "Graph Score Metabolites", plot_folder))
            scores.append(score3)

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

        # Calculate scores based on data
        if all(val != 0 for val in data[:4]):
            score1 = score_ECG(data[0], data[1], data[2], data[3])
            plot_individual_paths.append(generate_score_plot(score1, f"{patient_name}_1", "Graph Score ECG", plot_folder))
            scores.append(score1)

        if all(val != 0 for val in data[4:6]):
            score2 = score_Clinical(data[4], data[5])
            plot_individual_paths.append(generate_score_plot(score2, f"{patient_name}_2", "Graph Score Clinical", plot_folder))
            scores.append(score2)

        if all(val != 0 for val in data[6:9]):
            score3 = score_Metabolites(data[6], data[7], data[8])
            plot_individual_paths.append(generate_score_plot(score3, f"{patient_name}_3", "Graph Score Metabolites", plot_folder))
            scores.append(score3)

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

def generate_score_plot(score, index, name, plot_folder):
    fig, ax = plt.subplots()

    ax.axhline(y=-1, color='r', linestyle='--')  # Red dashed line at y = -1
    ax.axhline(y=1, color='b', linestyle='--')  # Blue dashed line at y = 1

    ax.plot(0, score, 'gx', markersize=10, markeredgewidth=2, label=f'y = {score}')  # Green 'x' marker

    ax.set_ylabel('y')
    ax.legend()

    ax.set_ylim(-10, 10)

    ax.grid(True)

    plt.title(name)

    # Add text annotations to the plot
    ax.text(0.02, 6, 'Sick', fontsize=10, color='blue', ha='center')
    ax.text(0.02, -7, 'Not sick', fontsize=10, color='red', ha='center')
    graph_path = os.path.join(plot_folder, f'graph_{index}.png')
    plt.savefig(graph_path)  # Save the plot
    plt.close()

    return f'{os.path.basename(plot_folder)}/graph_{index}.png'