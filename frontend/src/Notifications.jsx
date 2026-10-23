import { useEffect, useState } from "react";
import { api } from "./api";

export default function Notifications({ onChange }) {
  const [liste, setListe] = useState([]);
  const [rechargement, setRechargement] = useState(0);

  // Charge les notifications, puis recommence toutes les 5 secondes
  useEffect(() => {
    let actif = true;
    async function charger() {
      const reponse = await api("/notifications/");
      if (reponse.ok && actif) setListe(await reponse.json());
    }
    charger();
    const minuteur = setInterval(charger, 5000);
    return () => {
      actif = false;
      clearInterval(minuteur);
    };
  }, [rechargement]);

  function actualiser() {
    setRechargement((n) => n + 1);
    onChange();
  }

  async function marquerLue(id) {
    await api(`/notifications/${id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lue: true }),
    });
    actualiser();
  }

  async function toutLire() {
    await api("/notifications/tout_lire/", { method: "POST" });
    actualiser();
  }

  const nonLues = liste.filter((n) => !n.lue).length;

  return (
    <div className="panneau" style={{ marginTop: 0 }}>
      <div className="ligne" style={{ borderBottom: "none" }}>
        <h2 style={{ margin: 0 }}>{nonLues} non lue(s)</h2>
        {nonLues > 0 && (
          <button className="bouton bouton-clair" onClick={toutLire}>
            Tout marquer comme lu
          </button>
        )}
      </div>
      {liste.length === 0 && <p className="petit">Aucune notification pour le moment.</p>}
      {liste.map((n) => (
        <div
          key={n.id}
          className={"notif" + (n.lue ? "" : " nonlue")}
          onClick={() => !n.lue && marquerLue(n.id)}
        >
          <span>{n.contenu}</span>
          <span className="petit">{new Date(n.date).toLocaleString("fr-FR")}</span>
        </div>
      ))}
    </div>
  );
}