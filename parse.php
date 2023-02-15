#!/usr/bin/php
<?php
// Implementační dokumentace k 1. úloze do IPP 2022/2023
// Jméno a příjmení: Ivan Golikov
// Login: xgolik00

ini_set('display_errors', 'stderr');

/*-------------------------------------------------
                HELPING FUNCTIONS
-------------------------------------------------*/


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

function getLine($writer, $line) {

    $line = trim($line, " \n");
    $data = explode('#', $line);

    if ($writer->getInstructionOrder() == 0) {
        if (strtolower($data[0]) != ".ippcode23")
            printHeaderError();

        $writer->startWrite();
    } else {

        $parts = explode(' ', $data[0]);

        switch($parts[0]){

            case "DEFVAR":
            case "POPS": 
                $instruction = new VarInstr($parts[0], $parts[1]);
                break;

            case "CALL":
            case "LABEL":
            case "JUMP":
                $instruction = new LabelInstr($parts[0], $parts[1]);
                break;

            case "CREATEFRAME":
            case "PUSHFRAME":
            case "POPFRAME":
            case "RETURN":
            case "BREAK":
                $instruction = new FreeInstr($parts[0]);
                break;
        }

        $instruction->convertToXML($writer);
    }

}

/*-------------------------------------------------
                    PRINTS
-------------------------------------------------*/


function printHelp() {
    printf("Usage: parser.php [options] <input >output\n");
    exit(0);
}

function printParametersError() {
    fprintf(STDERR, "Bad arguments!\n");
    exit(10);
}

function printHeaderError() {
    fprintf(STDERR, "Missing line .IPPcode23!\n");
    exit(21);
}

function printOperationCodeError() {
    fprintf(STDERR, "Unknown instruction!\n");
    exit(22);
}

function printLexicalError() {
    fprintf(STDERR, "Lexical or syntax error!\n");
    exit(23);
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
        $this->xml->setIndent(true);
        $this->xml->setIndentString("\t");

        $this->xml->startDocument("1.0", "UTF-8");
        $this->xml->startElement('program');
        $this->xml->writeAttribute('language', 'IPPcode23');

        $this->instructionOrder++;
    }

    public function endWriteAndWriteOut() {
        $this->xml->endElement();
        $this->xml->endDocument();

        echo $this->xml->outputMemory();
    }

    public function startWriteInstruction($opcode) {
        $this->xml->startElement('instruction');
        $this->xml->writeAttribute('order', $this->instructionOrder);
        $this->xml->writeAttribute('opcode', strtoupper($opcode));

        $this->arg++;
    }

    public function endWriteInstruction() {
        $this->xml->endElement();

        $this->arg = 0;
        $this->instructionOrder++;
    }

    public function writeArgument($type, $code) {
        $this->xml->startElement('arg'.$this->arg);
        $this->xml->writeAttribute('type', strtolower($type));
        $this->xml->text($code);
        $this->xml->endElement();
    }

    public function getInstructionOrder() {
        return $this->instructionOrder;
    }

}

/*-------------------------------------------------
                    CLASSES CREATOR
-------------------------------------------------*/


abstract class InstructionCreator {

    abstract public function getInstruction(): ArgumentsProducts;

    public function convertToXML($writer): void {

        $instruction = $this->getInstruction();

        $instruction->fillWriter($writer);
    }
}

class VarInstr extends InstructionCreator {

    private $inst, $var;

    public function __construct(string $inst, string $var) {
        $this->inst = $inst;
        $this->var = $var;
    }

    public function getInstruction(): ArgumentsProducts {
        return new VarArg($this->inst, $this->var);
    }
}

class LabelInstr extends InstructionCreator {

    private $inst, $var;

    public function __construct(string $inst, string $var) {
        $this->inst = $inst;
        $this->var = $var;
    }

    public function getInstruction(): ArgumentsProducts {
        return new LabelArg($this->inst, $this->var);
    }
}

class FreeInstr extends InstructionCreator {

    private $inst;

    public function __construct(string $inst) {
        $this->inst = $inst;
    }

    public function getInstruction(): ArgumentsProducts {
        return new FreeArg($this->inst);
    }
}

/*-------------------------------------------------
                    CLASSES PRODUCT
-------------------------------------------------*/


interface ArgumentsProducts {

    public function fillWriter($writer): void;
}

class VarArg implements ArgumentsProducts {

    private $inst, $var;

    public function __construct($inst, $var) {
        $this->inst = $inst;
        $this->var = $var;
    }
    
    public function fillWriter($writer): void {
        $writer->startWriteInstruction($this->inst);
        $writer->writeArgument("var", $this->var);
        $writer->endWriteInstruction();
    }
}

class LabelArg implements ArgumentsProducts {

    private $inst, $label;

    public function __construct($inst, $label) {
        $this->inst = $inst;
        $this->label = $label;
    }
    
    public function fillWriter($writer): void {
        $writer->startWriteInstruction($this->inst);
        $writer->writeArgument("label", $this->label);
        $writer->endWriteInstruction();
    }
}

class FreeArg implements ArgumentsProducts {

    private $inst;

    public function __construct($inst) {
        $this->inst = $inst;
    }
    
    public function fillWriter($writer): void {
        $writer->startWriteInstruction($this->inst);
        $writer->endWriteInstruction();
    }
}

/*-------------------------------------------------
                    MAIN CODE
-------------------------------------------------*/


checkArguments();

$writer = new Writer();

while ($line = fgets(STDIN))
    getLine($writer, $line);

$writer->endWriteAndWriteOut();
exit(0);


?>