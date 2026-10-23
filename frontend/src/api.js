const TOKEN_KEY = "ltic_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

// Envoie une demande à l'API en ajoutant le token (le « badge »)
export async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Token ${token}`;
  return fetch(`/api${path}`, { ...options, headers });
}

// Se connecter : envoie le nom et le mot de passe, garde le token reçu
export async function login(username, password) {
  const response = await fetch("/api/auth/login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) {
    throw new Error("Nom d'utilisateur ou mot de passe incorrect");
  }
  const data = await response.json();
  setToken(data.token);
}