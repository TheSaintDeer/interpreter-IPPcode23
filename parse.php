#!/usr/bin/php
<?php
// Implementační dokumentace k 1. úloze do IPP 2022/2023
// Jméno a příjmení: Ivan Golikov
// Login: xgolik00

ini_set('display_errors', 'stderr');

checkArguments();

$writer = new Writer();

getLine($writer);

$writer->endWriteAndWriteOut();
exit(0);

///////////////////////////

function checkArguments() {
    global $argc;

    $opts = getopt("", ["help"]);

    if ($argc == 1)
        return;

    elseif ($argc == 2)
        if (array_key_exists('help', $opts))
            printHelp();

    printParametersError();
}

function getLine($writer) {

    $data = trim(fgets(STDIN), " \n");
    $line = explode('#', $data);


    if ($writer->getInstructionOrder() == 0) {
        if (strtolower($line[0]) != ".ippcode23")
            printHeaderError();

        $writer->startWrite();
    } else {

    }

}

/*-------------------------------------------------
                    PRINTS
-------------------------------------------------*/


function printHelp() {
    printf("Usage: parser.php [options] <input >output\n");
    exit(0);
}

function printHeaderError() {
    fprintf(STDERR, "Missing line .IPPcode23!\n");
    exit(21);
}

function printParametersError() {
    fprintf(STDERR, "Bad arguments!\n");
    exit(10);
}


/*-------------------------------------------------
                    CLASS WRITER
-------------------------------------------------*/

class Writer {
    private $xml;

    private $instructionOrder = 0;
    private $arg = 0;

    public function startWrite() {
        $this->xml = new XMLWriter;
        $this->xml->openMemory();
        $this->xml->setIndent(4);

        $this->xml->startDocument("1.0", "UTF-8");
        $this->xml->startElement('program');
        $this->xml->writeAttribute('language', 'IPPcode23');

        $this->incrementInstructionOrder();
    }

    public function endWriteAndWriteOut() {
        $this->xml->endElement();
        $this->xml->endDocument();

        echo $this->xml->outputMemory();
    }

    public function getInstructionOrder() {
        return $this->instructionOrder;
    }

    public function incrementInstructionOrder() {
        $this->instructionOrder++;
    }
}

?>