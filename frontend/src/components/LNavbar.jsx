import React from "react";
import { NavLink } from "react-router-dom";

const LNavbar = () => {
  return (
    <nav className="l-navbar">
      <ul className="nav-list">
        <li>
          <NavLink
            to="/"
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            Home
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/analytics"
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            Analytics
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/upload"
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            Upload
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/review"
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            Review
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/teacher-dashboard"
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            Teacher Dashboard
          </NavLink>
        </li>
      </ul>
    </nav>
  );
};

export default LNavbar;
