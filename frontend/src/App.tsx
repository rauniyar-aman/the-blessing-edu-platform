import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import AdminDashboard from "./pages/AdminDashboard";
import AgencyDashboard from "./pages/AgencyDashboard";
import StudentDashboard from "./pages/StudentDashboard";
import Login from "./pages/Login";
import StudentSignup from "./pages/StudentSignup";
import AgencyRegistration from "./pages/AgencyRegistration";
import Applications from "./pages/Applications";
import CourseFinder from "./pages/CourseFinder";
import CommissionCenter from "./pages/CommissionCenter";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Login />} />
        <Route path="student-signup" element={<StudentSignup />} />
        <Route path="agency-registration" element={<AgencyRegistration />} />
        <Route path="admin" element={<AdminDashboard />} />
        <Route path="agency" element={<AgencyDashboard />} />
        <Route path="student" element={<StudentDashboard />} />
        <Route path="applications" element={<Applications />} />
        <Route path="course-finder" element={<CourseFinder />} />
        <Route path="commissions" element={<CommissionCenter />} />
      </Route>
    </Routes>
  );
}
