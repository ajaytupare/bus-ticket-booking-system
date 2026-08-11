// Main JavaScript File for BusGo

document.addEventListener('DOMContentLoaded', function () {
    // Password Visibility Toggle
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('toggleIcon');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function () {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            if (toggleIcon) {
                toggleIcon.className = isPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye';
            }
        });
    }

    // Bus Listing Client-side Filtering & Sorting
    const busListContainer = document.getElementById('busListContainer');
    const filterTypes = document.querySelectorAll('.filter-type');
    const priceSort = document.getElementById('priceSort');
    const resetFilters = document.getElementById('resetFilters');
    const busCountLabel = document.getElementById('busCountLabel');

    if (busListContainer) {
        const busCards = Array.from(document.querySelectorAll('.bus-item-card'));

        function applyFiltersAndSort() {
            const selectedType = document.querySelector('.filter-type:checked')?.value || 'ALL';
            const sortOrder = priceSort ? priceSort.value : 'DEFAULT';

            let visibleCards = busCards.filter(card => {
                const cardType = card.getAttribute('data-type') || '';
                if (selectedType === 'ALL') return true;
                return cardType.includes(selectedType);
            });

            // Sorting
            if (sortOrder === 'LOW_HIGH') {
                visibleCards.sort((a, b) => parseFloat(a.getAttribute('data-price')) - parseFloat(b.getAttribute('data-price')));
            } else if (sortOrder === 'HIGH_LOW') {
                visibleCards.sort((a, b) => parseFloat(b.getAttribute('data-price')) - parseFloat(a.getAttribute('data-price')));
            }

            // Render visibility
            busCards.forEach(card => card.style.display = 'none');
            visibleCards.forEach(card => {
                busListContainer.appendChild(card); // Re-order DOM
                card.style.display = 'block';
            });

            if (busCountLabel) {
                busCountLabel.textContent = `Showing ${visibleCards.length} Bus(es)`;
            }
        }

        filterTypes.forEach(radio => radio.addEventListener('change', applyFiltersAndSort));
        if (priceSort) priceSort.addEventListener('change', applyFiltersAndSort);

        if (resetFilters) {
            resetFilters.addEventListener('click', function () {
                document.getElementById('typeAll').checked = true;
                if (priceSort) priceSort.value = 'DEFAULT';
                applyFiltersAndSort();
            });
        }
    }
});
