/**
 * EcoRoute AI - Dynamic Chart.js Analytics Visualizer
 */

class AnalyticsCharts {
    static async initAdminDashboardCharts() {
        try {
            const resp = await fetch('/api/chart-data/admin');
            const data = await resp.json();

            // 1. Daily Waste Collection Bar Chart
            const dailyCtx = document.getElementById('dailyCollectionChart');
            if (dailyCtx) {
                new Chart(dailyCtx, {
                    type: 'bar',
                    data: {
                        labels: data.daily_labels,
                        datasets: [{
                            label: 'Waste Collected (kg)',
                            data: data.daily_weights,
                            backgroundColor: '#2E7D32',
                            borderColor: '#1B5E20',
                            borderWidth: 1,
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
                            x: { grid: { display: false } }
                        }
                    }
                });
            }

            // 2. Category Distribution Doughnut Chart
            const catCtx = document.getElementById('categoryDistributionChart');
            if (catCtx) {
                new Chart(catCtx, {
                    type: 'doughnut',
                    data: {
                        labels: data.cat_labels,
                        datasets: [{
                            data: data.cat_values,
                            backgroundColor: data.cat_colors,
                            hoverOffset: 8
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'bottom' }
                        },
                        cutout: '70%'
                    }
                });
            }

            // 3. Vehicle Utilization Doughnut Chart
            const vehicleCtx = document.getElementById('vehicleUtilizationChart');
            if (vehicleCtx) {
                new Chart(vehicleCtx, {
                    type: 'pie',
                    data: {
                        labels: data.vehicle_utilization.labels,
                        datasets: [{
                            data: data.vehicle_utilization.values,
                            backgroundColor: ['#81C784', '#0288D1', '#FB8C00', '#D32F2F']
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });
            }

        } catch (err) {
            console.error('Error rendering dashboard charts:', err);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    AnalyticsCharts.initAdminDashboardCharts();
});
