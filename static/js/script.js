// ============================================
// UPLOAD PAGE FUNCTIONALITY
// ============================================

function initUploadHandlers() {
    const fileInput = document.getElementById('file-upload');
    const dropZoneLabel = document.getElementById('dropZoneLabel');
    const uploadPrompt = document.getElementById('upload-prompt');
    const fileSelectedState = document.getElementById('file-selected-state');
    const selectedFileName = document.getElementById('selected-file-name');
    const submitBtn = document.getElementById('submitBtn');
    const errorAlert = document.getElementById('errorAlert');
    const successAlert = document.getElementById('successAlert');

    const ALLOWED = ['py', 'java', 'js', 'css', 'html'];

    if (!dropZoneLabel) return; // Exit if not on upload page

    // Drag and drop on the label
    dropZoneLabel.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZoneLabel.classList.add('drag-over');
    });

    dropZoneLabel.addEventListener('dragleave', () => {
        dropZoneLabel.classList.remove('drag-over');
    });

    dropZoneLabel.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZoneLabel.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect();
        }
    });

    fileInput.addEventListener('change', handleFileSelect);

    function handleFileSelect() {
        hideAlerts();
        const file = fileInput.files[0];
        if (!file) return;

        const ext = file.name.split('.').pop().toLowerCase();
        if (!ALLOWED.includes(ext)) {
            showError('Invalid file type. Allowed: .' + ALLOWED.join(', .'));
            fileInput.value = '';
            return;
        }

        selectedFileName.textContent = file.name;
        uploadPrompt.classList.add('hidden');
        fileSelectedState.classList.remove('hidden');
        fileSelectedState.classList.add('flex');
        submitBtn.disabled = false;
    }

    window.uploadFile = async function() {
        const file = fileInput.files[0];
        if (!file) {
            showError('Please select a file.');
            return;
        }

        hideAlerts();
        submitBtn.disabled = true;
        submitBtn.textContent = 'Uploading...';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', { method: 'POST', body: formData });
            const data = await response.json();

            if (response.ok && data.file_id) {
                showSuccess('Upload successful! Redirecting to analysis...');
                submitBtn.textContent = 'Success!';
                setTimeout(() => { window.location.href = '/analyze/' + data.file_id; }, 1200);
            } else {
                showError(data.error || 'Upload failed. Please try again.');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Confirm Source Code';
            }
        } catch (err) {
            showError('Network error. Please try again.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Confirm Source Code';
        }
    };

    function showError(msg) {
        errorAlert.textContent = msg;
        errorAlert.classList.remove('hidden');
        successAlert.classList.add('hidden');
    }

    function showSuccess(msg) {
        successAlert.textContent = msg;
        successAlert.classList.remove('hidden');
        errorAlert.classList.add('hidden');
    }

    function hideAlerts() {
        errorAlert.classList.add('hidden');
        successAlert.classList.add('hidden');
    }
}

// ============================================
// DASHBOARD PAGE FUNCTIONALITY
// ============================================

function initDashboardHandlers() {
    const deleteModal = document.getElementById('delete-modal');
    if (!deleteModal) return; // Exit if not on dashboard page

    window.confirmDelete = function(fileId, filename) {
        document.getElementById('modal-filename').textContent = filename;
        document.getElementById('delete-form').action = '/delete/' + fileId;
        document.getElementById('delete-modal').classList.remove('hidden');
    };

    window.closeModal = function() {
        document.getElementById('delete-modal').classList.add('hidden');
    };

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeModal();
    });
}

// ============================================
// RESULTS PAGE FUNCTIONALITY
// ============================================

function initResultsHandlers() {
    document.addEventListener('DOMContentLoaded', () => {
        const issueRows = document.querySelectorAll('.issue-row');
        if (issueRows.length === 0) return; // Exit if not on results page

        issueRows.forEach(el => {
            el.addEventListener('click', () => {
                const issue = el.dataset.issue;
                if (!issue) return;
                try {
                    navigator.clipboard.writeText(issue);
                } catch (e) {
                    // ignore if clipboard unavailable
                }
                alert('Issue details copied to clipboard:\n\n' + issue);
            });
        });
    });
}

// ============================================
// SETTINGS PAGE FUNCTIONALITY
// ============================================

function initSettingsHandlers() {
    const avatarInput = document.getElementById('avatar-input');
    if (!avatarInput) return; // Exit if not on settings page

    const avatarPreview = document.getElementById('avatar-preview');
    const avatarFallback = document.getElementById('avatar-preview-fallback');

    window.previewAvatar = function(input) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                if (avatarPreview) {
                    avatarPreview.src = e.target.result;
                    avatarPreview.classList.remove('hidden');
                }
                if (avatarFallback) avatarFallback.classList.add('hidden');
            };
            reader.readAsDataURL(input.files[0]);
            // Cancel any pending removal if a new file is chosen
            document.getElementById('remove-avatar-flag').value = '0';
            const btn = document.getElementById('remove-avatar-btn');
            if (btn) btn.classList.remove('hidden');
        }
    };

    window.removeAvatar = function() {
        // Set removal flag
        document.getElementById('remove-avatar-flag').value = '1';
        // Show initial fallback and hide image preview
        if (avatarPreview) {
            avatarPreview.src = '';
            avatarPreview.classList.add('hidden');
        }
        if (avatarFallback) avatarFallback.classList.remove('hidden');
        // Clear the file input
        document.getElementById('avatar-input').value = '';
        // Hide the remove button
        const btn = document.getElementById('remove-avatar-btn');
        if (btn) btn.classList.add('hidden');
    };
}

// ============================================
// INITIALIZE ALL HANDLERS ON PAGE LOAD
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initUploadHandlers();
    initDashboardHandlers();
    initResultsHandlers();
    initSettingsHandlers();
});
