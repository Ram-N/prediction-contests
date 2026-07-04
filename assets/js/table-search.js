/**
 * Table Search Widget
 *
 * Automatically adds a search box above every table with the class
 * "table-searchable". Filters rows by matching the search text against
 * the Name column (2nd column). WOTC and AI header rows (with emoji
 * prefixes) are always shown.
 */
$(function () {
  $('.table-searchable').each(function () {
    var $table = $(this);

    // Create search input
    var $input = $('<input>', {
      type: 'text',
      class: 'form-control form-control-sm mb-2',
      placeholder: 'Search by name\u2026'
    }).css('max-width', '300px');

    $input.insertBefore($table);

    // Cache rows (skip header row)
    var $rows = $table.find('tbody tr');
    // If no tbody, fall back to all tr except the first two (header + separator)
    if ($rows.length === 0) {
      $rows = $table.find('tr').slice(1); // skip <thead> row
    }

    $input.on('input', function () {
      var query = $(this).val().toLowerCase().trim();

      if (!query) {
        $rows.show();
        return;
      }

      $rows.each(function () {
        var $cells = $(this).find('td, th');
        // Name is in the 1st column (index 0)
        var name = $cells.eq(0).text().toLowerCase();
        // Check Location column (index 1) for emoji markers (WOTC/AI rows)
        var marker = $cells.eq(1).text().trim();
        var isSpecialRow = (marker.indexOf('\uD83D\uDC65') !== -1 || marker.indexOf('\uD83E\uDD16') !== -1);

        if (isSpecialRow || name.indexOf(query) !== -1) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
    });
  });
});
