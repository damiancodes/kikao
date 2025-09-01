// Main JavaScript for Job Scraper Dashboard

$(document).ready(function() {
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Initialize popovers
    $('[data-bs-toggle="popover"]').popover();
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Add loading states to forms
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"]');
        const originalText = submitBtn.html();
        
        submitBtn.prop('disabled', true);
        submitBtn.html('<i class="fas fa-spinner fa-spin me-1"></i>Processing...');
        
        // Re-enable button after 10 seconds as fallback
        setTimeout(function() {
            submitBtn.prop('disabled', false);
            submitBtn.html(originalText);
        }, 10000);
    });
});

// Utility functions
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('main .container-fluid').prepend(alertHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDuration(seconds) {
    if (!seconds) return 'N/A';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

function formatNumber(number) {
    if (!number) return '0';
    
    return new Intl.NumberFormat('en-US').format(number);
}

function formatCurrency(amount, currency = 'USD') {
    if (!amount) return 'N/A';
    
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// API helper functions
function makeApiRequest(url, method = 'GET', data = null) {
    const options = {
        url: url,
        method: method,
        contentType: 'application/json',
        dataType: 'json'
    };
    
    if (data) {
        options.data = JSON.stringify(data);
    }
    
    return $.ajax(options);
}

// Job-related functions
function loadJobStatistics() {
    makeApiRequest('/api/jobs/statistics/')
        .done(function(data) {
            updateStatisticsCards(data);
        })
        .fail(function(xhr, status, error) {
            console.error('Error loading job statistics:', error);
        });
}

function updateStatisticsCards(stats) {
    $('.stat-total-jobs').text(formatNumber(stats.total_jobs));
    $('.stat-active-jobs').text(formatNumber(stats.active_jobs));
    $('.stat-recent-jobs').text(formatNumber(stats.recent_jobs));
    $('.stat-companies-count').text(formatNumber(stats.companies_count));
    $('.stat-sources-count').text(formatNumber(stats.sources_count));
    $('.stat-remote-jobs').text(formatNumber(stats.remote_jobs));
}

// Company-related functions
function loadCompanyStatistics() {
    makeApiRequest('/api/companies/statistics/')
        .done(function(data) {
            updateCompanyStatistics(data);
        })
        .fail(function(xhr, status, error) {
            console.error('Error loading company statistics:', error);
        });
}

function updateCompanyStatistics(stats) {
    $('.stat-total-companies').text(formatNumber(stats.total_companies));
    $('.stat-verified-companies').text(formatNumber(stats.verified_companies));
    $('.stat-companies-with-contact').text(formatNumber(stats.companies_with_contact));
}

// Scraping session functions
function loadScrapingSessions(limit = 10) {
    makeApiRequest(`/api/sessions/?limit=${limit}`)
        .done(function(data) {
            displayScrapingSessions(data.results);
        })
        .fail(function(xhr, status, error) {
            console.error('Error loading scraping sessions:', error);
        });
}

function displayScrapingSessions(sessions) {
    if (sessions.length === 0) {
        $('#scrapingSessions').html('<div class="alert alert-info">No scraping sessions found.</div>');
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-striped">';
    html += '<thead><tr>';
    html += '<th>Query</th><th>Status</th><th>Jobs Found</th><th>Success Rate</th><th>Duration</th><th>Created</th>';
    html += '</tr></thead><tbody>';
    
    sessions.forEach(session => {
        const statusClass = getStatusClass(session.status);
        const successRate = session.success_rate ? `${session.success_rate.toFixed(1)}%` : 'N/A';
        const duration = session.duration ? formatDuration(session.duration) : 'N/A';
        
        html += `<tr>
            <td>
                <strong>${session.query}</strong>
                ${session.location ? `<br><small class="text-muted">${session.location}</small>` : ''}
            </td>
            <td><span class="badge ${statusClass}">${session.status}</span></td>
            <td>${formatNumber(session.jobs_found)}</td>
            <td>${successRate}</td>
            <td>${duration}</td>
            <td>${formatDate(session.created_at)}</td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    $('#scrapingSessions').html(html);
}

function getStatusClass(status) {
    switch(status) {
        case 'completed': return 'bg-success';
        case 'running': return 'bg-primary';
        case 'failed': return 'bg-danger';
        case 'pending': return 'bg-warning';
        case 'cancelled': return 'bg-secondary';
        default: return 'bg-secondary';
    }
}

// Export functions
function exportToCSV(data, filename) {
    if (!data || data.length === 0) {
        showAlert('No data to export', 'warning');
        return;
    }
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function exportToExcel(data, filename) {
    // This would require a library like SheetJS
    // For now, we'll use CSV export
    exportToCSV(data, filename.replace('.xlsx', '.csv'));
}

// Real-time updates
function startRealTimeUpdates() {
    // Update statistics every 30 seconds
    setInterval(function() {
        loadJobStatistics();
        loadCompanyStatistics();
    }, 30000);
    
    // Update scraping sessions every 10 seconds
    setInterval(function() {
        loadScrapingSessions(5);
    }, 10000);
}

// Initialize real-time updates if on dashboard
if (window.location.pathname === '/' || window.location.pathname === '/dashboard/') {
    startRealTimeUpdates();
}

// Error handling
$(document).ajaxError(function(event, xhr, settings, thrownError) {
    console.error('AJAX Error:', {
        url: settings.url,
        status: xhr.status,
        error: thrownError
    });
    
    if (xhr.status === 403) {
        showAlert('Access denied. Please check your permissions.', 'danger');
    } else if (xhr.status === 404) {
        showAlert('Resource not found.', 'warning');
    } else if (xhr.status >= 500) {
        showAlert('Server error. Please try again later.', 'danger');
    } else if (xhr.status === 0) {
        showAlert('Network error. Please check your connection.', 'danger');
    }
});

// Utility for debouncing function calls
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Search with debouncing
const debouncedSearch = debounce(function(query) {
    // Implement search functionality
    console.log('Searching for:', query);
}, 300);

// Initialize search input
$('#searchInput').on('input', function() {
    const query = $(this).val();
    if (query.length > 2) {
        debouncedSearch(query);
    }
});
