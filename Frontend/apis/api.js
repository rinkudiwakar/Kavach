const API = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

export function saveToken(token) { localStorage.setItem("kv_token", token); }
export function getToken() { return localStorage.getItem("kv_token"); }

async function fetchJson(path, opts = {}) {
  const res = await fetch(`${API}${path}`, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw { status: res.status, data };
  return data;
}

export function register(payload) {
  return fetchJson("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
export function login(payload) {
  return fetchJson("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function addMember(payload) {
  return fetchJson("/api/family/add-member", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload),
  });
}

export async function uploadVoiceSample(memberId, file) {
  const fd = new FormData();
  fd.append("member_id", memberId);
  fd.append("audio", file, file.name);
  const res = await fetch(`${API}/api/family/add-voice`, {
    method: "POST",
    headers: { ...authHeaders() },
    body: fd,
  });
  return res.json();
}

export async function verifyVoice(file) {
  const fd = new FormData();
  fd.append("audio", file, file.name);
  const res = await fetch(`${API}/api/family/verify`, {
    method: "POST",
    headers: { ...authHeaders() },
    body: fd,
  });
  return res.json();
}
// ...existing code...