import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Login = () => {
  const API_PATH = import.meta.env.VITE_REACT_API_URL;
  const navigate = useNavigate();

  const [data, setData] = useState({
    email: '',
    password: '',
  });

  const [msg, setMsg] = useState({
    type: '',
    text: '',
  });

  function handleinp(event) {
    const { name, value } = event.target;
    setData({
      ...data,
      [name]: value,
    });
  }

  function handlesubmit(event) {
    event.preventDefault();

    fetch(`${API_PATH}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
      .then(async (res) => {
        const text = await res.text();
        const responseData = text ? JSON.parse(text) : {};

        if (res.ok) {
          setMsg({
            type: 'success',
            text: responseData.message || 'Login successful!',
          });

          // Save token to localStorage
          if (responseData.token) {
            localStorage.setItem('token', responseData.token);
          }

          setTimeout(() => {
            navigate('/chat'); 
          }, 2000);
        } else {
          setMsg({
            type: 'error',
            text: responseData.detail || 'Login failed. Please try again.',
          });
        }
      })
      .catch((error) => {
        setMsg({
          type: 'error',
          text: error.message || 'An error occurred. Please try again.',
        });
      });
  }

  return (
    <div className="main">
      <form className="form" onSubmit={handlesubmit}>
        <input
          className="inp"
          type="email"
          placeholder="Enter Your Email"
          name="email"
          value={data.email}
          onChange={handleinp}
          required
        />
        <input
          className="inp"
          type="password"
          placeholder="Enter Password"
          name="password"
          value={data.password}
          onChange={handleinp}
          required
        />
        <p className="para">
          Don't have an account? Please <Link to="/register">Register</Link>
        </p>
        <button className="btn" type="submit">
          Login
        </button>
      </form>
      <h1 className={msg.type}>{msg.text}</h1>
    </div>
  );
};

export default Login;
