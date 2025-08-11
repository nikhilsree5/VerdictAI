import React, { useState } from 'react';

function Verdict({ type }) {
  const [text, setText] = useState(''); //  State for storing the text input
  const [file, setFile] = useState(null); //  State for storing the file input
  const [result, setResult] = useState(null); //  State for storing the result of the analysis
  const [loading, setLoading] = useState(false); //  State for loading animation



  const handleAnalyze = async () => {
    setLoading(true); //  loading animation
    let response;

    try {
      if (type === 'sms') {
        response = await fetch('http://localhost:5000/api/analyze_sms', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });
      } else {
        const formData = new FormData();
        formData.append('file', file);
        response = await fetch('http://localhost:5000/api/analyze_document', {
          method: 'POST',
          body: formData
        });
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error analyzing:', error);
    } finally {
      setLoading(false); //Stop loading
    }
  };
  return (
    <div className="container">
      <h1>VerdictAI</h1>
      {type === 'sms' ? (
        <textarea
          rows="6"
          placeholder="Enter SMS text..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
      ) : (
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      )}
      <button onClick={handleAnalyze}>Analyze</button>

      {loading && <p className="loading">🔄 Loading...</p>} {/* 👈 Loading animation */}

      {result && !loading && (
        <div className="result">
          <h2>Major Emotion: {result.Predicted_Sentiment} - {result.cd}%</h2>
            <ul>
                {result.emotions.map(({ emotion, prob }) => (
                <li key={emotion}>
                     {emotion}: {prob}%
                </li>
                ))}
            </ul>




        </div>
      )}
    </div>
  );
}

export default Verdict;