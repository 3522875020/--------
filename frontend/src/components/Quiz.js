import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';

function Quiz() {
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [score, setScore] = useState(0);
  const [wrongQuestions, setWrongQuestions] = useState({});
  const history = useHistory();

  useEffect(() => {
    fetchQuestions();
  }, []);

  const fetchQuestions = async () => {
    const response = await fetch('/api/questions');
    const data = await response.json();
    setQuestions(data.questions);
  };

  const handleAnswer = (answer) => {
    const question = questions[currentQuestion];
    if (answer === question.correct_answer) {
      setScore(score + 1);
    } else {
      setWrongQuestions({
        ...wrongQuestions,
        [question.number]: {
          ...question,
          your_answer: answer
        }
      });
    }

    if (currentQuestion + 1 < questions.length) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      history.push('/result', { score, total: questions.length, wrongQuestions });
    }
  };

  if (questions.length === 0) return <div>Loading...</div>;

  const question = questions[currentQuestion];
  return (
    <div className="quiz">
      <div className="progress">
        Question {currentQuestion + 1}/{questions.length}
      </div>
      <div className="question">
        {question.question}
      </div>
      <div className="options">
        {Object.entries(question.options).map(([key, value]) => (
          <button
            key={key}
            onClick={() => handleAnswer(key)}
            className="option"
          >
            {key}. {value}
          </button>
        ))}
      </div>
    </div>
  );
}

export default Quiz; 