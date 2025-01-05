import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import rehypeRaw from 'rehype-raw'
import remarkGfm from 'remark-gfm'

function Quiz() {
  const [questions, setQuestions] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [score, setScore] = useState(0)
  const [wrongQuestions, setWrongQuestions] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAnswer, setShowAnswer] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const selectedChapter = location.state?.chapter
  const isWrongQuestionMode = location.pathname === '/wrong-questions'

  useEffect(() => {
    fetchQuestions()
  }, [selectedChapter])

  const fetchQuestions = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const url = selectedChapter 
        ? `/api/questions/${selectedChapter}`
        : '/api/questions'
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`Failed to fetch questions: ${response.statusText}`)
      }
      const data = await response.json()
      
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

  const handleAnswer = (answer) => {
    const question = questions[currentQuestion]
    const isCorrect = answer === question.correct_answer

    if (isCorrect) {
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

    question.your_answer = answer
    
    setShowAnswer(true)
  }

  const goToNextQuestion = () => {
    setShowAnswer(false)
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

  const renderMarkdown = (text) => {
    return (
      <ReactMarkdown
        rehypePlugins={[rehypeRaw]}
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({node, ...props}) => <p className="markdown-p" {...props} />,
          img: ({node, ...props}) => (
            <img 
              className="markdown-img" 
              loading="lazy" 
              {...props} 
              style={{maxWidth: '100%', height: 'auto'}}
            />
          ),
          table: ({node, ...props}) => (
            <div className="table-container">
              <table className="markdown-table" {...props} />
            </div>
          )
        }}
      >
        {text}
      </ReactMarkdown>
    )
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

  const question = questions[currentQuestion]
  return (
    <div className="quiz">
      <div className="progress">
        第 {currentQuestion + 1}/{questions.length} 题
      </div>
      <div className="question">
        {renderMarkdown(question.question)}
      </div>
      <div className="options">
        {Object.entries(question.options).map(([key, value]) => (
          <button
            key={key}
            onClick={() => !showAnswer && handleAnswer(key)}
            className={`option ${
              showAnswer ? 
                key === question.correct_answer ? 
                  'correct' : 
                  'wrong' 
                : ''
            }`}
            disabled={showAnswer}
          >
            {key}. {renderMarkdown(value)}
          </button>
        ))}
      </div>
      {showAnswer && (
        <div className="answer-section">
          <div className={`answer-result ${
            question.your_answer === question.correct_answer ? 
              'correct' : 
              'wrong'
          }`}>
            {question.your_answer === question.correct_answer ? 
              '✓ 回答正确！' : 
              `✗ 回答错误。正确答案是：${question.correct_answer}`
            }
          </div>
          <button 
            className="next-button"
            onClick={goToNextQuestion}
          >
            下一题
          </button>
        </div>
      )}
    </div>
  )
}

export default Quiz 