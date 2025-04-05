import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Profile from './pages/Profile';
import Superset from './pages/Superset';
import Navbar from './components/Navbar';

function App() {
    useEffect(() => {
        // Глобальная настройка при монтировании компонента
        axios.defaults.withCredentials = true;
        axios.defaults.baseURL = 'http://localhost:5000';
    }, []);
    return (
        <BrowserRouter>
            <Navbar />
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/superset" element={<Superset />} />
                <Route path="*" element={<Login />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;