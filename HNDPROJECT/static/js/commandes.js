// static/cart/form.js
$(document).ready(function() {
    // Gestionnaire d'événements pour le bouton Add Item
    $('.add-item').click(function() {
      var $itemRow = $('#items-table tbody tr.item-row:last');
      var $newItemRow = $itemRow.clone();
      $newItemRow.find('input').val('');
      $itemRow.after($newItemRow);
      updateTotal();
    });
  
    // Gestionnaire d'événements pour le bouton Remove Item
    $(document).on('click', '.remove-item', function() {
      $(this).closest('tr').remove();
      updateTotal();
    });
  
    // Gestionnaire d'événements pour mettre à jour le prix total en fonction des quantités et des prix unitaires
    $(document).on('change', 'input[name="price"], input[name="quantity"]', updateTotal);
  
    // Fonction pour mettre à jour le prix total
    function updateTotal() {
      $('#items-table tbody tr.item-row').each(function() {
        var $itemRow = $(this);
        var price = parseFloat($itemRow.find('input[name="price"]').val()) || 0;
        var quantity = parseFloat($itemRow.find('input[name="quantity"]').val()) || 1;
        var total = price * quantity;
        $itemRow.find('input[name="total"]').val(total.toFixed(2));
      });
    }
  });



// PDF export
DataTable.ext.buttons.pdfFlash = $.extend( {}, flashButton, {
	className: 'buttons-pdf buttons-flash',

	text: function ( dt ) {
		return dt.i18n( 'buttons.pdf', 'PDF' );
	},

	action: function ( e, dt, button, config ) {
		// Set the text
		var flash = config._flash;
		var data = dt.buttons.exportData( config.exportOptions );
		var totalWidth = dt.table().node().offsetWidth;

		// Calculate the column width ratios for layout of the table in the PDF
		var ratios = dt.columns( config.columns ).indexes().map( function ( idx ) {
			return dt.column( idx ).header().offsetWidth / totalWidth;
		} );

		flash.setAction( 'pdf' );
		flash.setFileName( _filename( config ) );

		_setText( flash, JSON.stringify( {
			title:       _filename(config, false),
			message: typeof config.message == 'function' ? config.message(dt, button, config) : config.message,
			colWidth:    ratios.toArray(),
			orientation: config.orientation,
			size:        config.pageSize,
			header:      config.header ? data.header : null,
			footer:      config.footer ? data.footer : null,
			body:        data.body
		} ) );
	},

	extension: '.pdf',

	orientation: 'portrait',

	pageSize: 'A4',

	message: '',

	newline: '\n'
} );

