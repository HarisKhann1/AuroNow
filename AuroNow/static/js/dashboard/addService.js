// Restore the scroll position when the page loads
document.addEventListener('DOMContentLoaded', function() {
    const savedScrollPosition = sessionStorage.getItem('scrollPosition');
    if (savedScrollPosition) {
        window.scrollTo(0, parseInt(savedScrollPosition));
        sessionStorage.removeItem('scrollPosition');
    }


// Function to validate empty
function validateEmptyInput(e, categoryInput, AddCategoryAlert, text) {

     // Check if input is empty
     if (categoryInput.value.trim() === '') {
        e.preventDefault(); // Prevent form submission
        // Add styles for invalid input
        categoryInput.classList.add('border', 'border-red-500', 'rounded-lg');
        AddCategoryAlert.classList.remove('hidden');  // Show error message
        AddCategoryAlert.classList.add('text-red-500'); // Add error styles
        AddCategoryAlert.innerHTML = `${text}`; // Set error message
    }
}

// add category form validation
const addCategoryForm = document.getElementById('add-category-form');
addCategoryForm.addEventListener('submit', (e) => {
    const categoryInput = document.getElementById('category');
    const AddCategoryAlert = document.getElementById('add-category-alert');
    validateEmptyInput(e, categoryInput, AddCategoryAlert, 'category is required.'); // Call the function to validate input
    localStorage.setItem('categoryAddedStatus', 'true'); // Set the item in localStorage
});

// show alert message if category added successfully
const categoryStatus = localStorage.getItem('categoryAddedStatus');
if (categoryStatus === 'true') {
    const AddCategoryAlert = document.getElementById('add-category-alert');
    AddCategoryAlert.classList.remove('hidden'); // Show the alert
    AddCategoryAlert.classList.add('text-green-600'); // Add success styles
    AddCategoryAlert.innerHTML = 'Data added Successfully'; // Set success message
    
    setTimeout(() => {
        AddCategoryAlert.classList.add('hidden'); // Hide the alert after 3 seconds
        localStorage.removeItem('categoryAddedStatus'); // Remove the item from localStorage
    }, 5000); // 5 seconds delay
}

// Listen for form submission of serviceForm
const serviceForm = document.getElementById('serviceForm');
serviceForm.addEventListener('submit', (e) => {
    const serviceNameInput = document.getElementById('service-name');
    const servicePriceInput = document.getElementById('service-price');
    const serviceDurationInput = document.getElementById('service-duration');
    const serviceCategoryInput = document.getElementById('service-category');
    const serviceDescriptionInput = document.getElementById('service-description');

    const serviceNameAlert = document.getElementById('serviceNameAlert');
    const servicePriceAlert = document.getElementById('servicePriceAlert');
    const serviceDurationAlert = document.getElementById('serviceDurationAlert');
    const serviceCategoryAlert = document.getElementById('serviceCategoryAlert');
    const serviceDescriptionAlert = document.getElementById('serviceDescriptionAlert');

    // Validate empty inputs
    validateEmptyInput(e, serviceNameInput, serviceNameAlert, 'Service name is required.');
    validateEmptyInput(e, servicePriceInput, servicePriceAlert, 'Service price is required.');
    validateEmptyInput(e, serviceDurationInput, serviceDurationAlert, 'Service duration is required.');
    validateEmptyInput(e, serviceCategoryInput, serviceCategoryAlert, 'Service category is required.');
    validateEmptyInput(e, serviceDescriptionInput, serviceDescriptionAlert, 'Service description is required.');
    localStorage.setItem('serviceAddedStatus', 'true'); // Set the item in localStorage
});

// show alert message if category added successfully
const serviceStatus = localStorage.getItem('serviceAddedStatus');
if (serviceStatus === 'true') {
    const addServiceAlert = document.getElementById('serviceSuccessAlert');
    addServiceAlert.classList.remove('hidden'); // Show the alert
    addServiceAlert.classList.add('text-green-600'); // Add success styles
    addServiceAlert.innerHTML = 'Data added Successfully'; // Set success message
    
    setTimeout(() => {
        addServiceAlert.classList.add('hidden'); // Hide the alert after 3 seconds
        localStorage.removeItem('serviceAddedStatus'); // Remove the item from localStorage
    }, 5000); // 5 seconds delay
}

});
