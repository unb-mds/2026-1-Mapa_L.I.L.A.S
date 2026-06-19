import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Inicio from './pages/Inicio';
import ProjetosLei from './pages/ProjetosLei';
import PLDetalhado from './pages/PLDetalhado';
import Graficos from './pages/Graficos';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/projetos" element={<ProjetosLei />} />
        <Route path="/projetos/:casa/:numero/:ano" element={<PLDetalhado />} />
        <Route path="/graficos" element={<Graficos />} />
      </Routes>
    </BrowserRouter>
  );
}