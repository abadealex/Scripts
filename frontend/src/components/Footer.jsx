// components/Footer.jsx
export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300 py-8 px-6 text-center text-sm">
      <div className="container mx-auto flex flex-col md:flex-row justify-center space-x-6">
        <a href="/about" className="hover:text-white">About</a>
        <a href="/docs" className="hover:text-white">Docs</a>
        <a href="/privacy" className="hover:text-white">Privacy</a>
        <a href="https://github.com/yourrepo" target="_blank" rel="noreferrer" className="hover:text-white">GitHub</a>
      </div>
      <p className="mt-4">&copy; {new Date().getFullYear()} SmartScripts</p>
    </footer>
  );
}
