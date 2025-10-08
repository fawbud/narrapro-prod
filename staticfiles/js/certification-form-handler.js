/**
 * JavaScript to handle dynamic professional certification forms functionality
 * Works for both registration and edit profile forms
 */

// Define global initialization function for certification forms
window.initializeCertificationForms = function(container) {
    console.log('initializeCertificationForms called with container:', container);

    const maxCertifications = 10;
    const addButton = container.querySelector('#add-certification-btn');
    const certificationContainer = container.querySelector('#certification-forms');

    console.log('Certification form handler initialized', {
        addButton: !!addButton,
        certificationContainer: !!certificationContainer,
        container: !!container
    });

    if (!addButton || !certificationContainer) {
        console.error('Certification form elements not found');
        return;
    }

    // Check if already initialized to prevent duplicate listeners
    if (addButton.dataset.initialized === 'true') {
        console.log('Certification forms already initialized, skipping');
        return;
    }
    addButton.dataset.initialized = 'true';

    function updateAddButtonVisibility() {
        const currentEntries = certificationContainer.querySelectorAll('.certification-entry').length;
        if (currentEntries >= maxCertifications) {
            addButton.style.display = 'none';
        } else {
            addButton.style.display = 'inline-block';
        }
        console.log('Updated add button visibility', { currentEntries, maxCertifications, visible: currentEntries < maxCertifications });
    }

    addButton.addEventListener('click', function() {
        const currentEntries = certificationContainer.querySelectorAll('.certification-entry').length;
        console.log('Add certification button clicked', { currentEntries, maxCertifications });

        if (currentEntries < maxCertifications) {
            const newCertificationHtml = `
                <div class="border rounded p-3 mb-3 certification-entry">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="mb-0">Sertifikasi ${currentEntries + 1}</h6>
                        <button type="button" class="btn btn-outline-danger btn-sm remove-certification-btn">
                            <i class="fas fa-trash me-1"></i>Hapus
                        </button>
                    </div>
                    <div class="row">
                        <div class="col-12 mb-3">
                            <label class="form-label">Nama Sertifikasi</label>
                            <input type="text" name="certification-${currentEntries}-title" class="form-control" placeholder="Nama sertifikasi">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12 mb-3">
                            <label class="form-label">Deskripsi</label>
                            <textarea name="certification-${currentEntries}-description" class="form-control" rows="3" placeholder="Deskripsi sertifikasi, organisasi penerbit, atau detail lainnya"></textarea>
                        </div>
                    </div>
                </div>
            `;

            certificationContainer.insertAdjacentHTML('beforeend', newCertificationHtml);
            updateAddButtonVisibility();
        }
    });

    // Handle remove certification
    certificationContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-certification-btn') || e.target.parentElement.classList.contains('remove-certification-btn')) {
            const certificationEntry = e.target.closest('.certification-entry');
            console.log('Removing certification entry');
            certificationEntry.remove();

            // Renumber remaining certification entries
            const entries = certificationContainer.querySelectorAll('.certification-entry');
            entries.forEach((entry, index) => {
                const inputs = entry.querySelectorAll('input, textarea');
                inputs.forEach(input => {
                    const name = input.getAttribute('name');
                    if (name && name.startsWith('certification-')) {
                        const parts = name.split('-');
                        if (parts.length === 3) {
                            input.setAttribute('name', `certification-${index}-${parts[2]}`);
                        }
                    }
                });

                const title = entry.querySelector('h6');
                if (title) {
                    title.textContent = `Sertifikasi ${index + 1}`;
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
    console.log('DOM loaded, attempting to initialize certification forms on document');
    window.initializeCertificationForms(document);
});
