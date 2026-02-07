import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { label: "Login", to: "/" },
  { label: "Student Signup", to: "/student-signup" },
  { label: "Agency Registration", to: "/agency-registration" },
  { label: "Admin", to: "/admin" },
  { label: "Agency", to: "/agency" },
  { label: "Student", to: "/student" },
  { label: "Applications", to: "/applications" },
  { label: "Course Finder", to: "/course-finder" },
  { label: "Commissions", to: "/commissions" }
];

export default function Layout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>The Blessing Edu</h1>
        <nav>
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? "active" : "")}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
