document.addEventListener('DOMContentLoaded', function() {
    // Simple table searching / filtering
    const searchInputs = document.querySelectorAll('[data-search-table]');
    searchInputs.forEach(input => {
        const tableId = input.getAttribute('data-search-table');
        const table = document.getElementById(tableId);
        if (!table) return;

        input.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(filter)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });

    // Prevent details from toggling when clicking inputs or links inside summary
    const summaryInteractives = document.querySelectorAll('summary input, summary a');
    summaryInteractives.forEach(element => {
        element.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
});
