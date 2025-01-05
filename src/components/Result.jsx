import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

function Result() {
  const location = useLocation()
  const navigate = useNavigate()
  const { score, total, wrongQuestions } = location.state || {}

  if (!score) {
    return <div>No result data available</div>
  }

  return (
    <div className="result">
      <h2>测验完成！</h2>
      <div className="score">
        得分：{score}/{total}
      </div>
      {Object.keys(wrongQuestions).length > 0 && (
        <div className="wrong-questions">
          <h3>错题回顾：</h3>
          {Object.entries(wrongQuestions).map(([num, q]) => (
            <div key={num} className="wrong-question">
              <p>第{q.chapter}章 第{num}题: {q.question}</p>
              <div className="options">
                {Object.entries(q.options).map(([key, value]) => (
                  <div key={key} className="option">
                    {key}. {value}
                  </div>
                ))}
              </div>
              <p>正确答案：{q.correct_answer}</p>
              <p>你的答案：{q.your_answer}</p>
            </div>
          ))}
        </div>
      )}
      <button onClick={() => navigate('/')}>返回主菜单</button>
    </div>
  )
}

export default Result 