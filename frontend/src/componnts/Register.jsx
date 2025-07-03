import React from 'react'
import { useState } from 'react'
import {Link,useNavigate} from 'react-router-dom'

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
    function handleinp(event){
        const {name,value}= event.target;
        setData({
            ...data,
            [name]: value
        });
    }
    function handlesubmit(event){
        event.preventDefault();
        fetch(`${API_PATH}/register`,{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)

        })
        .then(async (res) => {
            const text = await res.text();
            const data = text ? JSON.parse(text) : {};

            if (res.ok) {
                setMsg({
                    type: 'success',
                    text: data.message || "Registration successful"
                });
                setTimeout(() => {
                    navigate('/');
                }, 2000);
            } 
            else {
                setMsg({
                    type: 'error',
                    text: data.detail || "Registration failed. Please try again."
                    });
                    }
                })
        .catch((error) => {
            setMsg({
                type: 'error',
                text: error.message
            });
        })

    }


  return (
    <div className='main'>
        <form className='form' onSubmit={handlesubmit}>
            <input className='inp' type="text" placeholder="Enter Your Name" name='username' value={data.username} onChange={handleinp} required />
            <input className='inp' type="email" placeholder="Enter Your Email" name='email' value={data.email} onChange={handleinp} required />
            <input className='inp' type="password" placeholder="Enter Password" name='password' value={data.password} onChange={handleinp} required />
            <p className='para'>Alrady have a account please <Link to={'/'}>login</Link></p>
            <button className='btn' type="submit">Register</button>
        </form>
        <h1 className={msg.type}>{msg.text}</h1>
        
    </div>
  )
}

export default Register