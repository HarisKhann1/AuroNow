document.addEventListener('DOMContentLoaded', function() {   
  const sidebarToggleBtn = document.querySelector('[data-drawer-toggle="default-sidebar"]');   
  const sidebarCloseBtn = document.querySelector('[data-drawer-hide="default-sidebar"]');   
  const sidebar = document.getElementById('default-sidebar');   
  const sidebarItems = document.querySelectorAll('.sidebar-item');     

  function toggleSidebar() {     
      sidebar.classList.toggle('-translate-x-full');   
  }     

  if (sidebarToggleBtn) {     
      sidebarToggleBtn.addEventListener('click', toggleSidebar);   
  }     

  if (sidebarCloseBtn) {     
      sidebarCloseBtn.addEventListener('click', toggleSidebar);   
  }     

  sidebarItems.forEach(item => {     
      item.addEventListener('click', function(event) {         
          if (window.innerWidth < 640) { // Close sidebar on mobile        
              toggleSidebar();       
          }     
      });   
  });     

  window.addEventListener('resize', function() {     
      if (window.innerWidth >= 640 && sidebar.classList.contains('-translate-x-full')) {       
          sidebar.classList.remove('-translate-x-full');     
      }   
  }); 
});