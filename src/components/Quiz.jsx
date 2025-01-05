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
      setError(null)
      
      // 先测试API是否正常运行
      const testResponse = await fetch('/api/test')
      if (!testResponse.ok) {
        throw new Error('API test failed')
      }
      const testData = await testResponse.json()
      console.log('API test result:', testData)
      
      // 获取实际题目
      const url = selectedChapter 
        ? `/api/questions/${selectedChapter}`
        : '/api/questions'
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`Failed to fetch questions: ${response.statusText}`)
      }
      const data = await response.json()
      console.log('Questions data:', data)
      
      if (data.error) {
        throw new Error(data.error)
      }
      if (!data.questions || !Array.isArray(data.questions)) {
        throw new Error('Invalid questions data format')
      }
      setQuestions(data.questions)
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