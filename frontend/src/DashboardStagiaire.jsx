import { useEffect, useState } from "react";
import { api } from "./api";
import Layout from "./Layout";

const ETATS = [
  { valeur: "A_FAIRE", label: "À faire" },
  { valeur: "EN_COURS", label: "En cours" },
  { valeur: "TERMINEE", label: "Terminée" },
];

export default function DashboardStagiaire({ user, onDeconnecter }) {
  const [stages, setStages] = useState([]);
  const [taches, setTaches] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [feedbacks, setFeedbacks] = useState([]);
  const [nom, setNom] = useState("");
  const [fichier, setFichier] = useState(null);
  const [message, setMessage] = useState("");
  const [rechargement, setRechargement] = useState(0);

  // Charge les données depuis l'API (au début, et à chaque rechargement)
  useEffect(() => {
    let actif = true;
    async function charger() {
      const chemins = ["/stages/", "/taches/", "/documents/", "/feedbacks/"];
      const reponses = await Promise.all(chemins.map((c) => api(c)));
      const [s, t, d, f] = await Promise.all(reponses.map((r) => r.json()));
      if (actif) {
        setStages(s);
        setTaches(t);
        setDocuments(d);
        setFeedbacks(f);
      }
    }
    charger();
    return () => {
      actif = false;
    };
  }, [rechargement]);

  function recharger() {
    setRechargement((n) => n + 1);
  }

  async function changerEtat(id, etat) {
    await api(`/taches/${id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ etat }),
    });
    recharger();
  }

  async function deposer(event) {
    event.preventDefault();
    const formulaire = event.currentTarget;
    if (!nom || !fichier) {
      setMessage("Écrivez un nom et choisissez un fichier.");
      return;
    }
    const donnees = new FormData();
    donnees.append("nom", nom);
    donnees.append("fichier", fichier);
    const reponse = await api("/documents/", { method: "POST", body: donnees });
    if (reponse.ok) {
      setMessage("Document déposé.");
      setNom("");
      setFichier(null);
      formulaire.reset();
      recharger();
    } else {
      setMessage("Erreur : le document n'a pas été déposé.");
    }
  }

  // Calculs pour les cartes et l'anneau
  const total = taches.length;
  const nbAFaire = taches.filter((t) => t.etat === "A_FAIRE").length;
  const nbEnCours = taches.filter((t) => t.etat === "EN_COURS").length;
  const nbTerminees = taches.filter((t) => t.etat === "TERMINEE").length;
  const pourcentage = total ? Math.round((nbTerminees / total) * 100) : 0;
  const finVert = total ? (nbTerminees / total) * 100 : 0;
  const finViolet = total ? ((nbTerminees + nbEnCours) / total) * 100 : 0;
  const fondAnneau = total
    ? `conic-gradient(#22c55e 0 ${finVert}%, #8b5cf6 ${finVert}% ${finViolet}%, #3f3f46 ${finViolet}% 100%)`
    : "#3f3f46";

  return (
    <Layout
      user={user}
      roleLabel="Stagiaire"
      titre="Mon tableau de bord"
      onDeconnecter={onDeconnecter}
    >
      <div className="grille-stats">
        <div className="stat">
          <div className="stat-nom">Tâches au total</div>
          <div className="stat-valeur">{total}</div>
        </div>
        <div className="stat">
          <div className="stat-nom">À faire</div>
          <div className="stat-valeur">{nbAFaire}</div>
        </div>
        <div className="stat">
          <div className="stat-nom">En cours</div>
          <div className="stat-valeur">{nbEnCours}</div>
        </div>
        <div className="stat">
          <div className="stat-nom">Terminées</div>
          <div className="stat-valeur">{nbTerminees}</div>
        </div>
      </div>

      <div className="deux-colonnes">
        <div className="panneau">
          <h2>Mes tâches</h2>
          {total === 0 && <p className="petit">Aucune tâche pour le moment.</p>}
          {taches.map((t) => (
            <div className="ligne" key={t.id}>
              <div>
                {t.titre}
                {t.echeance && <span className="petit"> (avant le {t.echeance})</span>}
              </div>
              <select value={t.etat} onChange={(e) => changerEtat(t.id, e.target.value)}>
                {ETATS.map((e) => (
                  <option key={e.valeur} value={e.valeur}>
                    {e.label}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>

        <div className="colonne">
          <div className="panneau">
            <h2>Avancement</h2>
            <div className="donut-zone">
              <div className="donut" style={{ background: fondAnneau }}>
                <div className="donut-centre">{pourcentage}%</div>
              </div>
              <div className="legende">
                <div>
                  <span className="puce" style={{ background: "#22c55e" }} />
                  Terminées
                </div>
                <div>
                  <span className="puce" style={{ background: "#8b5cf6" }} />
                  En cours
                </div>
                <div>
                  <span className="puce" style={{ background: "#3f3f46" }} />
                  À faire
                </div>
              </div>
            </div>
          </div>

          <div className="panneau">
            <h2>Mon stage</h2>
            {stages.length === 0 && <p className="petit">Aucun stage pour le moment.</p>}
            {stages.map((s) => (
              <p key={s.id}>
                <strong>{s.sujet}</strong>
                <br />
                <span className="petit">
                  du {s.date_debut} au {s.date_fin}
                </span>
              </p>
            ))}
          </div>
        </div>
      </div>

      <div className="panneau">
        <h2>Mes documents</h2>
        <form className="ligne" onSubmit={deposer}>
          <input
            type="text"
            placeholder="Nom du document"
            value={nom}
            onChange={(e) => setNom(e.target.value)}
          />
          <input type="file" onChange={(e) => setFichier(e.target.files[0])} />
          <button className="bouton" type="submit">
            Déposer
          </button>
        </form>
        {message && <p className="petit">{message}</p>}
        {documents.length === 0 && <p className="petit">Aucun document déposé.</p>}
        {documents.map((d) => (
          <div key={d.id}>
            <div className="ligne">
              <a href={d.fichier} target="_blank" rel="noreferrer">
                {d.nom}
              </a>
              <span className="petit">{d.date_depot.slice(0, 10)}</span>
            </div>
            {feedbacks
              .filter((f) => f.document === d.id)
              .map((f) => (
                <p className="feedback" key={f.id}>
                  Feedback : {f.commentaire}
                </p>
              ))}
          </div>
        ))}
      </div>
    </Layout>
  );
}