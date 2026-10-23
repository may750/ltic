import { useEffect, useState } from "react";
import { api } from "./api";
import Layout from "./Layout";

const ROLES = {
  STAGIAIRE: "Stagiaire",
  ENCADRANT: "Encadrant",
  ADMIN: "Administrateur",
};

// Une ligne de statistique avec une barre colorée
function LigneStat({ label, valeur, max, couleur }) {
  const pct = max ? (valeur / max) * 100 : 0;
  return (
    <div className="stat-ligne">
      <span className="petit">{label}</span>
      <div className="barre">
        <div style={{ width: `${pct}%`, background: couleur }} />
      </div>
      <strong>{valeur}</strong>
    </div>
  );
}

export default function DashboardAdmin({ user, onDeconnecter }) {
  const [utilisateurs, setUtilisateurs] = useState([]);
  const [stages, setStages] = useState([]);
  const [taches, setTaches] = useState([]);
  const [documents, setDocuments] = useState([]);

  // Charge toutes les données (l'administrateur a le droit de tout voir)
  useEffect(() => {
    let actif = true;
    async function charger() {
      const chemins = ["/utilisateurs/", "/stages/", "/taches/", "/documents/"];
      const reponses = await Promise.all(chemins.map((c) => api(c)));
      const [u, s, t, d] = await Promise.all(reponses.map((r) => r.json()));
      if (actif) {
        setUtilisateurs(u);
        setStages(s);
        setTaches(t);
        setDocuments(d);
      }
    }
    charger();
    return () => {
      actif = false;
    };
  }, []);

  const compter = (liste, champ, valeur) => liste.filter((x) => x[champ] === valeur).length;
  const noms = Object.fromEntries(utilisateurs.map((u) => [u.id, u.username]));

  return (
    <Layout
      user={user}
      roleLabel="Administrateur"
      titre="Tableau de bord de l'administrateur"
      onDeconnecter={onDeconnecter}
    >
      <div className="grille-stats">
        <div className="stat">
          <div className="stat-nom">Stagiaires</div>
          <div className="stat-valeur">{compter(utilisateurs, "role", "STAGIAIRE")}</div>
        </div>
        <div className="stat">
          <div className="stat-nom">Encadrants</div>
          <div className="stat-valeur">{compter(utilisateurs, "role", "ENCADRANT")}</div>
        </div>
        <div className="stat">
          <div className="stat-nom">Stages</div>
          <div className="stat-valeur">{stages.length}</div>
        </div>
        <div className="stat">
          <div className="stat-nom">Documents</div>
          <div className="stat-valeur">{documents.length}</div>
        </div>
      </div>

      <div className="deux-colonnes">
        <div className="panneau">
          <h2>Tous les utilisateurs</h2>
          {utilisateurs.map((u) => (
            <div className="ligne" key={u.id}>
              <div>
                <strong>{u.username}</strong>
                {u.role === "STAGIAIRE" && u.encadrant && (
                  <span className="petit"> (encadrant : {noms[u.encadrant]})</span>
                )}
              </div>
              <span className="role">{ROLES[u.role]}</span>
            </div>
          ))}
          <p style={{ marginTop: 16 }}>
            <a
              className="bouton"
              style={{ color: "white", textDecoration: "none", display: "inline-block" }}
              href="http://127.0.0.1:8000/admin/"
              target="_blank"
              rel="noreferrer"
            >
              Créer ou modifier des comptes
            </a>
          </p>
        </div>

        <div className="colonne">
          <div className="panneau">
            <h2>Tâches par état</h2>
            <LigneStat label="À faire" valeur={compter(taches, "etat", "A_FAIRE")} max={taches.length} couleur="#71717a" />
            <LigneStat label="En cours" valeur={compter(taches, "etat", "EN_COURS")} max={taches.length} couleur="#8b5cf6" />
            <LigneStat label="Terminées" valeur={compter(taches, "etat", "TERMINEE")} max={taches.length} couleur="#22c55e" />
          </div>

          <div className="panneau">
            <h2>Stages par statut</h2>
            <LigneStat label="En attente" valeur={compter(stages, "statut", "EN_ATTENTE")} max={stages.length} couleur="#71717a" />
            <LigneStat label="En cours" valeur={compter(stages, "statut", "EN_COURS")} max={stages.length} couleur="#8b5cf6" />
            <LigneStat label="Terminés" valeur={compter(stages, "statut", "TERMINE")} max={stages.length} couleur="#22c55e" />
          </div>
        </div>
      </div>

      <div className="panneau">
        <h2>Tous les stages</h2>
        {stages.length === 0 && <p className="petit">Aucun stage pour le moment.</p>}
        {stages.map((s) => (
          <div className="ligne" key={s.id}>
            <div>
              <strong>{s.sujet}</strong>
              <span className="petit"> : {noms[s.stagiaire]}</span>
            </div>
            <span className="petit">
              du {s.date_debut} au {s.date_fin}
            </span>
          </div>
        ))}
      </div>
    </Layout>
  );
}