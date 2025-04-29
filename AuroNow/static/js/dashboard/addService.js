document.addEventListener('DOMContentLoaded', function() {
    
    // Function to validate empty
    function validateEmptyInput(e, categoryInput, AddCategoryAlert, text) {
        console.log('Validating empty input...');
        
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

    // const shopTimingForm = document.getElementById('add-shop-timing-form');
    // if (shopTimingForm) {
    //     shopTimingForm.addEventListener('submit', (e) => {
    //         const day = document.getElementById('day');
    //         const openingTime = document.getElementById('opening-timing');
    //         const closingTime = document.getElementById('closing-timing');
            
    //         const dayAlert = document.getElementById('day-alert');
    //         const openingTimeAlert = document.getElementById('opening-timing-alert');
    //         const closingTimeAlert = document.getElementById('closing-timing-alert');

    //         // Validate empty input
    //         if (day && dayAlert) validateEmptyInput(e, day, dayAlert, 'Day is required.');
    //         if (openingTime && openingTimeAlert) validateEmptyInput(e, openingTime, openingTimeAlert, 'Opening time is required.');
    //         if (closingTime && closingTimeAlert) validateEmptyInput(e, closingTime, closingTimeAlert, 'Closing time is required.');
    //     });
    // }else {
    //     console.log('Shop timing form not found.');
    // }

    // add category form validation
    const addCategoryForm = document.getElementById('add-category-form');
    addCategoryForm.addEventListener('submit', (e) => {
        const categoryInput = document.getElementById('category');
        const AddCategoryAlert = document.getElementById('add-category-alert');
        validateEmptyInput(e, categoryInput, AddCategoryAlert, 'category is required.'); // Call the function to validate input
    });

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
    });

    // Hide the add shop timimg message after 3 seconds
    setTimeout(function () {
        const message = document.getElementById('add-shop-timing-message');
        if (message) {
            message.classList.add('hidden');
        }
    }, 5000);

    // Hide the category message after 5 seconds
    setTimeout(function () {
        const message = document.getElementById('add-category-message');
        if (message) {
            message.classList.add('hidden');
        }
    }, 5000);

});
