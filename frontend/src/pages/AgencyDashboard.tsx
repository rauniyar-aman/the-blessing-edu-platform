export default function AgencyDashboard() {
  return (
    <div>
      <h2>Agency Dashboard</h2>
      <div className="grid">
        <div className="card">
          <h3>Students</h3>
          <p>Manage students added by your agency (no portal access).</p>
        </div>
        <div className="card">
          <h3>Applications</h3>
          <p>Create and track applications for your students.</p>
        </div>
        <div className="card">
          <h3>Course Finder</h3>
          <p>Check eligibility and pick programs.</p>
        </div>
        <div className="card">
          <h3>Settings</h3>
          <p>Toggle stage change email notifications.</p>
        </div>
      </div>
    </div>
  );
}
