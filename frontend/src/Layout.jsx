import { useState } from "react";
import Messagerie from "./Messagerie";

// Le « cadre » commun à toutes les pages : menu à gauche + contenu à droite
export default function Layout({ user, roleLabel, titre, onDeconnecter, children }) {
  const [page, setPage] = useState("tableau");

  return (
    <div className="app">
      <aside className="menu">
        <div className="logo">LTIC</div>
        <p className="menu-titre">MENU</p>
        <nav>
          <div
            className={"menu-item cliquable" + (page === "tableau" ? " actif" : "")}
            onClick={() => setPage("tableau")}
          >
            Tableau de bord
          </div>
          <div
            className={"menu-item cliquable" + (page === "messagerie" ? " actif" : "")}
            onClick={() => setPage("messagerie")}
          >
            Messagerie
          </div>
          <div className="menu-item">
            Notifications <span className="bientot">bientôt</span>
          </div>
        </nav>
        <div className="menu-bas">
          <div className="utilisateur">
            <div className="avatar">{user.username[0].toUpperCase()}</div>
            <div>
              <div>{user.username}</div>
              <div className="petit">{roleLabel}</div>
            </div>
          </div>
          <button className="bouton bouton-clair" onClick={onDeconnecter}>
            Se déconnecter
          </button>
        </div>
      </aside>
      <main className="contenu">
        {page === "tableau" ? (
          <>
            <h1 className="titre-page">{titre}</h1>
            {children}
          </>
        ) : (
          <>
            <h1 className="titre-page">Messagerie</h1>
            <Messagerie user={user} />
          </>
        )}
      </main>
    </div>
  );
}