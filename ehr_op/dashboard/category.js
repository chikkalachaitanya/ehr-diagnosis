// Category Analysis Page Script

let dashboardData = null;
let currentCategory = null;
let charts = {};

// Initialize
async function initCategoryPage() {
    try {
        // Get category from URL
        const urlParams = new URLSearchParams(window.location.search);
        currentCategory = urlParams.get('cat');

        if (!currentCategory) {
            alert('No category specified.');
            window.location.href = 'index.html';
            return;
        }

        document.getElementById('categoryTitle').textContent = `${currentCategory} Analysis`;
        document.title = `${currentCategory} Analysis | Healthcare Dashboard`;

        // Load data
        const response = await fetch('data.json');
        dashboardData = await response.json();

        if (!dashboardData.category_data || !dashboardData.category_data[currentCategory]) {
            alert('Category data not found.');
            window.location.href = 'index.html';
            return;
        }

        const categoryData = dashboardData.category_data[currentCategory];

        // Render Page
        updateMetrics(categoryData.metrics);
        renderCharts(categoryData);
        updateExecutiveSummary(categoryData);
        updateFacilityTable(categoryData);
        updateTimestamp();

    } catch (error) {
        console.error('Error initializing category page:', error);
    }
}

// Update Metrics
function updateMetrics(metrics) {
    animateValue(document.getElementById('totalCases'), metrics.total_diagnoses);
    animateValue(document.getElementById('activeFacilities'), metrics.unique_facilities);
    animateValue(document.getElementById('uniqueDiagnoses'), metrics.unique_diagnosis_types);
    animateValue(document.getElementById('avgPerFacility'), metrics.avg_per_facility, true);
}

// Animate numeric values
function animateValue(element, end, isFloat = false) {
    const start = 0;
    const duration = 1000;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 4);

        const current = start + (end - start) * ease;

        element.textContent = isFloat
            ? current.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
            : Math.floor(current).toLocaleString();

        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// Render Charts
function renderCharts(data) {
    // Top Diagnoses
    createChart('topDiagnoses', 'bar', data.top_diagnoses.labels, data.top_diagnoses.values, 'Frequency',
        ['rgba(102, 126, 234, 0.8)', 'rgba(118, 75, 162, 0.8)']);

    // Sub-category Breakdown
    createChart('subcategory', 'bar', data.subcategory_breakdown.labels, data.subcategory_breakdown.values, 'Cases',
        ['rgba(250, 112, 154, 0.8)', 'rgba(254, 215, 102, 0.8)']);

    // Top Facilities
    createChart('topFacilities', 'bar', data.top_facilities.labels, data.top_facilities.values, 'Volume',
        ['rgba(240, 147, 251, 0.8)', 'rgba(245, 87, 108, 0.8)'], true);

    // Type Breakdown (Doughnut)
    createDoughnutChart('typeBreakdown', data.type_breakdown);
}

// Generic Chart Creator
function createChart(canvasId, type, labels, values, label, colors, horizontal = false) {
    const ctx = document.getElementById(`${canvasId}Chart`).getContext('2d');

    const gradient = ctx.createLinearGradient(0, 0, horizontal ? 400 : 0, horizontal ? 0 : 400);
    gradient.addColorStop(0, colors[0]);
    gradient.addColorStop(1, colors[1]);

    new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: gradient,
                borderColor: colors[0].replace('0.8', '1'),
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: horizontal ? 'y' : 'x',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(10, 14, 39, 0.95)',
                    padding: 12,
                    cornerRadius: 8
                }
            },
            scales: {
                x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#718096' } },
                y: { grid: { display: false }, ticks: { color: '#718096' } }
            },
            animation: { duration: 1000, easing: 'easeInOutQuart' }
        }
    });
}

// Doughnut Chart Creator
function createDoughnutChart(canvasId, dataObj) {
    const ctx = document.getElementById(`${canvasId}Chart`).getContext('2d');
    const labels = Object.keys(dataObj);
    const values = Object.values(dataObj);
    const colors = [
        'rgba(102, 126, 234, 0.8)', 'rgba(240, 147, 251, 0.8)',
        'rgba(79, 172, 254, 0.8)', 'rgba(250, 112, 154, 0.8)'
    ];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: '#0a0e27',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#a0aec0' } },
                tooltip: { backgroundColor: 'rgba(10, 14, 39, 0.95)' }
            }
        }
    });
}

// Update Facility Table
function updateFacilityTable(data) {
    const tbody = document.getElementById('facilityTableBody');
    if (!data.facility_details) return;

    data.facility_details.forEach(facility => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="facility-name">${facility.facility_name}</td>
            <td><span class="count-badge">${facility.total_count.toLocaleString()}</span></td>
            <td>${facility.unique_diagnoses.toLocaleString()}</td>
        `;
        tbody.appendChild(row);
    });
}

// Executive Summary
function updateExecutiveSummary(data) {
    const summaryText = document.getElementById('executiveSummaryText');
    const total = data.metrics.total_diagnoses.toLocaleString();
    const topDiag = data.top_diagnoses.labels[0];
    const topFac = data.top_facilities.labels[0];

    const text = `
        <strong>${currentCategory}</strong> represents a significant portion of healthcare activity with <strong>${total}</strong> total cases.
        The data highlights <strong>${topDiag}</strong> as the primary diagnosis, requiring focused attention.
        <strong>${topFac}</strong> leads facility performance in this category. 
        The distribution involves <strong>${data.metrics.unique_facilities.toLocaleString()}</strong> distinct facilities, 
        suggesting a widespread prevalence across the network.
    `;

    summaryText.innerHTML = text;
}

// Timestamp
function updateTimestamp() {
    const now = new Date();
    document.getElementById('lastUpdated').textContent = now.toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
}

document.addEventListener('DOMContentLoaded', initCategoryPage);
