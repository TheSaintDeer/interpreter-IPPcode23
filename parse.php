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

            case "MOVE":
            case "INT2CHAR":
            case "STRLEN":
            case "TYPE":
            case "NOT":
                $instruction = new VarSymbInstr($parts[0], $parts[1], $parts[2]);
                break;

            case "PUSHS":
            case "WRITE":
            case "EXIT":
            case "DPRINT":
                $instruction = new SymbInstr($parts[0], $parts[1]);
                break;

            case "ADD":
            case "SUB":
            case "MUL":
            case "IDIV":
            case "LT":
            case "GT":
            case "EQ":
            case "AND":
            case "OR":
            case "STRI2INT":
            case "CONCAT":
            case "GETCHAR":
            case "SETCHAR":
                $instruction = new Var2SymbInstr($parts[0], $parts[1], $parts[2], $parts[3]);
                break;

            case "READ":
                $instruction = new VarTypeInstr($parts[0], $parts[1], $parts[2]);
                break;

            case "JUMPIFEQ":
            case "JUMPIFNEQ":
                $instruction = new Label2SymbInstr($parts[0], $parts[1], $parts[2], $parts[3]);
                break;

            default:
                printOperationCodeError();
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

        $this->arg++;
    }

    public function writeSymb($data) {
        $dataType = explode("@", $data);

        if (in_array($dataType[0], array("GF", "LF", "TF")))
            $this->writeArgument("var", $data);
        elseif (in_array($dataType[0], array("int", "bool", "string", "nil")))
            $this->writeArgument($dataType[0], $dataType[1]);
        else
            printLexicalError();
    }

    public function writeType($type) {
        //TODO checking types
        $this->writeArgument("type", $type);
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

    private $inst, $label;

    public function __construct(string $inst, string $label) {
        $this->inst = $inst;
        $this->label = $label;
    }

    public function getInstruction(): ArgumentsProducts {
        return new LabelArg($this->inst, $this->label);
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

class VarSymbInstr extends InstructionCreator {

    private $inst, $var, $symb;

    public function __construct(string $inst, string $var, string $symb) {
        $this->inst = $inst;
        $this->var = $var;
        $this->symb = $symb;
    }

    public function getInstruction(): ArgumentsProducts {
        return new VarSymbArg($this->inst, $this->var, $this->symb);
    }
}

class SymbInstr extends InstructionCreator {

    private $inst, $symb;

    public function __construct(string $inst, string $symb) {
        $this->inst = $inst;
        $this->symb = $symb;
    }

    public function getInstruction(): ArgumentsProducts {
        return new SymbArg($this->inst, $this->symb);
    }
}

class Var2SymbInstr extends InstructionCreator {

    private $inst, $var, $symb1, $symb2;

    public function __construct(string $inst, string $var, string $symb1, string $symb2) {
        $this->inst = $inst;
        $this->var = $var;
        $this->symb1 = $symb1;
        $this->symb2 = $symb2;
    }

    public function getInstruction(): ArgumentsProducts {
        return new Var2SymbArg($this->inst, $this->var, $this->symb1, $this->symb2);
    }
}

class VarTypeInstr extends InstructionCreator {

    private $inst, $var, $type;

    public function __construct(string $inst, string $var, string $type) {
        $this->inst = $inst;
        $this->var = $var;
        $this->type = $type;
    }

    public function getInstruction(): ArgumentsProducts {
        return new VarTypeArg($this->inst, $this->var, $this->type);
    }
}

class Label2SymbInstr extends InstructionCreator {

    private $inst, $label, $symb1, $symb2;

    public function __construct(string $inst, string $label, string $symb1, string $symb2) {
        $this->inst = $inst;
        $this->label = $label;
        $this->symb1 = $symb1;
        $this->symb2 = $symb2;
    }

    public function getInstruction(): ArgumentsProducts {
        return new Label2SymbArg($this->inst, $this->label, $this->symb1, $this->symb2);
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

class Var2SymbArg implements ArgumentsProducts {

    private $inst, $var, $symb1, $symb2;

    public function __construct(string $inst, string $var, string $symb1, string $symb2) {
        $this->inst = $inst;
        $this->var = $var;
        $this->symb1 = $symb1;
        $this->symb2 = $symb2;
    }
    
    public function fillWriter($writer): void {
        $writer->startWriteInstruction($this->inst);
        $writer->writeArgument("var", $this->var);
        $writer->writeSymb($this->symb1);
        $writer->writeSymb($this->symb2);
        $writer->endWriteInstruction();
    }
}

class SymbArg implements ArgumentsProducts {

    private $inst, $symb;

    public function __construct($inst, $symb) {
        $this->inst = $inst;
        $this->symb = $symb;
    }
    
    public function fillWriter($writer): void {
        $writer->startWriteInstruction($this->inst);
        $writer->writeSymb($this->symb);
        $writer->endWriteInstruction();
    }
}

class VarSymbArg implements ArgumentsProducts {

    private $inst, $var, $symb;

    public function __construct($inst, $var, $symb) {
        $this->inst = $inst;
        $this->var = $var;
        $this->symb = $symb;
    }
    
    public function fillWriter($writer): void {
        $writer->startWriteInstruction($this->inst);
        $writer->writeArgument("var", $this->var);
        $writer->writeSymb($this->symb);
        $writer->endWriteInstruction();
    }
}

class VarTypeArg implements ArgumentsProducts {

    private $inst, $var, $type;

    public function __construct($inst, $var, $type) {
        $this->inst = $inst;
        $this->var = $var;
        $this->type = $type;
    }
    
    public function fillWriter($writer): void {
        $writer->startWriteInstruction($this->inst);
        $writer->writeArgument("var", $this->var);
        $writer->writeType($this->type);
        $writer->endWriteInstruction();
    }
}

class Label2SymbArg implements ArgumentsProducts {

    private $inst, $label, $symb1, $symb2;

    public function __construct(string $inst, string $label, string $symb1, string $symb2) {
        $this->inst = $inst;
        $this->label = $label;
        $this->symb1 = $symb1;
        $this->symb2 = $symb2;
    }
    
    public function fillWriter($writer): void {
        $writer->startWriteInstruction($this->inst);
        $writer->writeArgument("label", $this->label);
        $writer->writeSymb($this->symb1);
        $writer->writeSymb($this->symb2);
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