import React, { useState, useEffect } from 'react';
import { getPrompts, createTestResult } from '../../services/api';

function ManualTestingInterface() {
  const [category, setCategory] = useState('');
  const [challenge, setChallenge] = useState('');
  const [prompts, setPrompts] = useState([]);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [response, setResponse] = useState('');
  const [modelName, setModelName] = useState('');
  const [success, setSuccess] = useState(true);
  const [notes, setNotes] = useState('');

  useEffect(() => {
    async function fetchPrompts() {
      if (category || challenge) {
        try {
          const fetchedPrompts = await getPrompts({ category, challenge });
          setPrompts(fetchedPrompts);
        } catch (error) {
          alert(`Error fetching prompts: ${error.message}`);
        }
      }
    }
    fetchPrompts();
  }, [category, challenge]);

  const handleCopyPrompt = (prompt) => {
    navigator.clipboard.writeText(prompt.prompt_text);
    setSelectedPrompt(prompt);
  };

  const handleSubmit = async () => {
    if (!selectedPrompt) {
      alert('Please select a prompt first.');
      return;
    }

    const resultData = {
      prompt_id: selectedPrompt.prompt_id,
      model_name: modelName,
      response: response,
      success: success,
      notes: notes,
      category: selectedPrompt.category,
      challenge_id: selectedPrompt.challenge_id,
      timestamp: new Date().toISOString(),
    };

    try {
      await createTestResult(resultData);
      alert('Result submitted successfully!');
      // Optionally clear the form
      setResponse('');
      setModelName('');
      setSuccess(true);
      setNotes('');
      setSelectedPrompt(null);
    } catch (error) {
      alert(`Error submitting result: ${error.message}`);
    }
  };

  return (
    <div>
      <h2>Manual Prompt Testing</h2>

      <div>
        <label htmlFor="category">Category:</label>
        <input
          type="text"
          id="category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        />
      </div>

      <div>
        <label htmlFor="challenge">Challenge:</label>
        <input
          type="text"
          id="challenge"
          value={challenge}
          onChange={(e) => setChallenge(e.target.value)}
        />
      </div>

      <h3>Prompts:</h3>
      <ul>
        {prompts.map((prompt) => (
          <li key={prompt.prompt_id}>
            {prompt.prompt_text}
            <button onClick={() => handleCopyPrompt(prompt)}>Copy</button>
          </li>
        ))}
      </ul>

      <h3>Response:</h3>
      {selectedPrompt && (
        <div>
          <p>
            <strong>Prompt:</strong> {selectedPrompt.prompt_text}
          </p>
          <p>
            <strong>Category:</strong> {selectedPrompt.category}
          </p>
          <p>
            <strong>Challenge:</strong> {selectedPrompt.challenge_id}
          </p>
        </div>
      )}

      <div>
        <label htmlFor="response">Response:</label>
        <textarea
          id="response"
          value={response}
          onChange={(e) => setResponse(e.target.value)}
        />
      </div>

      <div>
        <label htmlFor="modelName">Model Name:</label>
        <input
          type="text"
          id="modelName"
          value={modelName}
          onChange={(e) => setModelName(e.target.value)}
        />
      </div>

      <div>
        <label>Success:</label>
        <input
          type="radio"
          id="success-true"
          name="success"
          value="true"
          checked={success}
          onChange={() => setSuccess(true)}
        />
        <label htmlFor="success-true">True</label>

        <input
          type="radio"
          id="success-false"
          name="success"
          value="false"
          checked={!success}
          onChange={() => setSuccess(false)}
        />
        <label htmlFor="success-false">False</label>
      </div>

      <div>
        <label htmlFor="notes">Notes:</label>
        <textarea
          id="notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>

      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}

export default ManualTestingInterface;