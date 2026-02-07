export default function StudentDashboard() {
  return (
    <div>
      <h2>Student Dashboard</h2>
      <div className="grid">
        <div className="card">
          <h3>My Applications</h3>
          <p>Track your current stage and tasks.</p>
        </div>
        <div className="card">
          <h3>Documents</h3>
          <p>Upload and attach document versions to applications.</p>
        </div>
        <div className="card">
          <h3>Course Finder</h3>
          <p>Run eligibility checks and explore programs.</p>
        </div>
      </div>
    </div>
  );
}
