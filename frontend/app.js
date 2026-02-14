// API Base URL
const API_URL = 'http://localhost:8000/api';

// Global state
let uploadedFile = null;
let fileData = null;
let selectedVoucherType = null;
let columnMappings = {};
let selectedCompany = 'Vrhealthy';  // Default company

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const rowCount = document.getElementById('rowCount');
const voucherSection = document.getElementById('voucherSection');
const mappingSection = document.getElementById('mappingSection');
const previewSection = document.getElementById('previewSection');
const actionButtons = document.getElementById('actionButtons');
const resultsSection = document.getElementById('resultsSection');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');
const healthStatus = document.getElementById('healthStatus');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadCompanies();
    checkHealth();
});

// Setup Event Listeners
function setupEventListeners() {
    // Upload zone
    uploadZone.addEventListener('click', () => fileInput.click());
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);

    // Voucher type buttons
    document.querySelectorAll('.voucher-btn').forEach(btn => {
        btn.addEventListener('click', () => selectVoucherType(btn.dataset.type));
    });

    // Company selector
    document.getElementById('companySelect').addEventListener('change', handleCompanyChange);

    // Action buttons
    document.getElementById('processBtn').addEventListener('click', processFile);
    document.getElementById('resetBtn').addEventListener('click', reset);
}

// Load Companies
async function loadCompanies() {
    try {
        const response = await fetch(`${API_URL}/companies`);
        const data = await response.json();

        const companySelect = document.getElementById('companySelect');
        companySelect.innerHTML = '';

        if (data.companies && data.companies.length > 0) {
            data.companies.forEach(company => {
                const option = document.createElement('option');
                option.value = company;
                option.textContent = company;
                if (company === selectedCompany) {
                    option.selected = true;
                }
                companySelect.appendChild(option);
            });
        } else {
            const option = document.createElement('option');
            option.value = 'Vrhealthy';
            option.textContent = 'Vrhealthy (default)';
            companySelect.appendChild(option);
        }
    } catch (error) {
        console.error('Error loading companies:', error);
        // Set default company
        const companySelect = document.getElementById('companySelect');
        companySelect.innerHTML = '<option value="Vrhealthy">Vrhealthy (default)</option>';
    }
}

// Handle Company Change
function handleCompanyChange(e) {
    selectedCompany = e.target.value;
    checkHealth();  // Refresh health status with new company
}

// Health Check
async function checkHealth() {
    try {
        const url = selectedCompany ? `${API_URL}/health?company=${encodeURIComponent(selectedCompany)}` : `${API_URL}/health`;
        const response = await fetch(url);
        const data = await response.json();

        const indicator = healthStatus.querySelector('.status-indicator');
        const statusText = healthStatus.querySelector('.status-text');

        if (data.tally_connected) {
            indicator.classList.add('connected');
            indicator.classList.remove('disconnected');
            statusText.textContent = `Connected to Tally (${data.tally_company})`;
        } else {
            indicator.classList.remove('connected');
            indicator.classList.add('disconnected');
            statusText.textContent = 'Tally not connected';
        }
    } catch (error) {
        const indicator = healthStatus.querySelector('.status-indicator');
        const statusText = healthStatus.querySelector('.status-text');
        indicator.classList.remove('connected');
        indicator.classList.add('disconnected');
        statusText.textContent = 'Backend not reachable';
    }
}

// Drag and Drop Handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Handle File Upload
async function handleFile(file) {
    uploadedFile = file;

    showLoading('Uploading and analyzing file...');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        fileData = await response.json();

        // Update UI
        fileName.textContent = fileData.filename;
        rowCount.textContent = fileData.row_count;
        fileInfo.classList.remove('hidden');

        // Show voucher type selection
        voucherSection.classList.remove('hidden');

        hideLoading();

    } catch (error) {
        hideLoading();
        alert(`Error: ${error.message}`);
    }
}

