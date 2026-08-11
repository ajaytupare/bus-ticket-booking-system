// Booking & Seat Selection Engine - BusGo

document.addEventListener('DOMContentLoaded', function () {
    const seatButtons = document.querySelectorAll('.seat-btn.available');
    const selectedSeatsDisplay = document.getElementById('selectedSeatsDisplay');
    const totalAmountDisplay = document.getElementById('totalAmountDisplay');
    const btnPayAmount = document.getElementById('btnPayAmount');
    const inputSelectedSeats = document.getElementById('inputSelectedSeats');
    const confirmBookingBtn = document.getElementById('confirmBookingBtn');
    const passengerFieldsContainer = document.getElementById('passengerFieldsContainer');
    const seatValidationError = document.getElementById('seatValidationError');

    let selectedSeats = [];

    seatButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const seatCode = this.getAttribute('data-seat');

            if (selectedSeats.includes(seatCode)) {
                // Deselect
                selectedSeats = selectedSeats.filter(s => s !== seatCode);
                this.classList.remove('selected');
            } else {
                // Check selection limit rule
                if (selectedSeats.length >= requiredSeatsCount) {
                    alert(`You can select only ${requiredSeatsCount} seat(s). Deselect a seat first if you wish to change your selection.`);
                    return;
                }
                selectedSeats.push(seatCode);
                this.classList.add('selected');
            }

            updateBookingState();
        });
    });

    function updateBookingState() {
        const isComplete = selectedSeats.length === requiredSeatsCount;

        // Display selected seats
        if (selectedSeatsDisplay) {
            selectedSeatsDisplay.textContent = selectedSeats.length > 0 ? selectedSeats.sort().join(', ') : 'None';
        }

        // Hidden Form Input
        if (inputSelectedSeats) {
            inputSelectedSeats.value = selectedSeats.sort().join(',');
        }

        // Total Amount Calculation
        const totalFare = selectedSeats.length * pricePerSeat;
        const formattedFare = `₹${totalFare.toFixed(2)}`;

        if (totalAmountDisplay) totalAmountDisplay.textContent = formattedFare;
        if (btnPayAmount) btnPayAmount.textContent = totalFare.toFixed(2);

        // Validation Error Alert visibility
        if (seatValidationError) {
            if (selectedSeats.length > 0 && !isComplete) {
                seatValidationError.textContent = `Please select ${requiredSeatsCount - selectedSeats.length} more seat(s).`;
                seatValidationError.classList.remove('d-none');
            } else {
                seatValidationError.classList.add('d-none');
            }
        }

        // Enable / Disable Confirm Submit Button
        if (confirmBookingBtn) {
            confirmBookingBtn.disabled = !isComplete;
        }

        // Render Passenger Information Fields
        renderPassengerForms();
    }

    function renderPassengerForms() {
        if (!passengerFieldsContainer) return;

        if (selectedSeats.length === 0) {
            passengerFieldsContainer.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fa-solid fa-chair fa-2x mb-2 d-block text-secondary opacity-50"></i>
                    Please select <strong>${requiredSeatsCount} seat(s)</strong> on the seat grid to enter passenger details.
                </div>
            `;
            return;
        }

        const sortedSeats = [...selectedSeats].sort();
        let html = '';

        sortedSeats.forEach((seat, idx) => {
            const passNum = idx + 1;
            html += `
                <div class="passenger-card p-3 bg-light rounded-3 mb-3 border">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="fw-bold text-slate mb-0">Passenger ${passNum}</h6>
                        <span class="badge bg-primary-custom font-monospace">Seat ${seat}</span>
                    </div>
                    <div class="row g-2">
                        <div class="col-md-6">
                            <label class="form-label small text-muted mb-1">Full Name *</label>
                            <input type="text" class="form-control form-control-sm" name="passenger_${passNum}_name" placeholder="Passenger Name" required>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label small text-muted mb-1">Age *</label>
                            <input type="number" class="form-control form-control-sm" name="passenger_${passNum}_age" min="1" max="110" placeholder="Age" required>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label small text-muted mb-1">Gender *</label>
                            <select class="form-select form-select-sm" name="passenger_${passNum}_gender" required>
                                <option value="Male">Male</option>
                                <option value="Female">Female</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                    </div>
                </div>
            `;
        });

        passengerFieldsContainer.innerHTML = html;
    }

    // Initial render
    updateBookingState();
});
