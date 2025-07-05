// components/Navbar.jsx
export default function Navbar() {
  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-6 py-4 flex justify-between items-center">
        <div className="text-xl font-bold text-blue-600">SmartScripts</div>
        <div className="space-x-6 text-gray-700 font-medium">
          <a href="/" className="hover:text-blue-600">Home</a>
          <a href="/login" className="hover:text-blue-600">Login</a>
          <a href="/signup" className="hover:text-blue-600">Signup</a>
        </div>
      </div>
    </nav>
  );
}
