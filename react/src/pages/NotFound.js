import { useNavigate } from 'react-router-dom';

const NotFound = () => {
    const navigate = useNavigate();

    return (
        <div className="not-found">
            <h1>404 - Страница не найдена</h1>
            <button onClick={() => navigate('/')}>На главную</button>
        </div>
    );
};

export default NotFound;