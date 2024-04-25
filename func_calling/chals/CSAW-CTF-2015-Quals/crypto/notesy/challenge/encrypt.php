<?php

$m = str_split(strtoupper($_GET['m']));

$map = array(
    "A" => 'U',
    "B" => 'N',
    "C" => 'H',
    "D" => 'M',
    "E" => 'A',
    "F" => 'Q',
    "G" => 'W',
    "H" => 'Z',
    "I" => 'I',
    "J" => 'D',
    "K" => 'Y',
    "L" => 'P',
    "M" => 'R',
    "N" => 'C',
    "O" => 'J',
    "P" => 'K',
    "Q" => 'B',
    "R" => 'G',
    "S" => 'V',
    "T" => 'S',
    "U" => 'L',
    "V" => 'O',
    "W" => 'E',
    "X" => 'T',
    "Y" => 'X',
    "Z" => 'F'
);

foreach ($m as $key => $value) {
    if (array_key_exists($value, $map)){
        echo $map[$value];
    }
    else{
        echo htmlentities($value);
    }
}

?>