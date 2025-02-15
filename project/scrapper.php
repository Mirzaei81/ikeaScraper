<?php
/**
 * This script retrieves products from a WooCommerce site, checks each product’s SKU against an IKEA search API,
 * and if the “target” price (calculated from the API response) is higher than the current meta price,
 * updates the product meta data via a PUT request.
 *
 * Note: Ensure the environment variables WOOCOMERCE_HOST, WOOCOMERCE_KEY, and WOOCOMERCE_SECRET are set.
 */

/**
 * Main function to retrieve and process products.
 */
$GLOBALS["report"] = array(array("sku","status","description"));
function get_products_sku() {
    // Retrieve required environment variables.
    $wooHost   = "zardaan.com";
    $wooKey    = "ck_a7c4ee3e95750281d91852de92d2755cd052de22";
    $wooSecret = "cs_25e8448c6d1a5c7da9a0ae014cc8ed6c5b0e61a9";

    if (!$wooHost || !$wooKey || !$wooSecret) {
        die("Missing WooCommerce environment variables.\n");
    }

    // Base URL for WooCommerce products API.
    $wc_api_url = "https://{$wooHost}/wp-json/wc/v3/products";

    // --- First, get the first page of products ---
    $response = wc_get_request($wc_api_url, array(), $wooKey, $wooSecret);
    if ($response === false) {
        echo "Failed to retrieve products.\n";
        return;
    }
    $products = json_decode($response['body'], true);
    if ($products === null) {
        echo "Failed to decode JSON response for products.\n";
        return;
    }

    // Process each product from the first request.
    foreach ($products as $p) {
        process_product($p, $wooHost, $wooKey, $wooSecret);
    }

    // --- Handle pagination ---
    // The WooCommerce REST API returns the total number of products in the X-WP-Total header.
    // (Sometimes there is also an X-WP-TotalPages header.) Here we assume 10 products per page.
    if (isset($response['headers']['x-wp-total'])) {
        $total_products = (int)$response['headers']['x-wp-total'];
        $per_page       = 10; // adjust if you use a different per_page value
        $pages          = ceil($total_products / $per_page);

        // Already processed page 1; now process pages 2 .. $pages.
        for ($page = 2; $page <= $pages; $page++) {
            $params = array('page' => $page);
            $pageResponse = wc_get_request($wc_api_url, $params, $wooKey, $wooSecret);
            if ($pageResponse === false) {
                echo "Failed to retrieve products for page $page.\n";
                break;
            }
            $products_page = json_decode($pageResponse['body'], true);
            if ($products_page === null) {
                echo "Failed to decode JSON for products page $page.\n";
                break;
            }
            foreach ($products_page as $p) {
                process_product($p, $wooHost, $wooKey, $wooSecret);
            }
        }
    } else {
        echo "Header X-WP-Total not found in WooCommerce response.\n";
    }
}

/**
 * Helper function to process a single product.
 *
 * @param array  $p         The product data.
 * @param string $wooHost   WooCommerce host.
 * @param string $wooKey    WooCommerce API key.
 * @param string $wooSecret WooCommerce API secret.
 */
