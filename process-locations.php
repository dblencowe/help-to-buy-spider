<?php

define("MAPS_HOST", "maps.googleapis.com");
define("KEY", "AIzaSyDce7zgVxoVi8qY2Z1Nx2akrNC4jhAMNuE");	//Personal Google Maps API key

$csv = array_map("str_getcsv", file("points.csv", FILE_SKIP_EMPTY_LINES));
$keys = array_shift($csv);
array_push($keys, 'latitude', 'longitude');
$newCsv = [$keys];
$firstRow = true;
if (($handle = fopen("points.csv", "r")) !== false) {
    while (($data = fgetcsv($handle, 1000, ",")) !== false) {
        if ($firstRow) {
            $firstRow = false;
            continue;
        }
        
        if (empty($data[1])) {
            continue;
        }

        $delay = 0;
        $base_url = "https://" . MAPS_HOST . "/maps/api/geocode/xml?key=" . KEY;
        $request_url = $base_url . "&address=" . urlencode($data[1]);
        $xml = simplexml_load_file($request_url) or die("URL not loading");
        if (in_array($xml->status, ['OK', 'ZERO_RESULTS'])) {
            $geocode_pending = false;
            if ($xml->status == 'OK') {
                array_push($data, (float) $xml->result->geometry->location->lat, (float) $xml->result->geometry->location->lng);
            }
            $newCsv[] = $data;
        } elseif (strcmp($xml->status, "OVER_QUERY_LIMIT") == 0){
            $delay += 100000;
        } else {
            $geocode_pending = false;
            echo "Address " . $data[1] . " failed to be Geocoded.<br>Received status " . $xml->status . "<br><br>" . $request_url;
        }
        
        usleep($delay);
    }
    fclose($handle);
    file_put_contents('./points.csv', generateCsv($newCsv));
}

function generateCsv($data, $delimiter = ',', $enclosure = '"') {
    $handle = fopen('php://temp', 'r+');
    foreach ($data as $line) {
            fputcsv($handle, $line, $delimiter, $enclosure);
    }
    rewind($handle);
    while (!feof($handle)) {
            $contents .= fread($handle, 8192);
    }
    fclose($handle);
    return $contents;
}