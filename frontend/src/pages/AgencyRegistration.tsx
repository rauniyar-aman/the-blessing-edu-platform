export default function AgencyRegistration() {
  return (
    <div className="card">
      <h2>Agency Registration Request</h2>
      <p>Submit your agency details for admin verification.</p>
      <div className="form-row">
        <label>Agency name</label>
        <input type="text" placeholder="Agency name" />
      </div>
      <div className="form-row">
        <label>Country</label>
        <input type="text" placeholder="Country" />
      </div>
      <div className="form-row">
        <label>Contact name</label>
        <input type="text" placeholder="Contact person" />
      </div>
      <div className="form-row">
        <label>Contact email</label>
        <input type="email" placeholder="contact@agency.com" />
      </div>
      <button type="button">Submit request</button>
    </div>
  );
}
