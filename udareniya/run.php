<?php
include('./simplehtmldom/simple_html_dom.php');


function main($argv) {
    $word = $argv[1];
    $f = urlencode(mb_substr($word, 0, 1));
    $w = urlencode($word);
    $url = "http://accentonline.ru/$f/$w";
    # echo $url;
    $html = file_get_html($url);
    foreach($html->find('.word-accent') as $e) {
        echo $e->innertext;
        echo "\n";
    }
}


main($argv);
