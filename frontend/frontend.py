from flask import Flask, render_template, request, jsonify, flash
import requests
from wtforms import Form, FloatField, SelectField, validators
import re
import os

app = Flask(__name__)
app.secret_key = 'liver_disease_prediction_app'  # Required for flash messages

class FloatValidationError(ValueError):
    pass

def validate_float(form, field):
    if field.data is None:
        raise validators.ValidationError('This field is required.')
    
    try:
        value = float(field.data)
        if value < 0:
            raise validators.ValidationError(f'{field.label.text} cannot be negative.')
    except (ValueError, TypeError):
        raise validators.ValidationError(f'{field.label.text} must be a valid number.')

class PredictionForm(Form):
    age = FloatField('Age', [
        validators.InputRequired(message="Age is required"),
        validators.NumberRange(min=0.1, max=120, message="Age must be between 0.1 and 120")
    ])
    
    gender = SelectField('Gender', choices=[('1', 'Male'), ('0', 'Female')], 
                         validators=[validators.InputRequired(message="Gender is required")])
    
    total_bilirubin = FloatField('Total Bilirubin', [
        validators.InputRequired(message="Total Bilirubin is required"),
        validators.NumberRange(min=0, max=100, message="Total Bilirubin must be between 0 and 100")
    ])
    
    direct_bilirubin = FloatField('Direct Bilirubin', [
        validators.InputRequired(message="Direct Bilirubin is required"),
        validators.NumberRange(min=0, max=100, message="Direct Bilirubin must be between 0 and 100")
    ])
    
    alkaline_phosphotase = FloatField('Alkaline Phosphotase', [
        validators.InputRequired(message="Alkaline Phosphotase is required"),
        validators.NumberRange(min=0, max=2000, message="Alkaline Phosphotase must be between 0 and 2000")
    ])
    
    alanine_aminotransferase = FloatField('Alanine Aminotransferase', [
        validators.InputRequired(message="Alanine Aminotransferase is required"),
        validators.NumberRange(min=0, max=2000, message="Alanine Aminotransferase must be between 0 and 2000")
    ])
    
    aspartate_aminotransferase = FloatField('Aspartate Aminotransferase', [
        validators.InputRequired(message="Aspartate Aminotransferase is required"),
        validators.NumberRange(min=0, max=2000, message="Aspartate Aminotransferase must be between 0 and 2000")
    ])
    
    total_proteins = FloatField('Total Proteins', [
        validators.InputRequired(message="Total Proteins is required"),
        validators.NumberRange(min=0, max=20, message="Total Proteins must be between 0 and 20")
    ])
    
    albumin = FloatField('Albumin', [
        validators.InputRequired(message="Albumin is required"),
        validators.NumberRange(min=0, max=10, message="Albumin must be between 0 and 10")
    ])
    
    albumin_globulin_ratio = FloatField('Albumin Globulin Ratio', [
        validators.InputRequired(message="Albumin Globulin Ratio is required"),
        validators.NumberRange(min=0, max=10, message="Albumin Globulin Ratio must be between 0 and 10")
    ])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PredictionForm(request.form)
    prediction_result = None
    error_message = None
    
    if request.method == 'POST':
        if form.validate():
            try:
                # Additional custom validation to ensure all fields are valid float values
                for field_name, field in form._fields.items():
                    if field_name != 'gender':
                        try:
                            value = float(field.data)
                            if not isinstance(value, float):
                                form.errors.setdefault(field_name, []).append(f"{field.label.text} must be a valid number.")
                                return render_template('index.html', form=form, result=None, error="Please fix form errors.")
                        except (ValueError, TypeError):
                            form.errors.setdefault(field_name, []).append(f"{field.label.text} must be a valid number.")
                            return render_template('index.html', form=form, result=None, error="Please fix form errors.")
                
                # Prepare data for API request
                payload = {
                    'age': float(form.age.data),
                    'gender': int(form.gender.data),
                    'total_bilirubin': float(form.total_bilirubin.data),
                    'direct_bilirubin': float(form.direct_bilirubin.data),
                    'alkaline_phosphotase': float(form.alkaline_phosphotase.data),
                    'alanine_aminotransferase': float(form.alanine_aminotransferase.data),
                    'aspartate_aminotransferase': float(form.aspartate_aminotransferase.data),
                    'total_proteins': float(form.total_proteins.data),
                    'albumin': float(form.albumin.data),
                    'albumin_globulin_ratio': float(form.albumin_globulin_ratio.data)
                }
                
                # Make API request to the backend using the environment variable
                backend_url = os.getenv('BACKEND_URL', 'http://backend-service:8000')
                response = requests.post(f'{backend_url}/predict', json=payload)
                
                if response.status_code == 200:
                    prediction_result = response.json()
                else:
                    error_message = f"API Error: {response.status_code}"
                    try:
                        error_details = response.json().get('detail', 'Unknown error')
                        error_message += f" - {error_details}"
                    except:
                        pass
            except Exception as e:
                error_message = f"Error: {str(e)}"
        else:
            # Form validation failed
            error_message = "Please fix the errors in the form."
    
    return render_template('index.html', form=form, result=prediction_result, error=error_message)

# Create a simple API endpoint for testing
@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.json
        
        # Validate that all required fields are present and valid
        required_fields = [
            'age', 'gender', 'total_bilirubin', 'direct_bilirubin', 
            'alkaline_phosphotase', 'alanine_aminotransferase', 'aspartate_aminotransferase',
            'total_proteins', 'albumin', 'albumin_globulin_ratio'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Validate numeric fields (except gender)
            if field != 'gender':
                try:
                    value = float(data[field])
                    if value < 0:
                        return jsonify({"error": f"{field} cannot be negative"}), 400
                except (ValueError, TypeError):
                    return jsonify({"error": f"{field} must be a valid number"}), 400
        
        # Validate gender specifically
        if data['gender'] not in [0, 1, '0', '1']:
            return jsonify({"error": "Gender must be 0 (Female) or 1 (Male)"}), 400
            
        # Convert gender to int if it's a string
        if isinstance(data['gender'], str):
            data['gender'] = int(data['gender'])
            
        backend_url = os.getenv('BACKEND_URL', 'http://backend-service:8000')
        response = requests.post(f'{backend_url}/predict', json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)