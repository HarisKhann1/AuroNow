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

function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    const showPasswordIcon = document.getElementById('showPasswordIcon');
    const hidePasswordIcon = document.getElementById('hidePasswordIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        showPasswordIcon.classList.add('hidden');
        hidePasswordIcon.classList.remove('hidden');
    } else {
        passwordInput.type = 'password';
        showPasswordIcon.classList.remove('hidden');
        hidePasswordIcon.classList.add('hidden');
    }
}