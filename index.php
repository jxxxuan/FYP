<?php
session_start();

// Custom utilities class and function
//require_once 'utils/booking_process.php';
require_once 'utils/constant.php';
require_once 'utils/helper.php';
require_once 'utils/Database.php';
date_default_timezone_set('Asia/Kuala_Lumpur');

// Parse the current request URL to match PHP file
$requestUri = str_replace(
    '\\/',
    DIRECTORY_SEPARATOR,
    ltrim(str_replace(BASEPATH, '', parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH)), '/')
);

$file = $requestUri === '' ? 'home' : $requestUri;
$main = getView($file);

$exist = file_exists($main);
if (!$exist) {
    $main = getView('404');
}

require_once APPPATH . 'views' . DIRECTORY_SEPARATOR . 'layout' . DIRECTORY_SEPARATOR . 'app.php';

if (!$exist) {
    http_response_code(404);
    exit();
}

?>
