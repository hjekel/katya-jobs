// Katya's JobFinder — Feedback page

document.addEventListener("DOMContentLoaded", () => {
    loadFeedbackHistory();
});

function onLanguageChange() {
    loadFeedbackHistory();
}

async function submitFeedback(e) {
    e.preventDefault();
    const improve = document.getElementById("fb-improve").value.trim();
    const boards = document.getElementById("fb-boards").value.trim();
    const suggestions = document.getElementById("fb-suggestions").value.trim();

    if (!improve && !boards && !suggestions) return;

    await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ improve, job_boards: boards, suggestions }),
    });

    // Clear form
    document.getElementById("fb-improve").value = "";
    document.getElementById("fb-boards").value = "";
    document.getElementById("fb-suggestions").value = "";

    // Show success message
    const success = document.getElementById("feedback-success");
    success.style.display = "block";
    setTimeout(() => { success.style.display = "none"; }, 3000);

    // Reload history
    loadFeedbackHistory();
}

async function loadFeedbackHistory() {
    const resp = await fetch("/api/feedback");
    const data = await resp.json();
    const list = document.getElementById("feedback-list");
    const empty = document.getElementById("feedback-empty");

    const items = data.feedback || [];
    if (items.length === 0) {
        list.innerHTML = "";
        empty.style.display = "block";
        return;
    }

    empty.style.display = "none";
    list.innerHTML = items.map(fb => {
        const date = new Date(fb.created_at).toLocaleDateString();
        let content = "";
        if (fb.improve_text) content += `<div class="fb-section"><strong>${escHtml(t('feedback-improve-label'))}:</strong> ${escHtml(fb.improve_text)}</div>`;
        if (fb.job_boards_text) content += `<div class="fb-section"><strong>${escHtml(t('feedback-boards-label'))}:</strong> ${escHtml(fb.job_boards_text)}</div>`;
        if (fb.suggestions_text) content += `<div class="fb-section"><strong>${escHtml(t('feedback-suggestions-label'))}:</strong> ${escHtml(fb.suggestions_text)}</div>`;
        return `<div class="feedback-entry"><div class="feedback-entry-date">${escHtml(date)}</div>${content}</div>`;
    }).join("");
}

function escHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
