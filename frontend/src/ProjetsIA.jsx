import { useEffect, useState } from "react";
import { api } from "./api";

// Anneau qui montre le score de pertinence (0 à 100)
function Anneau({ score }) {
  const pct = Math.round(score);
  return (
    <div
      className="anneau-score"
      style={{
        background: `conic-gradient(var(--violet) 0 ${pct}%, rgba(255,255,255,0.1) ${pct}% 100%)`,
      }}
    >
      <div className="anneau-centre">{pct}%</div>
    </div>
  );
}

export default function ProjetsIA() {
  const [profil, setProfil] = useState({
    specialite: "",
    competences: "",
    centres_interet: "",
    cv: null,
  });
  const [fichier, setFichier] = useState(null);
  const [cleFichier, setCleFichier] = useState(0);
  const [suggestions, setSuggestions] = useState([]);
  const [messageProfil, setMessageProfil] = useState("");
  const [erreurIA, setErreurIA] = useState("");
  const [chargement, setChargement] = useState(false);
  const [sauvegarde, setSauvegarde] = useState(false);

  // Au début : on charge le profil et les suggestions déjà enregistrées
  useEffect(() => {
    let actif = true;
    async function charger() {
      const [rp, rs] = await Promise.all([api("/profil/"), api("/suggestions/")]);
      const donneesProfil = rp.ok ? await rp.json() : null;
      const donneesSuggestions = rs.ok ? await rs.json() : [];
      if (actif) {
        if (donneesProfil) setProfil(donneesProfil);
        setSuggestions(donneesSuggestions);
      }
    }
    charger();
    return () => {
      actif = false;
    };
  }, []);

  function modifier(champ, valeur) {
    setProfil({ ...profil, [champ]: valeur });
  }

  async function enregistrer(event) {
    event.preventDefault();
    setSauvegarde(true);
    setMessageProfil("");
    const donnees = new FormData();
    donnees.append("specialite", profil.specialite || "");
    donnees.append("competences", profil.competences || "");
    donnees.append("centres_interet", profil.centres_interet || "");
    if (fichier) donnees.append("cv", fichier);
    const reponse = await api("/profil/", { method: "PATCH", body: donnees });
    if (reponse.ok) {
      setProfil(await reponse.json());
      setFichier(null);
      setCleFichier((n) => n + 1);
      setMessageProfil("Profil enregistré.");
    } else {
      let texte = "Le profil n'a pas été enregistré.";
      try {
        const erreurs = await reponse.json();
        if (erreurs.cv) texte = erreurs.cv[0];
      } catch {
        // on garde le message par défaut
      }
      setMessageProfil(texte);
    }
    setSauvegarde(false);
  }

  async function generer() {
    setChargement(true);
    setErreurIA("");
    try {
      const reponse = await api("/suggestions/", { method: "POST" });
      const donnees = await reponse.json();
      if (reponse.ok) {
        setSuggestions(donnees);
      } else {
        setErreurIA(donnees.detail || "Une erreur est survenue.");
      }
    } catch {
      setErreurIA("Impossible de joindre le serveur.");
    }
    setChargement(false);
  }

  return (
    <div>
      <div className="panneau" style={{ marginTop: 0 }}>
        <h2>Mon profil</h2>
        <p className="petit">
          L'IA utilise ces informations pour vous proposer des projets. Votre nom, e-mail,
          téléphone et liens sont masqués automatiquement avant l'envoi. N'ajoutez pas
          d'informations sensibles.
        </p>
        <form className="formulaire-profil" onSubmit={enregistrer}>
          <label>Spécialité</label>
          <input
            type="text"
            value={profil.specialite || ""}
            onChange={(e) => modifier("specialite", e.target.value)}
          />
          <label>Compétences (séparées par des virgules)</label>
          <input
            type="text"
            value={profil.competences || ""}
            onChange={(e) => modifier("competences", e.target.value)}
          />
          <label>Centres d'intérêt</label>
          <textarea
            rows={3}
            value={profil.centres_interet || ""}
            onChange={(e) => modifier("centres_interet", e.target.value)}
          />
          <label>CV (PDF, 5 Mo maximum)</label>
          {profil.cv && (
            <a href={profil.cv} target="_blank" rel="noreferrer">
              Voir mon CV actuel
            </a>
          )}
          <input
            key={cleFichier}
            type="file"
            accept="application/pdf"
            onChange={(e) => setFichier(e.target.files[0] || null)}
          />
          <div>
            <button className="bouton" type="submit" disabled={sauvegarde}>
              {sauvegarde ? "Enregistrement..." : "Enregistrer"}
            </button>
          </div>
          {messageProfil && <p className="petit">{messageProfil}</p>}
        </form>
      </div>

      <div className="panneau">
        <div className="ligne" style={{ borderBottom: "none" }}>
          <h2 style={{ margin: 0 }}>Projets suggérés par l'IA</h2>
          <button className="bouton" onClick={generer} disabled={chargement}>
            {chargement
              ? "L'IA réfléchit..."
              : suggestions.length
                ? "Régénérer"
                : "Générer mes suggestions"}
          </button>
        </div>
        {erreurIA && <p className="erreur">{erreurIA}</p>}
        {suggestions.length === 0 && !chargement && (
          <p className="petit">
            Aucune suggestion pour le moment. Complétez votre profil, enregistrez-le, puis
            cliquez sur « Générer ».
          </p>
        )}
        <div className="cartes-ia">
          {suggestions.map((s) => (
            <div className="carte-ia" key={s.id}>
              <Anneau score={s.score} />
              <h3>{s.titre}</h3>
              <p>{s.description}</p>
              {s.competences_cibles && (
                <>
                  <div className="petit">Compétences à acquérir</div>
                  <div className="comps">
                    {s.competences_cibles
                      .split(",")
                      .map((c) => c.trim())
                      .filter(Boolean)
                      .map((c, i) => (
                        <span className="puce-comp" key={i}>
                          {c}
                        </span>
                      ))}
                  </div>
                </>
              )}
              {s.explication && <p className="petit">{s.explication}</p>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}