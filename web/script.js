// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeBtn = document.getElementById('removeBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingCard = document.getElementById('loadingCard');
const errorCard = document.getElementById('errorCard');
const errorMessage = document.getElementById('errorMessage');
const resultsContainer = document.getElementById('resultsContainer');

let selectedFile = null;
let loadingStepIndex = 0;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAPIHealth();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    uploadZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    removeBtn.addEventListener('click', removeFile);
    analyzeBtn.addEventListener('click', analyzeResume);
    
    // Drag and drop
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);
}

// File Selection
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
        setFile(file);
    } else {
        showError('Please select a PDF file');
    }
}

function setFile(file) {
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'flex';
    analyzeBtn.disabled = false;
    hideError();
}

function removeFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    analyzeBtn.disabled = true;
}

// Drag and Drop
function handleDragOver(e) {
    e.preventDefault();
    uploadZone.classList.add('dragover');
}

function handleDragLeave() {
    uploadZone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
        setFile(file);
    } else {
        showError('Please drop a PDF file');
    }
}

// Analyze Resume
async function analyzeResume() {
    if (!selectedFile) return;
    
    hideError();
    resultsContainer.style.display = 'none';
    loadingCard.style.display = 'block';
    
    // Animate loading steps
    animateLoadingSteps();
    
    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await fetch(`${API_BASE_URL}/api/analyze-resume`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
        
        loadingCard.style.display = 'none';
        resultsContainer.style.display = 'block';
        
        // Smooth scroll to results
        setTimeout(() => {
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
        
    } catch (error) {
        loadingCard.style.display = 'none';
        showError(`Analysis failed: ${error.message}. Make sure the API server is running.`);
    }
}

// Display Results
function displayResults(data) {
    resultsContainer.innerHTML = `
        ${createInfoCard(data)}
        ${createSkillsCard(data)}
        ${createCareerCard(data)}
        ${createSalaryCard(data)}
        ${createSkillGapCard(data)}
        ${createSuggestedJobsCard(data)}
        ${createRecommendationsCard(data)}
    `;
}

// Create Info Card
function createInfoCard(data) {
    return `
        <div class="result-card">
            <div class="card-title">
                <span class="card-icon">👤</span>
                <h2>Professional Profile</h2>
            </div>
            <div class="info-grid">
                <div class="info-box">
                    <div class="info-icon">⏳</div>
                    <div class="info-label">Experience</div>
                    <div class="info-value">${data.experience_years || '0'}Y</div>
                </div>
                <div class="info-box">
                    <div class="info-icon">🎓</div>
                    <div class="info-label">Education</div>
                    <div class="info-value" style="font-size: 1.2em; padding-top: 10px;">${data.education || 'N/A'}</div>
                </div>
                <div class="info-box">
                    <div class="info-icon">💎</div>
                    <div class="info-label">Skill Count</div>
                    <div class="info-value">${data.skills.length}</div>
                </div>
            </div>
        </div>
    `;
}

// Create Skills Card
function createSkillsCard(data) {
    const skillsHTML = data.skills.map(skill => 
        `<div class="skill-badge">${skill}</div>`
    ).join('');
    
    return `
        <div class="result-card">
            <div class="card-title">
                <span class="card-icon">🛠️</span>
                <h2>Your Skills</h2>
            </div>
            <div class="skills-container">
                ${skillsHTML}
            </div>
        </div>
    `;
}

// Create Career Card
function createCareerCard(data) {
    if (!data.career_predictions || data.career_predictions.length === 0) {
        return '';
    }
    
    const careersHTML = data.career_predictions.map((pred, index) => {
        const percentage = (pred.probability * 100).toFixed(1);
        
        return `
            <div class="career-item">
                <div class="career-header">
                    <div class="career-rank">#${index + 1}</div>
                    <div class="career-name">${pred.role}</div>
                    <div class="career-percentage">${percentage}%</div>
                </div>
                <div class="career-description">${getCareerDescription(pred.probability)}</div>
            </div>
        `;
    }).join('');
    
    return `
        <div class="result-card">
            <div class="card-title">
                <span class="card-icon">🚀</span>
                <h2>Career Predictions</h2>
            </div>
            <p class="card-subtitle">AI-powered career path recommendations based on your profile</p>
            <div class="careers-container">
                ${careersHTML}
            </div>
        </div>
    `;
}

// Create Salary Card
function createSalaryCard(data) {
    if (!data.salary_prediction) return '';
    
    const salary = data.salary_prediction;
    const salaryLakhs = (salary.predicted_salary / 100000).toFixed(1);
    const minLakhs = (salary.min_salary / 100000).toFixed(1);
    const maxLakhs = (salary.max_salary / 100000).toFixed(1);
    
    return `
        <div class="result-card">
            <div class="card-title">
                <span class="card-icon">💰</span>
                <h2>Market Valuation</h2>
            </div>
            <div class="info-box" style="width: 100%; margin-top: 20px;">
                <div class="info-label">Predicted Annual Salary</div>
                <div class="info-value" style="font-size: 4em; color: var(--primary);">₹${salaryLakhs}L</div>
                <p style="color: var(--text-secondary); margin-top: 15px;">
                    Market Range: <strong>₹${minLakhs}L - ₹${maxLakhs}L</strong>
                </p>
                <div class="badge" style="display: inline-flex; margin-top: 20px; box-shadow: none; background: rgba(255,255,255,0.05);">
                    <span class="badge-icon">🇮🇳</span>
                    <span>India Market Rate</span>
                </div>
            </div>
        </div>
    `;
}

// Create Skill Gap Card
function createSkillGapCard(data) {
    if (!data.skill_gaps || data.skill_gaps.length === 0) return '';
    
    const gapsHTML = data.skill_gaps.map(gap => {
        const priority = gap.priority_score > 0.8 ? 'High' : 
                        gap.priority_score > 0.6 ? 'Medium' : 'Low';
        
        return `
            <div class="recommendation-item">
                <div class="rec-icon">⚡</div>
                <div style="flex: 1;">
                    <div style="font-weight: 700; color: var(--text-primary); font-size: 1.1em;">${gap.skill}</div>
                    <div style="color: var(--text-secondary); font-size: 0.9em;">Priority Priority: ${priority}</div>
                </div>
            </div>
        `;
    }).join('');
    
    return `
        <div class="result-card">
            <div class="card-title">
                <span class="card-icon">📉</span>
                <h2>Growth Opportunities</h2>
            </div>
            <p class="card-subtitle">Master these missing skills to maximize your market value</p>
            <div class="gaps-container" style="margin-top: 20px;">
                ${gapsHTML}
            </div>
        </div>
    `;
}

// Create Suggested Jobs Card
function createSuggestedJobsCard(data) {
    console.log('💼 Suggested Jobs in response:', data.suggested_jobs);
    
    let jobsHTML = '';
    
    if (!data.suggested_jobs || data.suggested_jobs.length === 0) {
        jobsHTML = `
            <div class="recommendation-item" style="display: block; opacity: 0.6; text-align: center; border-left: none;">
                <div style="font-size: 1.1em; color: var(--text-secondary);">No immediate matches from MongoDB for your top predicted role yet.</div>
            </div>
        `;
    } else {
        jobsHTML = data.suggested_jobs.map(job => {
            const minLakhs = (job.salary_min / 100000).toFixed(1);
            const maxLakhs = (job.salary_max / 100000).toFixed(1);
            const salaryText = job.salary_min > 0 ? `₹${minLakhs}L - ₹${maxLakhs}L` : 'Competitive Salary';
            
            return `
                <div class="recommendation-item job-item" style="display: block;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                        <div style="font-weight: 700; color: var(--primary); font-size: 1.2em;">${job.title}</div>
                        <div class="career-percentage" style="font-size: 0.8em;">LIVE MATCH</div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                        <div style="color: var(--text-secondary); font-size: 0.9em;">🏢 ${job.company}</div>
                        <div style="color: var(--text-secondary); font-size: 0.9em;">📍 ${job.location}</div>
                    </div>
                    <div style="color: var(--accent-green); font-weight: 600;">💰 ${salaryText}</div>
                </div>
            `;
        }).join('');
    }
    
    return `
        <div class="result-card" id="suggestedJobsCard">
            <div class="card-title">
                <span class="card-icon">💼</span>
                <h2>Real-Time Job Matches</h2>
            </div>
            <p class="card-subtitle">Live job openings extracted from MongoDB matching your top predicted career path</p>
            <div class="jobs-container" style="margin-top: 20px;">
                ${jobsHTML}
            </div>
        </div>
    `;
}

// Create Recommendations Card
function createRecommendationsCard(data) {
    if (!data.recommendations || data.recommendations.length === 0) return '';
    
    const recsHTML = data.recommendations.map(rec => 
        `<div class="recommendation-item">
            <div class="rec-icon">✨</div>
            <div class="rec-text">${rec}</div>
        </div>`
    ).join('');
    
    return `
        <div class="result-card">
            <div class="card-title">
                <span class="card-icon">💡</span>
                <h2>Strategic Career Advice</h2>
            </div>
            <div class="recommendations-list">
                ${recsHTML}
            </div>
        </div>
    `;
}

// Helper Functions
function getCareerDescription(probability) {
    if (probability > 0.7) return 'Excellent match - Highly recommended career path';
    if (probability > 0.5) return 'Good match - Consider developing relevant skills';
    return 'Potential path - Requires significant skill development';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function animateLoadingSteps() {
    const steps = document.querySelectorAll('.step');
    loadingStepIndex = 0;
    
    const interval = setInterval(() => {
        if (loadingStepIndex < steps.length) {
            steps[loadingStepIndex].classList.add('active');
            loadingStepIndex++;
        } else {
            clearInterval(interval);
        }
    }, 1000);
}

function showError(message) {
    errorMessage.textContent = message;
    errorCard.style.display = 'flex';
    setTimeout(() => hideError(), 5000);
}

function hideError() {
    errorCard.style.display = 'none';
}

// Check API Health
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✓ API server is running');
        }
    } catch (error) {
        console.warn('⚠ API server is not running');
        showError('API server is not running. Please start it with: python3 src/api/main.py');
    }
}
