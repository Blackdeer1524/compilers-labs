`python parser.py < test.txt | xclip -selection clipboard`






|   |)|#EOF|#Number|*|+|(|
|---|---|---|---|---|---|---|
|F|---|---|#Number|---|---|( E )|
|T|---|---|F T1|---|---|F T1|
|T1|---|---|---|* F T1|𝓔|---|
|E|---|---|T E1|---|---|T E1|
|E1|𝓔|𝓔|---|---|+ T E1|---|
|Init|---|---|E #EOF|---|---|E #EOF|





|   |n|+|(|*|)|#EOF|
|---|---|---|---|---|---|---|
|E|T E1|---|T E1|---|---|---|
|F|n|---|( E )|---|---|---|
|T|F T1|---|F T1|---|---|---|
|T1|---|𝓔|---|* F T1|---|---|
|E1|---|+ T E1|---|---|𝓔|𝓔|
|#Init|E #EOF|---|E #EOF|---|---|---|

|   |`end|#QStr|#IDENT|`or|#EOF|`is|`axiom|
|---|---|---|---|---|---|---|---|
|Production|-|-|Axiom NonTerm `is Rule RuleAlt `end Production|-|𝓔|-|Axiom NonTerm `is Rule RuleAlt `end Production|
|Axiom|-|-|𝓔|-|-|-|`axiom|
|NonTerm|-|-|#IDENT|-|-|-|-|
|RuleItem|-|Term|NonTerm|-|-|-|-|
|Term|-|#QStr|-|-|-|-|-|
|Rule|-|RuleItem RuleTail|RuleItem RuleTail|-|-|-|-|
|RuleTail|𝓔|RuleItem RuleTail|RuleItem RuleTail|𝓔|-|-|-|
|RuleAlt|𝓔|-|-|`or Rule RuleAlt|-|-|-|
|#Init|-|-|Production #EOF|-|Production #EOF|-|Production #EOF|
