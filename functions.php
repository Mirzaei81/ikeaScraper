<?php

/**
 *
 * The framework's functions and definitions
 */

define('WOODMART_THEME_DIR', get_template_directory_uri());
define('WOODMART_THEMEROOT', get_template_directory());
define('WOODMART_IMAGES', WOODMART_THEME_DIR . '/images');
define('WOODMART_SCRIPTS', WOODMART_THEME_DIR . '/js');
define('WOODMART_STYLES', WOODMART_THEME_DIR . '/css');
define('WOODMART_FRAMEWORK', '/inc');
define('WOODMART_DUMMY', WOODMART_THEME_DIR . '/inc/dummy-content');
define('WOODMART_CLASSES', WOODMART_THEMEROOT . '/inc/classes');
define('WOODMART_CONFIGS', WOODMART_THEMEROOT . '/inc/configs');
define('WOODMART_HEADER_BUILDER', WOODMART_THEME_DIR . '/inc/header-builder');
define('WOODMART_ASSETS', WOODMART_THEME_DIR . '/inc/admin/assets');
define('WOODMART_ASSETS_IMAGES', WOODMART_ASSETS . '/images');
define('WOODMART_API_URL', 'https://xtemos.com/wp-json/xts/v1/');
define('WOODMART_DEMO_URL', 'https://woodmart.xtemos.com/');
define('WOODMART_PLUGINS_URL', WOODMART_DEMO_URL . 'plugins/');
define('WOODMART_DUMMY_URL', WOODMART_DEMO_URL . 'dummy-content-new/');
define('WOODMART_TOOLTIP_URL', WOODMART_DEMO_URL . 'theme-settings-tooltips/');
define('WOODMART_SLUG', 'woodmart');
define('WOODMART_CORE_VERSION', '1.0.43');
define('WOODMART_WPB_CSS_VERSION', '1.0.2');

if (! function_exists('woodmart_load_classes')) {
    function woodmart_load_classes()
    {
        $classes = array(
            'class-singleton.php',
            'class-api.php',
            'class-config.php',
            'class-layout.php',
            'class-autoupdates.php',
            'class-activation.php',
            'class-notices.php',
            'class-theme.php',
            'class-registry.php',
        );

        foreach ($classes as $class) {
            require WOODMART_CLASSES . DIRECTORY_SEPARATOR . $class;
        }
    }
}
function my_custom_frontend_css()
{
    echo '
    <style>
        .widefat * {
				word-wrap: normal !important;
		}
    </style>
    ';
}
add_action('admin_head', 'my_custom_frontend_css');



add_filter('woocommerce_checkout_fields', 'make_phone_field_required');

function make_phone_field_required($fields)
{
    // اجباری کردن فیلد تلفن
    $fields['billing']['billing_phone']['required'] = true;
    return $fields;
}





woodmart_load_classes();

new XTS\Theme();

define('WOODMART_VERSION', woodmart_get_theme_info('Version'));


add_filter('woocommerce_customer_search_customers', 'custom_add_billing_phone_to_search_function', 10, 4);
function custom_add_billing_phone_to_search_function($filter, $term, $limit, $type)
{
    if ($type == 'meta_query') {
        $filter['meta_query'][] = array(
            'key' => 'billing_phone',
            'value' => $term,
            'compare' => 'LIKE'
        );
    }
    return $filter;
}

add_action('rest_api_init', function () {
    register_rest_route('wc/v3', '/customers/pec/checkout1/(?P<order>\d+)', array(
        'methods' => 'GET',
        'callback' => 'prepare_transaction'
    ));
    register_rest_route('wc/v3', '/customers/phone/(?P<phone>\d+)', array(
        'methods' => 'GET',
        'callback' => 'get_customer_by_phone',
        'permission_callback' => function () {
            return current_user_can('manage_woocommerce');
        }
    ));
    register_rest_route('phone/v1', '/send-otp/(?P<phone>\d+)', array(
        'methods' => 'GET',
        'callback' => 'send_otp',
        'permission_callback' => '__return_true'
    ));
    register_rest_route('phone/v1', '/register/(?P<phone>\d+)', array(
        'methods' => 'POST',
        'callback' => 'register',
        'permission_callback' => '__return_true'
    ));
    register_rest_route('phone/v1', '/verify-otp/(?P<phone>\d+)', array(
        'methods' => 'POST',
        'callback' => 'verify_otp',
        'permission_callback' => '__return_true'
    ));
});

