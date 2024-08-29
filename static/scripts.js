document.getElementById('upload-form').addEventListener('submit', function (e) {
    e.preventDefault();

    var formData = new FormData();
    var fileField = document.querySelector('input[type="file"]');

    formData.append('file', fileField.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            var resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<h2>Extraction Results:</h2>' + formatResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

function formatResults(data) {
    let formattedString = '';

    for (let filename in data) {
        formattedString += `<h3>${filename}</h3>`;
        for (let category in data[filename]) {
            formattedString += `<h4>${category}</h4>`;
            for (let key in data[filename][category]) {
                let value = data[filename][category][key];
                formattedString += `<p><strong>${key}:</strong> ${value === null ? 'N/A' : value}</p>`;
            }
        }
    }

    return formattedString;
}
