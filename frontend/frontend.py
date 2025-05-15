from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import requests
from wtforms import Form, FloatField, SelectField, validators
import os
from prometheus_client import Counter

app = Flask(__name__)
app.secret_key = 'liver_disease_prediction_app'

# Prometheus frontend request counter
FRONTEND_REQUESTS = Counter(
    'frontend_requests_total',
    'Total frontend requests',
    ['endpoint']
)

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
    FRONTEND_REQUESTS.labels(endpoint='/').inc()
    form = PredictionForm(request.form)
    prediction_result = None
    error_message = None
    if request.method == 'POST':
        if form.validate():
            try:
                payload = { field: float(form._fields[field].data) if field != 'gender' else int(form.gender.data)
                            for field in form._fields }
                backend_url = os.getenv('BACKEND_URL', 'http://backend:8000')
                response = requests.post(f"{backend_url}/predict", json=payload)
                if response.ok:
                    prediction_result = response.json()
                else:
                    error_message = f"API Error {response.status_code}: {response.text}"
            except Exception as e:
                error_message = f"Error: {e}"
        else:
            error_message = "Please fix the errors in the form."
    return render_template('index.html', form=form, result=prediction_result, error=error_message)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    FRONTEND_REQUESTS.labels(endpoint='/api/predict').inc()
    data = request.json or {}
    required_fields = ['age', 'gender', 'total_bilirubin', 'direct_bilirubin',
                       'alkaline_phosphotase', 'alanine_aminotransferase',
                       'aspartate_aminotransferase', 'total_proteins',
                       'albumin', 'albumin_globulin_ratio']
    for f in required_fields:
        if f not in data:
            return jsonify({'error': f'Missing required field: {f}'}), 400
        if f != 'gender':
            try:
                if float(data[f]) < 0:
                    return jsonify({'error': f'{f} cannot be negative'}), 400
            except:
                return jsonify({'error': f'{f} must be a valid number'}), 400
    if data['gender'] not in [0, 1, '0', '1']:
        return jsonify({'error': 'Gender must be 0 or 1'}), 400
    data['gender'] = int(data['gender'])
    backend_url = os.getenv('BACKEND_URL', 'http://backend:8000')
    resp = requests.post(f"{backend_url}/predict", json=data)
    return jsonify(resp.json()), resp.status_code

# Route to submit feedback on predictions
@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.form
        prediction_correct = data.get('correct') == 'true'
        
        # If prediction was wrong, send data to backend for retraining
        if not prediction_correct:
            # Get data from form
            patient_data = {
                'age': float(data.get('age')),
                'gender': int(data.get('gender')),
                'total_bilirubin': float(data.get('total_bilirubin')),
                'direct_bilirubin': float(data.get('direct_bilirubin')),
                'alkaline_phosphotase': float(data.get('alkaline_phosphotase')),
                'alanine_aminotransferase': float(data.get('alanine_aminotransferase')),
                'aspartate_aminotransferase': float(data.get('aspartate_aminotransferase')),
                'total_proteins': float(data.get('total_proteins')),
                'albumin': float(data.get('albumin')),
                'albumin_globulin_ratio': float(data.get('albumin_globulin_ratio')),
                'actual_result': int(data.get('actual_result'))
            }
            
            # Send to backend
            backend_url = os.environ.get('BACKEND_URL', 'http://backend:8000')
            response = requests.post(f"{backend_url}/feedback", json=patient_data)
            
            # Check response status
            if response.status_code != 200:
                flash(f"Error sending feedback: {response.text}")
                return redirect(url_for('index'))
        
        flash("Thank you for your feedback!")
        return redirect(url_for('index'))
        
    except Exception as e:
        app.logger.error(f"Error in feedback submission: {str(e)}")
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