function get_customer_by_phone($request)
{
    global $wpdb;
    $phone = $request['phone'];

    $customer = $wpdb->get_row(
        $wpdb->prepare(
            "SELECT user_id FROM {$wpdb->prefix}usermeta 
            WHERE meta_key = 'billing_phone' AND meta_value = %s",
            $phone
        )
    );

    if ($customer) {
        $wc_customer = new WC_Customer($customer->user_id);
        return rest_ensure_response($wc_customer->get_data());
    }

    return new WP_Error('no_customer', 'No customer found with this phone number', array('status' => 404));
}

function register($request)
{
    global $wpdb;
    $phone = $request['phone'];
    $name = $request->get_param('name');

    $otp = generate_otp();

    // Store OTP in database
    $table_name = $wpdb->prefix . 'otp_storage';
    $data = array(
        'phone' => $phone,
        'name' => $name,
        'otp' => $otp,
        'created_at' => current_time('mysql')
    );
    $wpdb->insert($table_name, $data);
    $curl = curl_init();

    curl_setopt_array($curl, array(
        CURLOPT_URL => 'api.payamak-panel.com/post/Send.asmx/SendSimpleSMS2?username=09306622276&password=4b0856aa-db3f-4f51-a98f-448d1704fc2f&to=' . $phone . '&from=9982006278&text=%D8%B1%D9%85%D8%B2%20%D8%B9%D8%A8%D9%88%D8%B1%20%DB%8C%DA%A9%20%D8%A8%D8%A7%D8%B1%20%D9%85%D8%B5%D8%B1%D9%81%20%D8%B2%D8%B1%D8%AF%D8%A7%D9%86%3A%20%0ACode%3A%20' . $otp . '&isflash=false',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_TIMEOUT => 0,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
        CURLOPT_CUSTOMREQUEST => 'GET',
    ));

    $response = curl_exec($curl);
    curl_close($curl);

    return rest_ensure_response(array(
        'message' => 'OTP sent successfully',
        'response' => $response,
        'error' => $wpdb->last_error
    ));
}

function send_otp($request)
{
    global $wpdb;
    $phone = $request['phone'];
    $otp = generate_otp();

    // Store OTP in database
    $table_name = $wpdb->prefix . 'otp_storage';
    $data = array(
        'phone' => $phone,
        'otp' => $otp,
        'created_at' => current_time('mysql')
    );
    $wpdb->delete($table_name, array('phone' => $phone));
    $wpdb->insert($table_name, $data);
    $curl = curl_init();

    curl_setopt_array($curl, array(
        CURLOPT_URL => 'api.payamak-panel.com/post/Send.asmx/SendSimpleSMS2?username=09306622276&password=4b0856aa-db3f-4f51-a98f-448d1704fc2f&to=' . $phone . '&from=9982006278&text=%D8%B1%D9%85%D8%B2%20%D8%B9%D8%A8%D9%88%D8%B1%20%DB%8C%DA%A9%20%D8%A8%D8%A7%D8%B1%20%D9%85%D8%B5%D8%B1%D9%81%20%D8%B2%D8%B1%D8%AF%D8%A7%D9%86%3A%20%0ACode%3A%20' . $otp . '&isflash=false',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_TIMEOUT => 0,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
        CURLOPT_CUSTOMREQUEST => 'GET',
    ));

    $response = curl_exec($curl);
    curl_close($curl);

    return rest_ensure_response(array(
        'message' => 'OTP sent successfully',
        'response' => $response,
        'error' => $wpdb->last_error
    ));
}


function persianToAscii($string, $map) {
    $output = '';
    
    // Split string into individual UTF-8 characters
    $chars = preg_split('//u', $string, -1, PREG_SPLIT_NO_EMPTY);
    
    foreach ($chars as $char) {
        $output .= $map[$char] ?? $char;  // Use mapping or keep the original char if no match
    }
    
    return $output;
}



