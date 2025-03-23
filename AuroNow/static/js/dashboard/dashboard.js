// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get all relevant elements
    const sidebarToggleBtn = document.querySelector('[data-drawer-toggle="default-sidebar"]');
    const sidebarCloseBtn = document.querySelector('[data-drawer-hide="default-sidebar"]');
    const sidebar = document.getElementById('default-sidebar');
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    
    // Function to toggle sidebar visibility on mobile
    function toggleSidebar() {
      sidebar.classList.toggle('-translate-x-full');
    }
    
    // Add event listeners for sidebar toggle and close buttons
    if (sidebarToggleBtn) {
      sidebarToggleBtn.addEventListener('click', toggleSidebar);
    }
    
    if (sidebarCloseBtn) {
      sidebarCloseBtn.addEventListener('click', toggleSidebar);
    }
    
    // Function to set active sidebar item based on URL hash or page attribute
    function setActiveSidebarItem() {
      // Get current page from URL hash or default to dashboard
      const currentPage = window.location.hash.substring(1) || 'dashboard';
      
      // Remove active class from all sidebar items
      sidebarItems.forEach(item => {
        item.classList.remove('bg-[#EEEEEE]');
      });
      
      // Find and set active sidebar item
      const activeItem = document.querySelector(`.sidebar-item[data-page="${currentPage}"]`);
      if (activeItem) {
        activeItem.classList.add('bg-[#EEEEEE]');
      }
    }
    
    // Set active sidebar item on page load
    setActiveSidebarItem();
    
    // Add click event listeners to sidebar items
    sidebarItems.forEach(item => {
      item.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Get the page attribute value
        const page = this.getAttribute('data-page');
        
        // Update URL hash
        window.location.hash = page;
        
        // Update active sidebar item
        sidebarItems.forEach(sidebarItem => {
          sidebarItem.classList.remove('bg-[#EEEEEE]');
        });
        this.classList.add('bg-[#EEEEEE]');
        
        // On mobile, close sidebar after selection
        if (window.innerWidth < 640) { // sm breakpoint in Tailwind
          toggleSidebar();
        }
      });
    });
    
    // Listen for hash changes to update active sidebar item
    window.addEventListener('hashchange', setActiveSidebarItem);
    
    // Handle window resize events
    window.addEventListener('resize', function() {
      // If window width is greater than sm breakpoint and sidebar is hidden, show it
      if (window.innerWidth >= 640 && sidebar.classList.contains('-translate-x-full')) {
        sidebar.classList.remove('-translate-x-full');
      }
    });
  });