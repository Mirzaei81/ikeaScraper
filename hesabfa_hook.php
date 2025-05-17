<?php
// Original Answer
header('Content-Type: application/json');
$request = file_get_contents('php://input');
$req_dump = print_r( $request, true );
// Updated Answer
if ($json = json_decode(file_get_contents("php://input"), true)) {
   $data = $json;
   if($data["Password"]=="i7rq&:WI&ZcD" && $data["Action"]==181){
      
      create_vip_order($data["ObjectIdList"]);
   };
}
function create_vip_order($id) {
   try {
      global $woocommerce;
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
    "code": ' . $code . '
}',
         CURLOPT_HTTPHEADER => array(
            'Content-Type: application/json'
         ),
      ));

      $contact_res = curl_exec($curl);
      $contact = json_decode($contact_res,true);
      $first_name = $contact["Result"]["name"];
      $company = $contact["Result"]["company"];
      $phone = $contact["Result"]["Mobile"];
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
      "id": ' . $invoiceId . ';
   }',
         CURLOPT_HTTPHEADER => array(
            'Content-Type: application/json'
         ),
      ));

      $response = curl_exec($curl);

      curl_close($curl);
      $factor = json_decode($response, true);


      $order = wc_create_order();
      // Check if InvoiceItems exist and iterate through them
      if (isset($factor['Result']['InvoiceItems']) && is_array($factor['Result']['InvoiceItems'])) {
         foreach ($factor['Result']['InvoiceItems'] as $item) {
            if (isset($item['Item']['ProductCode'])) {
               $productCode = (int)$item['Item']['ProductCode'];
               $productQuant = (int)$item['Quantity'];
               $order->add_product(wc_get_product($productCodes),$productQuant); // Use wc_get_product instead of deprecated get_product
            }
         }
      }

      $address = array(
         'first_name' => $first_name,
         'last_name'  => $first_name,
         'company'  => $company,
         'phone'      => $phone,
         'address_1'  => $address_1,
         'address_2'  => $address_2,
         'city'       => $city,
         'state'      => $state,
         'postcode'   => $postcode,
         'country'    => $country,
      );

   
      // Now we create the order
      $order->set_address($address, 'billing');
      $order->set_address($address, 'shipping');
      $order->calculate_totals();
      $order->update_status("processing", 'Imported order', TRUE);
      file_put_contents("new_created_order.log",print_r($order,true));
      add_action('woocommerce_init', 'create_vip_order');
   } catch (Throwable $th) {
      file_put_contents("hesabfa_error.log", print_r($th, true));
   };
}

