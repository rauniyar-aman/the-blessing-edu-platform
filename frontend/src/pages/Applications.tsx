export default function Applications() {
  return (
    <div>
      <h2>Applications</h2>
      <div className="card">
        <h3>Create Application</h3>
        <div className="form-row">
          <label>Program</label>
          <select>
            <option>BSc Computer Science</option>
            <option>MS Data Science</option>
          </select>
        </div>
        <div className="form-row">
          <label>Intake</label>
          <div className="grid">
            <input type="text" placeholder="Month" />
            <input type="number" placeholder="Year" />
          </div>
        </div>
        <button type="button">Create application</button>
      </div>
      <div className="card">
        <h3>Application List</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Program</th>
              <th>Country</th>
              <th>Stage</th>
              <th>Assigned Staff</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>BSc Computer Science</td>
              <td>UK</td>
              <td><span className="badge">Applied</span></td>
              <td>Auto-assigned Staff</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
