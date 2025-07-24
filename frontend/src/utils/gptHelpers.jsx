// gptHelpers.js
// Helpers for GPT prompt generation and interaction

const OPENAI_API_KEY = process.env.REACT_APP_OPENAI_API_KEY || '';

export async function fetchGPTResponse(prompt) {
  if (!OPENAI_API_KEY) {
    throw new Error('OpenAI API key not configured');
  }

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: 'gpt-4',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7,
    }),
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.error?.message || 'GPT API request failed');
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

// Create a prompt to explain why an answer is incorrect
export function createExplainIncorrectPrompt(answer, rubric) {
  return `Explain why the following answer is incorrect based on this rubric:\n\nAnswer: ${answer}\nRubric: ${JSON.stringify(rubric, null, 2)}`;
}
