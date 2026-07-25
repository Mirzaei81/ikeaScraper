<?php

$clientHeaders = [
    'Content-Type: application/json',
    'Authorization: Basic YOUR_AUTH'
];

$currencies = [];

function zardanInit()
{
    global $currencies;

    $currencies = getMnscwPrices();

    $fp = fopen('offers.csv', 'w');

    fputcsv(
        $fp,
        ['name', 'tag', 'sku','price', 'stock']
    );

    fclose($fp);
}

function getMnscwPrices()
{
    $url =
        "https://zardaan.com/wp-json/mnswmc/v1/currency/9f8e7adfcdb7c395d33d08fcd968ade8";

    $response = file_get_contents($url);

    return json_decode($response, true);
}

function getItems()
{
    global $clientHeaders;

    $url =
        "https://zardaan.com/wp-json/wc/v3/get_nav/";

    $ch = curl_init($url);

    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => $clientHeaders
    ]);

    $response = curl_exec($ch);
    curl_close($ch);

    $data = json_decode($response, true);

    foreach ($data['response'] as $item) {
        yield $item;
    }
}

function updateItem($baseItem, $price, $stock, $tag)
{
    global $currencies;

    $curId = $baseItem['currency_id'];

    $payload = [
        'id'    => $baseItem['post_id'],
        'price' => round($price) * $currencies[$curId]['rate'] * 100,
        'base'  => round($price) * 10,
        'stock' => $stock
    ];

    $url =
        "https://zardaan.com/wp-json/wc/v3/price4/";

    $headers = [
        'Content-Type: application/json',
        'Authorization: Basic YOUR_AUTH'
    ];

    $ch = curl_init($url);

    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($payload),
        CURLOPT_HTTPHEADER => $headers
    ]);

    $response = curl_exec($ch);

    curl_close($ch);

    file_put_contents(
        'offers.csv',
        implode(',', [
            $baseItem['sku'],
            $stock,
            $baseItem['name'],
            'success',
            $tag
        ]) . PHP_EOL,
        FILE_APPEND
    );

    error_log($response);
}

function logError($sku, $stock, $name, $id, $reason, $tag = '')
{

    file_put_contents(
        'offers.csv',
        implode(',', [
            $sku,
            $stock,
            $name,
            $reason,
            $tag
        ]) . PHP_EOL,
        FILE_APPEND
    );
}