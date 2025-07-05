import React from "react";
import { Link } from "react-router-dom"; // If you use react-router

const Header = () => {
  // Example: You can replace this with your auth context or prop for user info
  const user = null; // or user object when logged in

  return (
    <header className="header">
      <nav className="navbar">
        <div className="navbar-logo">
          <Link to="/">SmartScripts</Link>
        </div>
        <ul className="navbar-links">
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/analytics">Analytics</Link>
          </li>
          <li>
            <Link to="/upload">Upload</Link>
          </li>
          <li>
            <Link to="/review">Review</Link>
          </li>
        </ul>
        <div className="navbar-user">
          {user ? (
            <>
              <span>Welcome, {user.name}</span>
              <button onClick={() => {/* handle logout */}}>Logout</button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link> | <Link to="/register">Register</Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Header;
