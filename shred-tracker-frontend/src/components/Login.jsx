import React, { useState } from 'react';
import axios from 'axios';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            // 注意：这里用的是我们在 vite.config.js 配置的 /api 代理
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await axios.post('/api/auth/login', formData);
            
            // 核心点：将 Token 存入本地，后续所有请求都要用到
            const token = response.data.access_token;
            localStorage.setItem('token', token);
            
            alert('登录成功！');
            // 这里后续可以加上页面跳转逻辑
        } catch (error) {
            alert('登录失败：' + (error.response?.data?.detail || '网络错误'));
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <form onSubmit={handleLogin} className="p-8 bg-white shadow-lg rounded-lg w-96">
                <h2 className="text-2xl font-bold mb-6 text-center text-blue-600">Shred Tracker 登录</h2>
                <input 
                    type="text" 
                    placeholder="用户名" 
                    className="w-full p-2 mb-4 border rounded"
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input 
                    type="password" 
                    placeholder="密码" 
                    className="w-full p-2 mb-6 border rounded"
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600">
                    登 录
                </button>
            </form>
        </div>
    );
};

export default Login;