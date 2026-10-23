import { useEffect, useState } from "react";
import { api } from "./api";
import Layout from "./Layout";

const JSON_HEADERS = { "Content-Type": "application/json" };
const STAGE_VIDE = { stagiaire: "", sujet: "", date_debut: "", date_fin: "" };
const TACHE_VIDE = { stage: "", titre: "", echeance: "" };

export default function DashboardEncadrant({ user, onDeconnecter }) {
  const [stagiaires, setStagiaires] = useState([]);
  const [stages, setStages] = useState([]);
  const [taches, setTaches] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [feedbacks, setFeedbacks] = useState([]);
  const [formStage, setFormStage] = useState(STAGE_VIDE);
  const [formTache, setFormTache] = useState(TACHE_VIDE);
  const [commentaires, setCommentaires] = useState({});
  const [message, setMessage] = useState("");
  const [rechargement, setRechargement] = useState(0);

  // Charge toutes les données de l'encadrant depuis l'API
  useEffect(() => {
    let actif = true;
    async function charger() {
      const chemins = ["/stagiaires/", "/stages/", "/taches/", "/documents/", "/feedbacks/"];
      const reponses = await Promise.all(chemins.map((c) => api(c)));
      const [sg, s, t, d, f] = await Promise.all(reponses.map((r) => r.json()));
      if (actif) {
        setStagiaires(sg);
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

  // Envoie un nouvel élément à l'API (stage, tâche ou feedback)
  async function envoyer(chemin, donnees) {
    const reponse = await api(chemin, {
      method: "POST",
      headers: JSON_HEADERS,
      body: JSON.stringify(donnees),
    });
    if (reponse.ok) {
      setMessage("Enregistré.");
      recharger();
      return true;
    }
    setMessage("Erreur : vérifiez que tous les champs sont remplis.");
    return false;
  }

  async function creerStage(event) {
    event.preventDefault();
    const ok = await envoyer("/stages/", {
      ...formStage,
      stagiaire: Number(formStage.stagiaire),
    });
    if (ok) setFormStage(STAGE_VIDE);
  }

  async function creerTache(event) {
    event.preventDefault();
    const ok = await envoyer("/taches/", {
      stage: Number(formTache.stage),
      titre: formTache.titre,
      echeance: formTache.echeance || null,
    });
    if (ok) setFormTache(TACHE_VIDE);
  }

  async function envoyerFeedback(documentId) {
    const texte = (commentaires[documentId] || "").trim();
    if (!texte) return;
    const ok = await envoyer("/feedbacks/", { document: documentId, commentaire: texte });
    if (ok) setCommentaires((c) => ({ ...c, [documentId]: "" }));
  }

  // Petits calculs
  const noms = Object.fromEntries(stagiaires.map((s) => [s.id, s.username]));
  const tachesFinies = taches.filter((t) => t.etat === "TERMINEE").length;

  function progression(stagiaireId) {
    const idsStages = stages.filter((s) => s.stagiaire === stagiaireId).map((s) => s.id);
    const siennes = taches.filter((t) => idsStages.includes(t.stage));
    const finies = siennes.filter((t) => t.etat === "TERMINEE").length;
    return {
      total: siennes.length,
      finies,
      pct: siennes.length ? Math.round((finies / siennes.length) * 100) : 0,
    };
  }

  return (
    <Layout
      user={user}
      roleLabel="Encadrant"
      titre="Tableau de bord de l'encadrant"
      onDeconnecter={onDeconnecter}
    >
      <div className="grille-stats">
        <div className="stat">
          <div className="stat-nom">Mes stagiaires</div>
          <div className="stat-valeur">{stagiaires.length}</div>
        </div>
        <div className="stat">
          <div className="stat-nom">Stages</div>
          <div className="stat-valeur">{stages.length}</div>
        </div>
        <div className="stat">
          <div className="stat-nom">Tâches terminées</div>
          <div className="stat-valeur">
            {tachesFinies}/{taches.length}
          </div>
        </div>
        <div className="stat">
          <div className="stat-nom">Documents reçus</div>
          <div className="stat-valeur">{documents.length}</div>
        </div>
      </div>

      {message && <p className="petit">{message}</p>}

      <div className="deux-colonnes">
        <div className="panneau">
          <h2>Mes stagiaires</h2>
          {stagiaires.length === 0 && <p className="petit">Aucun stagiaire assigné.</p>}
          {stagiaires.map((s) => {
            const p = progression(s.id);
            return (
              <div className="ligne" key={s.id}>
                <div>
                  <strong>{s.username}</strong>
                  <div className="petit">{s.specialite || "Spécialité non renseignée"}</div>
                </div>
                <div style={{ width: "40%" }}>
                  <div className="petit">
                    {p.finies}/{p.total} tâches ({p.pct} %)
                  </div>
                  <div className="barre">
                    <div style={{ width: `${p.pct}%` }} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="colonne">
          <div className="panneau">
            <h2>Créer un stage</h2>
            <form className="formulaire" onSubmit={creerStage}>
              <select
                value={formStage.stagiaire}
                onChange={(e) => setFormStage({ ...formStage, stagiaire: e.target.value })}
                required
              >
                <option value="">Choisir un stagiaire</option>
                {stagiaires.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.username}
                  </option>
                ))}
              </select>
              <input
                type="text"
                placeholder="Sujet du stage"
                value={formStage.sujet}
                onChange={(e) => setFormStage({ ...formStage, sujet: e.target.value })}
                required
              />
              <input
                type="date"
                value={formStage.date_debut}
                onChange={(e) => setFormStage({ ...formStage, date_debut: e.target.value })}
                required
              />
              <input
                type="date"
                value={formStage.date_fin}
                onChange={(e) => setFormStage({ ...formStage, date_fin: e.target.value })}
                required
              />
              <button className="bouton" type="submit">
                Créer
              </button>
            </form>
          </div>

          <div className="panneau">
            <h2>Ajouter une tâche</h2>
            <form className="formulaire" onSubmit={creerTache}>
              <select
                value={formTache.stage}
                onChange={(e) => setFormTache({ ...formTache, stage: e.target.value })}
                required
              >
                <option value="">Choisir un stage</option>
                {stages.map((s) => (
                  <option key={s.id} value={s.id}>
                    {noms[s.stagiaire]} : {s.sujet}
                  </option>
                ))}
              </select>
              <input
                type="text"
                placeholder="Titre de la tâche"
                value={formTache.titre}
                onChange={(e) => setFormTache({ ...formTache, titre: e.target.value })}
                required
              />
              <input
                type="date"
                value={formTache.echeance}
                onChange={(e) => setFormTache({ ...formTache, echeance: e.target.value })}
              />
              <button className="bouton" type="submit">
                Ajouter
              </button>
            </form>
          </div>
        </div>
      </div>

      <div className="panneau">
        <h2>Documents de mes stagiaires</h2>
        {documents.length === 0 && <p className="petit">Aucun document reçu.</p>}
        {documents.map((d) => (
          <div key={d.id}>
            <div className="ligne">
              <div>
                <a href={d.fichier} target="_blank" rel="noreferrer">
                  {d.nom}
                </a>
                <span className="petit">
                  {" "}
                  par {noms[d.stagiaire]}, le {d.date_depot.slice(0, 10)}
                </span>
              </div>
            </div>
            {feedbacks
              .filter((f) => f.document === d.id)
              .map((f) => (
                <p className="feedback" key={f.id}>
                  Feedback : {f.commentaire}
                </p>
              ))}
            <div className="formulaire" style={{ margin: "8px 0 14px" }}>
              <input
                type="text"
                style={{ flex: 1 }}
                placeholder="Écrire un feedback..."
                value={commentaires[d.id] || ""}
                onChange={(e) => setCommentaires({ ...commentaires, [d.id]: e.target.value })}
              />
              <button className="bouton" onClick={() => envoyerFeedback(d.id)}>
                Envoyer
              </button>
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}