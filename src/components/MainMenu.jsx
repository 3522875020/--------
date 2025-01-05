import React from 'react'
import { useNavigate } from 'react-router-dom'

function MainMenu() {
  const navigate = useNavigate()

  return (
    <div className="main-menu">
      <h1>园林植物景观设计测验</h1>
      <div className="menu-buttons">
        <button onClick={() => navigate('/chapters')}>开始新测验</button>
        <button onClick={() => navigate('/wrong-questions')}>练习错题</button>
        <button onClick={() => navigate('/history')}>历史记录</button>
      </div>
    </div>
  )
}

export default MainMenu 