function verify_otp($request)
{
    $persianToEnglish = [
    'ا' => 'a',
    'ب' => 'b',
    'پ' => 'p',
    'ت' => 't',
    'ث' => 's',
    'ج' => 'j',
    'چ' => 'ch',
    'ح' => 'h',
    'خ' => 'kh',
    'د' => 'd',
    'ذ' => 'z',
    'ر' => 'r',
    'ز' => 'z',
    'ژ' => 'zh',
    'س' => 's',
    'ش' => 'sh',
    'ص' => 's',
    'ض' => 'z',
    'ط' => 't',
    'ظ' => 'z',
    'ع' => 'a',
    'غ' => 'gh',
    'ف' => 'f',
    'ق' => 'gh',
    'ک' => 'k',
    'گ' => 'g',
    'ل' => 'l',
    'م' => 'm',
    'ن' => 'n',
    'و' => 'v',
    'ه' => 'h',
    'ی' => 'y',
    'ء' => "'",
    'ئ' => 'y',
    'أ' => 'a',
    'إ' => 'e',
    'ؤ' => 'o',
    'آ' => 'a',
    'ة' => 'h',
    'ﻻ' => 'la',   // Laam Alef ligature
    '؟' => '?',
    '،' => ',',
    '؛' => ';',
    ' ' => "_"
];

    global $wpdb;
    $phone = $request['phone'];
    $user_otp = $request->get_param('otp');

    $table_name = $wpdb->prefix . 'otp_storage';
    
    $stored_otp = $wpdb->get_results($wpdb->prepare(
        "SELECT `otp`,`name` FROM $table_name WHERE phone = %s",
        $phone
    ));

    if ($stored_otp[0]->otp && $stored_otp[0]->otp == $user_otp) {
        // OTP is valid, delete it from database
        $wpdb->delete($table_name, array('phone' => $phone));
        try {
            $customer = $wpdb->get_row(
                $wpdb->prepare(
                    "SELECT user_id FROM {$wpdb->prefix}usermeta 
                    WHERE meta_key = 'billing_phone' AND meta_value = %s",
                    $phone
                )
            );
            if ($customer) {
                $wc_customer = new WC_Customer($customer->user_id);
                $data = $wc_customer->get_data();
                return rest_ensure_response($data);
            } else {
                if($stored_otp[0]->name){
                    $name =  trim($stored_otp[0]->name);
                    $firstletter = mb_substr($name, 0, 1, 'UTF-8');
                    if(isset($persianToEnglish[$firstletter])){
                        $name = persianToAscii($name, $persianToEnglish);
                    }
                    $username =$name;
                    $email = $name . '@example.com'; // Placeholder email
                    $password = wp_generate_password();
                    $customer_id = wc_create_new_customer($email, $username, $password);
                    if (is_wp_error($customer_id)) {
                                          return WP_Error('User failed ', $customer_id->get_error_message(), array( 'status' => 400 ) );
                    }
                    update_user_meta($customer_id, 'billing_phone', $phone);
    				$wc_customer = new WC_Customer($customer->user_id);
    				$data=$wc_customer->get_data();


                    return rest_ensure_response($data);
                }else{
                    return WP_Error('User Not found ', 'No name in the db ', array( 'status' => 404 ) );
                }
            }
        } catch (Exception $e) {
            return rest_ensure_response(array(
                'message' => $e
            ));
        }
    } else {
        return rest_ensure_response(array(
            'message' => 'OTP not  found',
            'usr_otp' => $user_otp,
            'stored_otp'=>print_r($stored_otp[0]->otp,true),
            'error' => $wpdb->last_error
        ));
    }
}
function prepare_transaction($request){
    try{
    	$order_id= $request['order'];
    	$order = wc_get_order($order_id);
    	$currency = $order->get_currency();
    	$amount = intval($order->get_total());
        WC()->session = new WC_Session_Handler();
        WC()->session->init();
    	if (strtolower($currency) == strtolower('IRT') || strtolower($currency) == strtolower('TOMAN')
    		|| strtolower($currency) == strtolower('Iran TOMAN') || strtolower($currency) == strtolower('Iranian TOMAN')
    		|| strtolower($currency) == strtolower('Iran-TOMAN') || strtolower($currency) == strtolower('Iranian-TOMAN')
    		|| strtolower($currency) == strtolower('Iran_TOMAN') || strtolower($currency) == strtolower('Iranian_TOMAN')
    		|| strtolower($currency) == strtolower('تومان') || strtolower($currency) == strtolower('تومان ایران')
    	) {
    		$amount = $amount * 10;
    	} elseif (strtolower($currency) == strtolower('IRHT')) {
    		$amount = $amount * 1000 * 10;
    	} elseif (strtolower($currency) == strtolower('IRHR')) {
    		$amount = $amount * 1000;
    	}
    	$login_account = "gxLKt011cax0n4ie5mBb";
    	$unique_order_id = time();
    	$callback_url = add_query_arg('wc_order', $order_id, WC()->api_request_url('WC_PEC_Gateway'));
    	 WC()->session->set( 'pec_order_id',$order_id );
    	if(extension_loaded('soap')) {
    		try {
    			$parameters = array(
    				'LoginAccount'		=> $login_account,
    				'Amount' 			=> $amount,
    				'OrderId' 			=> $unique_order_id,
    				'CallBackUrl' 		=> $callback_url,
    			);
    			$soap_client = new soapclient('https://pec.shaparak.ir/NewIPGServices/Sale/SaleService.asmx?wsdl');
    			$result = $soap_client->SalePaymentRequest(array("requestData" => $parameters));
    			$status = $result->SalePaymentRequestResult->Status;
    			$token = $result->SalePaymentRequestResult->Token;
    			if($status == '0' && $token > 0){
    				// Send post method
    				$send_to_bank_url = add_query_arg('Token', $token, 'https://pec.shaparak.ir/NewIPG/');
    				return rest_ensure_response(array(
    					'message' => 'Success',
    					'uri'=>$send_to_bank_url,
    				));
    			} else {
    				$error_message = $result->SalePaymentRequestResult->Message;
    					return new WP_Error(
    						'payment error', // Unique error code
    						$error_message, // Error message
    						array('status' => 400) // HTTP status code
    					);					exit();
    			}
    		} catch (Exception $e) {
    				return new WP_Error(
    					'payment error', // Unique error code
    					$e, // Error message
    					array('status' => 400) // HTTP status code
    				);	
    				exit();
    		}
    	} else {
    			return new WP_Error(
    					'payment error', // Unique error code
    					"soap error", // Error message
    					array('status' => 400) // HTTP status code
    				);
    	}
            
    }catch (Exception $e) {
		return new WP_Error(
			'payment error', // Unique error code
			print_r($e,true), // Error message
			array('status' => 400) // HTTP status code
		);	
    }
}
function generate_otp($length = 4)
{
    return str_pad(rand(0, pow(10, $length) - 1), $length, '0', STR_PAD_LEFT);
}


