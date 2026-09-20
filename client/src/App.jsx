import { useState, useEffect } from 'react'

function App() {
  const [movies, setMovies] = useState([])
  const [newMovieTitle, setNewMovieTitle] = useState("") 
  
  // State cho Form Đánh giá
  const [userId, setUserId] = useState("")
  const [movieId, setMovieId] = useState("")
  const [rating, setRating] = useState(5) // Mặc định 5 sao

  const fetchMovies = async () => {
    try {
      const response = await fetch('http://localhost:8000/movies')
      const data = await response.json()
      setMovies(data)
    } catch (error) {
      console.error("Lỗi:", error)
    }
  }

  useEffect(() => {
    fetchMovies()
  }, [])

  const handleAddMovie = async (e) => {
    e.preventDefault()
    if (!newMovieTitle.trim()) return

    try {
      const response = await fetch('http://localhost:8000/movies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newMovieTitle }), 
      })
      if (response.ok) {
        setNewMovieTitle("")
        fetchMovies()
      }
    } catch (error) {
      console.error("Lỗi thêm phim:", error)
    }
  }

  // Hàm xử lý gửi Đánh giá
  const handleRateMovie = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('http://localhost:8000/ratings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_id: parseInt(userId),   // Ép kiểu về số nguyên cho khớp Pydantic schema
          movie_id: parseInt(movieId), 
          rating: parseInt(rating) 
        }), 
      })
      
      if (response.ok) {
        alert("Đánh giá thành công! Dữ liệu đã vào PostgreSQL.")
        setUserId("")
        setMovieId("")
      } else {
        const errorData = await response.json()
        alert(`Lỗi: ${errorData.detail}`)
      }
    } catch (error) {
      console.error("Lỗi đánh giá:", error)
    }
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🎬 Hệ Thống Gợi Ý Phim</h1>

      <div style={{ display: 'flex', gap: '40px', marginBottom: '30px' }}>
        {/* CỘT 1: THÊM PHIM */}
        <div style={{ flex: 1, padding: '15px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <h3>➕ Thêm Phim Mới</h3>
          <form onSubmit={handleAddMovie} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <input 
              type="text" 
              value={newMovieTitle} 
              onChange={(e) => setNewMovieTitle(e.target.value)} 
              placeholder="Tên phim..." 
              style={{ padding: '8px' }}
            />
            <button type="submit" style={{ padding: '8px', cursor: 'pointer' }}>Lưu Phim</button>
          </form>
        </div>

        {/* CỘT 2: ĐÁNH GIÁ PHIM */}
        <div style={{ flex: 1, padding: '15px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <h3>⭐ Gửi Đánh Giá</h3>
          <form onSubmit={handleRateMovie} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <input 
              type="number" 
              value={userId} 
              onChange={(e) => setUserId(e.target.value)} 
              placeholder="User ID (VD: 1)" 
              required
              style={{ padding: '8px' }}
            />
            <input 
              type="number" 
              value={movieId} 
              onChange={(e) => setMovieId(e.target.value)} 
              placeholder="Movie ID (VD: 5)" 
              required
              style={{ padding: '8px' }}
            />
            <select 
              value={rating} 
              onChange={(e) => setRating(e.target.value)}
              style={{ padding: '8px' }}
            >
              {[1, 2, 3, 4, 5].map(num => (
                <option key={num} value={num}>{num} Sao</option>
              ))}
            </select>
            <button type="submit" style={{ padding: '8px', cursor: 'pointer' }}>Gửi Rating</button>
          </form>
        </div>
      </div>
      
      {/* DANH SÁCH PHIM */}
      <h3>📋 Kho Phim Hiện Tại</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {movies.map((movie) => (
          <li key={movie.id} style={{ padding: '10px', borderBottom: '1px solid #eee' }}>
            <strong>{movie.title}</strong> <span style={{ color: 'gray' }}>(ID: {movie.id})</span>
          </li>
        ))}
      </ul>
      {movies.length === 0 && <p>Chưa có phim nào trong Database...</p>}
    </div>
  )
}

export default App