// Select Voucher Type
function selectVoucherType(type) {
    selectedVoucherType = type;

    // Update button states
    document.querySelectorAll('.voucher-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    event.target.closest('.voucher-btn').classList.add('selected');

    // Show mapping section
    renderMappings();
    mappingSection.classList.remove('hidden');

    // Show preview
    renderPreview();
    previewSection.classList.remove('hidden');

    // Show action buttons
    actionButtons.classList.remove('hidden');
}

// Render Column Mappings
function renderMappings() {
    const container = document.getElementById('mappingContainer');
    container.innerHTML = '';

    // Create mapping for each suggested mapping
    fileData.suggested_mappings.forEach(mapping => {
        const row = createMappingRow(mapping);
        container.appendChild(row);
    });

    // Add unmapped columns
    const mappedColumns = fileData.suggested_mappings.map(m => m.excel_column);
    const unmappedColumns = fileData.columns.filter(col => !mappedColumns.includes(col));

    unmappedColumns.forEach(col => {
        const row = createMappingRow({
            excel_column: col,
            tally_field: 'none',
            confidence: 0
        });
        container.appendChild(row);
    });
}

function createMappingRow(mapping) {
    const row = document.createElement('div');
    row.className = 'mapping-row';

    // Excel column
    const excelCol = document.createElement('div');
    excelCol.innerHTML = `<strong>${mapping.excel_column}</strong>`;

    // Arrow
    const arrow = document.createElement('div');
    arrow.className = 'mapping-arrow';
    arrow.textContent = '→';

    // Tally field selector
    const tallyField = document.createElement('div');
    const select = document.createElement('select');
    select.dataset.excelColumn = mapping.excel_column;
    select.addEventListener('change', updateMapping);

    // Add options
    const tallyFields = [
        { value: 'none', label: '-- Not Mapped --' },
        { value: 'date', label: 'Date' },
        { value: 'party_name', label: 'Party Name' },
        { value: 'amount', label: 'Amount' },
        { value: 'invoice_no', label: 'Invoice Number' },
        { value: 'narration', label: 'Narration' },
        { value: 'sales_ledger', label: 'Sales Ledger' },
        { value: 'purchase_ledger', label: 'Purchase Ledger' },
        { value: 'item_name', label: 'Item Name' },
        { value: 'quantity', label: 'Quantity' },
        { value: 'rate', label: 'Rate' },
        { value: 'contra_ledger', label: 'Contra Ledger (Cash/Bank)' },
        { value: 'taxable_value', label: 'Taxable Amount' },
        { value: 'cgst', label: 'CGST' },
        { value: 'sgst', label: 'SGST' },
        { value: 'igst', label: 'IGST' },
        { value: 'gst_number', label: 'GST Number (GSTIN)' },
    ];

    tallyFields.forEach(field => {
        const option = document.createElement('option');
        option.value = field.value;
        option.textContent = field.label;
        if (field.value === mapping.tally_field) {
            option.selected = true;
        }
        select.appendChild(option);
    });

    // Add confidence badge
    if (mapping.confidence > 0) {
        const badge = document.createElement('span');
        badge.className = `confidence-badge ${getConfidenceClass(mapping.confidence)}`;
        badge.textContent = `${Math.round(mapping.confidence * 100)}%`;
        tallyField.appendChild(select);
        tallyField.appendChild(badge);
    } else {
        tallyField.appendChild(select);
    }

    row.appendChild(excelCol);
    row.appendChild(arrow);
    row.appendChild(tallyField);

    // Initialize mapping
    if (mapping.tally_field !== 'none') {
        columnMappings[mapping.excel_column] = mapping.tally_field;
    }

    return row;
}

function getConfidenceClass(confidence) {
    if (confidence >= 0.8) return 'confidence-high';
    if (confidence >= 0.5) return 'confidence-medium';
    return 'confidence-low';
}

function updateMapping(e) {
    const excelColumn = e.target.dataset.excelColumn;
    const tallyField = e.target.value;

    if (tallyField === 'none') {
        delete columnMappings[excelColumn];
    } else {
        columnMappings[excelColumn] = tallyField;
    }
}

// Render Preview Table
function renderPreview() {
    const thead = document.getElementById('previewTableHead');
    const tbody = document.getElementById('previewTableBody');

    thead.innerHTML = '';
    tbody.innerHTML = '';

    // Create header
    const headerRow = document.createElement('tr');
    fileData.columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    // Create rows
    fileData.sample_data.forEach(row => {
        const tr = document.createElement('tr');
        fileData.columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = row[col] || '';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

// Process File
async function processFile() {
    // Validate mappings
    const requiredFields = ['date', 'party_name', 'amount'];
    const mappedFields = Object.values(columnMappings);

    const missingFields = requiredFields.filter(field => !mappedFields.includes(field));

    if (missingFields.length > 0) {
        alert(`Please map the following required fields: ${missingFields.join(', ')}`);
        return;
    }

    showLoading('Processing data and sending to Tally...');

    try {
        const createLedgers = document.getElementById('createLedgers').checked;

        const response = await fetch(`${API_URL}/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: fileData.filename,
                voucher_type: selectedVoucherType,
                mappings: columnMappings,
                create_missing_ledgers: createLedgers,
                company_name: selectedCompany
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Processing failed');
        }

        const result = await response.json();

        hideLoading();
        displayResults(result);

    } catch (error) {
        hideLoading();
        alert(`Error: ${error.message}`);
    }
}

// Display Results
function displayResults(result) {
    const container = document.getElementById('resultsContent');

    let html = `
        <div class="results-summary">
            <div class="result-stat success">
                <div class="result-stat-value">${result.success_count}</div>
                <div class="result-stat-label">Successful</div>
            </div>
            <div class="result-stat error">
                <div class="result-stat-value">${result.failed_count}</div>
                <div class="result-stat-label">Failed</div>
            </div>
        </div>
        <p><strong>${result.message}</strong></p>
    `;

    if (result.ledgers_created.length > 0) {
        html += `
            <div style="margin-top: 1rem; padding: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 0.5rem;">
                <strong>Ledgers Created:</strong> ${result.ledgers_created.join(', ')}
            </div>
        `;
    }

    if (result.errors.length > 0) {
        html += '<div class="error-list"><h3>Errors:</h3>';
        result.errors.forEach(error => {
            html += `
                <div class="error-item">
                    <div class="error-item-header">Row ${error.row_number}</div>
                    <div class="error-item-message"><strong>Error:</strong> ${error.error}</div>
                    ${error.reason ? `<div class="error-item-reason" style="margin-top:0.5rem; color:#d97706;"><strong>Reason:</strong> ${error.reason}</div>` : ''}
                    ${error.solution ? `<div class="error-item-solution" style="margin-top:0.5rem; color:#059669;"><strong>Solution:</strong> ${error.solution}</div>` : ''}
                </div>
            `;
        });
        html += '</div>';
    }

    container.innerHTML = html;
    resultsSection.classList.remove('hidden');

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Reset
function reset() {
    uploadedFile = null;
    fileData = null;
    selectedVoucherType = null;
    columnMappings = {};

    fileInfo.classList.add('hidden');
    voucherSection.classList.add('hidden');
    mappingSection.classList.add('hidden');
    previewSection.classList.add('hidden');
    actionButtons.classList.add('hidden');
    resultsSection.classList.add('hidden');

    fileInput.value = '';

    document.querySelectorAll('.voucher-btn').forEach(btn => {
        btn.classList.remove('selected');
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Loading Overlay
function showLoading(message = 'Processing...') {
    loadingText.textContent = message;
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}
