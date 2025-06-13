document.addEventListener("DOMContentLoaded", function () {
    
    // Function to collect all service data
    function collectAllServiceData() {
        const services = [];

        document.querySelectorAll('.service-container > div').forEach(serviceDiv => {
            const durationOfService = serviceDiv.querySelector('p').textContent.match(/\d+/)[0]; // Extract the service ID from the h3 text
            
            const select = serviceDiv.querySelector('select[name="member"]');
            
                    
            let selectedProfessional = null;
            if (select) {
                const selectedOption = select.options[select.selectedIndex];
                selectedProfessional = selectedOption.value;
            }

            
            services.push({
                selectedProfessional: selectedProfessional,
                duration: durationOfService
            });
        });
        
        const date = dateField.value;
        services.push({date: date})
        return services;
    }

    document.getElementById('continue-button').addEventListener('click', function () {
        const servicesData = collectAllServiceData();
        console.log('Submitting services data:', servicesData);
        const postUrl = "{% url 'select_time_date' %}";

        fetch('select-time-date/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // 'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(servicesData)
        })
            .then(response => response.json())
            .then(data => {
                // console.log('Success:', data);
                // alert(data.message || 'Submitted successfully');
                window.location.href = 'select-slot/'; // or load new HTML dynamically
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });

    // // CSRF token fetch helper
    // function getCookie(name) {
    //     let cookieValue = null;
    //     if (document.cookie && document.cookie !== '') {
    //         const cookies = document.cookie.split(';');
    //         for (let i = 0; i < cookies.length; i++) {
    //             const cookie = cookies[i].trim();
    //             if (cookie.substring(0, name.length + 1) === (name + '=')) {
    //                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
    //                 break;
    //             }
    //         }
    //     }
    //     return cookieValue;
    // }

    // Get today's date
    const today = new Date();
    let dateField = document.getElementById("dateField");
    
    // Format the date to YYYY-MM-DD
    const formatDate = (date) => {
      const year = date.getFullYear();
      const month = (date.getMonth() + 1).toString().padStart(2, "0");
      const day = date.getDate().toString().padStart(2, "0");
      return `${year}-${month}-${day}`;
    };

    // Calculate 6 days from today
    const maxDate = new Date();
    maxDate.setDate(today.getDate() + 6);

    // Set attributes
    dateField.min = formatDate(today);
    dateField.max = formatDate(maxDate);
    dateField.value = formatDate(today); // Default value

    // Warning if out of range
    dateField.addEventListener("change", () => {
      const selectedDate = new Date(dateField.value);
      if (selectedDate < today || selectedDate > maxDate) {
        alert("Please select a date within the allowed range (today + 6 days).");
        dateField.value = formatDate(today); // Reset to today
      }
    });

});
