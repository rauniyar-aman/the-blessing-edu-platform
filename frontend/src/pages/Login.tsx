export default function Login() {
  return (
    <div>
      <div className="card">
        <h2>Login</h2>
        <p>Use your credentials to access the platform.</p>
        <div className="form-row">
          <label>Email</label>
          <input type="email" placeholder="you@example.com" />
        </div>
        <div className="form-row">
          <label>Password</label>
          <input type="password" placeholder="••••••••" />
        </div>
        <button type="button">Sign in</button>
      </div>
    </div>
  );
}
