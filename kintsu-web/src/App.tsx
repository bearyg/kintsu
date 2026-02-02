import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import AssetGuard from './pages/AssetGuard';
import Kintsu from './pages/Kintsu';
import Privacy from './pages/Privacy';
import Terms from './pages/Terms';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="asset-guard" element={<AssetGuard />} />
          <Route path="kintsu" element={<Kintsu />} />
          <Route path="privacy" element={<Privacy />} />
          <Route path="terms" element={<Terms />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
