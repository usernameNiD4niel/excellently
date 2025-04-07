import pytest
import pandas as pd
import io
from http import HTTPStatus
import json

def test_process_excel_no_file(client, auth_headers):
    """Test processing Excel without file upload."""
    response = client.post('/api/excel/process', headers=auth_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_json()['message'] == 'No file uploaded'

def test_process_excel_invalid_file_type(client, auth_headers):
    """Test processing Excel with invalid file type."""
    data = {
        'file': (io.BytesIO(b'not an excel file'), 'test.txt')
    }
    response = client.post('/api/excel/process', 
                          headers=auth_headers,
                          data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_json()['message'] == 'Invalid file type'

def test_process_excel_no_formula(client, auth_headers):
    """Test processing Excel without formula configuration."""
    # Create a test Excel file
    df = pd.DataFrame({
        'Day': [1, 2, 3],
        'Year': [2024, 2024, 2024],
        'Month': [1, 2, 3]
    })
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    
    data = {
        'file': (excel_file, 'test.xlsx')
    }
    response = client.post('/api/excel/process',
                          headers=auth_headers,
                          data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_json()['message'] == 'No formula configuration provided'

def test_process_excel_invalid_formula(client, auth_headers):
    """Test processing Excel with invalid formula configuration."""
    # Create a test Excel file
    df = pd.DataFrame({
        'Day': [1, 2, 3],
        'Year': [2024, 2024, 2024],
        'Month': [1, 2, 3]
    })
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    
    # Invalid formula configuration
    formula_config = {
        'formula': [
            {
                'columns': ['InvalidColumn'],
                'formula': 'SUM(InvalidColumn...)'
            }
        ]
    }
    
    data = {
        'file': (excel_file, 'test.xlsx'),
        'formula': json.dumps(formula_config)
    }
    response = client.post('/api/excel/process',
                          headers=auth_headers,
                          data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Missing columns in Excel file' in response.get_json()['message']

def test_process_excel_success(client, auth_headers):
    """Test successful Excel processing."""
    # Create a test Excel file
    df = pd.DataFrame({
        'Day': [1, 2, 3],
        'Year': [2024, 2024, 2024],
        'Month': [1, 2, 3]
    })
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    
    # Valid formula configuration
    formula_config = {
        'formula': [
            {
                'columns': ['Day', 'Year', 'Month'],
                'formula': 'SUM(Day..., Year..., Month...)'
            }
        ]
    }
    
    data = {
        'file': (excel_file, 'test.xlsx'),
        'formula': json.dumps(formula_config)
    }
    response = client.post('/api/excel/process',
                          headers=auth_headers,
                          data=data)
    assert response.status_code == HTTPStatus.OK
    assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 