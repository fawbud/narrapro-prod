/**
 * JavaScript to handle dynamic education forms functionality
 * Works for both registration and edit profile forms
 */

// Define global initialization function for education forms
window.initializeEducationForms = function(container) {
    console.log('initializeEducationForms called with container:', container);

    const maxEducation = 5;
    const addButton = container.querySelector('#add-education-btn');
    const educationContainer = container.querySelector('#education-forms');

    console.log('Education form handler initialized', {
        addButton: !!addButton,
        educationContainer: !!educationContainer,
        container: !!container,
        containerHTML: container ? container.innerHTML.substring(0, 200) + '...' : 'null'
    });

    if (!addButton || !educationContainer) {
        console.error('Education form elements not found', {
            addButtonId: !!container.querySelector('#add-education-btn'),
            educationFormsId: !!container.querySelector('#education-forms'),
            allIds: Array.from(container.querySelectorAll('[id]')).map(el => el.id)
        });
        return;
    }

    // Check if already initialized to prevent duplicate listeners
    if (addButton.dataset.initialized === 'true') {
        console.log('Education forms already initialized, skipping');
        return;
    }
    addButton.dataset.initialized = 'true';

    function updateAddButtonVisibility() {
        const currentEntries = educationContainer.querySelectorAll('.education-entry').length;
        if (currentEntries >= maxEducation) {
            addButton.style.display = 'none';
        } else {
            addButton.style.display = 'inline-block';
        }
        console.log('Updated add button visibility', { currentEntries, maxEducation, visible: currentEntries < maxEducation });
    }

    addButton.addEventListener('click', function() {
        const currentEntries = educationContainer.querySelectorAll('.education-entry').length;
        console.log('Add button clicked', { currentEntries, maxEducation });

        if (currentEntries < maxEducation) {
            const newEducationHtml = `
                <div class="border rounded p-3 mb-3 education-entry">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="mb-0">Pendidikan ${currentEntries + 1}</h6>
                        <button type="button" class="btn btn-outline-danger btn-sm remove-education-btn">
                            <i class="fas fa-trash me-1"></i>Hapus
                        </button>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Jenjang Pendidikan *</label>
                            <select name="education-${currentEntries}-degree" class="form-select" required>
                                <option value="">-- Pilih Jenjang --</option>
                                <option value="SMA">SMA/SMK/Sederajat</option>
                                <option value="D3">Diploma 3 (D3)</option>
                                <option value="S1">Sarjana (S1)</option>
                                <option value="S2">Magister (S2)</option>
                                <option value="S3">Doktor (S3)</option>
                                <option value="Certificate">Sertifikat Profesional</option>
                                <option value="Other">Lainnya</option>
                            </select>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Sekolah/Universitas *</label>
                            <input type="text" name="education-${currentEntries}-school_university" class="form-control" placeholder="Nama Sekolah/Universitas" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Jurusan/Bidang Studi</label>
                            <input type="text" name="education-${currentEntries}-field_of_study" class="form-control" placeholder="Jurusan/Bidang Studi (opsional)">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Tahun Lulus</label>
                            <input type="number" name="education-${currentEntries}-graduation_year" class="form-control" placeholder="Tahun Lulus (opsional)" min="1950" max="2030">
                        </div>
                    </div>
                </div>
            `;

            educationContainer.insertAdjacentHTML('beforeend', newEducationHtml);
            updateAddButtonVisibility();
        }
    });

    // Handle remove education
    educationContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-education-btn') || e.target.parentElement.classList.contains('remove-education-btn')) {
            const educationEntry = e.target.closest('.education-entry');
            console.log('Removing education entry');
            educationEntry.remove();

            // Renumber remaining education entries
            const entries = educationContainer.querySelectorAll('.education-entry');
            entries.forEach((entry, index) => {
                const inputs = entry.querySelectorAll('input, select');
                inputs.forEach(input => {
                    const name = input.getAttribute('name');
                    if (name && name.startsWith('education-')) {
                        const parts = name.split('-');
                        if (parts.length === 3) {
                            input.setAttribute('name', `education-${index}-${parts[2]}`);
                        }
                    }
                });

                const title = entry.querySelector('h6');
                if (title) {
                    title.textContent = index === 0 ? 'Pendidikan Utama' : `Pendidikan ${index + 1}`;
                }
            });

            updateAddButtonVisibility();
        }
    });

    // Initial visibility check
    updateAddButtonVisibility();
};

// Auto-initialize if DOM is ready (for regular page loads)
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, attempting to initialize education forms on document');
    window.initializeEducationForms(document);
});