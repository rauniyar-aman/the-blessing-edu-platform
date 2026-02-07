export default function AdminDashboard() {
  return (
    <div>
      <h2>Admin & Staff Dashboard</h2>
      <div className="grid">
        <div className="card">
          <h3>Agency Verification</h3>
          <p>Review and approve incoming agency registration requests.</p>
        </div>
        <div className="card">
          <h3>Pipelines (UK/USA)</h3>
          <p>Edit country-based application pipelines and stages.</p>
        </div>
        <div className="card">
          <h3>Auto Assignment Rules</h3>
          <p>Configure assignment by university, country, or default staff.</p>
        </div>
        <div className="card">
          <h3>Tasks Dashboard</h3>
          <p>Monitor default and manual task checklists.</p>
        </div>
      </div>
      <div className="card">
        <h3>Applications Overview</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Program</th>
              <th>Stage</th>
              <th>Assigned Staff</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Direct Student</td>
              <td>BSc Computer Science</td>
              <td><span className="badge">Applied</span></td>
              <td>Staff Member</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
