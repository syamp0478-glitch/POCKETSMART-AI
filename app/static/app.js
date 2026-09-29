const $ = (selector) => document.querySelector(selector);
const tokenKey = "pocketsmart_token";
const planners = {
  home: { kicker: "01 / HOME PLANNER", title: "Let's make a plan.", description: "Tell us what you want to refresh. We'll help you find a considered mix that stays within your number.", form: `<label>Total budget <div class="input-prefix"><span>₹</span><input name="budget" type="number" min="1" step="100" placeholder="50000" required></div></label><label>Rooms to plan <div class="check-grid"><label class="check"><input type="checkbox" name="rooms" value="Living room" checked> Living room</label><label class="check"><input type="checkbox" name="rooms" value="Bedroom"> Bedroom</label><label class="check"><input type="checkbox" name="rooms" value="Kitchen"> Kitchen</label><label class="check"><input type="checkbox" name="rooms" value="Dining room"> Dining room</label></div></label><label>Style direction<select name="style"><option>Modern</option><option>Warm minimal</option><option>Scandinavian</option><option>Traditional</option><option>Eclectic</option></select></label><label>What matters most? <span class="optional">Optional</span><textarea name="priorities" rows="2" placeholder="Storage, natural light, easy-care materials…"></textarea></label><button class="button button-dark full-button">Build my home plan <span>→</span></button>` },
  party: { kicker: "02 / GATHERING PLANNER", title: "Make room for a good time.", description: "A few details help us shape a starter estimate for the things that bring everyone together.", form: `<label>Total budget <div class="input-prefix"><span>₹</span><input name="budget" type="number" min="1" step="100" placeholder="25000" required></div></label><div class="form-row"><label>What are you celebrating?<select name="event_type"><option>Birthday</option><option>Wedding</option><option>Anniversary</option><option>Corporate gathering</option><option>Housewarming</option><option>Other celebration</option></select></label><label>Guest count<input name="guests" type="number" min="1" max="5000" placeholder="30" required></label></div><label>Venue preference<select name="venue"><option>Flexible</option><option>At home</option><option>Outdoor</option><option>Community hall</option><option>Restaurant</option></select></label><label>City <span class="optional">Optional</span><input name="city" maxlength="100" placeholder="e.g. Bengaluru"></label><label>Any preferences? <span class="optional">Optional</span><textarea name="preferences" rows="2" placeholder="Vegetarian menu, kid-friendly, relaxed atmosphere…"></textarea></label><button class="button button-dark full-button">Build my event plan <span>→</span></button>` },
  jewelry: { kicker: "03 / JEWELRY PLANNER", title: "Find your finishing touch.", description: "Share the occasion and your style. An outfit photo is optional and is used only to inform this suggestion.", form: `<label>Total budget <div class="input-prefix"><span>₹</span><input name="budget" type="number" min="1" step="100" placeholder="5000" required></div></label><label>Occasion<input name="occasion" maxlength="100" placeholder="Wedding guest, festive dinner…" required></label><label>Style direction<select name="style"><option>Classic</option><option>Minimal</option><option>Traditional</option><option>Contemporary</option><option>Bold statement</option></select></label><label>Outfit colors <span class="optional">Optional</span><input name="outfit_colors" maxlength="200" placeholder="Navy, ivory, gold…"></label><label>Outfit photo <span class="optional">Optional · JPG, PNG, WEBP up to 5 MB</span><input name="image" type="file" accept="image/jpeg,image/png,image/webp"></label><label>Anything else? <span class="optional">Optional</span><textarea name="notes" rows="2" placeholder="Metal preference, pieces you already own…"></textarea></label><button class="button button-dark full-button">Build my jewelry plan <span>→</span></button>` }
};
let authMode = "login";

