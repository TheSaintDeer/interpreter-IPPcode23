#!/usr/bin/php
<?php
// Implementační dokumentace k 1. úloze do IPP 2022/2023
// Jméno a příjmení: Ivan Golikov
// Login: xgolik00

ini_set('display_errors', 'stderr');

/*-------------------------------------------------
                HELPING FUNCTIONS
-------------------------------------------------*/

// function to control input arguments
function checkArguments() {
    global $argc;

    $opts = getopt("", ["help", "stats:"]);

    if ($argc == 1) // one input argument
        return;

    elseif ($argc > 1) { // two or more input arguments
        if (array_key_exists('help', $opts))
            printHelp();

        if (array_key_exists('stats', $opts))
            return;
    }

    printParametersError();
}

/**
 * @var - element of array
 * my filter for array
 */
function filterArray ($var) {
    return ($var !== NULL && $var !== FALSE && $var !== "");
}

/**
 * @count - required number of function arguments
 * @parts - function arguments
 * count number arguments and delete empty elements in array
 */
function countOrderArguments($count, &$parts) {
    if (count($parts) != $count)
        printLexicalError();

    $arr = array();
    foreach ($parts as $element) {
        array_push($arr, $element);
    }   

    $parts = $arr;
}

/**
 * @writer - variable for writting XML 
 * @stats - variable for count statistics
 * @line - input line
 * function to process the input string
 */
