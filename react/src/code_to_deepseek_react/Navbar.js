import { useNavigate } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            await axios.post('/logout');
            localStorage.removeItem('access_token');
            navigate('/login');
        } catch (error) {
            console.error('Logout error:', error);
        }
    };

    return (
        <nav className="main-nav">
            <button onClick={() => navigate('/profile')}>Профиль</button>
            <button onClick={() => navigate('/superset')}>Дашборды</button>
            <button onClick={handleLogout}>Выйти</button>
        </nav>
    );
};

export default Navbar;