// Katya's JobFinder — Theme, Language & Ukraine Mode

// ===== Translations =====
const TRANSLATIONS = {
    en: {
        'site-title': "Katya's JobFinder",
        'nav-jobs': 'Jobs',
        'nav-applications': 'My Applications',
        'btn-scrape': 'Scan for Jobs',
        'jobs-count': '{n} jobs',
        'new-count': '{n} new',
        'filter-category': 'Category',
        'filter-location': 'Location',
        'filter-company': 'Company',
        'filter-source': 'Source',
        'btn-show-all': 'Show all ({n})',
        'btn-show-less': 'Show less',
        'btn-clear-filters': 'Clear all',
        'filter-label-category': 'Category',
        'filter-label-location': 'Location',
        'filter-label-company': 'Company',
        'filter-label-type': 'Type',
        'filter-label-source': 'Source',
        'type-direct': 'Direct employer',
        'type-recruiter': 'Via recruiter',
        'type-job_board': 'Job board',
        'chip-direct': 'Direct',
        'chip-recruiter': 'Via recruiter',
        'chip-job_board': 'Job board',
        'search-placeholder': 'Search jobs by title, company, or keyword...',
        'showing-jobs': 'Showing {shown} of {total} jobs',
        'showing-jobs-all': 'Showing {n} jobs',
        'no-jobs-found': 'No jobs found',
        'toggle-new': 'Show only new',
        'sort-label': 'Sort:',
        'sort-newest': 'Newest first',
        'sort-score': 'Best match',
        'sort-oldest': 'Oldest first',
        'btn-load-more': 'Load more',
        'btn-save': 'Save',
        'btn-saved': 'Saved!',
        'btn-already-saved': 'Already saved',
        'btn-hide': 'Hide',
        'btn-view': 'View \u2192',
        'salary-not-listed': 'Salary not listed',
        'commute-from': '\uD83D\uDE86 Commute from Haarlem',
        'get-directions': 'Get directions \u2192',
        'expand-hint': 'Click card to see why Katya fits',
        'analysing-fit': 'Analysing fit...',
        'fit-error': 'Could not load analysis.',
        'posted-on': 'Posted on {source}',
        'empty-title': 'No jobs yet',
        'empty-text': 'Click <strong>Scan for Jobs</strong> to search all job boards.',
        'scanning-text': 'Scanning 6 job boards... this may take a minute.',
        'scrape-done': 'Done! {details}',
        'scrape-running': 'Scrape is already running.',
        'scrape-error': 'Error scanning. Try again later.',
        'scrape-new': '{count} new',
        'col-interested': 'Interested',
        'col-applied': 'Applied',
        'col-interview': 'Interview',
        'col-offer': 'Offer',
        'col-rejected': 'Rejected',
        'btn-notes': 'Notes',
        'btn-cover-letter': 'Cover Letter',
        'btn-remove': 'Remove',
        'saved-label': 'Saved:',
        'applied-label': 'Applied:',
        'reminder-label': 'Reminder:',
        'modal-cover-letter': 'Cover Letter',
        'modal-edit-notes': 'Edit Notes',
        'notes-placeholder': 'Add your notes...',
        'label-date-applied': 'Date applied:',
        'label-reminder': 'Reminder date:',
        'btn-save-notes': 'Save',
        'btn-copy': 'Copy to clipboard',
        'btn-copied': 'Copied!',
        'generating-letter': 'Generating cover letter...',
        'letter-error': 'Error generating cover letter.',
        'kanban-empty-title': 'No saved applications',
        'kanban-empty-text': 'Go to <a href="/">Jobs</a> and click <strong>Save</strong> on jobs you\'re interested in.',
        'nav-feedback': 'Feedback',
        'filter-jobboards': 'Job Boards',
        'toggle-dutch': 'Hide jobs requiring Dutch',
        'add-board-placeholder': 'Add a job board...',
        'add-keyword-placeholder': 'Add search keyword...',
        'btn-add-keyword': 'Add',
        'score-breakdown-title': 'Score Breakdown',
        'score-total': 'Total',
        'feedback-title': 'Feedback',
        'feedback-subtitle': "Help us improve Katya's JobFinder",
        'feedback-improve-label': 'What would you like to improve?',
        'feedback-improve-placeholder': 'Tell us what could work better...',
        'feedback-boards-label': 'What job boards or websites should we add?',
        'feedback-boards-placeholder': 'e.g. Glassdoor, Nationale Vacaturebank...',
        'feedback-suggestions-label': 'Any other suggestions?',
        'feedback-suggestions-placeholder': "Anything else you'd like to tell us...",
        'feedback-submit': 'Send Feedback',
        'feedback-thanks': 'Thank you for your feedback!',
        'feedback-history-title': 'Previous Feedback',
        'feedback-empty': 'No feedback submitted yet.',
        'page-title-jobs': "Katya's JobFinder",
        'page-title-apps': "Katya's JobFinder \u2014 My Applications",
        'page-title-feedback': "Katya's JobFinder \u2014 Feedback",
    },
    ru: {
        'site-title': "\u041F\u043E\u0438\u0441\u043A \u0440\u0430\u0431\u043E\u0442\u044B \u041A\u0430\u0442\u0438",
        'nav-jobs': '\u0412\u0430\u043A\u0430\u043D\u0441\u0438\u0438',
        'nav-applications': '\u041C\u043E\u0438 \u0437\u0430\u044F\u0432\u043A\u0438',
        'btn-scrape': '\u041F\u043E\u0438\u0441\u043A \u0432\u0430\u043A\u0430\u043D\u0441\u0438\u0439',
        'jobs-count': '{n} \u0432\u0430\u043A\u0430\u043D\u0441\u0438\u0439',
        'new-count': '{n} \u043D\u043E\u0432\u044B\u0445',
        'filter-category': '\u041A\u0430\u0442\u0435\u0433\u043E\u0440\u0438\u044F',
        'filter-location': '\u041C\u0435\u0441\u0442\u043E\u043F\u043E\u043B\u043E\u0436\u0435\u043D\u0438\u0435',
        'filter-company': '\u041A\u043E\u043C\u043F\u0430\u043D\u0438\u044F',
        'filter-source': '\u0418\u0441\u0442\u043E\u0447\u043D\u0438\u043A',
        'btn-show-all': '\u041F\u043E\u043A\u0430\u0437\u0430\u0442\u044C \u0432\u0441\u0435 ({n})',
        'btn-show-less': '\u041F\u043E\u043A\u0430\u0437\u0430\u0442\u044C \u043C\u0435\u043D\u044C\u0448\u0435',
        'btn-clear-filters': '\u041E\u0447\u0438\u0441\u0442\u0438\u0442\u044C \u0432\u0441\u0435',
        'filter-label-category': '\u041A\u0430\u0442\u0435\u0433\u043E\u0440\u0438\u044F',
        'filter-label-location': '\u041C\u0435\u0441\u0442\u043E\u043F\u043E\u043B\u043E\u0436\u0435\u043D\u0438\u0435',
        'filter-label-company': '\u041A\u043E\u043C\u043F\u0430\u043D\u0438\u044F',
        'filter-label-type': '\u0422\u0438\u043F',
        'filter-label-source': '\u0418\u0441\u0442\u043E\u0447\u043D\u0438\u043A',
        'type-direct': '\u041F\u0440\u044F\u043C\u043E\u0439 \u0440\u0430\u0431\u043E\u0442\u043E\u0434\u0430\u0442\u0435\u043B\u044C',
        'type-recruiter': '\u0427\u0435\u0440\u0435\u0437 \u0440\u0435\u043A\u0440\u0443\u0442\u0435\u0440\u0430',
        'type-job_board': '\u0414\u043E\u0441\u043A\u0430 \u043E\u0431\u044A\u044F\u0432\u043B\u0435\u043D\u0438\u0439',
        'chip-direct': '\u041F\u0440\u044F\u043C\u043E\u0439',
        'chip-recruiter': '\u0427\u0435\u0440\u0435\u0437 \u0440\u0435\u043A\u0440\u0443\u0442\u0435\u0440\u0430',
        'chip-job_board': '\u0414\u043E\u0441\u043A\u0430 \u043E\u0431\u044A\u044F\u0432\u043B\u0435\u043D\u0438\u0439',
        'search-placeholder': '\u041F\u043E\u0438\u0441\u043A \u043F\u043E \u043D\u0430\u0437\u0432\u0430\u043D\u0438\u044E, \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438 \u0438\u043B\u0438 \u043A\u043B\u044E\u0447\u0435\u0432\u043E\u043C\u0443 \u0441\u043B\u043E\u0432\u0443...',
        'showing-jobs': '\u041F\u043E\u043A\u0430\u0437\u0430\u043D\u043E {shown} \u0438\u0437 {total} \u0432\u0430\u043A\u0430\u043D\u0441\u0438\u0439',
        'showing-jobs-all': '\u041F\u043E\u043A\u0430\u0437\u0430\u043D\u043E {n} \u0432\u0430\u043A\u0430\u043D\u0441\u0438\u0439',
        'no-jobs-found': '\u0412\u0430\u043A\u0430\u043D\u0441\u0438\u0438 \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D\u044B',
        'toggle-new': '\u0422\u043E\u043B\u044C\u043A\u043E \u043D\u043E\u0432\u044B\u0435',
        'sort-label': '\u0421\u043E\u0440\u0442\u0438\u0440\u043E\u0432\u043A\u0430:',
        'sort-newest': '\u0421\u043D\u0430\u0447\u0430\u043B\u0430 \u043D\u043E\u0432\u044B\u0435',
        'sort-score': '\u041B\u0443\u0447\u0448\u0435\u0435 \u0441\u043E\u0432\u043F\u0430\u0434\u0435\u043D\u0438\u0435',
        'sort-oldest': '\u0421\u043D\u0430\u0447\u0430\u043B\u0430 \u0441\u0442\u0430\u0440\u044B\u0435',
        'btn-load-more': '\u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u0435\u0449\u0451',
        'btn-save': '\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C',
        'btn-saved': '\u0421\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u043E!',
        'btn-already-saved': '\u0423\u0436\u0435 \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u043E',
        'btn-hide': '\u0421\u043A\u0440\u044B\u0442\u044C',
        'btn-view': '\u0421\u043C\u043E\u0442\u0440\u0435\u0442\u044C \u2192',
        'salary-not-listed': '\u0417\u0430\u0440\u043F\u043B\u0430\u0442\u0430 \u043D\u0435 \u0443\u043A\u0430\u0437\u0430\u043D\u0430',
        'commute-from': '\uD83D\uDE86 \u0414\u043E\u0440\u043E\u0433\u0430 \u0438\u0437 \u0425\u0430\u0440\u043B\u0435\u043C\u0430',
        'get-directions': '\u041C\u0430\u0440\u0448\u0440\u0443\u0442 \u2192',
        'expand-hint': '\u041D\u0430\u0436\u043C\u0438\u0442\u0435 \u043D\u0430 \u043A\u0430\u0440\u0442\u043E\u0447\u043A\u0443, \u0447\u0442\u043E\u0431\u044B \u0443\u0437\u043D\u0430\u0442\u044C \u043F\u043E\u0447\u0435\u043C\u0443 \u041A\u0430\u0442\u044F \u043F\u043E\u0434\u0445\u043E\u0434\u0438\u0442',
        'analysing-fit': '\u0410\u043D\u0430\u043B\u0438\u0437\u0438\u0440\u0443\u0435\u043C...',
        'fit-error': '\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u0430\u043D\u0430\u043B\u0438\u0437.',
        'posted-on': '\u0420\u0430\u0437\u043C\u0435\u0449\u0435\u043D\u043E \u043D\u0430 {source}',
        'empty-title': '\u041F\u043E\u043A\u0430 \u043D\u0435\u0442 \u0432\u0430\u043A\u0430\u043D\u0441\u0438\u0439',
        'empty-text': '\u041D\u0430\u0436\u043C\u0438\u0442\u0435 <strong>\u041F\u043E\u0438\u0441\u043A \u0432\u0430\u043A\u0430\u043D\u0441\u0438\u0439</strong>, \u0447\u0442\u043E\u0431\u044B \u043D\u0430\u0439\u0442\u0438 \u0440\u0430\u0431\u043E\u0442\u0443 \u043D\u0430 \u0432\u0441\u0435\u0445 \u0441\u0430\u0439\u0442\u0430\u0445.',
        'scanning-text': '\u0421\u043A\u0430\u043D\u0438\u0440\u0443\u0435\u043C 6 \u0441\u0430\u0439\u0442\u043E\u0432 \u0441 \u0432\u0430\u043A\u0430\u043D\u0441\u0438\u044F\u043C\u0438... \u044D\u0442\u043E \u043C\u043E\u0436\u0435\u0442 \u0437\u0430\u043D\u044F\u0442\u044C \u043C\u0438\u043D\u0443\u0442\u0443.',
        'scrape-done': '\u0413\u043E\u0442\u043E\u0432\u043E! {details}',
        'scrape-running': '\u041F\u043E\u0438\u0441\u043A \u0443\u0436\u0435 \u0437\u0430\u043F\u0443\u0449\u0435\u043D.',
        'scrape-error': '\u041E\u0448\u0438\u0431\u043A\u0430 \u0441\u043A\u0430\u043D\u0438\u0440\u043E\u0432\u0430\u043D\u0438\u044F. \u041F\u043E\u043F\u0440\u043E\u0431\u0443\u0439\u0442\u0435 \u043F\u043E\u0437\u0436\u0435.',
        'scrape-new': '{count} \u043D\u043E\u0432\u044B\u0445',
        'col-interested': '\u0418\u043D\u0442\u0435\u0440\u0435\u0441\u043D\u043E',
        'col-applied': '\u041E\u0442\u043A\u043B\u0438\u043A',
        'col-interview': '\u0421\u043E\u0431\u0435\u0441\u0435\u0434\u043E\u0432\u0430\u043D\u0438\u0435',
        'col-offer': '\u041E\u0444\u0444\u0435\u0440',
        'col-rejected': '\u041E\u0442\u043A\u0430\u0437',
        'btn-notes': '\u0417\u0430\u043C\u0435\u0442\u043A\u0438',
        'btn-cover-letter': '\u0421\u043E\u043F\u0440\u043E\u0432\u043E\u0434\u0438\u0442\u0435\u043B\u044C\u043D\u043E\u0435',
        'btn-remove': '\u0423\u0434\u0430\u043B\u0438\u0442\u044C',
        'saved-label': '\u0421\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u043E:',
        'applied-label': '\u041E\u0442\u043A\u043B\u0438\u043A:',
        'reminder-label': '\u041D\u0430\u043F\u043E\u043C\u0438\u043D\u0430\u043D\u0438\u0435:',
        'modal-cover-letter': '\u0421\u043E\u043F\u0440\u043E\u0432\u043E\u0434\u0438\u0442\u0435\u043B\u044C\u043D\u043E\u0435 \u043F\u0438\u0441\u044C\u043C\u043E',
        'modal-edit-notes': '\u0420\u0435\u0434\u0430\u043A\u0442\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u0437\u0430\u043C\u0435\u0442\u043A\u0438',
        'notes-placeholder': '\u0414\u043E\u0431\u0430\u0432\u044C\u0442\u0435 \u0437\u0430\u043C\u0435\u0442\u043A\u0438...',
        'label-date-applied': '\u0414\u0430\u0442\u0430 \u043E\u0442\u043A\u043B\u0438\u043A\u0430:',
        'label-reminder': '\u0414\u0430\u0442\u0430 \u043D\u0430\u043F\u043E\u043C\u0438\u043D\u0430\u043D\u0438\u044F:',
        'btn-save-notes': '\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C',
        'btn-copy': '\u0421\u043A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C',
        'btn-copied': '\u0421\u043A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u043D\u043E!',
        'generating-letter': '\u0413\u0435\u043D\u0435\u0440\u0438\u0440\u0443\u0435\u043C \u0441\u043E\u043F\u0440\u043E\u0432\u043E\u0434\u0438\u0442\u0435\u043B\u044C\u043D\u043E\u0435...',
        'letter-error': '\u041E\u0448\u0438\u0431\u043A\u0430 \u0433\u0435\u043D\u0435\u0440\u0430\u0446\u0438\u0438 \u043F\u0438\u0441\u044C\u043C\u0430.',
        'kanban-empty-title': '\u041D\u0435\u0442 \u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u044B\u0445 \u0437\u0430\u044F\u0432\u043E\u043A',
        'kanban-empty-text': '\u041F\u0435\u0440\u0435\u0439\u0434\u0438\u0442\u0435 \u043D\u0430 <a href="/">\u0412\u0430\u043A\u0430\u043D\u0441\u0438\u0438</a> \u0438 \u043D\u0430\u0436\u043C\u0438\u0442\u0435 <strong>\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C</strong> \u043D\u0430 \u0438\u043D\u0442\u0435\u0440\u0435\u0441\u043D\u044B\u0445 \u0432\u0430\u043A\u0430\u043D\u0441\u0438\u044F\u0445.',
        'nav-feedback': '\u041E\u0442\u0437\u044B\u0432\u044B',
        'filter-jobboards': '\u0421\u0430\u0439\u0442\u044B \u0432\u0430\u043A\u0430\u043D\u0441\u0438\u0439',
        'toggle-dutch': '\u0421\u043A\u0440\u044B\u0442\u044C \u0432\u0430\u043A\u0430\u043D\u0441\u0438\u0438, \u0442\u0440\u0435\u0431\u0443\u044E\u0449\u0438\u0435 \u0433\u043E\u043B\u043B\u0430\u043D\u0434\u0441\u043A\u0438\u0439',
        'add-board-placeholder': '\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u0441\u0430\u0439\u0442 \u0432\u0430\u043A\u0430\u043D\u0441\u0438\u0439...',
        'add-keyword-placeholder': '\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u043A\u043B\u044E\u0447\u0435\u0432\u043E\u0435 \u0441\u043B\u043E\u0432\u043E...',
        'btn-add-keyword': '\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C',
        'score-breakdown-title': '\u0420\u0430\u0437\u0431\u043E\u0440 \u043E\u0446\u0435\u043D\u043A\u0438',
        'score-total': '\u0418\u0442\u043E\u0433\u043E',
        'feedback-title': '\u041E\u0442\u0437\u044B\u0432\u044B',
        'feedback-subtitle': '\u041F\u043E\u043C\u043E\u0433\u0438\u0442\u0435 \u043D\u0430\u043C \u0443\u043B\u0443\u0447\u0448\u0438\u0442\u044C \u043F\u043E\u0438\u0441\u043A \u0440\u0430\u0431\u043E\u0442\u044B',
        'feedback-improve-label': '\u0427\u0442\u043E \u0431\u044B \u0432\u044B \u0445\u043E\u0442\u0435\u043B\u0438 \u0443\u043B\u0443\u0447\u0448\u0438\u0442\u044C?',
        'feedback-improve-placeholder': '\u0420\u0430\u0441\u0441\u043A\u0430\u0436\u0438\u0442\u0435, \u0447\u0442\u043E \u043C\u043E\u0436\u043D\u043E \u0441\u0434\u0435\u043B\u0430\u0442\u044C \u043B\u0443\u0447\u0448\u0435...',
        'feedback-boards-label': '\u041A\u0430\u043A\u0438\u0435 \u0441\u0430\u0439\u0442\u044B \u0432\u0430\u043A\u0430\u043D\u0441\u0438\u0439 \u0434\u043E\u0431\u0430\u0432\u0438\u0442\u044C?',
        'feedback-boards-placeholder': '\u043D\u0430\u043F\u0440. Glassdoor, Nationale Vacaturebank...',
        'feedback-suggestions-label': '\u0414\u0440\u0443\u0433\u0438\u0435 \u043F\u0440\u0435\u0434\u043B\u043E\u0436\u0435\u043D\u0438\u044F?',
        'feedback-suggestions-placeholder': '\u0427\u0442\u043E-\u043D\u0438\u0431\u0443\u0434\u044C \u0435\u0449\u0451...',
        'feedback-submit': '\u041E\u0442\u043F\u0440\u0430\u0432\u0438\u0442\u044C \u043E\u0442\u0437\u044B\u0432',
        'feedback-thanks': '\u0421\u043F\u0430\u0441\u0438\u0431\u043E \u0437\u0430 \u0432\u0430\u0448 \u043E\u0442\u0437\u044B\u0432!',
        'feedback-history-title': '\u041F\u0440\u0435\u0434\u044B\u0434\u0443\u0449\u0438\u0435 \u043E\u0442\u0437\u044B\u0432\u044B',
        'feedback-empty': '\u041F\u043E\u043A\u0430 \u043D\u0435\u0442 \u043E\u0442\u0437\u044B\u0432\u043E\u0432.',
        'page-title-jobs': "\u041F\u043E\u0438\u0441\u043A \u0440\u0430\u0431\u043E\u0442\u044B \u041A\u0430\u0442\u0438",
        'page-title-apps': "\u041F\u043E\u0438\u0441\u043A \u0440\u0430\u0431\u043E\u0442\u044B \u041A\u0430\u0442\u0438 \u2014 \u041C\u043E\u0438 \u0437\u0430\u044F\u0432\u043A\u0438",
        'page-title-feedback': "\u041F\u043E\u0438\u0441\u043A \u0440\u0430\u0431\u043E\u0442\u044B \u041A\u0430\u0442\u0438 \u2014 \u041E\u0442\u0437\u044B\u0432\u044B",
    },
    ua: {
        'site-title': "\u041F\u043E\u0448\u0443\u043A \u0440\u043E\u0431\u043E\u0442\u0438 \u041A\u0430\u0442\u0456",
        'nav-jobs': '\u0412\u0430\u043A\u0430\u043D\u0441\u0456\u0457',
        'nav-applications': '\u041C\u043E\u0457 \u0437\u0430\u044F\u0432\u043A\u0438',
        'btn-scrape': '\u041F\u043E\u0448\u0443\u043A \u0432\u0430\u043A\u0430\u043D\u0441\u0456\u0439',
        'jobs-count': '{n} \u0432\u0430\u043A\u0430\u043D\u0441\u0456\u0439',
        'new-count': '{n} \u043D\u043E\u0432\u0438\u0445',
        'filter-category': '\u041A\u0430\u0442\u0435\u0433\u043E\u0440\u0456\u044F',
        'filter-location': '\u041C\u0456\u0441\u0446\u0435\u0437\u043D\u0430\u0445\u043E\u0434\u0436\u0435\u043D\u043D\u044F',
        'filter-company': '\u041A\u043E\u043C\u043F\u0430\u043D\u0456\u044F',
        'filter-source': '\u0414\u0436\u0435\u0440\u0435\u043B\u043E',
        'btn-show-all': '\u041F\u043E\u043A\u0430\u0437\u0430\u0442\u0438 \u0432\u0441\u0435 ({n})',
        'btn-show-less': '\u041F\u043E\u043A\u0430\u0437\u0430\u0442\u0438 \u043C\u0435\u043D\u0448\u0435',
        'btn-clear-filters': '\u041E\u0447\u0438\u0441\u0442\u0438\u0442\u0438 \u0432\u0441\u0435',
        'filter-label-category': '\u041A\u0430\u0442\u0435\u0433\u043E\u0440\u0456\u044F',
        'filter-label-location': '\u041C\u0456\u0441\u0446\u0435\u0437\u043D\u0430\u0445\u043E\u0434\u0436\u0435\u043D\u043D\u044F',
        'filter-label-company': '\u041A\u043E\u043C\u043F\u0430\u043D\u0456\u044F',
        'filter-label-type': '\u0422\u0438\u043F',
        'filter-label-source': '\u0414\u0436\u0435\u0440\u0435\u043B\u043E',
        'type-direct': '\u041F\u0440\u044F\u043C\u0438\u0439 \u0440\u043E\u0431\u043E\u0442\u043E\u0434\u0430\u0432\u0435\u0446\u044C',
        'type-recruiter': '\u0427\u0435\u0440\u0435\u0437 \u0440\u0435\u043A\u0440\u0443\u0442\u0435\u0440\u0430',
        'type-job_board': '\u0414\u043E\u0448\u043A\u0430 \u043E\u0433\u043E\u043B\u043E\u0448\u0435\u043D\u044C',
        'chip-direct': '\u041F\u0440\u044F\u043C\u0438\u0439',
        'chip-recruiter': '\u0427\u0435\u0440\u0435\u0437 \u0440\u0435\u043A\u0440\u0443\u0442\u0435\u0440\u0430',
        'chip-job_board': '\u0414\u043E\u0448\u043A\u0430 \u043E\u0433\u043E\u043B\u043E\u0448\u0435\u043D\u044C',
        'search-placeholder': '\u041F\u043E\u0448\u0443\u043A \u0437\u0430 \u043D\u0430\u0437\u0432\u043E\u044E, \u043A\u043E\u043C\u043F\u0430\u043D\u0456\u0454\u044E \u0430\u0431\u043E \u043A\u043B\u044E\u0447\u043E\u0432\u0438\u043C \u0441\u043B\u043E\u0432\u043E\u043C...',
        'showing-jobs': '\u041F\u043E\u043A\u0430\u0437\u0430\u043D\u043E {shown} \u0437 {total} \u0432\u0430\u043A\u0430\u043D\u0441\u0456\u0439',
        'showing-jobs-all': '\u041F\u043E\u043A\u0430\u0437\u0430\u043D\u043E {n} \u0432\u0430\u043A\u0430\u043D\u0441\u0456\u0439',
        'no-jobs-found': '\u0412\u0430\u043A\u0430\u043D\u0441\u0456\u0457 \u043D\u0435 \u0437\u043D\u0430\u0439\u0434\u0435\u043D\u043E',
        'toggle-new': '\u041B\u0438\u0448\u0435 \u043D\u043E\u0432\u0456',
        'sort-label': '\u0421\u043E\u0440\u0442\u0443\u0432\u0430\u043D\u043D\u044F:',
        'sort-newest': '\u0421\u043F\u043E\u0447\u0430\u0442\u043A\u0443 \u043D\u043E\u0432\u0456',
        'sort-score': '\u041D\u0430\u0439\u043A\u0440\u0430\u0449\u0438\u0439 \u0437\u0431\u0456\u0433',
        'sort-oldest': '\u0421\u043F\u043E\u0447\u0430\u0442\u043A\u0443 \u0441\u0442\u0430\u0440\u0456',
        'btn-load-more': '\u0417\u0430\u0432\u0430\u043D\u0442\u0430\u0436\u0438\u0442\u0438 \u0449\u0435',
        'btn-save': '\u0417\u0431\u0435\u0440\u0435\u0433\u0442\u0438',
        'btn-saved': '\u0417\u0431\u0435\u0440\u0435\u0436\u0435\u043D\u043E!',
        'btn-already-saved': '\u0412\u0436\u0435 \u0437\u0431\u0435\u0440\u0435\u0436\u0435\u043D\u043E',
        'btn-hide': '\u041F\u0440\u0438\u0445\u043E\u0432\u0430\u0442\u0438',
        'btn-view': '\u0414\u0438\u0432\u0438\u0442\u0438\u0441\u044C \u2192',
        'salary-not-listed': '\u0417\u0430\u0440\u043F\u043B\u0430\u0442\u0430 \u043D\u0435 \u0432\u043A\u0430\u0437\u0430\u043D\u0430',
        'commute-from': '\uD83D\uDE86 \u0414\u043E\u0440\u043E\u0433\u0430 \u0437 \u0425\u0430\u0440\u043B\u0435\u043C\u0430',
        'get-directions': '\u041C\u0430\u0440\u0448\u0440\u0443\u0442 \u2192',
        'expand-hint': '\u041D\u0430\u0442\u0438\u0441\u043D\u0456\u0442\u044C \u043D\u0430 \u043A\u0430\u0440\u0442\u043A\u0443, \u0449\u043E\u0431 \u0434\u0456\u0437\u043D\u0430\u0442\u0438\u0441\u044F \u0447\u043E\u043C\u0443 \u041A\u0430\u0442\u044F \u043F\u0456\u0434\u0445\u043E\u0434\u0438\u0442\u044C',
        'analysing-fit': '\u0410\u043D\u0430\u043B\u0456\u0437\u0443\u0454\u043C\u043E...',
        'fit-error': '\u041D\u0435 \u0432\u0434\u0430\u043B\u043E\u0441\u044F \u0437\u0430\u0432\u0430\u043D\u0442\u0430\u0436\u0438\u0442\u0438 \u0430\u043D\u0430\u043B\u0456\u0437.',
        'posted-on': '\u0420\u043E\u0437\u043C\u0456\u0449\u0435\u043D\u043E \u043D\u0430 {source}',
        'empty-title': '\u041F\u043E\u043A\u0438 \u043D\u0435\u043C\u0430\u0454 \u0432\u0430\u043A\u0430\u043D\u0441\u0456\u0439',
        'empty-text': '\u041D\u0430\u0442\u0438\u0441\u043D\u0456\u0442\u044C <strong>\u041F\u043E\u0448\u0443\u043A \u0432\u0430\u043A\u0430\u043D\u0441\u0456\u0439</strong>, \u0449\u043E\u0431 \u0437\u043D\u0430\u0439\u0442\u0438 \u0440\u043E\u0431\u043E\u0442\u0443 \u043D\u0430 \u0432\u0441\u0456\u0445 \u0441\u0430\u0439\u0442\u0430\u0445.',
        'scanning-text': '\u0421\u043A\u0430\u043D\u0443\u0454\u043C\u043E 6 \u0441\u0430\u0439\u0442\u0456\u0432 \u0437 \u0432\u0430\u043A\u0430\u043D\u0441\u0456\u044F\u043C\u0438... \u0446\u0435 \u043C\u043E\u0436\u0435 \u0437\u0430\u0439\u043D\u044F\u0442\u0438 \u0445\u0432\u0438\u043B\u0438\u043D\u0443.',
        'scrape-done': '\u0413\u043E\u0442\u043E\u0432\u043E! {details}',
        'scrape-running': '\u041F\u043E\u0448\u0443\u043A \u0432\u0436\u0435 \u0437\u0430\u043F\u0443\u0449\u0435\u043D\u043E.',
        'scrape-error': '\u041F\u043E\u043C\u0438\u043B\u043A\u0430 \u0441\u043A\u0430\u043D\u0443\u0432\u0430\u043D\u043D\u044F. \u0421\u043F\u0440\u043E\u0431\u0443\u0439\u0442\u0435 \u043F\u0456\u0437\u043D\u0456\u0448\u0435.',
        'scrape-new': '{count} \u043D\u043E\u0432\u0438\u0445',
        'col-interested': '\u0426\u0456\u043A\u0430\u0432\u043E',
        'col-applied': '\u0412\u0456\u0434\u0433\u0443\u043A',
        'col-interview': '\u0421\u043F\u0456\u0432\u0431\u0435\u0441\u0456\u0434\u0430',
        'col-offer': '\u041E\u0444\u0444\u0435\u0440',
        'col-rejected': '\u0412\u0456\u0434\u043C\u043E\u0432\u0430',
        'btn-notes': '\u041D\u043E\u0442\u0430\u0442\u043A\u0438',
        'btn-cover-letter': '\u0421\u0443\u043F\u0440\u043E\u0432\u0456\u0434\u043D\u0438\u0439 \u043B\u0438\u0441\u0442',
        'btn-remove': '\u0412\u0438\u0434\u0430\u043B\u0438\u0442\u0438',
        'saved-label': '\u0417\u0431\u0435\u0440\u0435\u0436\u0435\u043D\u043E:',
        'applied-label': '\u0412\u0456\u0434\u0433\u0443\u043A:',
        'reminder-label': '\u041D\u0430\u0433\u0430\u0434\u0443\u0432\u0430\u043D\u043D\u044F:',
        'modal-cover-letter': '\u0421\u0443\u043F\u0440\u043E\u0432\u0456\u0434\u043D\u0438\u0439 \u043B\u0438\u0441\u0442',
        'modal-edit-notes': '\u0420\u0435\u0434\u0430\u0433\u0443\u0432\u0430\u0442\u0438 \u043D\u043E\u0442\u0430\u0442\u043A\u0438',
        'notes-placeholder': '\u0414\u043E\u0434\u0430\u0439\u0442\u0435 \u043D\u043E\u0442\u0430\u0442\u043A\u0438...',
        'label-date-applied': '\u0414\u0430\u0442\u0430 \u0432\u0456\u0434\u0433\u0443\u043A\u0443:',
        'label-reminder': '\u0414\u0430\u0442\u0430 \u043D\u0430\u0433\u0430\u0434\u0443\u0432\u0430\u043D\u043D\u044F:',
        'btn-save-notes': '\u0417\u0431\u0435\u0440\u0435\u0433\u0442\u0438',
        'btn-copy': '\u0421\u043A\u043E\u043F\u0456\u044E\u0432\u0430\u0442\u0438',
        'btn-copied': '\u0421\u043A\u043E\u043F\u0456\u0439\u043E\u0432\u0430\u043D\u043E!',
        'generating-letter': '\u0413\u0435\u043D\u0435\u0440\u0443\u0454\u043C\u043E \u0441\u0443\u043F\u0440\u043E\u0432\u0456\u0434\u043D\u0438\u0439 \u043B\u0438\u0441\u0442...',
        'letter-error': '\u041F\u043E\u043C\u0438\u043B\u043A\u0430 \u0433\u0435\u043D\u0435\u0440\u0430\u0446\u0456\u0457 \u043B\u0438\u0441\u0442\u0430.',
        'kanban-empty-title': '\u041D\u0435\u043C\u0430\u0454 \u0437\u0431\u0435\u0440\u0435\u0436\u0435\u043D\u0438\u0445 \u0437\u0430\u044F\u0432\u043E\u043A',
        'kanban-empty-text': '\u041F\u0435\u0440\u0435\u0439\u0434\u0456\u0442\u044C \u043D\u0430 <a href="/">\u0412\u0430\u043A\u0430\u043D\u0441\u0456\u0457</a> \u0456 \u043D\u0430\u0442\u0438\u0441\u043D\u0456\u0442\u044C <strong>\u0417\u0431\u0435\u0440\u0435\u0433\u0442\u0438</strong> \u043D\u0430 \u0446\u0456\u043A\u0430\u0432\u0438\u0445 \u0432\u0430\u043A\u0430\u043D\u0441\u0456\u044F\u0445.',
        'nav-feedback': '\u0412\u0456\u0434\u0433\u0443\u043A\u0438',
        'filter-jobboards': '\u0421\u0430\u0439\u0442\u0438 \u0432\u0430\u043A\u0430\u043D\u0441\u0456\u0439',
        'toggle-dutch': '\u0421\u0445\u043E\u0432\u0430\u0442\u0438 \u0432\u0430\u043A\u0430\u043D\u0441\u0456\u0457, \u0449\u043E \u0432\u0438\u043C\u0430\u0433\u0430\u044E\u0442\u044C \u0433\u043E\u043B\u043B\u0430\u043D\u0434\u0441\u044C\u043A\u0443',
        'add-board-placeholder': '\u0414\u043E\u0434\u0430\u0442\u0438 \u0441\u0430\u0439\u0442 \u0432\u0430\u043A\u0430\u043D\u0441\u0456\u0439...',
        'add-keyword-placeholder': '\u0414\u043E\u0434\u0430\u0442\u0438 \u043A\u043B\u044E\u0447\u043E\u0432\u0435 \u0441\u043B\u043E\u0432\u043E...',
        'btn-add-keyword': '\u0414\u043E\u0434\u0430\u0442\u0438',
        'score-breakdown-title': '\u0420\u043E\u0437\u0431\u0456\u0440 \u043E\u0446\u0456\u043D\u043A\u0438',
        'score-total': '\u0412\u0441\u044C\u043E\u0433\u043E',
        'feedback-title': '\u0412\u0456\u0434\u0433\u0443\u043A\u0438',
        'feedback-subtitle': '\u0414\u043E\u043F\u043E\u043C\u043E\u0436\u0456\u0442\u044C \u043D\u0430\u043C \u043F\u043E\u043A\u0440\u0430\u0449\u0438\u0442\u0438 \u043F\u043E\u0448\u0443\u043A \u0440\u043E\u0431\u043E\u0442\u0438',
        'feedback-improve-label': '\u0429\u043E \u0431 \u0432\u0438 \u0445\u043E\u0442\u0456\u043B\u0438 \u043F\u043E\u043A\u0440\u0430\u0449\u0438\u0442\u0438?',
        'feedback-improve-placeholder': '\u0420\u043E\u0437\u043A\u0430\u0436\u0456\u0442\u044C, \u0449\u043E \u043C\u043E\u0436\u043D\u0430 \u0437\u0440\u043E\u0431\u0438\u0442\u0438 \u043A\u0440\u0430\u0449\u0435...',
        'feedback-boards-label': '\u042F\u043A\u0456 \u0441\u0430\u0439\u0442\u0438 \u0432\u0430\u043A\u0430\u043D\u0441\u0456\u0439 \u0434\u043E\u0434\u0430\u0442\u0438?',
        'feedback-boards-placeholder': '\u043D\u0430\u043F\u0440. Glassdoor, Nationale Vacaturebank...',
        'feedback-suggestions-label': '\u0406\u043D\u0448\u0456 \u043F\u0440\u043E\u043F\u043E\u0437\u0438\u0446\u0456\u0457?',
        'feedback-suggestions-placeholder': '\u0411\u0443\u0434\u044C-\u0449\u043E \u0456\u043D\u0448\u0435...',
        'feedback-submit': '\u041D\u0430\u0434\u0456\u0441\u043B\u0430\u0442\u0438 \u0432\u0456\u0434\u0433\u0443\u043A',
        'feedback-thanks': '\u0414\u044F\u043A\u0443\u0454\u043C\u043E \u0437\u0430 \u0432\u0430\u0448 \u0432\u0456\u0434\u0433\u0443\u043A!',
        'feedback-history-title': '\u041F\u043E\u043F\u0435\u0440\u0435\u0434\u043D\u0456 \u0432\u0456\u0434\u0433\u0443\u043A\u0438',
        'feedback-empty': '\u041F\u043E\u043A\u0438 \u043D\u0435\u043C\u0430\u0454 \u0432\u0456\u0434\u0433\u0443\u043A\u0456\u0432.',
        'page-title-jobs': "\u041F\u043E\u0448\u0443\u043A \u0440\u043E\u0431\u043E\u0442\u0438 \u041A\u0430\u0442\u0456",
        'page-title-apps': "\u041F\u043E\u0448\u0443\u043A \u0440\u043E\u0431\u043E\u0442\u0438 \u041A\u0430\u0442\u0456 \u2014 \u041C\u043E\u0457 \u0437\u0430\u044F\u0432\u043A\u0438",
        'page-title-feedback': "\u041F\u043E\u0448\u0443\u043A \u0440\u043E\u0431\u043E\u0442\u0438 \u041A\u0430\u0442\u0456 \u2014 \u0412\u0456\u0434\u0433\u0443\u043A\u0438",
    },
};

