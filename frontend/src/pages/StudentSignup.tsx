export default function StudentSignup() {
  return (
    <div className="card">
      <h2>Student Signup</h2>
      <p>Create a direct student account for self-managed applications.</p>
      <div className="form-row">
        <label>Full name</label>
        <input type="text" placeholder="Full name" />
      </div>
      <div className="form-row">
        <label>Email</label>
        <input type="email" placeholder="student@example.com" />
      </div>
      <div className="form-row">
        <label>Password</label>
        <input type="password" />
      </div>
      <button type="button">Create account</button>
    </div>
  );
}
