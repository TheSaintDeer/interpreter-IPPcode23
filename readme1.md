## Implementační dokumentace k 1. úloze do IPP 2022/2023
## Jméno a příjmení: Ivan Golikov
## Login: xgolik00

### Zadání
Cílem projektu bylo napsat skript v jazyce PHP pro interpretaci jazyka Sti23 v CML. Tato interpretace zahrnuje lexikální a sémantickou analýzu.
### parser.php
Skript parse.php zahrnuje vlastní třídy jako Writer a Statistics. Třída Writer je navržena tak, aby generovala a vypisovala soubor XML. Zatímco třída Statistics je nezbytná pro shromažďování informací pro další úkol STATP. 

Samotný program je postaven na cyklu, který čte řádky až do setkání s EOF. Po přečtení každého jednotlivého řádku dochází k jeho zpracování. Odstranění mezer a '\n', rozdělení řádku na dvě části (instrukce a komentář) a poté určení, co je instrukce. Poté dojde ke generování souboru XML a shromažďování statistik. 

Samotné pokyny jsou rozděleny do osmi skupin, které jsou rozděleny podle argumentů. K dokončení dalšího úkolu NVP byl použit návrhový vzor 'factory method'. InstructionCreator je tedy abstraktní třída pro vytváření tříd typů instrukcí (Ver Instr, LabelInstr, Var2SymbInstr atd.) a již vytvářejí třídy pro generování samotného XML kódu podle definovaného scénáře.