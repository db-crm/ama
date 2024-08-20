document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard JavaScript loaded');

    const searchBar = document.getElementById('search-bar');
    const departmentFilter = document.getElementById('department-filter');
    const divisionFilter = document.getElementById('division-filter');
    const areaFilter = document.getElementById('area-filter');
    const itemsPerPage = document.getElementById('items-per-page');
    const tableBody = document.getElementById('assessment-table-body');
    const pagination = document.getElementById('pagination');

    const exportPdfBtn = document.getElementById('export-pdf');
    const exportExcelBtn = document.getElementById('export-excel');

    let currentPage = 1;
    let allDivisions = [];
    let allAreas = [];

    // Fetch all divisions and areas on page load
    fetch('/get-all-divisions-areas/')
        .then(response => response.json())
        .then(data => {
            allDivisions = data.divisions;
            allAreas = data.areas;
        })
        .catch(error => console.error('Error:', error));

    function fetchAssessments() {
        const searchTerm = searchBar.value;
        const department = departmentFilter.value;
        const division = divisionFilter.value;
        const area = areaFilter.value;
        const limit = itemsPerPage.value;
    
        const params = new URLSearchParams({
            search: searchTerm,
            department: department,
            division: division,
            area: area,
            items_per_page: limit,
            page: currentPage
        });
    
        fetch(`/get-filtered-assessments/?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                updateTable(data.assessments);
                updatePagination(data.total_pages, data.current_page);
                updateKPIs(data.kpis);
                updateExportUrls(params);
            })
            .catch(error => console.error('Error:', error));
    }

    function updateExportUrls(params) {
        exportPdfBtn.href = `/export_pdf/?${params.toString()}`;
        exportExcelBtn.href = `/export_excel/?${params.toString()}`;
    }

    function updateDivisionOptions() {
        const selectedDepartment = departmentFilter.value;
        divisionFilter.innerHTML = '<option value="">All Divisions</option>';
        
        const filteredDivisions = selectedDepartment 
            ? allDivisions.filter(div => div.division_department_id === parseInt(selectedDepartment))
            : allDivisions;

        filteredDivisions.forEach(division => {
            const option = document.createElement('option');
            option.value = division.id;
            option.textContent = division.division_name;
            divisionFilter.appendChild(option);
        });

        // Reset area filter when department changes
        areaFilter.innerHTML = '<option value="">All Areas</option>';
    }

    function updateAreaOptions() {
        const selectedDivision = divisionFilter.value;
        areaFilter.innerHTML = '<option value="">All Areas</option>';
        
        const filteredAreas = selectedDivision 
            ? allAreas.filter(area => area.area_division_id === parseInt(selectedDivision))
            : allAreas;

        filteredAreas.forEach(area => {
            const option = document.createElement('option');
            option.value = area.id;
            option.textContent = area.area_name;
            areaFilter.appendChild(option);
        });
    }

    function updateTable(assessments) {
        tableBody.innerHTML = '';
        assessments.forEach(assessment => {
            const row = `
                <tr>
                    <td>${assessment.process_name_c}</td>
                    <td>${assessment.process_lead}</td>
                    <td>${assessment.process_department}</td>
                    <td>${assessment.process_division}</td>
                    <td>${assessment.process_area}</td>
                    <td>${assessment.process_assessment_date}</td>
                    <td>${assessment.creation_date}</td>
                    <td><a class="btn btn-success btn-sm" href="/record/${assessment.id}"><i class="fa fa-eye" aria-hidden="true"></i></a></td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });
    }

    function updatePagination(totalPages, currentPage) {
        pagination.innerHTML = '';
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${i === currentPage ? 'active' : ''}`;
            li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            li.addEventListener('click', (e) => {
                e.preventDefault();
                currentPage = i;
                fetchAssessments();
            });
            pagination.appendChild(li);
        }
    }

    function updateKPIs(kpis) {
        document.getElementById('total-assessments').textContent = kpis.total_assessments;
        document.getElementById('assessments-this-month').textContent = kpis.assessments_this_month;
    }

    searchBar.addEventListener('input', () => {
        currentPage = 1;
        fetchAssessments();
    });

    departmentFilter.addEventListener('change', () => {
        currentPage = 1;
        updateDivisionOptions();
        fetchAssessments();
    });

    divisionFilter.addEventListener('change', () => {
        currentPage = 1;
        updateAreaOptions();
        fetchAssessments();
    });

    areaFilter.addEventListener('change', () => {
        currentPage = 1;
        fetchAssessments();
    });

    itemsPerPage.addEventListener('change', () => {
        currentPage = 1;
        fetchAssessments();
    });

    exportPdfBtn.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = this.href;
    });
    
    exportExcelBtn.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = this.href;
    });



    // Initial fetch
    fetchAssessments();
});