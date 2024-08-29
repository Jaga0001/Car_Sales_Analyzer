document.getElementById('upload-form').addEventListener('submit', function (e) {
    e.preventDefault();

    var formData = new FormData();
    var fileField = document.querySelector('input[type="file"]');

    formData.append('file', fileField.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.text())
        .then(data => {
            var resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<h2>Extraction Results:</h2>' + data;
        })
        .catch(error => {
            console.error('Error:', error);
        });
});
