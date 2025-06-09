import { render, screen } from '@testing-library/react';
import App from './App';

test('renders RAG chatbot header', () => {
  render(<App />);
  const linkElement = screen.getByText(/RAG-Enhanced Chatbot/i);
  expect(linkElement).toBeInTheDocument();
});