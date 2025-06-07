import React, { useState, useEffect } from 'react';

function IncidentReport({ report, loading, onUpdate }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedReport, setEditedReport] = useState({});

  useEffect(() => {
    setEditedReport(report || {});
  }, [report]);

  const formatDateTime = (dateTime) => {
    try {
      const date = new Date(dateTime);
      return date.toLocaleString();
    } catch {
      return dateTime;
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
    setEditedReport({...report});
  };

  const handleSave = () => {
    if (onUpdate) {
      onUpdate(editedReport);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedReport(report);
    setIsEditing(false);
  };

  const handleFieldChange = (field, value) => {
    setEditedReport(prev => ({
      ...prev,
      [field]: value
    }));
  };


  const downloadReport = () => {
    const reportText = JSON.stringify(isEditing ? editedReport : report, null, 2);
    const blob = new Blob([reportText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `incident_report_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (!report) {
    return <div className="loading">Loading report...</div>;
  }

  return (
    <div className={`incident-report ${isEditing ? 'edit-mode' : ''}`}>
      <div className="report-header">
        <h2>Incident Report</h2>
        <div className="report-actions">
          {!isEditing ? (
            <>
              <button onClick={handleEdit} className="btn btn-secondary">
                ✏️ Edit Report
              </button>
              <button onClick={downloadReport} className="btn btn-secondary">
                Download Report
              </button>
            </>
          ) : (
            <>
              <button onClick={handleSave} className="btn btn-primary">
                💾 Save Changes
              </button>
              <button onClick={handleCancel} className="btn btn-secondary">
                Cancel
              </button>
            </>
          )}
        </div>
      </div>


      <div className="report-content">
        <div className="report-section">
          <h3>Incident Details</h3>
          <div className="report-grid">
            <div className="report-field">
              <label>Date & Time:</label>
              {isEditing ? (
                <input
                  type="datetime-local"
                  value={editedReport.date_time?.slice(0, 16) || ''}
                  onChange={(e) => handleFieldChange('date_time', e.target.value)}
                  className="edit-input"
                />
              ) : (
                <span>{formatDateTime(report.date_time)}</span>
              )}
            </div>
            <div className="report-field">
              <label>Service User:</label>
              {isEditing ? (
                <input
                  type="text"
                  value={editedReport.service_user_name || ''}
                  onChange={(e) => handleFieldChange('service_user_name', e.target.value)}
                  className="edit-input"
                  placeholder="Enter service user name"
                />
              ) : (
                <span>{report.service_user_name}</span>
              )}
            </div>
            <div className="report-field">
              <label>Location:</label>
              {isEditing ? (
                <input
                  type="text"
                  value={editedReport.location || ''}
                  onChange={(e) => handleFieldChange('location', e.target.value)}
                  className="edit-input"
                  placeholder="Enter location"
                />
              ) : (
                <span>{report.location}</span>
              )}
            </div>
            <div className="report-field">
              <label>Incident Type:</label>
              {isEditing ? (
                <input
                  type="text"
                  value={editedReport.incident_type || ''}
                  onChange={(e) => handleFieldChange('incident_type', e.target.value)}
                  className="edit-input"
                  placeholder="e.g., Fall, Medical Emergency"
                />
              ) : (
                <span className="incident-type">{report.incident_type}</span>
              )}
            </div>
          </div>
        </div>

        <div className="report-section">
          <h3>Description</h3>
          {isEditing ? (
            <textarea
              value={editedReport.description || ''}
              onChange={(e) => handleFieldChange('description', e.target.value)}
              className="edit-textarea"
              rows={4}
              placeholder="Describe the incident in detail..."
            />
          ) : (
            <p className="description">{report.description}</p>
          )}
        </div>

        <div className="report-section">
          <h3>Response Details</h3>
          <div className="report-field">
            <label>Immediate Actions Taken:</label>
            {isEditing ? (
              <textarea
                value={editedReport.immediate_actions || ''}
                onChange={(e) => handleFieldChange('immediate_actions', e.target.value)}
                className="edit-textarea"
                rows={2}
                placeholder="Describe actions taken..."
              />
            ) : (
              <p>{report.immediate_actions}</p>
            )}
          </div>
          <div className="report-grid">
            <div className="report-field">
              <label>First Aid Administered:</label>
              {isEditing ? (
                <select
                  value={editedReport.first_aid_administered ? 'yes' : 'no'}
                  onChange={(e) => handleFieldChange('first_aid_administered', e.target.value === 'yes')}
                  className="edit-select"
                >
                  <option value="no">No</option>
                  <option value="yes">Yes</option>
                </select>
              ) : (
                <span className={`boolean-value ${report.first_aid_administered ? 'yes' : 'no'}`}>
                  {report.first_aid_administered ? 'Yes' : 'No'}
                </span>
              )}
            </div>
            <div className="report-field">
              <label>Emergency Services Contacted:</label>
              {isEditing ? (
                <select
                  value={editedReport.emergency_services_contacted ? 'yes' : 'no'}
                  onChange={(e) => handleFieldChange('emergency_services_contacted', e.target.value === 'yes')}
                  className="edit-select"
                >
                  <option value="no">No</option>
                  <option value="yes">Yes</option>
                </select>
              ) : (
                <span className={`boolean-value ${report.emergency_services_contacted ? 'yes' : 'no'}`}>
                  {report.emergency_services_contacted ? 'Yes' : 'No'}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="report-section">
          <h3>Notifications & Follow-up</h3>
          <div className="report-field">
            <label>Who Was Notified:</label>
            {isEditing ? (
              <input
                type="text"
                value={editedReport.who_was_notified || ''}
                onChange={(e) => handleFieldChange('who_was_notified', e.target.value)}
                className="edit-input"
                placeholder="e.g., Supervisor, Family"
              />
            ) : (
              <p>{report.who_was_notified || 'N/A'}</p>
            )}
          </div>
          <div className="report-field">
            <label>Witnesses:</label>
            {isEditing ? (
              <input
                type="text"
                value={editedReport.witnesses || ''}
                onChange={(e) => handleFieldChange('witnesses', e.target.value)}
                className="edit-input"
                placeholder="Names of witnesses or 'None'"
              />
            ) : (
              <p>{report.witnesses || 'None'}</p>
            )}
          </div>
          <div className="report-field">
            <label>Agreed Next Steps:</label>
            {isEditing ? (
              <textarea
                value={editedReport.agreed_next_steps || ''}
                onChange={(e) => handleFieldChange('agreed_next_steps', e.target.value)}
                className="edit-textarea"
                rows={2}
                placeholder="Describe follow-up actions..."
              />
            ) : (
              <p className="next-steps">{report.agreed_next_steps}</p>
            )}
          </div>
        </div>

        {(report.risk_assessment_needed || (isEditing && editedReport.risk_assessment_needed)) && (
          <div className="report-section risk-assessment">
            <h3>Risk Assessment Required</h3>
            {isEditing ? (
              <div>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={editedReport.risk_assessment_needed || false}
                    onChange={(e) => handleFieldChange('risk_assessment_needed', e.target.checked)}
                  />
                  Risk Assessment Needed
                </label>
                <input
                  type="text"
                  value={editedReport.risk_assessment_type || ''}
                  onChange={(e) => handleFieldChange('risk_assessment_type', e.target.value)}
                  className="edit-input"
                  placeholder="Type of risk assessment needed"
                  style={{ marginTop: '0.5rem' }}
                />
              </div>
            ) : (
              <div className="alert alert-warning">
                <strong>Type:</strong> {report.risk_assessment_type}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default IncidentReport;
