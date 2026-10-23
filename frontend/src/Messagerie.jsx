import { useEffect, useRef, useState } from "react";
import { api } from "./api";

const ROLES = { STAGIAIRE: "Stagiaire", ENCADRANT: "Encadrant", ADMIN: "Administrateur" };

export default function Messagerie({ user }) {
  const [contacts, setContacts] = useState([]);
  const [messages, setMessages] = useState([]);
  const [choisi, setChoisi] = useState(null);
  const [texte, setTexte] = useState("");
  const [erreur, setErreur] = useState("");
  const [rechargement, setRechargement] = useState(0);
  const fin = useRef(null);

  // Charge les contacts et les messages, puis recommence toutes les 5 secondes
  useEffect(() => {
    let actif = true;
    async function charger() {
      const [rc, rm] = await Promise.all([api("/contacts/"), api("/messages/")]);
      const c = await rc.json();
      const m = await rm.json();
      if (actif) {
        setContacts(c);
        setMessages(m);
      }
    }
    charger();
    const minuteur = setInterval(charger, 5000);
    return () => {
      actif = false;
      clearInterval(minuteur);
    };
  }, [rechargement]);

  // Les messages échangés avec le contact choisi
  const conversation = choisi
    ? messages.filter((m) => m.expediteur === choisi.id || m.destinataire === choisi.id)
    : [];

  // Descend automatiquement vers le dernier message
  useEffect(() => {
    fin.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation.length, choisi]);

  async function envoyer(event) {
    event.preventDefault();
    if (!texte.trim() || !choisi) return;
    const reponse = await api("/messages/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ destinataire: choisi.id, contenu: texte.trim() }),
    });
    if (reponse.ok) {
      setTexte("");
      setErreur("");
      setRechargement((n) => n + 1);
    } else {
      setErreur("Le message n'a pas été envoyé.");
    }
  }

  return (
    <div className="messagerie">
      <div className="panneau contacts">
        <h2>Contacts</h2>
        {contacts.length === 0 && <p className="petit">Aucun contact pour le moment.</p>}
        {contacts.map((c) => (
          <div
            key={c.id}
            className={"contact" + (choisi && choisi.id === c.id ? " actif" : "")}
            onClick={() => setChoisi(c)}
          >
            <div>{c.username}</div>
            <div className="petit">{ROLES[c.role]}</div>
          </div>
        ))}
      </div>

      <div className="panneau conversation">
        {!choisi && <p className="petit">Choisissez un contact pour voir la conversation.</p>}
        {choisi && (
          <>
            <h2>{choisi.username}</h2>
            <div className="fil">
              {conversation.length === 0 && (
                <p className="petit">Aucun message. Écrivez le premier !</p>
              )}
              {conversation.map((m) => (
                <div key={m.id} className={"bulle" + (m.expediteur === user.id ? " moi" : "")}>
                  {m.contenu}
                  <span className="heure">
                    {new Date(m.date_envoi).toLocaleTimeString("fr-FR", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
              ))}
              <div ref={fin} />
            </div>
            {erreur && <p className="erreur">{erreur}</p>}
            <form className="formulaire" onSubmit={envoyer}>
              <input
                type="text"
                style={{ flex: 1 }}
                placeholder="Écrire un message..."
                value={texte}
                onChange={(e) => setTexte(e.target.value)}
              />
              <button className="bouton" type="submit">
                Envoyer
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}