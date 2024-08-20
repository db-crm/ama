// dashboard.js
console.log('Dashboard JavaScript loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    
    const searchBar = document.getElementById('search-bar');
    const departmentFilter = document.getElementById('department-filter');
    const divisionFilter = document.getElementById('division-filter');
    const areaFilter = document.getElementById('area-filter');
    
    console.log('Search bar:', searchBar);
    console.log('Department filter:', departmentFilter);
    console.log('Division filter:', divisionFilter);
    console.log('Area filter:', areaFilter);
    
    // Add event listeners
    searchBar.addEventListener('input', function() {
        console.log('Search term:', this.value);
    });
    
    departmentFilter.addEventListener('change', function() {
        console.log('Selected department:', this.value);
    });
    
    divisionFilter.addEventListener('change', function() {
        console.log('Selected division:', this.value);
    });
    
    areaFilter.addEventListener('change', function() {
        console.log('Selected area:', this.value);
    });
});