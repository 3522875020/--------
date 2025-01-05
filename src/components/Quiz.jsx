import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

function Quiz() {
  const [questions, setQuestions] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [score, setScore] = useState(0)
  const [wrongQuestions, setWrongQuestions] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()
  const location = useLocation()
  const selectedChapter = location.state?.chapter

  useEffect(() => {
    fetchQuestions()
  }, [selectedChapter])

  const fetchQuestions = async () => {
    try {
      setLoading(true)
      const url = selectedChapter 
        ? `/api/questions/${selectedChapter}`
        : '/api/questions'
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error('Failed to fetch questions')
      }
      const data = await response.json()
      if (data.error) {
        throw new Error(data.error)
      }
      setQuestions(data.questions)
      setError(null)
    } catch (error) {
      console.error('Error fetching questions:', error)
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">加载中...</div>
  }

  if (error) {
    return <div className="error">
      <p>加载题目失败: {error}</p>
      <button className="back-button" onClick={() => navigate('/')}>
        返回主菜单
      </button>
    </div>
  }

  if (questions.length === 0) {
    return <div className="error">
      <p>没有找到题目</p>
      <button className="back-button" onClick={() => navigate('/')}>
        返回主菜单
      </button>
    </div>
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