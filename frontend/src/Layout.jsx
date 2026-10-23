// Le « cadre » commun à toutes les pages : menu à gauche + contenu à droite
export default function Layout({ user, roleLabel, titre, onDeconnecter, children }) {
  return (
    <div className="app">
      <aside className="menu">
        <div className="logo">LTIC</div>
        <p className="menu-titre">MENU</p>
        <nav>
          <div className="menu-item actif">Tableau de bord</div>
          <div className="menu-item">
            Messagerie <span className="bientot">bientôt</span>
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
        <h1 className="titre-page">{titre}</h1>
        {children}
      </main>
    </div>
  );
}