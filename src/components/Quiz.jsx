import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

function Quiz() {
  const [questions, setQuestions] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [score, setScore] = useState(0)
  const [wrongQuestions, setWrongQuestions] = useState({})
  const navigate = useNavigate()

  useEffect(() => {
    fetchQuestions()
  }, [])

  const fetchQuestions = async () => {
    try {
      const response = await fetch('/api/questions')
      const data = await response.json()
      setQuestions(data.questions)
    } catch (error) {
      console.error('Error fetching questions:', error)
    }
  }

  const handleAnswer = (answer) => {
    const question = questions[currentQuestion]
    if (answer === question.correct_answer) {
      setScore(score + 1)
    } else {
      setWrongQuestions({
        ...wrongQuestions,
        [question.number]: {
          ...question,
          your_answer: answer
        }
      })
    }

    if (currentQuestion + 1 < questions.length) {
      setCurrentQuestion(currentQuestion + 1)
    } else {
      navigate('/result', { 
        state: { 
          score, 
          total: questions.length, 
          wrongQuestions 
        } 
      })
    }
  }

  if (questions.length === 0) {
    return <div>Loading...</div>
  }

  const question = questions[currentQuestion]
  return (
    <div className="quiz">
      <div className="progress">
        第 {currentQuestion + 1}/{questions.length} 题
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
  )
}

export default Quiz 