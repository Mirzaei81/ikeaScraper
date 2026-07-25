<?php

$priceHeaders = [
    'Content-Type: application/json'
];
$headers = [
        'accept: */*',
        'accept-language: en-US,en;q=0.6',
        'content-type: text/plain;charset=UTF-8',
        'origin: https://www.ikea.com',
        'priority: u=1, i',
        'referer: https://www.ikea.com/',
        'sec-ch-ua: "Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile: ?0',
        'sec-ch-ua-platform: "Windows"',
        'sec-fetch-dest: empty',
        'sec-fetch-mode: cors',
        'sec-fetch-site: cross-site',
        'sec-gpc: 1',
        'session-id: 37b22e56-0c81-4897-88c0-a7297f554c31',
        'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-client-id: ef382663-a2a5-40d4-8afe-f0634821c0ed',
        ];


function getStock($sku)
{
    global $headers;

    $url = "https://api.salesitem.ingka.com/availabilities/ru/om?itemNos={$sku}&expand=StoresList";

    $ch = curl_init($url);

    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => $headers,
    ]);

    $response = curl_exec($ch);
    curl_close($ch);

    $data = json_decode($response, true);

    return $data['availabilities'][0]['buyingOption']['cashCarry']['availability']['quantity'] ?? 0;
}

function getPrice($sku)
{
    global $priceHeaders;

    if (!$sku) {
        return [null, null];
    }

    $url = "https://sik.search.blue.cdtapps.com/om/en/search?c=sr&v=20241114";

    $body = [
        "searchParameters" => [
            "input" => (int)$sku,
            "type" => "QUERY"
        ],
        "components" => [
            [
                "component" => "PRIMARY_AREA"
            ]
        ]
    ];

    for ($retry = 0; $retry < 5; $retry++) {

        $ch = curl_init($url);

        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($body),
            CURLOPT_HTTPHEADER => $priceHeaders,
            CURLOPT_TIMEOUT => 10 * (2 ** $retry)
        ]);

        $response = curl_exec($ch);

        if (!curl_errno($ch)) {
            curl_close($ch);

            $data = json_decode($response, true);

            if (empty($data['results'])) {
                return [null, null];
            }

            $item = $data['results'][0]['items'][0]['product'];

            return [
                $item['salesPrice']['numeral'],
                $item['tag']
            ];
        }

        curl_close($ch);
    }

    return [null, null];
}

function getProductDetail($item)
{
    try {
        $sku = $item['SKU'];

        [$price, $tag] = getPrice($sku);

        if (!$price) {
            logError(
                $sku,
                -1,
                $item['name'],
                $tag
            );

            return [null, null, null];
        }

        $stock = getStock($sku);

        return [$price, $tag, $stock];

    } catch (Exception $e) {

        error_log(
            "Error in item detail: " .
            json_encode($item) .
            " Error: " .
            $e->getMessage()
        );

        return [null, null, null];
    }
}