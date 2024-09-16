from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Listas globales para almacenar datos de pacientes, consultas y acciones
patients = []
pending_consultations = []
history = []
action_history = []

class Patient:
    def __init__(self, name, age, patient_id, dob, gender, address, phone, email, internal_id, diseases, surgeries, allergies, medications, family_history):
        self.name = name
        self.age = age
        self.patient_id = patient_id
        self.dob = dob
        self.gender = gender
        self.address = address
        self.phone = phone
        self.email = email
        self.internal_id = internal_id
        self.diseases = diseases
        self.surgeries = surgeries
        self.allergies = allergies
        self.medications = medications
        self.family_history = family_history
        self.history = []

    def add_consultation(self, date, doctor, diagnosis, medication):
        self.history.append({
            'date': date,
            'doctor': doctor,
            'diagnosis': diagnosis,
            'medication': medication
        })

    def has_consultations(self):
        return len(self.history) > 0

def add_patient_action(patient):
    action_history.append({
        'action': 'add_patient',
        'patient': patient
    })

def remove_patient_action(patient):
    action_history.append({
        'action': 'remove_patient',
        'patient': patient
    })

def add_consultation_action(patient, consultation):
    action_history.append({
        'action': 'add_consultation',
        'patient_id': patient.patient_id,
        'consultation': consultation
    })

def remove_consultation_action(patient, consultation):
    action_history.append({
        'action': 'remove_consultation',
        'patient_id': patient.patient_id,
        'consultation': consultation
    })

@app.route('/')
def index():
    return render_template('index.html', patients=patients)

@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        patient_id = request.form['patient_id']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        internal_id = request.form['internal_id']
        diseases = request.form['diseases']
        surgeries = request.form['surgeries']
        allergies = request.form['allergies']
        medications = request.form['medications']
        family_history = request.form['family_history']
        
        new_patient = Patient(name, age, patient_id, dob, gender, address, phone, email, internal_id, diseases, surgeries, allergies, medications, family_history)
        patients.append(new_patient)
        add_patient_action(new_patient)  # Track the addition of a new patient
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/add_consultation', methods=['GET', 'POST'])
def add_consultation():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        date = request.form['date']
        doctor = request.form['doctor']
        diagnosis = request.form['diagnosis']
        medication = request.form['medication']
        
        # Find the patient by patient_id
        patient = next((p for p in patients if p.patient_id == patient_id), None)
        if patient:
            consultation = {
                'date': date,
                'doctor': doctor,
                'diagnosis': diagnosis,
                'medication': medication
            }
            patient.add_consultation(date, doctor, diagnosis, medication)
            add_consultation_action(patient, consultation)  # Track the addition of a new consultation
            return redirect(url_for('index'))
    return render_template('add_consultation.html', patients=patients)

@app.route('/view_pending_consultations')
def view_pending_consultations():
    return render_template('pending.html', pending_consultations=[p for p in patients if not p.has_consultations()])

@app.route('/undo_last_action')
def undo_last_action():
    if not action_history:
        return redirect(url_for('index'))
    
    last_action = action_history.pop()
    
    if last_action['action'] == 'add_patient':
        patient = last_action['patient']
        patients.remove(patient)
    elif last_action['action'] == 'remove_patient':
        patient = last_action['patient']
        patients.append(patient)
    elif last_action['action'] == 'add_consultation':
        patient_id = last_action['patient_id']
        consultation = last_action['consultation']
        patient = next((p for p in patients if p.patient_id == patient_id), None)
        if patient:
            patient.history.remove(consultation)
    elif last_action['action'] == 'remove_consultation':
        patient_id = last_action['patient_id']
        consultation = last_action['consultation']
        patient = next((p for p in patients if p.patient_id == patient_id), None)
        if patient:
            patient.history.append(consultation)
    
    return redirect(url_for('index'))

@app.route('/view_patient_info/<patient_id>')
def view_patient_info(patient_id):
    patient = next((p for p in patients if p.patient_id == patient_id), None)
    if patient:
        return render_template('patient_info.html', patient=patient)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
