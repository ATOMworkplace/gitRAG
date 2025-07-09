import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Login from "./pages/Login";
import Home from "./pages/Home";
import Ai from "./pages/Ai";
import Repo from "./pages/Repo";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/home" element={<Home />} />
          <Route path="/ai" element={<Ai />} />
          <Route path="/repo" element={<Repo />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;