function escapeHtml(value) { return String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
function money(value, currency = "INR") { try { return new Intl.NumberFormat("en-IN", { style: "currency", currency, maximumFractionDigits: 0 }).format(value); } catch { return `${currency} ${Number(value).toLocaleString("en-IN")}`; } }
function showToast(message) { const node = $("#toast"); node.textContent = message; node.classList.add("show"); setTimeout(() => node.classList.remove("show"), 3000); }
function setAuth(mode) {
  authMode = mode;
  const register = mode === "register";
  $("#auth-title").textContent = register ? "A good place to start." : "Welcome back.";
  $("#auth-subtitle").textContent = register ? "Create an account to keep your plans close." : "Sign in to save your plans and pick up where you left off.";
  $("#name-wrap").classList.toggle("hidden", !register);
  $("#auth-name").required = register;
  $("#auth-password").autocomplete = register ? "new-password" : "current-password";
  $("#auth-submit").textContent = register ? "Create my account" : "Sign in";
  $("#auth-switch-text").textContent = register ? "Already have an account?" : "New to PocketSmart?";
  $("#auth-switch").textContent = register ? "Sign in" : "Create an account";
  $("#auth-error").textContent = "";
}
function openAuth(mode = "login") { setAuth(mode); $("#auth-section").classList.remove("hidden"); $("#auth-section").scrollIntoView({ behavior: "smooth", block: "center" }); }
function closeAuth() { $("#auth-section").classList.add("hidden"); }
function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (localStorage.getItem(tokenKey)) headers.set("Authorization", `Bearer ${localStorage.getItem(tokenKey)}`);
  if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  return fetch(path, { ...options, headers }).then(async (response) => {
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Something went wrong. Please try again.");
    return data;
  });
}
function updateAccount(user) {
  const signedIn = Boolean(user);
  $("#user-label").textContent = user ? `Hello, ${user.name.split(" ")[0]}` : "";
  $("#auth-open").classList.toggle("hidden", signedIn);
  $("#logout").classList.toggle("hidden", !signedIn);
  $("#history-link").classList.toggle("hidden", !signedIn);
}
async function refreshAccount() {
  if (!localStorage.getItem(tokenKey)) return updateAccount(null);
  try { const result = await api("/session-info"); updateAccount(result.user); }
  catch { localStorage.removeItem(tokenKey); updateAccount(null); }
}

$("#auth-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const submit = $("#auth-submit"); submit.disabled = true; submit.textContent = "One moment…";
  try {
    const body = { email: $("#auth-email").value.trim(), password: $("#auth-password").value };
    if (authMode === "register") body.name = $("#auth-name").value.trim();
    const data = await api(authMode === "register" ? "/register" : "/login", { method: "POST", body: JSON.stringify(body) });
    localStorage.setItem(tokenKey, data.access_token); updateAccount(data.user); closeAuth(); showToast(`You're signed in, ${data.user.name.split(" ")[0]}.`);
  } catch (error) { $("#auth-error").textContent = error.message; }
  finally { submit.disabled = false; submit.textContent = authMode === "register" ? "Create my account" : "Sign in"; }
});
$("#auth-open").addEventListener("click", () => openAuth("login"));
$("#auth-close").addEventListener("click", closeAuth);
$("#auth-switch").addEventListener("click", () => setAuth(authMode === "login" ? "register" : "login"));
$("#logout").addEventListener("click", async () => { try { await api("/logout", { method: "POST" }); } catch {} localStorage.removeItem(tokenKey); updateAccount(null); showToast("You are signed out."); });

function openPlanner(name) {
  if (!localStorage.getItem(tokenKey)) { openAuth("register"); showToast("Create an account to save your recommendations."); return; }
  const config = planners[name];
  $("#modal-kicker").textContent = config.kicker; $("#modal-title").textContent = config.title; $("#modal-description").textContent = config.description;
  $("#planner-form").innerHTML = config.form; $("#planner-modal").classList.remove("hidden");
  $("#planner-form").onsubmit = (event) => submitPlanner(event, name);
}
document.querySelectorAll("[data-planner]").forEach((button) => button.addEventListener("click", () => openPlanner(button.dataset.planner)));
$("#modal-close").addEventListener("click", () => $("#planner-modal").classList.add("hidden"));
$("#planner-modal").addEventListener("click", (event) => { if (event.target.id === "planner-modal") event.currentTarget.classList.add("hidden"); });

async function submitPlanner(event, planner) {
  event.preventDefault();
  const form = event.currentTarget; const button = form.querySelector("button[type=submit],button:not([type])");
  button.disabled = true; button.textContent = "Putting your plan together…";
  try {
    const data = new FormData(form); let body; let options = { method: "POST" };
    if (planner === "jewelry") {
      body = new FormData(); for (const [key, value] of data.entries()) if (key !== "image" || value.size) body.append(key, value);
      options.body = body;
    } else {
      const payload = Object.fromEntries(data.entries());
      if (planner === "home") payload.rooms = data.getAll("rooms");
      if (planner === "party") payload.guests = Number(payload.guests);
      payload.budget = Number(payload.budget); payload.currency = "INR";
      options.body = JSON.stringify(payload);
    }
    const result = await api(`/generate-${planner}`, options);
    $("#planner-modal").classList.add("hidden"); renderResult(result); showToast("Your plan is ready.");
  } catch (error) { showToast(error.message); }
  finally { button.disabled = false; button.textContent = planner === "home" ? "Build my home plan →" : planner === "party" ? "Build my event plan →" : "Build my jewelry plan →"; }
}

