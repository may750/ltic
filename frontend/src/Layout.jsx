import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import Messagerie from "./Messagerie";
import Notifications from "./Notifications";

// Le « cadre » commun à toutes les pages : menu à gauche + contenu à droite
export default function Layout({ user, roleLabel, titre, onDeconnecter, children }) {
  const [page, setPage] = useState("tableau");
  const [nonLues, setNonLues] = useState(0);

  // Compte les notifications non lues
  const chargerNonLues = useCallback(async () => {
    const reponse = await api("/notifications/");
    if (reponse.ok) {
      const liste = await reponse.json();
      setNonLues(liste.filter((n) => !n.lue).length);
    }
  }, []);

  useEffect(() => {
    chargerNonLues();
    const minuteur = setInterval(chargerNonLues, 5000);
    return () => clearInterval(minuteur);
  }, [chargerNonLues]);

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
          <div
            className={"menu-item cliquable" + (page === "notifications" ? " actif" : "")}
            onClick={() => setPage("notifications")}
          >
            Notifications
            {nonLues > 0 && <span className="badge">{nonLues}</span>}
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
        {page === "tableau" && (
          <>
            <h1 className="titre-page">{titre}</h1>
            {children}
          </>
        )}
        {page === "messagerie" && (
          <>
            <h1 className="titre-page">Messagerie</h1>
            <Messagerie user={user} />
          </>
        )}
        {page === "notifications" && (
          <>
            <h1 className="titre-page">Notifications</h1>
            <Notifications onChange={chargerNonLues} />
          </>
        )}
      </main>
    </div>
  );
}