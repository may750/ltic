import { useEffect, useState } from "react";
import { api, clearToken, getToken, login } from "./api";
import "./App.css";
import DashboardStagiaire from "./DashboardStagiaire";
import DashboardEncadrant from "./DashboardEncadrant";

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getToken()));

  // Au démarrage : si un token existe, on demande « qui suis-je ? »
  useEffect(() => {
    if (!getToken()) return;
    api("/auth/me/")
      .then((r) => (r.ok ? r.json() : null))
      .then(setUser)
      .finally(() => setLoading(false));
  }, []);

  function deconnecter() {
    clearToken();
    setUser(null);
  }

  if (loading) return <p className="centre">Chargement...</p>;
  if (!user) return <Connexion onConnecte={setUser} />;
  if (user.role === "STAGIAIRE") {
    return <DashboardStagiaire user={user} onDeconnecter={deconnecter} />;
  }
    if (user.role === "ENCADRANT") {
    return <DashboardEncadrant user={user} onDeconnecter={deconnecter} />;
  }
  return (
    <div className="carte">
      <h1>LTIC</h1>
      <p>
        Bonjour <strong>{user.username}</strong>
      </p>
      <p>Votre rôle : {user.role}</p>
      <button onClick={deconnecter}>Se déconnecter</button>
    </div>
  );
}

function Connexion({ onConnecte }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [erreur, setErreur] = useState("");

  async function envoyer(event) {
    event.preventDefault();
    setErreur("");
    try {
      await login(username, password);
      const reponse = await api("/auth/me/");
      onConnecte(await reponse.json());
    } catch (err) {
      setErreur(err.message);
    }
  }

  return (
    <form className="carte" onSubmit={envoyer}>
      <h1>LTIC</h1>
      <p>Gestion des stages</p>
      <label>Nom d'utilisateur</label>
      <input value={username} onChange={(e) => setUsername(e.target.value)} />
      <label>Mot de passe</label>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {erreur && <p className="erreur">{erreur}</p>}
      <button type="submit">Se connecter</button>
    </form>
  );
}