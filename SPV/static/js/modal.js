// modal.js

function closeModal() {
    document.getElementById("messageModal").style.display = "none";
}

function openModal() {
    document.getElementById("messageModal").style.display = "block";
    setTimeout(closeModal, 10000); // Automatically close after 10 seconds
}

// Open the modal if there are messages
window.onload = function() {
    if (document.getElementById("messageModal")) {
        openModal();
    }
};
