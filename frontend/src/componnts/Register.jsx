import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './logres.css';

const Register = () => {
  const API_PATH = import.meta.env.VITE_REACT_API_URL;
  const navigate = useNavigate();

  const [data, setData] = useState({
    username: '',
    email: '',
    password: ''
  });

  const [msg, setMsg] = useState({
    type: '',
    text: ''
  });

  const [isLoading, setIsLoading] = useState(false);

  function handleinp(event) {
    const { name, value } = event.target;
    setData({
      ...data,
      [name]: value
    });
  }

  function handlesubmit(event) {
    event.preventDefault();
    setIsLoading(true);
    setMsg({ type: '', text: '' });

    fetch(`${API_PATH}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
      .then(async (res) => {
        const text = await res.text();
        const responseData = text ? JSON.parse(text) : {};

        if (res.ok) {
          setMsg({
            type: 'success',
            text: responseData.message || 'Registration successful! Redirecting to login...'
          });
          setTimeout(() => {
            navigate('/');
          }, 1500);
        } else {
          setMsg({
            type: 'error',
            text: responseData.detail || 'Registration failed. Please try again.'
          });
        }
      })
      .catch((error) => {
        setMsg({
          type: 'error',
          text: error.message || 'An error occurred. Please try again.'
        });
      })
      .finally(() => {
        setIsLoading(false);
      });
  }

  return (
    <div className="main">
      <div className="auth-container">
        <div className="auth-header">
          <div className="medical-icon">🏥</div>
          <h1>Create Account</h1>
          <p>Join Medical Chat Assistant for personalized healthcare support</p>
        </div>

        <form className="form" onSubmit={handlesubmit}>
          <div className="input-group">
            <input
              id="username"
              className="inp"
              type="text"
              placeholder="Enter your full name"
              name="username"
              value={data.username}
              onChange={handleinp}
              required
              disabled={isLoading}
            />
          </div>

          <div className="input-group">
            <input
              id="email"
              className="inp"
              type="email"
              placeholder="Enter your email address"
              name="email"
              value={data.email}
              onChange={handleinp}
              required
              disabled={isLoading}
            />
          </div>

          <div className="input-group">
            <input
              id="password"
              className="inp"
              type="password"
              placeholder="Create a secure password"
              name="password"
              value={data.password}
              onChange={handleinp}
              required
              disabled={isLoading}
            />
          </div>

          <button 
            className={`btn ${isLoading ? 'loading' : ''}`} 
            type="submit"
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>

          <p className="para">
            Already have an account? <Link to="/">Sign In</Link>
          </p>
        </form>

        {msg.text && (
          <div className={`message ${msg.type}`}>
            {msg.text}
          </div>
        )}
      </div>
    </div>
  );
};

export default Register;