add_action('wp_dashboard_setup', 'csv_table_admin_menu');

function csv_table_admin_menu() {
    wp_add_dashboard_widget(
		'my_ikea_widget',
		'تخفیفات ikea',
		'csv_table_admin_page'
    );
}

function csv_table_admin_page() {
    // Path to your CSV file (adjust as needed)
    $csv_file = ABSPATH . 'offers.csv';

    echo '<div class="wrap" ><h1>فیلتر:</h1><div id="filter" style="display: flex;flex-direction:column"></div>';
    if (!file_exists($csv_file)) {
        echo '<p><strong>CSV file not found at:</strong> ' . esc_html($csv_file) . '</p></div>';
        return;
    }

    echo '<table class="widefat fixed" style="min-width:440px;display:block">';
    echo '<thead><tr><th>sku</th><th>موجودی انبار</th><th>نام محصول</th><th>تخفیف</th></tr></thead>';
    echo '<tbody id="ikea_offers" style="overflow-x:hidden;overflow-y:auto;display:block;max-height:500px">';

    if (($handle = fopen($csv_file, 'r')) !== false) {
        while (($data = fgetcsv($handle)) !== false) {
            // Only display rows with at least two columns
            if ($data[3]!='stock'&& count($data) >= 2) {
                echo '<tr>';
                echo '<td>' . esc_html($data[2]) . '</td>';
                echo '<td>' . esc_html($data[3]) . '</td>';
                echo '<td>' . esc_html($data[0]) . '</td>';
                if($data[1]=='NONE')
                echo '<td>' . 'IKEA_FAMILY' . '</td>';
                else
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
add_action('admin_enqueue_scripts','ikea_offer');

function ikea_offer() {
    wp_enqueue_script( 'ikea-off-js', plugins_url( '/js/ikeaOff.js'));
}

add_action('rest_api_init', function () {

	register_rest_route('hesabfa/v1', 'hsb_hook/', array(
		'methods'  => 'POST',
		'callback' => 'create_hsb_woo_order',
		'permission_callback' => function(){return true;}
	));
	
	register_rest_route('cwc/v1', 'price/', array(
		'methods'  => 'POST',
		'callback' => 'updatePrice',
		'permission_callback' => function(){return true;}
	));
});
function updatePrice($request){
// Get an instance of the WC_Product object
    $data = $request->get_params();
    $regular_price = $data["reqular_price"]; // Define the regular price
    $sale_price    = $data["sale_price"];
    $stock = $data['stock'];
    $product = wc_get_product( $data["id"] );
    
    // Set product sale price
    
    
    if ( $product ) {
        if(isset($reqular_price)){
            $product->update_meta_data('_mnswmc_regular_price', $regular_price);  
        }
        if(isset($sale_price)){
            $product->update_meta_data('_mnswmc_sale_price', $sale_price);
        }
    } 
    if(isset($stock)){
        $product->set_stock_quantity($stock);
    }
    // Sync data, refresh caches and saved data to the database
    $product->save();    
    return new WP_REST_Response(print_r($product), 200);

}
function create_hsb_woo_order( $request) {
   try {
      global $woocommerce;
	  $data = $request->get_params();
	  if($data["ObjectType"]!="Receipt"){
	      return new WP_REST_Response('Accepted', 201);
	  }
	  if($data["Password"]!="i7rq&:WI&ZcD"){
	      		return new WP_REST_Response('Unauthnicated', 401);
	  }
	  $id = $data["ObjectIdList"];
	 
      $id_str = "[" . implode(',', $id) . "]";
      $curl = curl_init();
      curl_setopt_array($curl, array(
         CURLOPT_URL => 'https://api.hesabfa.com/v1/receipt/GetById',
         CURLOPT_RETURNTRANSFER => true,
         CURLOPT_ENCODING => '',
         CURLOPT_MAXREDIRS => 10,
         CURLOPT_TIMEOUT => 0,
         CURLOPT_FOLLOWLOCATION => true,
         CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
         CURLOPT_CUSTOMREQUEST => 'POST',
         CURLOPT_POSTFIELDS => '{
    "loginToken": "6deb2b60112cd8cb927cbe6ccea860bbca6726964f642559972551d87f13afaed96e596d1a18fb49ed5fdbda5fa6335b",
    "apiKey": "hPYhvvcfeP1q4EAd1fucG9bCIJuAXUrW",
    "type": 1,
    "idList":  ' . $id_str . '
}',
         CURLOPT_HTTPHEADER => array(
            'Content-Type: application/json'
         ),
      ));

      $receipt_response  = curl_exec($curl);
        file_put_contents("receipt.log", print_r($reponse, true));

      $receipt = json_decode($receipt_response, true);
      $code = $receipt["Result"][0]["Items"][0]["Contact"]["Code"];
      $invoiceId = $receipt["Result"][0]["Invoice"]["Id"];
      curl_setopt_array($curl, array(
         CURLOPT_URL => 'https://api.hesabfa.com/v1/contact/get',
         CURLOPT_RETURNTRANSFER => true,
         CURLOPT_ENCODING => '',
         CURLOPT_MAXREDIRS => 10,
         CURLOPT_TIMEOUT => 0,
         CURLOPT_FOLLOWLOCATION => true,
         CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
         CURLOPT_CUSTOMREQUEST => 'POST',
         CURLOPT_POSTFIELDS => '{
  "loginToken": "6deb2b60112cd8cb927cbe6ccea860bbca6726964f642559972551d87f13afaed96e596d1a18fb49ed5fdbda5fa6335b",
    "apiKey": "hPYhvvcfeP1q4EAd1fucG9bCIJuAXUrW",
    "code": "' . $code . '"
}',
         CURLOPT_HTTPHEADER => array(
            'Content-Type: application/json'
         ),
      ));

      $contact_res = curl_exec($curl);
    file_put_contents("contact.log", print_r($reponse, true));
      $contact = json_decode($contact_res,true);
      $first_name = $contact["Result"]["name"];
      $company = $contact["Result"]["company"];
      $phone = $contact["Result"]["Phone"];
      $address_1 = $contact["Result"]["Address"];
      $address_2 = $contact["Result"]["Address"];
      $city = $contact["Result"]["City"];
      $state = $contact["Result"]["State"];
      $postcode = $contact["Result"]["PostalCode"];
      $country = $contact["Result"]["Country"];


      curl_setopt_array($curl, array(
         CURLOPT_URL => 'https://api.hesabfa.com/v1/invoice/getById',
         CURLOPT_RETURNTRANSFER => true,
         CURLOPT_ENCODING => '',
         CURLOPT_MAXREDIRS => 10,
         CURLOPT_TIMEOUT => 0,
         CURLOPT_FOLLOWLOCATION => true,
         CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
         CURLOPT_CUSTOMREQUEST => 'POST',
         CURLOPT_POSTFIELDS => '{
   "loginToken": "6deb2b60112cd8cb927cbe6ccea860bbca6726964f642559972551d87f13afaed96e596d1a18fb49ed5fdbda5fa6335b",
      "apiKey": "hPYhvvcfeP1q4EAd1fucG9bCIJuAXUrW",
      "id": ' . $invoiceId . '
   }',
         CURLOPT_HTTPHEADER => array(
            'Content-Type: application/json'
         ),
      ));

      $response = curl_exec($curl);
      file_put_contents("factor.log", print_r($reponse, true));

      $factor = json_decode($response, true);

      $line_items = [];
      if (isset($factor['Result']['InvoiceItems']) && is_array($factor['Result']['InvoiceItems'])) {
         foreach ($factor['Result']['InvoiceItems'] as $item) {
            if (isset($item['Item']['ProductCode'])) {
               $productCode = (int)$item['Item']['ProductCode'];
               $productQuant = (int)$item['Quantity'];
               $line_items[]=array(
                   "product_id"=>$productCode,
                   "quantity"=>$productQuant
                   );  // Use wc_get_product instead of deprecated get_product
            }
         }
      }
 
       $body = '{"payment_method": "bacs","payment_method_title": "Direct Bank Transfer","set_paid": true,"billing": {  "first_name": "'.$first_name.'",  "last_name": "'.$first_name.'",  "address_1": "'.$address_1.'",  "address_2": "",  "city": "'.$city.'",  "state": "'.$state.'",  "postcode": "'.$postcode.'",  "country": "'.$country3.'","phone": "'.$phone.'"},"shipping": {  "first_name": "'.$first_name.'",  "last_name": "'.$first_name.'",  "address_1": "'.$address_1.'",  "address_2": "",  "city": "'.$city.'",  "state": "'.$state.'",  "postcode": "'.$postcode.'",  "country": "'.$country3.'",   "phone": "'.$phone.'"},"line_items": '.json_encode($line_items).'}';
          curl_setopt($curl, CURLOPT_URL, 'https://zardaan.com/wp-json/wc/v3/orders');
         file_put_contents("body.log", print_r($reponse, true));
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($curl, CURLOPT_CUSTOMREQUEST, 'POST');
    curl_setopt($curl, CURLOPT_HTTPHEADER, array(
    'Authorization: Basic Y2tfYTdjNGVlM2U5NTc1MDI4MWQ5MTg1MmRlOTJkMjc1NWNkMDUyZGUyMjpjc18yNWU4NDQ4YzZkMWE1YzdkYTlhMGFlMDE0Y2M4ZWQ2YzViMGU2MWE5',
    'Content-Type: application/json',
    'Cookie: pxcelPage_c01002=1'
 
    ));
    curl_setopt($curl, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
    curl_setopt($curl, CURLOPT_USERPWD, 'consumer_key:consumer_secret');
curl_setopt($curl, CURLOPT_POSTFIELDS, $body);
       $response = curl_exec($curl);
      
      file_put_contents("order.log", print_r($reponse, true));
      file_put_contents("order.json", $body);

    $httpcode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        curl_close($curl);

		return new WP_REST_Response($httpcode.'Post created successfully Code:  ', 201);
   } catch (Throwable $th) {
		file_put_contents("hesabfa_error.log", print_r($th, true));
		return new WP_REST_Response('Post failed' . print_r($th, true), 201);
   };
}


add_action('wp_dashboard_setup', 'custom_dashboard_widgets');
add_action( 'admin_post_download_products', 'handle_download_products' ); 
add_action('admin_post_upload_products', 'handle_upload_products'); 
add_action('admin_post_upload_groups', 'handle_upload_groups');
function custom_dashboard_widgets() {
    wp_add_dashboard_widget(
        'custom_dashboard_widget',              // Widget slug
        'افزونه افزونه نواسان',                        // Widget title (means "Quick Tools")
        'custom_dashboard_widget_display'       // Display function
    );
}
function custom_dashboard_widget_display() {
    ?>
	<div style="text-align: center;">
		<form method="post" enctype="multipart/form-data" action="<?php echo admin_url('admin-post.php'); ?>">
			<button type="submit" name="action" value="download_products" style="margin: 5px; padding: 10px 20px;">
				دانلود مشخصات محصولات
			</button>
			<div>
				<label for="fileInput" style="cursor:pointer;background-color:yellow;border-radius:0.5rem; padding:1rem">
					اپلود فایل
					<input hidden accept=".csv" id="fileInput" type="file" name="csv_file" style="all:unset;" />
				</label>
				<div style="display:flex;flex-direction:row;margin:">
					<button disabled id="prod" type="submit" name="action" value="upload_products" style="margin: 5px; padding: 10px 20px;">
						بروز رسانی نوع نرخ کالا
					</button>
					<button disabled id="group" type="submit" name="action" value="upload_groups" style="margin: 5px; padding: 10px 20px;">
						بروز رسانی گرد کردن در گروه
					</button>
				</div>
			</div>
		</form>
	</div>
	<script>
		console.log('This is valid inside a div.');

		const prod = document.querySelector("#prod")
		const group = document.querySelector("#group")
		const fileInput = document.querySelector("#fileInput")
		fileInput.addEventListener("change", () => {
			console.log("file uploded")
			prod.style.backgroundColor = '#11bdfcff'
			group.style.backgroundColor = '#11bdfcff'
			group.style.color = 'white'
			prod.style.color = 'white'
			group.disabled =false;
			prod.disabled =false;

		})
	</script>
    <?php 

}

function handle_download_products(){
    if (!current_user_can('manage_options')) {
			wp_die('Unauthorized user');
		}

		global $wpdb;
        $wpdb->show_errors( true );
        $wpdb->query("SET SESSION sort_buffer_size = 256000000");

		$query = <<<SQL
		SELECT 
              wc.sku AS SKU,
              case pm.meta_value
                  WHEN 61923 THEN 'مسافری دبی'
                WHEN 54063 THEN 'کالای درشت رقابتی'
                WHEN 54062 THEN 'کالای کوچک رقابتی'
                WHEN 52114 THEN 'کالای خیلی درشت'
                WHEN 51451 THEN 'کالای درشت ترکیه'
                WHEN 51450 THEN 'لیر ترکیه'
                WHEN 44915 THEN 'دلار آمریکا'
                WHEN 44085 THEN 'قیمت درهم دبی'
                WHEN 43948 THEN 'سفارش کالای درشت'
                WHEN 43947 THEN 'سفارش کالای کوچک'
                WHEN 43946 THEN 'خرید قدیم'
                WHEN 23110 THEN 'کالای درشت'
                WHEN 10347 THEN 'کالای کوچک'
                ELSE 'Unknown'
             END AS 'قیمت درهم',
            	wc.stock_status AS status,
              p.post_title AS product_name,
              GROUP_CONCAT(DISTINCT t.name ORDER BY t.name SEPARATOR ', ')
            FROM wp_posts p
            INNER JOIN wp_term_relationships tr ON p.ID = tr.object_id
            INNER JOIN wp_term_taxonomy tt ON tr.term_taxonomy_id = tt.term_taxonomy_id
            INNER JOIN wp_terms t ON tt.term_id = t.term_id
            INNER JOIN wp_postmeta pm on p.ID = pm.post_id
            INNER JOIN wp_wc_product_meta_lookup wc on wc.product_id = p.ID
            WHERE  p.post_type = 'product' and pm.meta_key = '_mnswmc_currency_id'
            GROUP BY wc.sku,pm.meta_value,wc.stock_status, p.post_title;
SQL;


		$results = $wpdb->get_results($query, ARRAY_A);

		if (empty($results)) {
			wp_die('No products found for CSV export.'.	$wpdb->last_error);
		}

		// Define CSV filename
		$filename = 'products_export_' . date('Y-m-d') . '.csv';

		// Send headers to prompt download
		header('Content-Type: text/csv; charset=utf-8');
		header('Expires: 0');
           header("Pragma: public");
        header("Cache-Control: must-revalidate, post-check=0, pre-check=0");
        header("Cache-Control: private", false);
        header('Content-Type: text/csv; charset=utf-8');
        header("Content-Disposition: attachment; filename=\"" . $filename . " " . $date . ".csv\";" );
        header("Content-Transfer-Encoding: binary");
		// Output CSV
		$output = fopen('php://output', 'w');

		// Output column headers (CSV header row)
		fputcsv($output, array_keys($results[0]));

		// Output data rows
		foreach ($results as $row) {
			fputcsv($output, $row);
		}

		fclose($output);

		exit; // Important: stop execution after sending file
	}

function handle_upload_products()
{
	if (isset($_FILES['csv_file'])) {
		global $wpdb;


		$fileTmpPath = $_FILES['csv_file']['tmp_name'];
		$sql = <<<SQL
		UPDATE wp_postmeta pm
		JOIN wp_wc_product_meta_lookup wc ON pm.post_id = wc.product_id
		SET pm.meta_value = '%s'
		WHERE pm.meta_key = '_mnswmc_currency_ids'
		AND wc.sku = '%s';
		SQL;
		echo $sql;
		if (($handle = fopen($fileTmpPath, 'r')) !== false) {
			$header = $row = fgetcsv($handle);
			while (($row = fgetcsv($handle)) !== false) {
				$results = $wpdb->get_results($wpdb->prepare($sql,$map[$row[2]],$row[0]));
				if ($wpdb->last_error) {
					wp_die('Database query failed: ' . esc_html($wpdb->last_error));
				}
				echo $results;
			}
			fclose($handle);
			wp_redirect(admin_url());
			exit;
		} else {
			wp_die('Unable to open the uploaded CSV file.');
		}
	} else {
		wp_die('File not uploaded or upload error.');
	}
}
function handle_upload_groups(){
	if (isset($_FILES['csv_file'])) {
		global $wpdb;
		$fileTmpPath = $_FILES['csv_file']['tmp_name'];
		$sql = <<<SQL
		UPDATE wp_postmeta pm
		INNER JOIN wp_posts p ON pm.post_id = p.ID
		INNER JOIN wp_term_relationships tr ON p.ID = tr.object_id
		INNER JOIN wp_term_taxonomy tt ON tr.term_taxonomy_id = tt.term_taxonomy_id
		INNER JOIN wp_terms t ON tt.term_id = t.term_id
		SET pm.meta_value = %s
		WHERE tt.taxonomy = 'product_cat'
		AND t.name = %s
		AND pm.meta_key = '_mnswmc_price_rounding';
		SQL;
		if (($handle = fopen($fileTmpPath, 'r')) !== false) {
			$header = $row = fgetcsv($handle);
			while (($row = fgetcsv($handle)) !== false) {
				$results = $wpdb->get_results($wpdb->prepare($sql,$row[1],$row[0]));
				if ($wpdb->last_error) {
					wp_die('Database query failed: ' . esc_html($wpdb->last_error));
				}
			}
			fclose($handle);
			wp_redirect(admin_url());
			exit;
		} else {
			wp_die('Unable to open the uploaded CSV file.');
		}
	} else {
		wp_die('File not uploaded or upload error.');
	}
}
