import os
import pandas as pd
from flask import jsonify, request, send_file, Blueprint
from http import HTTPStatus
from werkzeug.utils import secure_filename
from app.api.auth import token_required
import tempfile
from datetime import datetime
import io

# Create blueprint with a unique name
api = Blueprint('excel_api', __name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def apply_formula(df, formula_config):
    """Apply formula to the DataFrame."""
    try:
        # Create a copy of the DataFrame to avoid modifying the original
        result_df = df.copy()
        
        # Apply each formula in the configuration
        for formula_item in formula_config['formula']:
            columns = formula_item['columns']
            formula = formula_item['formula']
            
            # Replace column placeholders with actual column references
            for col in columns:
                formula = formula.replace(f'{col}...', f'df["{col}"]')
            
            # Evaluate the formula
            result_df['Result'] = eval(formula)
        
        return result_df
    except Exception as e:
        raise ValueError(f"Error applying formula: {str(e)}")

@api.route('/excel/process', methods=['POST'])
@token_required
def process_excel(current_user):
    """Process Excel file with formulas."""
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), HTTPStatus.BAD_REQUEST
    
    file = request.files['file']
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'message': 'Invalid file format'}), HTTPStatus.BAD_REQUEST
    
    try:
        # Read Excel file
        df = pd.read_excel(file)
        
        # Get formula from request
        formula_data = request.form.get('formula')
        if not formula_data:
            return jsonify({'message': 'No formula provided'}), HTTPStatus.BAD_REQUEST
        
        # Process formulas (implement your formula processing logic here)
        # For now, we'll just return the original file
        
        # Save processed file to memory
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'processed_{file.filename}'
        )
        
    except Exception as e:
        return jsonify({'message': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    finally:
        # Clean up temporary file
        if 'tmp' in locals():
            os.unlink(tmp.name) 