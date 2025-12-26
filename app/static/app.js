let allTitles = [];
const input = document.getElementById("movie-input");
const suggestions = document.getElementById("suggestions");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const btn = document.getElementById("recommend-btn");

// Fetch titles once
fetch("/api/movies")
  .then((r) => r.json())
  .then((data) => {
    allTitles = data.titles || [];
  });

input.addEventListener("input", () => {
  const q = input.value.toLowerCase().trim();
  suggestions.innerHTML = "";
  if (!q) return;
  const matched = allTitles
    .filter((t) => t.toLowerCase().includes(q))
    .slice(0, 8);

  matched.forEach((title) => {
    const li = document.createElement("li");
    li.textContent = title;
    li.onclick = () => {
      input.value = title;
      suggestions.innerHTML = "";
    };
    suggestions.appendChild(li);
  });
});

btn.addEventListener("click", () => {
  const title = input.value.trim();
  if (!title) {
    statusEl.textContent = "Please enter a movie title.";
    return;
  }
  statusEl.textContent = "Loading recommendations...";
  resultsEl.innerHTML = "";

  fetch("/api/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.error) {
        statusEl.textContent = data.error;
        return;
      }
      statusEl.textContent = "";
      renderResults(data.recommendations);
    })
    .catch(() => {
      statusEl.textContent = "Error fetching recommendations.";
    });
});

function renderResults(recs) {
  resultsEl.innerHTML = "";
  if (!recs || recs.length === 0) {
    resultsEl.textContent = "No recommendations found.";
    return;
  }
  recs.forEach((m) => {
    const card = document.createElement("article");
    card.className = "movie-card";

    card.innerHTML = `
      <img src="${m.poster_url || ""}" alt="${m.title}" />
      <div class="movie-info">
        <h2>${m.title}</h2>
      </div>
    `;
    resultsEl.appendChild(card);
  });
}
