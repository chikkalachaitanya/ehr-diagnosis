// Dashboard Application
let dashboardData = null;
let charts = {};

// Initialize dashboard
async function initDashboard() {
    try {
        // Load data
        const response = await fetch('data.json');
        dashboardData = await response.json();

        // Render Global Overview
        updateMetrics(dashboardData.metrics);
        renderGlobalCharts(dashboardData);
        updateFacilityTable(dashboardData.facility_details);
        updateTimestamp();

        // Render All Category Sections
        renderAllCategories();

        console.log('Dashboard initialized successfully');
    } catch (error) {
        console.error('Error initializing dashboard:', error);
    }
}

// Render Global Charts
function renderGlobalCharts(data) {
    // Top 15 Diagnoses
    createChart('topDiagnosesChart', 'bar', data.top_diagnoses.labels, data.top_diagnoses.values, 'Number of Cases',
        ['rgba(102, 126, 234, 0.8)', 'rgba(118, 75, 162, 0.8)'], false, false);

    // Top 10 Facilities
    createChart('topFacilitiesChart', 'bar', data.top_facilities.labels, data.top_facilities.values, 'Total Cases',
        ['rgba(240, 147, 251, 0.8)', 'rgba(245, 87, 108, 0.8)'], true, false);

    createDoughnutChart('typeBreakdownChart', data.type_breakdown);

    // Top 10 Categories
    createChart('categoryChart', 'bar', data.category_breakdown.labels, data.category_breakdown.values, 'Cases',
        ['rgba(79, 172, 254, 0.8)', 'rgba(0, 242, 254, 0.8)'], true, false);

    // Top 15 Sub-categories
    createChart('subcategoryChart', 'bar', data.subcategory_breakdown.labels, data.subcategory_breakdown.values, 'Cases',
        ['rgba(250, 112, 154, 0.8)', 'rgba(254, 215, 102, 0.8)'], false, false);
}

// Render All Categories
function renderAllCategories() {
    if (!dashboardData.category_data) return;

    const container = document.getElementById('allCategoriesContainer');
    const categories = Object.keys(dashboardData.category_data).sort();

    container.innerHTML = ''; // Clear container to prevent duplicates / gaps

    categories.forEach((category, index) => {
        const data = dashboardData.category_data[category];
        const sectionId = `cat-section-${index}`;

        const html = `
            <div class="category-section" style="animation-delay: ${index * 0.1}s">
                <div class="category-header-banner">
                    <h2>${category} Analysis</h2>
                    <div class="category-badges">
                        <span class="badge badge-cases">${data.metrics.total_diagnoses.toLocaleString()} Cases</span>
                        <span class="badge badge-facilities">${data.metrics.unique_facilities.toLocaleString()} Facilities</span>
                    </div>
                </div>
                
                <div class="category-content-grid">
                    <!-- Top Diagnoses -->
                    <div class="chart-card">
                        <h3>Top Diagnoses</h3>
                        <div class="chart-container small">
                            <canvas id="${sectionId}-diagnoses"></canvas>
                        </div>
                    </div>
                    
                    <!-- Top Facilities -->
                    <div class="chart-card">
                        <h3>Top Facilities</h3>
                        <div class="chart-container small">
                            <canvas id="${sectionId}-facilities"></canvas>
                        </div>
                    </div>
                </div>
                
                <div class="category-footer">
                    <p>Top Diagnosis: <strong>${data.top_diagnoses.labels[0]}</strong> (${data.top_diagnoses.values[0].toLocaleString()} cases)</p>
                    <a href="category.html?cat=${encodeURIComponent(category)}" class="view-details-link">View Full Report →</a>
                </div>
            </div>
        `;

        const wrapper = document.createElement('div');
        wrapper.innerHTML = html;
        container.appendChild(wrapper);

        // Render Charts for this section
        setTimeout(() => {
            // Mini charts for categories - still show labels as requested
            createChart(`${sectionId}-diagnoses`, 'bar', data.top_diagnoses.labels.slice(0, 5), data.top_diagnoses.values.slice(0, 5), 'Cases',
                ['rgba(102, 126, 234, 0.8)', 'rgba(118, 75, 162, 0.8)'], false, true);

            createChart(`${sectionId}-facilities`, 'bar', data.top_facilities.labels.slice(0, 5), data.top_facilities.values.slice(0, 5), 'Volume',
                ['rgba(240, 147, 251, 0.8)', 'rgba(245, 87, 108, 0.8)'], true, true);
        }, 100);
    });
}

// Update Metrics
function updateMetrics(metrics) {
    document.getElementById('totalDiagnoses').textContent = metrics.total_diagnoses.toLocaleString();
    document.getElementById('uniqueFacilities').textContent = metrics.unique_facilities.toLocaleString();
    document.getElementById('uniqueDiagnoses').textContent = metrics.unique_diagnosis_types.toLocaleString();
    document.getElementById('avgPerFacility').textContent = metrics.avg_per_facility.toLocaleString();
}

// Chart Helpers
function createChart(canvasId, type, labels, values, label, colors, horizontal = false, isMini = false) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Destroy existing chart if it exists
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    const gradient = ctx.createLinearGradient(0, 0, horizontal ? 400 : 0, horizontal ? 0 : 400);
    gradient.addColorStop(0, colors[0]);
    gradient.addColorStop(1, colors[1]);

    const config = {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: gradient,
                borderColor: colors[0].replace('0.8', '1'),
                borderWidth: 1,
                borderRadius: 4,
                barPercentage: 0.7,
                categoryPercentage: 0.8
            }]
        },
        options: {
            indexAxis: horizontal ? 'y' : 'x',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: !isMini, // Hide legend on mini charts to save space
                    position: 'top',
                    labels: { color: '#a0aec0', padding: 20 }
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 14, 39, 0.95)',
                    padding: 12,
                    cornerRadius: 8,
                    titleColor: '#fff',
                    bodyColor: '#cbd5e0',
                    displayColors: false
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        display: true,
                        color: '#718096',
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 0,
                        font: { size: isMini ? 10 : 11 } // Smaller font for mini, but visible
                    }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        display: true,
                        color: '#718096',
                        font: { size: isMini ? 10 : 11 },
                        autoSkip: true
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    };

    // Mini Chart Overrides for Layout (Adjusted)
    if (isMini) {
        // Ensure axis labels are visible even in mini mode (user request)
        if (horizontal) {
            config.options.scales.x.ticks.display = true;
        } else {
            config.options.scales.y.ticks.display = true;
        }
    }

    charts[canvasId] = new Chart(ctx, config);
}

function createDoughnutChart(canvasId, dataObj) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return;

    const labels = Object.keys(dataObj);
    const values = Object.values(dataObj);
    const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c'];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: '#0a0e27',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#a0aec0', boxWidth: 12 } }
            }
        }
    });
}

function updateFacilityTable(facilities) {
    const tbody = document.getElementById('facilityTableBody');
    if (!facilities) return;
    tbody.innerHTML = '';

    // Sort logic to ensure we show top facilities (sanity check)
    // The pre-calculated facilities should already be sorted in backend, but good to be safe if client-side logic existed.
    // However, here we just take the list passed.

    facilities.slice(0, 10).forEach(f => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${f.facility_name}</td><td><span class="count-badge">${f.total_count.toLocaleString()}</span></td><td>${f.unique_diagnoses}</td>`;
        tbody.appendChild(row);
    });
}

function updateTimestamp() {
    const el = document.getElementById('lastUpdated');
    if (el) el.textContent = new Date().toLocaleDateString();
}

document.addEventListener('DOMContentLoaded', initDashboard);
