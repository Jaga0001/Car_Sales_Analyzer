document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('upload-form');
    const resultsDiv = document.getElementById('results');

    form.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent the default form submission

        const formData = new FormData(form);

        fetch('/upload', {
            method: 'POST',
            body: formData,
        })
            .then(response => response.text())
            .then(data => {
                resultsDiv.innerHTML = data; // Update results div with the response data
            })
            .catch(error => {
                console.error('Error:', error);
                resultsDiv.innerHTML = '<p>An error occurred while processing the file. Please try again.</p>';
            });
    });
});