function getLine($writer, $stats, $line) {

    $line = trim($line, " \n"); // remove spaces at the beginning and end of a string
    $data = explode('#', $line, 2); // splitting a string into two parts: instruction and comment

    // header not yet read 
    if ($writer->getInstructionOrder() == 0) {
        
        if ($data[0] == "")
            return;

        if (trim($data[0], " ") != ".IPPcode23")
            printHeaderError();

        $writer->startWrite();
    } else {  // header was read
        $parts = array_filter(explode(' ', $data[0]), "filterArray");
        
        switch(strtoupper($parts[0])) {

            case "DEFVAR":
            case "POPS": 
                countOrderArguments(2, $parts);
                $instruction = new VarInstr($parts[0], $parts[1]);
                break;

            case "CALL":
            case "LABEL":
            case "JUMP":
                countOrderArguments(2, $parts);
                $instruction = new LabelInstr($parts[0], $parts[1]);
                break;

            case "CREATEFRAME":
            case "PUSHFRAME":
            case "POPFRAME":
            case "RETURN":
            case "BREAK":
                countOrderArguments(1, $parts);
                $instruction = new FreeInstr($parts[0]);
                break;

            case "MOVE":
            case "INT2CHAR":
            case "STRLEN":
            case "TYPE":
            case "NOT":
                countOrderArguments(3, $parts);
                $instruction = new VarSymbInstr($parts[0], $parts[1], $parts[2]);
                break;

            case "PUSHS":
            case "WRITE":
            case "EXIT":
            case "DPRINT":
                countOrderArguments(2, $parts);
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
                countOrderArguments(4, $parts);
                $instruction = new Var2SymbInstr($parts[0], $parts[1], $parts[2], $parts[3]);
                break;

            case "READ":
                countOrderArguments(3, $parts);
                $instruction = new VarTypeInstr($parts[0], $parts[1], $parts[2]);
                break;

            case "JUMPIFEQ":
            case "JUMPIFNEQ":
                countOrderArguments(4, $parts);
                $instruction = new Label2SymbInstr($parts[0], $parts[1], $parts[2], $parts[3]);
                break;

            case "":
                break;

            default:
                printOperationCodeError();
        }


        if (isset($data[1]))
            $stats->writeIn($data[0], $data[1]);
        else
            $stats->writeIn($data[0], null);

        if ($parts[0] != "")
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
                    TYPES OF ARGUMENTS
-------------------------------------------------*/


function isVar($arg) {
    if (preg_match('/^(GF|LF|TF)@(_|-|\$|&|%|\*|!|\?|[a-zA-Z])(_|-|\$|&|%|\*|!|\?|[a-zA-Z0-9])*$/', $arg))
        return $arg;
    
    printLexicalError();
}

function isConst($arg) {
    if (preg_match('/^(int|bool|string|nil)@.*$/', $arg)) {

        $data = explode('@', $arg, 2);
        switch ($data[0]) {
            case "int":
                if (preg_match('/^0|-\d\d*|\d\d*$/', $data[1]))
                    return $arg;
                break;

            case "bool":
                if (preg_match('/^(true|false)$/', $data[1]))
                    return $arg;
                break;

            case "string":
                if (preg_match('/^$|^(_|\w|\\\d\d\d|[á|č|ď|é|ě|í|ň|ó|ř|š|ť|ú|ů|ý|ž])(\w|\\\d\d\d|[\<,\-,\>,\/,\@,\=,\§,\,,\;,\(,\),\&]|[á|č|ď|é|ě|í|ň|ó|ř|š|ť|ú|ů|ý|ž])*$/', $data[1]))
                    return $arg;
                break;

            case "nil":
                if (preg_match('/^nil$/', $data[1]))
                    return $arg;
                break;
        }

    } 
    printLexicalError();
}

function isType($arg) {
    if (preg_match('/^(int|bool|string)$/', $arg))
        return $arg;
    
    printLexicalError();
}

function isLabel($arg) {
    if (preg_match('/^(\?|!|_|-|\$|&|%|\*|[a-zA-Z])(\?|!|_|-|\$|&|%|\*|[a-zA-Z0-9])*$/', $arg))
        return $arg;
    
    printLexicalError();
}

function isSymb($arg) {
    if (preg_match('/^(int|bool|string|nil)@.*$/', $arg))
        return isConst($arg);
    elseif (preg_match('/^(GF|LF|TF)@.*$/', $arg))
        return isVar($arg);

    printLexicalError();
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
        $this->xml->setIndentString("  ");

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
        $dataType = explode("@", $data, 2);

        if (in_array($dataType[0], array("GF", "LF", "TF")))
            $this->writeArgument("var", $data);
        elseif (in_array($dataType[0], array("int", "bool", "string", "nil")))
            $this->writeArgument($dataType[0], $dataType[1]);
        else
            printLexicalError();
    }

    public function writeType($type) {
        $this->writeArgument("type", $type);
    }

    public function getInstructionOrder() {
        return $this->instructionOrder;
    }

}

/*-------------------------------------------------
                CLASS FOR STATISTICS
-------------------------------------------------*/


class Statistics {

    private $stats = [
        'loc' => 0,
        'comments' => 0,
        'label' => 0,
        'jumps' => 0,
        'fwjumps' => 0,
        'backjumps' => 0,
    ];

    private $labels = array();
    private $calls = array();

    private function addStat($stat) {
        $this->stats[$stat]++;
    }

    public function writeIn($instr, $comment) {

        if ($comment != null)
            $this->addStat("comments");

        if ($instr != null) {

            $this->addStat("loc");
            $parts = array_filter(explode(' ', $instr), "filterArray");

            if ($parts[0] == "LABEL") {
                $this->addStat("label");
                array_push($this->labels, $parts[1]);
            }

            $isJump = in_array($parts[0], array("JUMP", "JUMPIFEQ", "JUMPIFNEQ"));

            if ($isJump) {
                $this->addStat("jumps");

                if (in_array($parts[1], $this->labels))
                    $this->addStat("fwjumps");
                else
                    $this->addStat("backjumps");
            }

            if ($parts[0] == "CALL") {
                $this->addStat("jumps");

                if (in_array($parts[1], $this->labels)) {
                    $this->addStat("fwjumps");
                    array_push($this->calls, "b");
                } else {
                    $this->addStat("backjumps");
                    array_push($this->calls, "f");
                }
            }

            if ($parts[0] == "RETURN") {
                $this->addStat("jumps");

                if (!empty($call))
                    $move = array_pop($calls);

                if ($move == "f")
                    $this->addStat("fwjumps");
                else
                    $this->addStat("backjumps");
            }
        }
        
    }

    public function writeOut() {
        global $argc;
        global $argv;

        if ($argc > 2) {
            
            if (strncmp($argv[1], "--stats", 7) !== 0)
                printParametersError();
            else
                $nameOfFile = explode("=", $argv[1]);
            
            $handle = fopen($nameOfFile[1], "w");

            for ($i = 2; $i < $argc; $i++) {

                if (strncmp($argv[$i], "--stats", 7) === 0) {
                    fclose($handle);
                    $nameOfFile = explode("=", $argv[$i]);
                    $handle = fopen($nameOfFile[1], "w");

                } elseif (strncmp($argv[$i], "--loc", 5) === 0) {
                    fwrite($handle, $this->stats['loc']."\n");

                } elseif (strncmp($argv[$i], "--comments", 10) === 0) {
                    fwrite($handle, $this->stats['comments']."\n");

                } elseif (strncmp($argv[$i], "--label", 7) === 0) {
                    fwrite($handle, $this->stats['label']."\n");

                } elseif (strncmp($argv[$i], "--jumps", 7) === 0) {
                    fwrite($handle, $this->stats['jumps']."\n");

                } elseif (strncmp($argv[$i], "--fwjumps", 9) === 0) {
                    fwrite($handle, $this->stats['fwjumps']."\n");

                } elseif (strncmp($argv[$i], "--backjumps", 11) === 0) {
                    fwrite($handle, $this->stats['backjumps']."\n");

                } elseif (strncmp($argv[$i], "--print", 7) === 0) {
                    fwrite($handle, $this->stats['backjumps']);
                    $text = explode("=", $argv[$i]);
                    fwrite($handle, $text[1]."\n");
                }

            }

            fclose($handle);
        }

        
    }
    
}

/*-------------------------------------------------
                    CLASSES OF CREATORS
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
                    CLASSES OF PRODUCTS
-------------------------------------------------*/


interface ArgumentsProducts {

    public function fillWriter($writer): void;
}

class VarArg implements ArgumentsProducts {

    private $inst, $var;

    public function __construct($inst, $var) {
        $this->inst = $inst;
        $this->var = isVar($var);
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
        $this->label = isLabel($label);
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
        $this->var = isVar($var);
        $this->symb1 = isSymb($symb1);
        $this->symb2 = isSymb($symb2);
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
        $this->symb = isSymb($symb);
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
        $this->var = isVar($var);
        $this->symb = isSymb($symb);
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
        $this->var = isVar($var);
        $this->type = isType($type);
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
        $this->label = isLabel($label);
        $this->symb1 = isSymb($symb1);
        $this->symb2 = isSymb($symb2);
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


$writer = new Writer();
$stats = new Statistics();

checkArguments();

while ($line = fgets(STDIN))
    getLine($writer, $stats, $line);

$writer->endWriteAndWriteOut();
$stats->writeOut();
exit(0);

?>