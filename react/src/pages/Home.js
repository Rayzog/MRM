import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Home = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    return (
        <div className="home-container">
            <h1>Добро пожаловать{user ? `, ${user.username}` : ''}!</h1>
            {!user && (
                <button onClick={() => navigate('/login')}>Войти в систему</button>
            )}
        </div>
    );
};

export default Home;