// ===== Cookie helpers =====
function setCookie(name, value, days) {
    const d = new Date();
    d.setTime(d.getTime() + (days || 365) * 24 * 60 * 60 * 1000);
    document.cookie = name + '=' + value + ';expires=' + d.toUTCString() + ';path=/;SameSite=Lax';
}

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : null;
}

// ===== Current state =====
let currentLang = getCookie('lang') || 'en';
let darkMode = getCookie('darkMode') === 'true';
let ukraineMode = getCookie('ukraineMode') === 'true';

// ===== Translation function =====
function t(key, params) {
    let text = (TRANSLATIONS[currentLang] && TRANSLATIONS[currentLang][key]) || TRANSLATIONS.en[key] || key;
    if (params) {
        for (const k of Object.keys(params)) {
            text = text.replace('{' + k + '}', params[k]);
        }
    }
    return text;
}

// ===== Apply translations to static HTML =====
function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(function(el) {
        el.textContent = t(el.getAttribute('data-i18n'));
    });
    document.querySelectorAll('[data-i18n-html]').forEach(function(el) {
        el.innerHTML = t(el.getAttribute('data-i18n-html'));
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el) {
        el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
    });
    // Update page title
    if (document.querySelector('.kanban-main')) {
        document.title = t('page-title-apps');
    } else if (document.querySelector('.feedback-main')) {
        document.title = t('page-title-feedback');
    } else {
        document.title = t('page-title-jobs');
    }
}

