<?php

require_once 'ikea_parser.php';
require_once 'zardan.php';

zardanInit();
ikeaInit();

foreach (getItems() as $item) {
    [$price, $tag, $stock] = getProductDetail($item);

    if ($price) {
        updateItem($item, $price, $stock, $tag);
    }
}