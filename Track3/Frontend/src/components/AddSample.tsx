import React, { useState } from 'react';
import './AddSample.css';

interface DonorData {
  donor_age: number | '';
  donor_gender: string;
  donor_occupation: string;
  blood_type: string;
  collection_site: string;
  donation_date: string;
  expiry_date: string;
  collection_volume_ml: number | '';
  hemoglobin_g_dl: number | '';
}

const AddSample: React.FC = () => {
  const [formData, setFormData] = useState<DonorData>({
    donor_age: '',
    donor_gender: '',
    donor_occupation: '',
    blood_type: '',
    collection_site: '',
    donation_date: '',
    expiry_date: '',
    collection_volume_ml: '',
    hemoglobin_g_dl: ''
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);

  const bloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
  const genders = ['M', 'F', 'Other'];
  const volumes = ['250', '350', '450', '500'];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name.includes('age') || name.includes('ml') || name.includes('g_dl') 
        ? (value === '' ? '' : Number(value))
        : value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'text/csv') {
      setCsvFile(file);
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

      const response = await fetch('https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/collections', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add blood collection record');
      }

      const data = await response.json();
      setSuccess(`Blood collection record added successfully! ID: ${data.donation_record_id}`);
      
      // Reset form
      setFormData({
        donor_age: '',
        donor_gender: '',
        donor_occupation: '',
        blood_type: '',
        collection_site: '',
        donation_date: '',
        expiry_date: '',
        collection_volume_ml: '',
        hemoglobin_g_dl: ''
      });
      
    } catch (error) {
      console.error('Error adding blood collection:', error);
      setError(error instanceof Error ? error.message : 'Failed to add blood collection record');
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

      const response = await fetch('https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/collections/upload-csv', {
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
      setSuccess(`CSV file uploaded successfully! ${data.message || 'Records processed.'}`);
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
      donor_age: '',
      donor_gender: '',
      donor_occupation: '',
      blood_type: '',
      collection_site: '',
      donation_date: '',
      expiry_date: '',
      collection_volume_ml: '',
      hemoglobin_g_dl: ''
    });
    setError('');
    setSuccess('');
  };

  const navigateToAddSample = () => {
    window.location.href = '/add-sample';
  };

  const navigateToBloodUsage = () => {
    window.location.href = '/blood-usage';
  };

  const navigateToDashboard = () => {
    window.location.href = '/dashboard';
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
    <div className="add-sample-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="logo" onClick={navigateToDashboard}>
            🏠
          </div>
        </div>
        
        <div className="sidebar-menu">
          <div className="menu-item active" onClick={navigateToAddSample} title="Add Sample">
            <span className="menu-icon">+</span>
          </div>
          <div className="menu-item" onClick={navigateToBloodUsage} title="Blood Usage">
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
          <h1 className="form-title">Add New Sample</h1>
          
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

          <form onSubmit={handleSubmit} className="add-sample-form">
            {/* Donor Demographics Section */}
            <div className="form-section">
              <h2 className="section-title">Donor Demographics</h2>
              
              <div className="form-row">
                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">👤</span>
                    <input
                      type="number"
                      name="donor_age"
                      placeholder="Enter Donor Age *"
                      value={formData.donor_age}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      min="16"
                      max="65"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">⚧</span>
                    <select
                      name="donor_gender"
                      value={formData.donor_gender}
                      onChange={handleInputChange}
                      required
                      className="form-input form-select"
                    >
                      <option value="">Gender *</option>
                      {genders.map(gender => (
                        <option key={gender} value={gender}>
                          {gender === 'M' ? 'Male' : gender === 'F' ? 'Female' : 'Other'}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group full-width">
                  <div className="input-wrapper">
                    <span className="input-icon">💼</span>
                    <input
                      type="text"
                      name="donor_occupation"
                      placeholder="Occupation"
                      value={formData.donor_occupation}
                      onChange={handleInputChange}
                      className="form-input"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Clinical Data Section */}
            <div className="form-section">
              <h2 className="section-title">Clinical Data</h2>
              
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
                    <span className="input-icon">💧</span>
                    <select
                      name="collection_volume_ml"
                      value={formData.collection_volume_ml}
                      onChange={handleInputChange}
                      required
                      className="form-input form-select"
                    >
                      <option value="">Volume(bags)</option>
                      {volumes.map(volume => (
                        <option key={volume} value={volume}>{volume}ml</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">🏥</span>
                    <input
                      type="text"
                      name="collection_site"
                      placeholder="Collection Site"
                      value={formData.collection_site}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">🔬</span>
                    <input
                      type="number"
                      name="hemoglobin_g_dl"
                      placeholder="Hemoglobin Level (g/dL)"
                      value={formData.hemoglobin_g_dl}
                      onChange={handleInputChange}
                      className="form-input"
                      step="0.1"
                      min="0"
                      max="20"
                    />
                  </div>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">📅</span>
                    <input
                      type="date"
                      name="donation_date"
                      value={formData.donation_date}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                    />
                    <label className="date-label">Date:</label>
                  </div>
                </div>

                <div className="form-group">
                  <div className="input-wrapper">
                    <span className="input-icon">⏰</span>
                    <input
                      type="date"
                      name="expiry_date"
                      value={formData.expiry_date}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                    />
                    <label className="date-label">Expiry:</label>
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
                      {csvFile ? csvFile.name : 'Choose CSV file...'}
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
                {isLoading ? 'Saving...' : 'Save'}
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

export default AddSample;
