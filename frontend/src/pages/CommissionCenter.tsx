export default function CommissionCenter() {
  return (
    <div>
      <h2>Commission Center</h2>
      <div className="card">
        <h3>Commission Structure (Owner/Manager only)</h3>
        <p>Search university commission structures when enabled by admin.</p>
        <table className="table">
          <thead>
            <tr>
              <th>University</th>
              <th>Country</th>
              <th>Level</th>
              <th>Commission %</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>London Global University</td>
              <td>UK</td>
              <td>UG</td>
              <td>12%</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div className="card">
        <h3>Commission Earned</h3>
        <p>Records are created only when commission is received from universities.</p>
        <table className="table">
          <thead>
            <tr>
              <th>Application</th>
              <th>Amount</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>MS Data Science</td>
              <td>USD 2,500</td>
              <td><span className="badge">Received</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
