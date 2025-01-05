import React from 'react'
import { useNavigate } from 'react-router-dom'

function ChapterSelect() {
  const navigate = useNavigate()
  const [chapters, setChapters] = useState([])

  useEffect(() => {
    fetchChapters()
  }, [])

  const fetchChapters = async () => {
    try {
      const response = await fetch('/api/chapters')
      const data = await response.json()
      setChapters(data.chapters)
    } catch (error) {
      console.error('Error fetching chapters:', error)
    }
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