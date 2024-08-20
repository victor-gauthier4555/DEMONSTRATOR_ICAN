function handleFileSelection() {
    var input = document.getElementById('file');
    var fileNamesDisplay = document.getElementById('file-names');
    var uploadBtn = document.getElementById('upload-btn');

    if (input.files.length > 0) {
        var fileNames = Array.from(input.files).map(file => file.name).join(', ');
        fileNamesDisplay.innerText = 'Selected files : ' + fileNames;
        fileNamesDisplay.style.marginTop = '10px';
        fileNamesDisplay.style.fontSize = '16px';
        uploadBtn.disabled = false;
        uploadBtn.style.backgroundColor = '#1f255b'; // Même couleur que l'état activé
        uploadBtn.style.cursor = 'pointer';
    } else {
        fileNamesDisplay.innerText = '';
        uploadBtn.disabled = true;
        uploadBtn.style.backgroundColor = 'rgba(27,31,59,0.46)'; // Grise le bouton
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
});







