import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

function ChapterSelect() {
  const navigate = useNavigate()
  const [chapters, setChapters] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchChapters()
  }, [])

  const fetchChapters = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/chapters')
      if (!response.ok) {
        throw new Error('Failed to fetch chapters')
      }
      const data = await response.json()
      if (data.error) {
        throw new Error(data.error)
      }
      setChapters(data.chapters)
      setError(null)
    } catch (error) {
      console.error('Error fetching chapters:', error)
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
      <p>加载章节失败: {error}</p>
      <button className="back-button" onClick={() => navigate('/')}>
        返回主菜单
      </button>
    </div>
  }

  const handleChapterSelect = (chapter) => {
    navigate('/quiz', { state: { chapter } })
  }

  return (
    <div className="chapter-select">
      <h2>选择章节</h2>
      <div className="chapter-list">
        <button 
          className="chapter-button"
          onClick={() => handleChapterSelect(null)}
        >
          全部章节
        </button>
        {chapters.map(chapter => (
          <button
            key={chapter}
            className="chapter-button"
            onClick={() => handleChapterSelect(chapter)}
          >
            第{chapter}章
          </button>
        ))}
      </div>
      <button 
        className="back-button"
        onClick={() => navigate('/')}
      >
        返回
      </button>
    </div>
  )
}

export default ChapterSelect 