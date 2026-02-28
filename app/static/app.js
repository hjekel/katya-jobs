// Katya Jobs — Frontend (Jobs page)

let currentSource = "";
let currentOffset = 0;
let currentTotal = 0;
const PAGE_SIZE = 50;
let searchTimeout = null;
const HOME_ENCODED = "Laan+van+Decima+1B,+Haarlem";

document.addEventListener("DOMContentLoaded", () => {
    loadStats();
    loadJobs();
});

async function api(path, opts = {}) {
    const resp = await fetch(path, opts);
    return resp.json();
}

// ——— Load jobs ———
async function loadJobs(append = false) {
    if (!append) currentOffset = 0;

    const search = document.getElementById("search-input").value.trim();
    const onlyNew = document.getElementById("toggle-new").checked;
    const minSalary = parseInt(document.getElementById("min-salary").value) || 0;

    const params = new URLSearchParams({ limit: PAGE_SIZE, offset: currentOffset });
    if (currentSource) params.set("source", currentSource);
    if (search) params.set("search", search);
    if (onlyNew) params.set("only_new", "true");
    if (minSalary > 0) params.set("min_salary", minSalary);

    const data = await api(`/api/jobs?${params}`);
    currentTotal = data.total;

    const container = document.getElementById("jobs-container");
    const emptyState = document.getElementById("empty-state");
    const loadMoreContainer = document.getElementById("load-more-container");

    if (!append) container.innerHTML = "";

    if (data.jobs.length === 0 && !append) {
        emptyState.style.display = "block";
        loadMoreContainer.style.display = "none";
        return;
    }

    emptyState.style.display = "none";
    data.jobs.forEach(job => container.appendChild(createJobCard(job)));

    const shown = currentOffset + data.jobs.length;
    loadMoreContainer.style.display = shown < currentTotal ? "block" : "none";
}

function loadMore() {
    currentOffset += PAGE_SIZE;
    loadJobs(true);
}

// ——— Build Google Maps commute URL ———
function mapsUrl(location) {
    if (!location) return null;
    const dest = encodeURIComponent(location);
    return `https://www.google.com/maps/dir/${HOME_ENCODED}/${dest}?travelmode=transit`;
}

// ——— Create a job card ———
function createJobCard(job) {
    const card = document.createElement("div");
    card.className = "job-card" + (job.is_new ? " is-new" : "");
    card.id = `job-${job.id}`;

    const scoreClass = job.score >= 70 ? "high" : job.score >= 40 ? "medium" : "low";
    const sourceClass = `source-${job.source}`;

    // Salary display
    let salaryHtml;
    if (job.salary_min && job.salary_max) {
        if (job.salary_min === job.salary_max) {
            salaryHtml = `<div class="job-salary has-salary">\u20AC${job.salary_min.toLocaleString()}/month</div>`;
        } else {
            salaryHtml = `<div class="job-salary has-salary">\u20AC${job.salary_min.toLocaleString()} - \u20AC${job.salary_max.toLocaleString()}/month</div>`;
        }
    } else {
        salaryHtml = `<div class="job-salary no-salary">Salary not listed</div>`;
    }

    // Commute display
    let commuteHtml = "";
    if (job.location) {
        const url = mapsUrl(job.location);
        commuteHtml = `
            <div class="job-commute">
                <span>\uD83D\uDE86 Commute from Haarlem</span>
                <a href="${escHtml(url)}" target="_blank" rel="noopener"
                   onclick="event.stopPropagation()">Get directions \u2192</a>
            </div>`;
    }

    card.innerHTML = `
        <div class="job-card-header">
            <a class="job-title" href="${escHtml(job.url)}" target="_blank" rel="noopener"
               onclick="event.stopPropagation()">
                ${escHtml(job.title)}
            </a>
            <span class="job-score ${scoreClass}">${job.score}pts</span>
        </div>
        <div class="job-meta">
            ${job.company ? `<span>\uD83C\uDFE2 ${escHtml(job.company)}</span>` : ""}
            ${job.location ? `<span>\uD83D\uDCCD ${escHtml(job.location)}</span>` : ""}
            ${job.date_posted ? `<span>\uD83D\uDCC5 ${escHtml(job.date_posted)}</span>` : ""}
        </div>
        ${salaryHtml}
        ${commuteHtml}
        ${job.snippet ? `<p class="job-snippet">${escHtml(job.snippet)}</p>` : ""}
        <div class="job-footer">
            <span class="job-source ${sourceClass}">${escHtml(job.source)}</span>
            <div class="job-actions">
                <button class="btn-save" id="save-${job.id}"
                        onclick="event.stopPropagation(); saveJob(${job.id})">Save</button>
                <button class="btn-hide"
                        onclick="event.stopPropagation(); hideJob(${job.id})">Hide</button>
                <a class="btn-apply" href="${escHtml(job.url)}" target="_blank" rel="noopener"
                   onclick="event.stopPropagation()">View \u2192</a>
            </div>
        </div>
        <div class="expand-hint">Click card to see why Katya fits</div>
        <div class="job-fit" id="fit-${job.id}"></div>
    `;

    card.addEventListener("click", (e) => {
        if (e.target.closest("a, button")) return;
        toggleFit(job);
    });

    return card;
}

