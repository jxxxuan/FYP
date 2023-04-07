<?php
$date = new DateTime();

// Format the datetime object into the MySQL format
$formatted_date = $date->format('Y-m-d H:i:s');

echo $formatted_date;
?>