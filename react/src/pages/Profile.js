import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Profile = () => {
    const [userData, setUserData] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const token = localStorage.getItem('access_token');
                const response = await axios.get('/profile', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                setUserData(response.data.user);
            } catch (error) {
                console.error('Profile error:', error);
                navigate('/login');
            }
        };

        fetchProfile();
    }, [navigate]);

    if (!userData) return <div>Loading...</div>;

    return (
        <div className="profile-container">
            <h1>Профиль пользователя</h1>
            <div className="profile-info">
                <p>Логин: {userData.username}</p>
                <p>Email: {userData.email}</p>
                <p>Последняя активность: {new Date(userData.last_active).toLocaleString()}</p>
            </div>
            <button onClick={() => navigate('/superset')}>Перейти к дашбордам</button>
        </div>
    );
};

export default Profile;