// ——— Toggle fit analysis ———
async function toggleFit(job) {
    const fitEl = document.getElementById(`fit-${job.id}`);
    if (!fitEl) return;

    if (fitEl.classList.contains("open")) {
        fitEl.classList.remove("open");
        return;
    }
    if (fitEl.dataset.loaded) {
        fitEl.classList.add("open");
        return;
    }

    fitEl.innerHTML = `<p class="job-fit-loading">Analysing fit...</p>`;
    fitEl.classList.add("open");

    try {
        const params = new URLSearchParams({
            title: job.title || "",
            snippet: job.snippet || "",
            location: job.location || "",
        });
        const data = await api(`/api/fit?${params}`);
        fitEl.innerHTML = `
            <p class="job-fit-tagline">${escHtml(data.tagline)}</p>
            <ul class="job-fit-bullets">
                ${data.bullets.map(b => `<li>${escHtml(b)}</li>`).join("")}
            </ul>
        `;
        fitEl.dataset.loaded = "1";
    } catch (err) {
        fitEl.innerHTML = `<p class="job-fit-loading">Could not load analysis.</p>`;
    }
}

// ——— Save job to application tracker ———
async function saveJob(jobId) {
    const data = await api(`/api/applications/${jobId}/save`, { method: "POST" });
    const btn = document.getElementById(`save-${jobId}`);
    if (btn) {
        btn.classList.add("saved");
        btn.textContent = data.status === "created" ? "Saved!" : "Already saved";
    }
}

// ——— Source filter ———
function setSource(btn, source) {
    currentSource = source;
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    loadJobs();
}

function debounceSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => loadJobs(), 300);
}

// ——— Scrape ———
async function startScrape() {
    const btn = document.getElementById("btn-scrape");
    const statusBar = document.getElementById("status-bar");
    const statusText = document.getElementById("status-text");

    btn.disabled = true;
    btn.classList.add("spinning");
    statusBar.style.display = "flex";
    statusText.textContent = "Scanning 6 job boards... this may take a minute.";

    try {
        const data = await api("/api/scrape", { method: "POST" });
        if (data.status === "completed") {
            const parts = Object.entries(data.results)
                .map(([src, count]) => `${src}: ${count} new`)
                .join(", ");
            statusText.textContent = `Done! ${parts}`;
        } else {
            statusText.textContent = "Scrape is already running.";
        }
        loadStats();
        loadJobs();
    } catch (err) {
        statusText.textContent = "Error scanning. Try again later.";
    } finally {
        btn.disabled = false;
        btn.classList.remove("spinning");
        setTimeout(() => { statusBar.style.display = "none"; }, 5000);
    }
}

async function hideJob(jobId) {
    await api(`/api/jobs/${jobId}/hide`, { method: "POST" });
    const card = document.getElementById(`job-${jobId}`);
    if (card) {
        card.style.transition = "opacity 0.3s, transform 0.3s";
        card.style.opacity = "0";
        card.style.transform = "translateX(30px)";
        setTimeout(() => card.remove(), 300);
    }
    loadStats();
}

async function loadStats() {
    const data = await api("/api/stats");
    document.getElementById("stat-total").textContent = `${data.total} jobs`;
    const newBadge = document.getElementById("stat-new");
    if (data.new > 0) {
        newBadge.textContent = `${data.new} new`;
        newBadge.style.display = "inline";
    } else {
        newBadge.style.display = "none";
    }
}

function escHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
