// Main JavaScript for Site Survey AI interface

document.addEventListener('DOMContentLoaded', function() {
    loadSystemStatus();
    loadDatabaseStats();
    
    // Handle form submission
    document.getElementById('survey-form').addEventListener('submit', handleSurveySubmission);
});

async function loadSystemStatus() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        const statusHtml = `
            <div class="system-info">
                <div class="info-card">
                    <h4>System Status</h4>
                    <div class="value">${data.status}</div>
                </div>
                <div class="info-card">
                    <h4>Mode</h4>
                    <div class="value">${data.mode}</div>
                </div>
                <div class="info-card">
                    <h4>Model</h4>
                    <div class="value">${data.config.model_name}</div>
                </div>
                <div class="info-card">
                    <h4>ML Features</h4>
                    <div class="value">${data.features.ml_dependencies ? '✅ Available' : '❌ Unavailable'}</div>
                </div>
            </div>
        `;
        
        if (data.warnings && data.warnings.length > 0) {
            const warningsHtml = data.warnings.map(warning => 
                `<div class="status-indicator status-warning">⚠️ ${warning}</div>`
            ).join('');
            document.getElementById('system-status').innerHTML = statusHtml + '<div style="margin-top: 1rem;">' + warningsHtml + '</div>';
        } else {
            document.getElementById('system-status').innerHTML = statusHtml;
        }
    } catch (error) {
        document.getElementById('system-status').innerHTML = 
            '<div class="status-indicator status-fail">❌ Unable to connect to server</div>';
    }
}

async function loadDatabaseStats() {
    try {
        const response = await fetch('/stats');
        const data = await response.json();
        
        const statsHtml = `
            <div class="db-info">
                <div class="info-card">
                    <h4>Total Surveys</h4>
                    <div class="value">${data.total_surveys || 0}</div>
                </div>
                <div class="info-card">
                    <h4>Database Size</h4>
                    <div class="value">${data.db_size || 'Unknown'}</div>
                </div>
                <div class="info-card">
                    <h4>Collections</h4>
                    <div class="value">${data.collections || 0}</div>
                </div>
            </div>
        `;
        
        document.getElementById('db-stats').innerHTML = statsHtml;
    } catch (error) {
        document.getElementById('db-stats').innerHTML = 
            '<div class="status-indicator status-warning">⚠️ Database stats unavailable</div>';
    }
}

async function handleSurveySubmission(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const images = formData.getAll('images');
    
    if (images.length === 0 || images[0].size === 0) {
        alert('Please select at least one image to analyze.');
        return;
    }
    
    // Show loading state
    const btnText = document.getElementById('btn-text');
    const loading = document.getElementById('loading');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    btnText.style.display = 'none';
    loading.style.display = 'inline';
    analyzeBtn.disabled = true;
    
    try {
        const response = await fetch('/analyze-survey', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayResults(result);
        } else {
            displayError(result);
        }
    } catch (error) {
        displayError({ error: 'Network error', message: error.message });
    } finally {
        // Reset button state
        btnText.style.display = 'inline';
        loading.style.display = 'none';
        analyzeBtn.disabled = false;
    }
}

function displayResults(result) {
    const resultsSection = document.getElementById('results-section');
    const resultsContent = document.getElementById('results-content');
    
    let statusClass = 'status-warning';
    let statusIcon = '⚠️';
    
    if (result.status === 'pass') {
        statusClass = 'status-pass';
        statusIcon = '✅';
    } else if (result.status === 'fail') {
        statusClass = 'status-fail';
        statusIcon = '❌';
    }
    
    const confidencePercentage = Math.round(result.confidence_score * 100);
    
    let similarSurveysHtml = '';
    if (result.similar_surveys_found) {
        similarSurveysHtml = `
            <div style="margin-top: 1rem;">
                <strong>Similar Surveys Found:</strong>
                <ul style="margin-top: 0.5rem; margin-left: 1rem;">
                    <li>✅ Passing Examples: ${result.similar_surveys_found.passing}</li>
                    <li>❌ Failing Examples: ${result.similar_surveys_found.failing}</li>
                </ul>
            </div>
        `;
    }
    
    const resultsHtml = `
        <div class="result-item">
            <div class="result-header">
                <div class="status-indicator ${statusClass}">
                    ${statusIcon} ${result.status.toUpperCase()}
                </div>
                <div class="confidence-score">
                    Confidence: ${confidencePercentage}%
                </div>
            </div>
            
            <div style="margin-top: 1rem;">
                <strong>Survey ID:</strong> ${result.survey_id}
            </div>
            
            <div style="margin-top: 1rem;">
                <strong>Images Processed:</strong> ${result.num_images_processed}
            </div>
            
            <div style="margin-top: 1rem;">
                <strong>Component Analyses:</strong> ${result.component_analyses_count}
            </div>
            
            ${similarSurveysHtml}
            
            <div style="margin-top: 1rem;">
                <strong>Analysis Report:</strong>
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 5px; margin-top: 0.5rem; white-space: pre-wrap; font-family: monospace; font-size: 0.9rem;">
${result.report}
                </div>
            </div>
        </div>
    `;
    
    resultsContent.innerHTML = resultsHtml;
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Refresh database stats
    setTimeout(loadDatabaseStats, 1000);
}

function displayError(error) {
    const resultsSection = document.getElementById('results-section');
    const resultsContent = document.getElementById('results-content');
    
    let errorMessage = error.message || 'An error occurred during analysis.';
    let suggestion = error.suggestion || '';
    
    const errorHtml = `
        <div class="result-item">
            <div class="result-header">
                <div class="status-indicator status-fail">
                    ❌ ERROR
                </div>
            </div>
            
            <div style="margin-top: 1rem;">
                <strong>Error:</strong> ${error.error}
            </div>
            
            <div style="margin-top: 1rem;">
                <strong>Details:</strong> ${errorMessage}
            </div>
            
            ${suggestion ? `
                <div style="margin-top: 1rem;">
                    <strong>Suggestion:</strong> ${suggestion}
                </div>
            ` : ''}
        </div>
    `;
    
    resultsContent.innerHTML = errorHtml;
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}