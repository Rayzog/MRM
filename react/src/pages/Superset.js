import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Superset = () => {
    const [iframeUrl, setIframeUrl] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            navigate('/login');
            return;
        }

        setIframeUrl(`http://localhost:5000/superset-proxy/superset/welcome/`);
    }, [navigate]);

    return (
        <div className="superset-container">
            <nav className="superset-nav">
                <button onClick={() => navigate('/profile')}>Назад в профиль</button>
            </nav>
            <iframe
                title="Superset Dashboard"
                src={iframeUrl}
                width="100%"
                height="800px"
                referrerPolicy="no-referrer"
            />
        </div>
    );
};

export default Superset;