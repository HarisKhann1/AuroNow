document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form');

    form.addEventListener('submit', (e) => {
        e.preventDefault(); // Prevent form from submitting by default

        // Get references to the input elements
        const name = document.getElementById('name');
        const email = document.getElementById('email');
        const city = document.getElementById('city');
        const phone = document.getElementById('phone');
        const password = document.getElementById('password');

        // Flag to track overall form validity
        let flag = true;

        /**
         * Displays an error message under the input and styles it with a red border.
         * @param {HTMLElement} input - The input element to show error for.
         * @param {string} message - The error message to display.
         */
        function showInputError(input, message) {
            // Add red border
            input.classList.remove('border-slate-300');
            input.classList.add('border-red-500');

            // Remove previous error message if present
            const prevError = input.parentNode.querySelector('p.text-red-500.text-sm.mt-1');
            if (prevError) prevError.remove();

            // Create and append new error message
            const p = document.createElement('p');
            p.classList.add('text-red-500', 'text-sm', 'mt-1');
            p.innerText = message;
            input.parentNode.appendChild(p);

            // Mark form as invalid
            flag = false;
        }

        /**
         * Validates whether a required input is filled.
         * If not, displays an error using showInputError.
         * @param {HTMLElement} input - The input element to validate.
         * @param {string} message - The message to show if the field is empty.
         */
        function validateAllInput(input, message) {
            if (input.value.trim() === '') {
                showInputError(input, message);
            } else {
                // Remove error if input is valid
                const prevError = input.parentNode.querySelector('p.text-red-500.text-sm.mt-1');
                if (prevError) prevError.remove();

                input.classList.remove('border-red-500');
                input.classList.add('border-slate-300');
            }
        }

        // Validate required fields
        validateAllInput(name, 'Name is required');
        validateAllInput(email, 'Email is required');
        validateAllInput(city, 'City is required');
        validateAllInput(phone, 'Phone is required');
        validateAllInput(password, 'Password is required');
        
        /**
         * Additional format validations:
         * These run only if the field is not empty to avoid duplicate errors.
         */

        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (email.value.trim() !== '' && !emailRegex.test(email.value)) {
            showInputError(email, 'Invalid email format');
        }

        // Validate phone number format (10 to 15 digits only)
        const phoneRegex = /^\d{11}$/;
        if (phone.value.trim() !== '' && !phoneRegex.test(phone.value)) {
            showInputError(phone, 'Phone number must be 11 digits');
        }

        // Validate password strength
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;
        if (password.value.trim() !== '' && !passwordRegex.test(password.value)) {
            showInputError(password, 'Password must be at least 8 characters, include uppercase, lowercase, number, and special character');
        }

        // If all fields are valid, allow form submission
        if (flag) {
            form.submit();
        }
    });
});
