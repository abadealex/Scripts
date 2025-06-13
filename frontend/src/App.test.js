import React from 'react'; // Ensure React is in scope for JSX
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom'; // For toBeInTheDocument()
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
