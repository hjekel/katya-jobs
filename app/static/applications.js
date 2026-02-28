// Katya's JobFinder — Applications Kanban Board

let allApplications = [];
let editingJobId = null;

document.addEventListener("DOMContentLoaded", loadApplications);

// Called by theme.js when language changes
function onLanguageChange() {
    renderKanban();
}

async function api(path, opts = {}) {
    const resp = await fetch(path, opts);
    return resp.json();
}

// ——— Load applications ———
async function loadApplications() {
    const data = await api("/api/applications");
    allApplications = data.applications;
    renderKanban();
}

function renderKanban() {
    const statuses = ["interested", "applied", "interview", "offer", "rejected"];
    const counts = {};

    statuses.forEach(s => {
        const col = document.getElementById(`col-${s}`);
        col.innerHTML = "";
        counts[s] = 0;
    });

    if (allApplications.length === 0) {
        document.getElementById("kanban-empty").style.display = "block";
        document.getElementById("kanban-board").style.display = "none";
        return;
    }

    document.getElementById("kanban-empty").style.display = "none";
    document.getElementById("kanban-board").style.display = "flex";

    allApplications.forEach(app => {
        const col = document.getElementById(`col-${app.status}`);
        if (!col) return;
        col.appendChild(createKanbanCard(app));
        counts[app.status] = (counts[app.status] || 0) + 1;
    });

    statuses.forEach(s => {
        document.getElementById(`count-${s}`).textContent = counts[s] || 0;
    });
}

// ——— Create kanban card ———
function createKanbanCard(app) {
    const card = document.createElement("div");
    card.className = "kanban-card";
    card.draggable = true;
    card.dataset.jobId = app.job_id;

    card.addEventListener("dragstart", (e) => {
        e.dataTransfer.setData("text/plain", app.job_id);
        card.classList.add("dragging");
    });
    card.addEventListener("dragend", () => card.classList.remove("dragging"));

    const dateSaved = app.date_saved ? new Date(app.date_saved).toLocaleDateString() : "";
    const dateApplied = app.date_applied ? `${t('applied-label')} ${app.date_applied}` : "";

    let reminderHtml = "";
    if (app.reminder_date) {
        const isOverdue = new Date(app.reminder_date) <= new Date();
        reminderHtml = `<div class="kanban-card-reminder">${isOverdue ? "\u26A0" : "\u23F0"} ${t('reminder-label')} ${app.reminder_date}</div>`;
    }

    card.innerHTML = `
        <a class="kanban-card-title" href="${escHtml(app.url)}" target="_blank" rel="noopener">
            ${escHtml(app.title)}
        </a>
        <div class="kanban-card-company">
            ${app.company ? escHtml(app.company) : ""}
            ${app.location ? ` \u2022 ${escHtml(app.location)}` : ""}
        </div>
        <div class="kanban-card-date">
            ${t('saved-label')} ${dateSaved}
            ${dateApplied ? ` \u2022 ${dateApplied}` : ""}
        </div>
        ${app.notes ? `<div class="kanban-card-notes">${escHtml(app.notes)}</div>` : ""}
        ${reminderHtml}
        <div class="kanban-card-actions">
            <button class="kanban-btn" onclick="openNotes(${app.job_id})">${escHtml(t('btn-notes'))}</button>
            <button class="kanban-btn" onclick="generateCoverLetter(${app.job_id}, '${escAttr(app.title)}')">${escHtml(t('btn-cover-letter'))}</button>
            <button class="kanban-btn danger" onclick="removeApp(${app.job_id})">${escHtml(t('btn-remove'))}</button>
        </div>
    `;

    return card;
}

// ——— Drag & Drop ———
async function kanbanDrop(e, newStatus) {
    e.preventDefault();
    e.currentTarget.classList.remove("drag-over");

    const jobId = e.dataTransfer.getData("text/plain");
    if (!jobId) return;

    const update = { status: newStatus };
    if (newStatus === "applied") {
        update.date_applied = new Date().toISOString().split("T")[0];
    }

    await api(`/api/applications/${jobId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(update),
    });

    await loadApplications();
}

// ——— Notes modal ———
function openNotes(jobId) {
    editingJobId = jobId;
    const app = allApplications.find(a => a.job_id === jobId);
    document.getElementById("notes-text").value = app?.notes || "";
    document.getElementById("notes-date-applied").value = app?.date_applied || "";
    document.getElementById("notes-reminder").value = app?.reminder_date || "";
    document.getElementById("notes-overlay").style.display = "flex";
}

function closeNotesModal() {
    document.getElementById("notes-overlay").style.display = "none";
    editingJobId = null;
}

async function saveNotes() {
    if (!editingJobId) return;
    const notes = document.getElementById("notes-text").value;
    const dateApplied = document.getElementById("notes-date-applied").value || null;
    const reminderDate = document.getElementById("notes-reminder").value || null;

    await api(`/api/applications/${editingJobId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notes, date_applied: dateApplied, reminder_date: reminderDate }),
    });

    closeNotesModal();
    await loadApplications();
}

// ——— Cover letter ———
async function generateCoverLetter(jobId, title) {
    document.getElementById("modal-title").textContent = `${t('modal-cover-letter')} \u2014 ${title}`;
    document.getElementById("modal-letter").textContent = t('generating-letter');
    document.getElementById("modal-overlay").style.display = "flex";

    try {
        const data = await api(`/api/cover-letter?job_id=${jobId}`);
        document.getElementById("modal-letter").textContent = data.letter;
    } catch (err) {
        document.getElementById("modal-letter").textContent = t('letter-error');
    }
}

function closeModal() {
    document.getElementById("modal-overlay").style.display = "none";
}

function copyLetter() {
    const text = document.getElementById("modal-letter").textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById("btn-copy-letter");
        btn.textContent = t('btn-copied');
        setTimeout(() => { btn.textContent = t('btn-copy'); }, 2000);
    });
}

// ——— Remove application ———
async function removeApp(jobId) {
    await api(`/api/applications/${jobId}`, { method: "DELETE" });
    await loadApplications();
}

// ——— Helpers ———
function escHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function escAttr(str) {
    return (str || "").replace(/'/g, "\\'").replace(/"/g, "&quot;");
}
