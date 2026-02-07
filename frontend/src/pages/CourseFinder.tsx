export default function CourseFinder() {
  return (
    <div>
      <h2>Course Finder & Eligibility</h2>
      <div className="grid">
        <div className="card">
          <h3>Agency Eligibility</h3>
          <div className="form-row">
            <label>Select Student</label>
            <select>
              <option>Jane Doe (jane@example.com)</option>
              <option>John Smith (john@example.com)</option>
            </select>
          </div>
          <div className="form-row">
            <label>GPA</label>
            <input type="number" placeholder="3.0" />
          </div>
          <div className="form-row">
            <label>English Score (overall)</label>
            <input type="number" placeholder="6.5" />
          </div>
          <div className="form-row">
            <label>GRE (optional)</label>
            <input type="number" placeholder="Optional" />
          </div>
          <button type="button">Check eligibility</button>
        </div>
        <div className="card">
          <h3>Direct Student Eligibility</h3>
          <div className="form-row">
            <label>GPA</label>
            <input type="number" placeholder="3.0" />
          </div>
          <div className="form-row">
            <label>English Score (overall)</label>
            <input type="number" placeholder="6.5" />
          </div>
          <div className="form-row">
            <label>SAT (optional)</label>
            <input type="number" placeholder="Optional" />
          </div>
          <button type="button">Check eligibility</button>
        </div>
      </div>
      <div className="card">
        <h3>Results</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Program</th>
              <th>University</th>
              <th>Eligibility</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>MS Data Science</td>
              <td>California Tech College</td>
              <td><span className="badge">Eligible</span></td>
            </tr>
            <tr>
              <td>BSc Computer Science</td>
              <td>London Global University</td>
              <td><span className="badge">Borderline</span></td>
            </tr>
            <tr>
              <td>BA Business</td>
              <td>London Global University</td>
              <td><span className="badge">Not Eligible</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
