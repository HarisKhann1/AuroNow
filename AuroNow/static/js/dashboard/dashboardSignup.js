// Initialize Feather icons
document.addEventListener('DOMContentLoaded', function() {
    feather.replace();
    
    // Password toggle functionality for first password field
    const togglePassword1 = document.getElementById('togglePassword1');
    const password1 = document.getElementById('id_password1');
    const showIcon1 = document.getElementById('showPasswordIcon1');
    const hideIcon1 = document.getElementById('hidePasswordIcon1');

    togglePassword1.addEventListener('click', function() {
        if (password1.type === 'password') {
            password1.type = 'text';
            showIcon1.classList.add('hidden');
            hideIcon1.classList.remove('hidden');
        } else {
            password1.type = 'password';
            showIcon1.classList.remove('hidden');
            hideIcon1.classList.add('hidden');
        }
    });
    
    // Password toggle functionality for confirm password field
    const togglePassword2 = document.getElementById('togglePassword2');
    const password2 = document.getElementById('id_password2');
    const showIcon2 = document.getElementById('showPasswordIcon2');
    const hideIcon2 = document.getElementById('hidePasswordIcon2');
    
    togglePassword2.addEventListener('click', function() {
        // Toggle password visibility
        if (password2.type === 'password') {
            password2.type = 'text';
            showIcon2.classList.add('hidden');
            hideIcon2.classList.remove('hidden');
        } else {
            password2.type = 'password';
            showIcon2.classList.remove('hidden');
            hideIcon2.classList.add('hidden');
        }
    });
    
    // Phone validation - only allow digits
    const phone = document.getElementById('id_phone');
    phone.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^\d]/g, '');
        
        // Validate phone - must be exactly 11 digits
        if (this.value.length > 0 && this.value.length !== 11) {
            this.classList.add('border-red-500');
            this.classList.remove('border-gray-300');
        } else {
            this.classList.remove('border-red-500');
            this.classList.add('border-gray-300');
        }
    });
    
    // Location functionality
    const getLocationBtn = document.getElementById('getLocationBtn');
    const latitudeInput = document.getElementById('id_latitude');
    const longitudeInput = document.getElementById('id_longitude');
    const locationStatus = document.getElementById('locationStatus');
    const locationStatusText = document.getElementById('locationStatusText');
    const signupForm = document.getElementById('signupForm');
    
    // Try to get location on page load
    requestLocationPermission();
    
    // Geolocation API implementation
    getLocationBtn.addEventListener('click', function() {
        requestLocationPermission();
    });
    
    function requestLocationPermission() {
        if (navigator.geolocation) {
            locationStatus.classList.remove('hidden');
            locationStatusText.textContent = "Fetching your location...";
            locationStatusText.classList.remove('text-red-500');
            locationStatusText.classList.add('text-gray-600');
            
            navigator.geolocation.getCurrentPosition(
                // Success callback
                function(position) {
                    latitudeInput.value = position.coords.latitude.toFixed(6);
                    longitudeInput.value = position.coords.longitude.toFixed(6);
                    
                    locationStatusText.textContent = "Location fetched successfully!";
                    locationStatusText.classList.remove('text-gray-600');
                    locationStatusText.classList.add('text-green-600');
                    
                    // Hide status after 3 seconds
                    setTimeout(function() {
                        locationStatus.classList.add('hidden');
                    }, 3000);
                },
                // Error callback
                function(error) {
                    let errorMessage = "Unable to retrieve your location.";
                    
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage = "Location access denied. Please enter coordinates manually.";
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage = "Location information unavailable. Please enter coordinates manually.";
                            break;
                        case error.TIMEOUT:
                            errorMessage = "Location request timed out. Please enter coordinates manually.";
                            break;
                    }
                    
                    locationStatusText.textContent = errorMessage;
                    locationStatusText.classList.remove('text-gray-600');
                    locationStatusText.classList.add('text-red-500');
                }
            );
        } else {
            locationStatus.classList.remove('hidden');
            locationStatusText.textContent = "Geolocation is not supported by your browser. Please enter coordinates manually.";
            locationStatusText.classList.remove('text-gray-600');
            locationStatusText.classList.add('text-red-500');
        }
    }
    
    // Form validation for latitude and longitude
    function validateCoordinates() {
        const latitude = latitudeInput.value.trim();
        const longitude = longitudeInput.value.trim();
        
        // Regex for decimal coordinates
        const coordRegex = /^-?\d+(\.\d+)?$/;
        
        if (!latitude || !longitude) {
            alert("Shop location is required. Please provide both latitude and longitude.");
            return false;
        }
        
        if (!coordRegex.test(latitude) || !coordRegex.test(longitude)) {
            alert("Please enter valid coordinates. Latitude and longitude must be decimal numbers.");
            return false;
        }
        
        const latNum = parseFloat(latitude);
        const lngNum = parseFloat(longitude);
        
        // Validate latitude range (-90 to 90)
        if (latNum < -90 || latNum > 90) {
            alert("Latitude must be between -90 and 90 degrees.");
            return false;
        }
        
        // Validate longitude range (-180 to 180)
        if (lngNum < -180 || lngNum > 180) {
            alert("Longitude must be between -180 and 180 degrees.");
            return false;
        }
        
        return true;
    }
    
    // Form submission validation
    signupForm.addEventListener('submit', function(e) {
        if (!validateCoordinates()) {
            e.preventDefault();
        }
    });
    
    // Coordinate input validation
    latitudeInput.addEventListener('input', function() {
        this.value = this.value.replace(/[^\d.-]/g, '');
    });
    
    longitudeInput.addEventListener('input', function() {
        this.value = this.value.replace(/[^\d.-]/g, '');
    });
});