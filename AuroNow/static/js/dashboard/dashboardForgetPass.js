const messages = document.querySelectorAll('.toast-message');

messages.forEach(function(message) {
    const timeout = message.getAttribute('data-timeout');
    
    // Set a timeout to remove the message after the specified time
    setTimeout(function() {
        message.style.transition = 'opacity 0.5s ease-out';
        message.style.opacity = '0';  // Fade out
        setTimeout(function() {
            message.remove();  // Remove after fade out
        }, 500);  // Wait for the fade-out to complete
    }, timeout);
});