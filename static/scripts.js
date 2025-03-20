function handleFileSelection() {
    var input = document.getElementById('file');
    var fileNamesDisplay = document.getElementById('file-names');
    var uploadBtn = document.getElementById('upload-btn');
    var checkbox = document.getElementById('use_default_csv'); // Récupère la case à cocher

    if (input.files.length > 0) {
        var fileNames = Array.from(input.files).map(file => file.name).join(', ');
        fileNamesDisplay.innerText = 'Selected files : ' + fileNames;
        fileNamesDisplay.style.marginTop = '10px';
        fileNamesDisplay.style.fontSize = '16px';
        uploadBtn.disabled = false;
        uploadBtn.style.backgroundColor = '#1f255b'; // Active le bouton
        uploadBtn.style.cursor = 'pointer';
    } else {
        fileNamesDisplay.innerText = '';

        // Si aucun fichier n'est sélectionné, on vérifie si la case est cochée
        if (checkbox.checked) {
            uploadBtn.disabled = false;
            uploadBtn.style.backgroundColor = '#1f255b'; // Active le bouton
            uploadBtn.style.cursor = 'pointer';
        } else {
            uploadBtn.disabled = true;
            uploadBtn.style.backgroundColor = 'rgba(27,31,59,0.46)'; // Désactive le bouton
            uploadBtn.style.cursor = 'not-allowed';
        }
    }
}

// Nouvelle fonction pour gérer la case "Use default CSV file"
function toggleSubmitButton() {
    var fileInput = document.getElementById('file');
    var checkbox = document.getElementById('use_default_csv');
    var uploadBtn = document.getElementById('upload-btn');

    // Active le bouton si un fichier est sélectionné ou si la case est cochée
    if (fileInput.files.length > 0 || checkbox.checked) {
        uploadBtn.disabled = false;
        uploadBtn.style.backgroundColor = '#1f255b'; // Active le bouton
        uploadBtn.style.cursor = 'pointer';
    } else {
        uploadBtn.disabled = true;
        uploadBtn.style.backgroundColor = 'rgba(27,31,59,0.46)'; // Désactive le bouton
        uploadBtn.style.cursor = 'not-allowed';
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const menuToggle = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");

    menuToggle.addEventListener("click", function() {
        sidebar.classList.toggle("open");
    });

    // Empêcher la modification des valeurs des champs de type number en scrollant
    const numberInputs = document.querySelectorAll('input[type=number]');
    numberInputs.forEach(input => {
        input.addEventListener('wheel', function(event) {
            event.preventDefault();
        });
    });

    // Empêcher la modification avec les touches fléchées
    numberInputs.forEach(input => {
        input.addEventListener('keydown', function(event) {
            if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
                event.preventDefault();
            }
        });
    });

    // Ajout des gestionnaires d'événements pour activer le bouton Submit
    var fileInput = document.getElementById('file');
    var checkbox = document.getElementById('use_default_csv');

    if (fileInput) fileInput.addEventListener("change", toggleSubmitButton);
    if (checkbox) checkbox.addEventListener("change", toggleSubmitButton);
});