// ===== Dark mode =====
function applyTheme() {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    var btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = darkMode ? '\u2600\uFE0F' : '\uD83C\uDF19';
}

function toggleDarkMode() {
    darkMode = !darkMode;
    setCookie('darkMode', darkMode);
    applyTheme();
}

// ===== Ukraine mode =====
function applyUkraineMode() {
    var btn = document.getElementById('ukraine-toggle');
    if (currentLang === 'ua') {
        if (btn) btn.style.display = '';
        if (ukraineMode) {
            document.body.classList.add('ukraine-mode');
        } else {
            document.body.classList.remove('ukraine-mode');
        }
    } else {
        if (btn) btn.style.display = 'none';
        document.body.classList.remove('ukraine-mode');
    }
    var uaBtn = document.getElementById('ukraine-toggle');
    if (uaBtn) uaBtn.classList.toggle('active', ukraineMode && currentLang === 'ua');
}

function toggleUkraineMode() {
    ukraineMode = !ukraineMode;
    setCookie('ukraineMode', ukraineMode);
    applyUkraineMode();
}

// ===== Language switcher =====
function setLanguage(lang) {
    currentLang = lang;
    setCookie('lang', lang);
    document.querySelectorAll('.lang-btn').forEach(function(btn) {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });
    applyTranslations();
    applyUkraineMode();
    // Trigger page-specific re-render
    if (typeof onLanguageChange === 'function') {
        onLanguageChange();
    }
}

// ===== Init on DOM ready =====
function initTheme() {
    applyTheme();
    // Set active lang button
    document.querySelectorAll('.lang-btn').forEach(function(btn) {
        btn.classList.toggle('active', btn.dataset.lang === currentLang);
        btn.addEventListener('click', function() { setLanguage(btn.dataset.lang); });
    });
    // Theme toggle
    var themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) themeBtn.addEventListener('click', toggleDarkMode);
    // Ukraine toggle
    var uaBtn = document.getElementById('ukraine-toggle');
    if (uaBtn) uaBtn.addEventListener('click', toggleUkraineMode);
    applyUkraineMode();
    applyTranslations();
}

document.addEventListener('DOMContentLoaded', initTheme);
