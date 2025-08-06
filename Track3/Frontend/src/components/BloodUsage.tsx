import React, { useState } from 'react';
import './BloodUsage.css';

interface BloodUsageData {
  patient_id: string;
  patient_name: string;
  patient_age: number | '';
  patient_gender: string;
  blood_type: string;
  usage_date: string;
  hospital_department: string;
  notes?: string;
}

const BloodUsage: React.FC = () => {
  const [formData, setFormData] = useState<BloodUsageData>({
    patient_id: '',
    patient_name: '',
    patient_age: '',
    patient_gender: '',
    blood_type: '',
    usage_date: '',
    hospital_department: '',
    notes: ''
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);

  const bloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
  const genders = ['M', 'F', 'Other'];
  const departments = [
    'Emergency Department',
    'Surgery',
    'ICU',
    'Cardiology',
    'Oncology',
    'Orthopedics',
    'Pediatrics',
    'Obstetrics',
    'Internal Medicine',
    'Trauma Unit'
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name.includes('age') 
        ? (value === '' ? '' : Number(value))
        : value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'text/csv') {
      setCsvFile(file);
      setError('');
    } else {
      setError('Please select a valid CSV file');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Prepare the data for submission
      const submissionData = {
        patient_id: formData.patient_id,
        patient_name: formData.patient_name,
        patient_age: formData.patient_age,
        patient_gender: formData.patient_gender,
        blood_type: formData.blood_type,
        usage_date: formData.usage_date,
        hospital_department: formData.hospital_department,
        notes: formData.notes
      };

      const response = await fetch('https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/usage', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submissionData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to record blood usage');
      }

      const data = await response.json();
      setSuccess(`Blood usage recorded successfully! Usage ID: ${data.usage_record_id || data.id || 'Generated'}`);
      
      // Reset form
      setFormData({
        patient_id: '',
        patient_name: '',
        patient_age: '',
        patient_gender: '',
        blood_type: '',
        usage_date: '',
        hospital_department: '',
        notes: ''
      });
      
    } catch (error) {
      console.error('Error recording blood usage:', error);
      setError(error instanceof Error ? error.message : 'Failed to record blood usage');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCsvUpload = async () => {
    if (!csvFile) {
      setError('Please select a CSV file first');
      return;
    }

    setUploadLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const formData = new FormData();
      formData.append('file', csvFile);

      const response = await fetch('https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/usage/upload-csv', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'accept': 'application/json',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload CSV file');
      }

      const data = await response.json();
      setSuccess(`CSV file uploaded successfully! ${data.message || 'Usage records processed.'}`);
      setCsvFile(null);
      
      // Reset file input
      const fileInput = document.getElementById('csv-file') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      
    } catch (error) {
      console.error('Error uploading CSV:', error);
      setError(error instanceof Error ? error.message : 'Failed to upload CSV file');
    } finally {
      setUploadLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      patient_id: '',
      patient_name: '',
      patient_age: '',
      patient_gender: '',
      blood_type: '',
      usage_date: '',
      hospital_department: '',
      notes: ''
    });
    setError('');
    setSuccess('');
  };

  const navigateToAddSample = () => {
    window.location.href = '/add-sample';
  };

  const navigateToDashboard = () => {
    window.location.href = '/dashboard';
  };

  const navigateToBloodUsage = () => {
    window.location.href = '/blood-usage';
  };

  const navigateToForecasting = () => {
    window.location.href = '/forecasting';
  };

  const navigateToFeedbackAnalytics = () => {
    window.location.href = '/feedback-analytics';
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userData');
    window.location.href = '/';
  };

  return (
    <div className="blood-usage-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="logo" onClick={navigateToDashboard}>
            🏠
          </div>
        </div>
        
        <div className="sidebar-menu">
          <div className="menu-item" onClick={navigateToAddSample} title="Add Sample">
            <span className="menu-icon">+</span>
          </div>
          <div className="menu-item active" onClick={navigateToBloodUsage} title="Blood Usage">
            <span className="menu-icon">🩸</span>
          </div>
          <div className="menu-item" onClick={navigateToDashboard} title="Dashboard">
            <span className="menu-icon">🏠</span>
          </div>
          <div className="menu-item" onClick={navigateToForecasting} title="Forecasting">
            <span className="menu-icon">📊</span>
          </div>
          <div className="menu-item" onClick={navigateToFeedbackAnalytics} title="Feedback Analytics">
            <span className="menu-icon">📈</span>
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="menu-item logout" onClick={handleLogout}>
            <span className="menu-icon">🚪</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="form-container">
          <h1 className="form-title">Blood Usage Entry</h1>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {success && (
            <div className="success-message">
              {success}
            </div>
          )}

          <form onSubmit={handleSubmit} className="blood-usage-form">
            {/* Patient Information Section */}
            <div className="form-section">
              <h2 className="section-title">Patient Information</h2>
              
              <div className="form-row">
                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">🆔</span>
                    <input
                      type="text"
                      name="patient_id"
                      placeholder="Patient ID"
                      value={formData.patient_id}
                      onChange={handleInputChange}
                      className="form-input"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">👤</span>
                    <input
                      type="text"
                      name="patient_name"
                      placeholder="Patient Name"
                      value={formData.patient_name}
                      onChange={handleInputChange}
                      className="form-input"
                    />
                  </div>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">🎂</span>
                    <input
                      type="number"
                      name="patient_age"
                      placeholder="Patient Age *"
                      value={formData.patient_age}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      min="0"
                      max="120"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">⚧</span>
                    <select
                      name="patient_gender"
                      value={formData.patient_gender}
                      onChange={handleInputChange}
                      required
                      className="form-input form-select"
                    >
                      <option value="">Patient Gender *</option>
                      {genders.map(gender => (
                        <option key={gender} value={gender}>
                          {gender === 'M' ? 'Male' : gender === 'F' ? 'Female' : 'Other'}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* Blood Usage Details Section */}
            <div className="form-section">
              <h2 className="section-title">Blood Usage Details</h2>
              
              <div className="form-row">
                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">🩸</span>
                    <select
                      name="blood_type"
                      value={formData.blood_type}
                      onChange={handleInputChange}
                      required
                      className="form-input form-select"
                    >
                      <option value="">Blood Type *</option>
                      {bloodTypes.map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon"></span>
                    <input
                      type="date"
                      name="usage_date"
                      value={formData.usage_date}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                    />
                    <label className="date-label">Usage Date:</label>
                  </div>
                </div>
              </div>
            </div>

            {/* Medical Information Section */}
            <div className="form-section">
              <h2 className="section-title">Medical Information</h2>
              
              <div className="form-row">
                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">🏥</span>
                    <select
                      name="hospital_department"
                      value={formData.hospital_department}
                      onChange={handleInputChange}
                      required
                      className="form-input form-select"
                    >
                      <option value="">Hospital Department *</option>
                      {departments.map(dept => (
                        <option key={dept} value={dept}>{dept}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon"></span>
                    <textarea
                      name="notes"
                      placeholder="Additional Notes (Optional)"
                      value={formData.notes}
                      onChange={handleInputChange}
                      className="form-input form-textarea"
                      rows={3}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* CSV Upload Section */}
            <div className="form-section">
              <h2 className="section-title">Bulk Upload</h2>
              <div className="csv-upload-container">
                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">📄</span>
                    <input
                      type="file"
                      id="csv-file"
                      accept=".csv"
                      onChange={handleFileChange}
                      className="form-input file-input"
                    />
                    <label htmlFor="csv-file" className="file-label">
                      {csvFile ? csvFile.name : 'Choose CSV file for bulk usage upload...'}
                    </label>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleCsvUpload}
                  disabled={!csvFile || uploadLoading}
                  className="upload-btn"
                >
                  {uploadLoading ? 'Uploading...' : 'Upload CSV'}
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="form-actions">
              <button
                type="submit"
                disabled={isLoading}
                className="save-btn"
              >
                {isLoading ? 'Recording...' : 'Record Usage'}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="cancel-btn"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default BloodUsage;