function renderResult(plan) {
  $("#history-section").classList.add("hidden"); $("#results").classList.remove("hidden");
  const labels = { home: "A more considered space", party: "A gathering worth remembering", jewelry: "Your finishing touch" };
  $("#result-title").textContent = labels[plan.planner] || "Your plan";
  const rows = plan.recommendations.map((item) => `<article class="recommendation"><div class="recommendation-icon">${item.category === "Food" ? "✳" : item.category === "Decor" ? "✿" : item.category === "Earrings" ? "◇" : "✦"}</div><div class="recommendation-info"><span>${escapeHtml(item.category)} · ${escapeHtml(item.platform)}</span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.reason)}</small></div><div class="recommendation-price"><strong>${money(item.estimated_price, plan.currency)}</strong><a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">Explore option ↗</a></div></article>`).join("");
  const allocations = plan.allocation.map((item) => `<div class="allocation-line"><span>${escapeHtml(item.category)}</span><span>${money(item.amount, plan.currency)} <small>${item.percent}%</small></span></div>`).join("");
  $("#result-content").innerHTML = `<div class="plan-summary"><div class="summary-copy"><span class="eyebrow">${plan.ai_enabled ? "GEMINI PERSONALIZED NOTE" : "YOUR BUDGET SNAPSHOT"}</span><p>${escapeHtml(plan.summary)}</p><small>${plan.ai_enabled ? "AI suggestions can be imperfect. Check details before purchase." : "Add a Gemini API key in .env for personalized AI guidance."}</small></div><div class="budget-box"><span>YOUR BUDGET</span><strong>${money(plan.budget, plan.currency)}</strong><div class="progress"><i style="width:${Math.min(100, plan.budget ? (plan.estimated_total / plan.budget) * 100 : 0)}%"></i></div><small>Estimated ${money(plan.estimated_total, plan.currency)} · ${money(plan.remaining, plan.currency)} left</small></div></div><div class="plan-columns"><div><h3>Ideas to explore <span>${plan.recommendations.length}</span></h3><div class="recommendation-list">${rows || `<p class="empty-state">This budget may need a little more room for the sample options. Try a higher budget to see ideas.</p>`}</div><p class="disclaimer">Prices are illustrative estimates, not live offers. Links open marketplace searches; confirm price, stock, delivery, and seller details before purchasing.</p></div><aside class="allocation-card"><span class="eyebrow">ESTIMATED MIX</span><h3>Where it could go</h3>${allocations || "<p>No items fit this budget yet.</p>"}<div class="allocation-total"><span>Estimated total</span><strong>${money(plan.estimated_total, plan.currency)}</strong></div></aside></div>`;
  $("#results").scrollIntoView({ behavior: "smooth", block: "start" });
}
$("#clear-results").addEventListener("click", () => { $("#results").classList.add("hidden"); $("#planners").scrollIntoView({ behavior: "smooth" }); });

async function showHistory() {
  if (!localStorage.getItem(tokenKey)) return openAuth();
  try {
    const history = await api("/history"); const content = $("#history-content");
    content.innerHTML = history.length ? history.map((item) => `<button class="history-item" data-id="${item.id}"><span class="eyebrow">${escapeHtml(item.planner)} · ${new Date(item.created_at).toLocaleDateString()}</span><strong>${escapeHtml(item.result.summary)}</strong><span>${money(item.result.estimated_total, item.result.currency)} estimated · View plan →</span></button>`).join("") : `<p class="empty-state">Your saved plans will show up here after you create one.</p>`;
    content.querySelectorAll("[data-id]").forEach((button) => button.addEventListener("click", async () => { try { const row = await api(`/recommendations-details/${button.dataset.id}`); renderResult(row.result); } catch (e) { showToast(e.message); } }));
    $("#results").classList.add("hidden"); $("#history-section").classList.remove("hidden"); $("#history-section").scrollIntoView({ behavior: "smooth" });
  } catch (error) { showToast(error.message); }
}
$("#history-link").addEventListener("click", showHistory);
$("#close-history").addEventListener("click", () => $("#history-section").classList.add("hidden"));

setAuth(location.pathname === "/register" ? "register" : "login");
if (["/login", "/register"].includes(location.pathname)) setTimeout(() => openAuth(location.pathname.slice(1)), 100);
refreshAccount();
