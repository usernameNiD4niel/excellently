(() => {
    // DOM Elements
    const excelFileInput = document.getElementById('excelFile');
    const columnSelector = document.getElementById('columnSelector');
    const columnOptions = document.getElementById('columnOptions');
    const formulaBuilder = document.getElementById('formulaBuilder');
    const formulaType = document.getElementById('formulaType');
    const selectedColumns = document.getElementById('selectedColumns');
    const customFormulaGroup = document.getElementById('customFormulaGroup');
    const customFormula = document.getElementById('customFormula');
    const addFormulaBtn = document.getElementById('addFormulaBtn');
    const formulasList = document.getElementById('formulasList');
    const formulasContainer = document.getElementById('formulasContainer');
    const processBtn = document.getElementById('processBtn');
    const result = document.getElementById('result');
    const downloadLink = document.getElementById('downloadLink');
    const error = document.getElementById('error');
    const loginForm = document.getElementById('loginForm');
    const loginEmail = document.getElementById('loginEmail');
    const loginPassword = document.getElementById('loginPassword');
    const loginBtn = document.getElementById('loginBtn');
    const authSection = document.getElementById('authSection');
    const userInfo = document.getElementById('userInfo');
    const logoutBtn = document.getElementById('logoutBtn');

    // Constants
    const API_KEY = 'EXCELLENTLY_API_KEY';

    // State
    let excelFile = null;
    let columns = [];
    let selectedColumnsList = [];
    let formulas = [];
    let currentUser = null;

    // Check authentication on load
    checkAuthStatus();

    // Event Listeners
    excelFileInput.addEventListener('change', handleFileUpload);
    formulaType.addEventListener('change', handleFormulaTypeChange);
    addFormulaBtn.addEventListener('click', addFormula);
    processBtn.addEventListener('click', processExcel);
    loginBtn.addEventListener('click', handleLogin);
    logoutBtn.addEventListener('click', handleLogout);

    // Check authentication status
    async function checkAuthStatus() {
        try {
            const response = await fetch('/auth/me', {
                method: 'GET',
                headers: {
                    'X-API-KEY': API_KEY
                },
                credentials: 'include' // Important for cookies
            });

            if (response.ok) {
                const data = await response.json();
                currentUser = data;
                showAuthenticatedUI();
            } else {
                showLoginUI();
            }
        } catch (err) {
            console.error('Auth check failed:', err);
            showLoginUI();
        }
    }

    // Show login UI
    function showLoginUI() {
        authSection.style.display = 'block';
        userInfo.style.display = 'none';
        currentUser = null;
    }

    // Show authenticated UI
    function showAuthenticatedUI() {
        authSection.style.display = 'none';
        userInfo.style.display = 'block';
        if (currentUser) {
            document.getElementById('userName').textContent = currentUser.name || currentUser.username;
        }
    }

    // Get headers with API key
    function getHeaders() {
        return {
            'X-API-KEY': API_KEY
        };
    }

    // Handle login
    async function handleLogin() {
        const email = loginEmail.value;
        const password = loginPassword.value;

        if (!email || !password) {
            showError('Please enter both email and password');
            return;
        }

        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    ...getHeaders(),
                    'Content-Type': 'application/json'
                },
                credentials: 'include', // Important for cookies
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Login failed');
            }

            const data = await response.json();
            currentUser = data.user;

            // Update UI
            showAuthenticatedUI();
            error.style.display = 'none';
        } catch (err) {
            showError(err.message);
        }
    }

    // Handle logout
    async function handleLogout() {
        try {
            const response = await fetch('/auth/logout', {
                method: 'POST',
                headers: getHeaders(),
                credentials: 'include' // Important for cookies
            });

            if (!response.ok) {
                throw new Error('Logout failed');
            }

            // Update UI
            showLoginUI();
        } catch (err) {
            showError(err.message);
        }
    }

    // Handle file upload
    function handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Check file type
        const fileType = file.name.split('.').pop().toLowerCase();
        if (!['xlsx', 'xls'].includes(fileType)) {
            showError('Please upload a valid Excel file (.xlsx or .xls)');
            return;
        }

        excelFile = file;
        
        // For demo purposes, we'll use a predefined set of columns
        // In a real app, you would parse the Excel file to get the actual columns
        columns = ['Day', 'Year', 'Month', 'Sales', 'Revenue', 'Profit'];
        
        // Display column selector
        displayColumnSelector();
    }

    // Display column selector
    function displayColumnSelector() {
        columnOptions.innerHTML = '';
        
        columns.forEach(column => {
            const columnOption = document.createElement('div');
            columnOption.className = 'column-option';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `column-${column}`;
            checkbox.value = column;
            checkbox.addEventListener('change', handleColumnSelection);
            
            const label = document.createElement('label');
            label.htmlFor = `column-${column}`;
            label.textContent = column;
            
            columnOption.appendChild(checkbox);
            columnOption.appendChild(label);
            columnOptions.appendChild(columnOption);
        });
        
        columnSelector.style.display = 'block';
        formulaBuilder.style.display = 'block';
    }

    // Handle column selection
    function handleColumnSelection() {
        selectedColumnsList = Array.from(document.querySelectorAll('.column-option input:checked'))
            .map(checkbox => checkbox.value);
        
        updateSelectedColumnsDisplay();
    }

    // Update selected columns display
    function updateSelectedColumnsDisplay() {
        selectedColumns.innerHTML = '';
        
        if (selectedColumnsList.length === 0) {
            selectedColumns.innerHTML = '<p>No columns selected</p>';
            return;
        }
        
        selectedColumnsList.forEach(column => {
            const columnTag = document.createElement('span');
            columnTag.className = 'column-tag';
            columnTag.textContent = column;
            selectedColumns.appendChild(columnTag);
        });
    }

    // Handle formula type change
    function handleFormulaTypeChange() {
        if (formulaType.value === 'CUSTOM') {
            customFormulaGroup.style.display = 'block';
        } else {
            customFormulaGroup.style.display = 'none';
        }
    }

    // Add formula
    function addFormula() {
        if (selectedColumnsList.length === 0) {
            showError('Please select at least one column');
            return;
        }
        
        let formulaText = '';
        
        if (formulaType.value === 'CUSTOM') {
            formulaText = customFormula.value;
            if (!formulaText) {
                showError('Please enter a custom formula');
                return;
            }
        } else {
            formulaText = `${formulaType.value}(${selectedColumnsList.map(col => `${col}...`).join(', ')})`;
        }
        
        // Add formula to list
        formulas.push({
            columns: [...selectedColumnsList],
            formula: formulaText
        });
        
        // Update formulas display
        updateFormulasDisplay();
        
        // Show formulas list
        formulasList.style.display = 'block';
    }

    // Update formulas display
    function updateFormulasDisplay() {
        formulasContainer.innerHTML = '';
        
        formulas.forEach((formula, index) => {
            const formulaItem = document.createElement('div');
            formulaItem.className = 'formula-item';
            
            const formulaText = document.createElement('p');
            formulaText.textContent = `Formula ${index + 1}: ${formula.formula}`;
            
            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = 'Delete';
            deleteBtn.addEventListener('click', () => {
                formulas.splice(index, 1);
                updateFormulasDisplay();
            });
            
            formulaItem.appendChild(formulaText);
            formulaItem.appendChild(deleteBtn);
            formulasContainer.appendChild(formulaItem);
        });
    }

    // Process Excel
    async function processExcel() {
        if (!currentUser) {
            showError('Please log in to process Excel files');
            return;
        }
        
        if (!excelFile) {
            showError('Please upload an Excel file');
            return;
        }
        
        if (formulas.length === 0) {
            showError('Please add at least one formula');
            return;
        }
        
        try {
            // Create form data
            const formData = new FormData();
            formData.append('file', excelFile);
            formData.append('formula', JSON.stringify({ formula: formulas }));
            
            // Send request
            const response = await fetch('/api/excel/process', {
                method: 'POST',
                headers: getHeaders(),
                credentials: 'include', // Important for cookies
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Error processing Excel file');
            }
            
            // Get blob from response
            const blob = await response.blob();
            
            // Create download link
            const url = URL.createObjectURL(blob);
            downloadLink.href = url;
            downloadLink.download = `processed_${excelFile.name}`;
            
            // Show result
            result.style.display = 'block';
            error.style.display = 'none';
        } catch (err) {
            showError(err.message);
        }
    }

    // Show error
    function showError(message) {
        error.textContent = message;
        error.style.display = 'block';
        result.style.display = 'none';
    }
})();

async function init() {
    const response = await fetch('/api/users');
    const users = await response.json();
    console.log(users);
}