function process_product($p, $wooHost, $wooKey, $wooSecret) {
    sleep(5);
    // Ensure the product has a SKU.
    if (!isset($p['sku'])) {
        return;
    }
    $sku = $p['sku'];

    // Build the JSON payload for the IKEA search API.
    // Using an associative array and json_encode ensures that string values are properly quoted.
    $data_array = [
        "searchParameters" => [
            "input" => $sku,
            "type"  => "QUERY"
        ],
        "components" => [
            ["component" => "PRIMARY_AREA"]
        ]
    ];
    $data_json = json_encode($data_array);

    // Send POST request to the IKEA search API.
    $ikea_url = "https://sik.search.blue.cdtapps.com/ae/en/search";
    $params   = [
        "c" => "sr",
        "v" => 20241114
    ];
    $ikea_response = send_post_request($ikea_url, $params, $data_json);
    if ($ikea_response === false) {
        echo "Failed IKEA request for SKU $sku\n";
        return;
    }
    if ($ikea_response['httpCode'] != 200) {
        echo $ikea_url;
        echo "IKEA API error for SKU $sku: " . $ikea_response['body'] . "\n";
        array_push($GLOBALS["report"],array($p["sku"],"error",$ikea_response["httpcode"]));
        return;
    }
    $ikeaData = json_decode($ikea_response['body'], true);
    if ($ikeaData === null  ) {
        echo "Failed decoding IKEA API response for SKU $sku.\n";
        array_push($GLOBALS["report"],array($p["sku"],"Invalid Sku/Discontinued","sku داده شده در سایت موجود نمی باشد"));
        return;
    }
    if( count($ikeaData["results"])==0){
        echo "Failed decoding IKEA API response for SKU $sku.\n";
        print_r($ikea_response["body"]);
        array_push($GLOBALS["report"],array($p["sku"],"Invalid Sku/Discontinued","sku داده شده در سایت موجود نمی باشد"));
        return;
    }
    // Ensure that the expected data is present.
    if(!isset($ikeaData["results"][0]["items"][0]["product"]["onlineSellable"])){
        echo "No sales price numeral found for SKU $sku\n";
        array_push($GLOBALS["report"],array($p["sku"],"OutOfStock","sku  در سایت موجود نمیباشد "));
        return;
    }
    
    if (!isset($ikeaData["results"][0]["items"][0]["product"]["salesPrice"]["numeral"])) {
        echo "No sales price numeral found for SKU $sku\n";
        array_push($GLOBALS["report"],array($p["sku"],"noPrice","sku  بدون قیمت میباشد "));
        return;
    }
    $ikea_numeric = $ikeaData["results"][0]["items"][0]["product"]["salesPrice"]["numeral"];

    // Calculate targetPrice.
    // If the fractional part is greater than 0.5 then round, else leave as is.
    $fraction    = $ikea_numeric - floor($ikea_numeric);
    $targetPrice = ($fraction > 0.5) ? round($ikea_numeric) : $ikea_numeric;

    // Check for meta data; loop through meta_data array to find the key "_mnswmc_regular_price".
    if (!isset($p["meta_data"]) || !is_array($p["meta_data"])) {
        echo "No meta_data found for product ID {$p['id']} SKU $sku\n";
        return;
    }
    $meta_datas = $p["meta_data"];
    foreach ($meta_datas as $index => $meta) {
        if ($meta["key"] === "_mnswmc_regular_price") {
            // Compare the target price to the current price.
            // Casting to float ensures proper numeric comparison.
            $currentPrice = $meta["value"];
            if ((float)$targetPrice > (float)$currentPrice) {
                // Update the meta_data value.
                $meta_datas[$index]["value"] = $targetPrice;
                $update_payload = json_encode(["meta_data" => $meta_datas]);

                // Prepare the PUT request URL for updating this product.
                $update_url = "https://{$wooHost}/wp-json/wc/v3/products/{$p['id']}";
                $update_response = wc_put_request($update_url, $update_payload, $wooKey, $wooSecret);
                if ($update_response !== false && $update_response['httpCode'] < 300) {
                    echo "Updated product {$p['id']} (SKU: $sku): $currentPrice -> $targetPrice\n";
                } else {
                    echo "Failed to update product {$p['id']} (SKU: $sku).\n";
                }
            }
            // Once the matching meta key is processed, exit the loop.
            break;
        }
    }
}

/**
 * Sends a GET request using cURL.
 *
 * @param string $url       The URL endpoint.
 * @param array  $params    Optional query parameters.
 * @param string $wooKey    Basic auth username.
 * @param string $wooSecret Basic auth password.
 *
 * @return array|false      Returns an array with keys 'body', 'httpCode', and 'headers' on success, false on error.
 */
function wc_get_request($url, $params, $wooKey, $wooSecret) {
    $ch = curl_init();

    // Append query parameters if provided.
    if (!empty($params)) {
        $url .= '?' . http_build_query($params);
    }
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    // Use basic authentication.
    curl_setopt($ch, CURLOPT_USERPWD, "$wooKey:$wooSecret");

    // Set connection and overall timeouts.
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10); // 10 seconds to connect
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);          // 30 seconds maximum total execution time

    // Capture response headers.
    $headers = [];
    curl_setopt($ch, CURLOPT_HEADERFUNCTION, function ($curl, $header) use (&$headers) {
        $len    = strlen($header);
        $header = explode(':', $header, 2);
        if (count($header) < 2) { // ignore invalid headers
            return $len;
        }
        $name              = strtolower(trim($header[0]));
        $value             = trim($header[1]);
        $headers[$name]    = $value;
        return $len;
    });

    $body = curl_exec($ch);
    if (curl_errno($ch)) {
        echo "cURL GET error: " . curl_error($ch) . "\n";
        curl_close($ch);
        return false;
    }
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return [
        'headers'  => $headers,
        'body'     => $body,
        'httpCode' => $httpCode
    ];
}

