// Add this to your theme's functions.php or a custom plugin

add_action('admin_menu', 'csv_table_admin_menu');

function csv_table_admin_menu() {
    add_menu_page(
        'CSV Table',           // Page title
        'CSV Table',           // Menu title
        'manage_options',      // Capability
        'csv-table-admin',     // Menu slug
        'csv_table_admin_page' // Callback function
    );
}

function csv_table_admin_page() {
    // Path to your CSV file (adjust as needed)
    $csv_file = WP_CONTENT_DIR . '/out.csv';

    echo '<div class="wrap" ><div id="filter" style="display: flex;flex-direction:row"><h1>فیلتر:</h1>';

    if (!file_exists($csv_file)) {
        echo '<p><strong>CSV file not found at:</strong> ' . esc_html($csv_file) . '</p></div>';
        return;
    }

    echo '<table  class="widefat fixed" style="max-width:600px;"> ';
    echo '<thead><tr><th>Column 1</th><th>Column 2</th></tr></thead>';
    echo '<tbody id="ikea_offers">';

    if (($handle = fopen($csv_file, 'r')) !== false) {
        while (($data = fgetcsv($handle)) !== false) {
            // Only display rows with at least two columns
            if (count($data) >= 2) {
                echo '<tr>';
                echo '<td>' . esc_html($data[0]) . '</td>';
                echo '<td>' . esc_html($data[1]) . '</td>';
                echo '</tr>';
            }
        }
        fclose($handle);
    } else {
        echo '<tr><td colspan="2">Unable to open CSV file.</td></tr>';
    }

    echo '</tbody></table></div>';
}
function add_custom_scripts() {
    wp_enqueue_script( 'custom-script',  './ikeaOff.js', array(), '1.0', true );
}
add_action( 'wp_enqueue_scripts', 'add_custom_scripts' );