/**
 * Sends a POST request using cURL.
 *
 * @param string $url       The URL endpoint.
 * @param array  $params    Query parameters to append.
 * @param string $data_json The JSON data to post.
 *
 * @return array|false      Returns an array with keys 'body' and 'httpCode' on success, false on error.
 */
function send_post_request($url, $params, $data_json) {
    $ch = curl_init();

    // Append query parameters.
    if (!empty($params)) {
        $url .= '?' . http_build_query($params);
    }
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data_json);
    curl_setopt($ch, CURLOPT_SSLVERSION, 3);
    curl_setopt($ch, CURLOPT_PROXY, 'http://127.0.0.1:10809');

    // Set Content-Type header.
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        'Content-Type: application/json'
    ));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER,0);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);


    // Set timeouts.
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10); // 10 seconds to connect
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);          // 30 seconds total

    $body = curl_exec($ch);
    if (curl_errno($ch)) {
        echo "cURL POST error: " . curl_error($ch) . "\n";
        curl_close($ch);
        return false;
    }
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return [
        'body'     => $body,
        'httpCode' => $httpCode
    ];
}

/**
 * Sends a PUT request using cURL.
 *
 * @param string $url        The URL endpoint.
 * @param string $data_json  The JSON data to send.
 * @param string $wooKey     Basic auth username.
 * @param string $wooSecret  Basic auth password.
 *
 * @return array|false       Returns an array with keys 'body' and 'httpCode' on success, false on error.
 */
function wc_put_request($url, $data_json, $wooKey, $wooSecret) {
    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "PUT");
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data_json);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    // Set basic authentication.
    curl_setopt($ch, CURLOPT_USERPWD, "$wooKey:$wooSecret");

    // Set header for JSON content.
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        'Content-Type: application/json'
    ));

    // Set timeouts.
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10); // 10 seconds to connect
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);          // 30 seconds total

    $body = curl_exec($ch);
    if (curl_errno($ch)) {
        echo "cURL PUT error: " . curl_error($ch) . "\n";
        curl_close($ch);
        return false;
    }
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return [
        'body'     => $body,
        'httpCode' => $httpCode
    ];
}
function create_csv_string($data) {
    // Open temp file pointer
    if (!$fp = fopen('./out.csv', 'w+')) return FALSE;

    // Loop data and write to file pointer
    foreach ($data as $line) {
        fputcsv($fp, $line);
    }
    
    // Place stream pointer at beginning
    rewind($fp);
    
    // Return the data
    return stream_get_contents($fp);
}
function wc_email_request($csvData,$subject)
{
    $multipartSep = '-----' . md5(time()) . '-----';

    // Arrays are much more readable
    $headers = array(
        "From: ikea@mobel.ir",
        "Reply-To: Mobelikea@gmail.com",
        "Content-Type: multipart/mixed; boundary=\"$multipartSep\""
    );

    // Make the attachment
    $attachment = chunk_split(base64_encode(create_csv_string($csvData)));
    $time = date("c");
    // Make the body of the message
    $body = "--$multipartSep\r\n"
    . "Content-Type: text/plain; charset=ISO-8859-1; format=flowed\r\n"
    . "Content-Transfer-Encoding: 7bit\r\n"
    . "\r\n"
    . "Daily report on ikea products\r\n created at $time \r\n for cancling server please stop the cron job at https://clients.netafraz.com/clientarea.php?action=productdetails&id=311768"
    . "--$multipartSep\r\n"
    . "Content-Type: text/csv\r\n"
    . "Content-Transfer-Encoding: base64\r\n"
    . "Content-Disposition: attachment; filename=\"file.csv\"\r\n"
    . "\r\n"
    . "$attachment\r\n"
    . "--$multipartSep--";

    // Send the email, return the result
    $success = @mail("mobelir1@mobel.ir", $subject, $body, implode("\r\n", $headers),);
    if (!$success) {
        $error = error_get_last();
        preg_match("/\d+/", $error["message"], $error);
        switch ($error[0]) {
            case 554:
                error_log(print_r($error[0],true), 3, "./email-error.log");
            default:     
                error_log(print_r($error[0],true), 3, "./error.log");
        }
    }
}
// Run the main function.
get_products_sku();
$time = date("c");
wc_email_request($GLOBALS["report"],"genrated report data at $time");

?>
