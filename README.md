`python parser.py < test.txt | xclip -selection clipboard`

|   |#EOF|#QuotedStr|`end|`or|`is|#Ident|`epsilon|`axiom|
|---|---|---|---|---|---|---|---|---|
|Production|𝓔|---|---|---|---|Axiom NonTerm `is Rule RuleAlt `end Production|---|Axiom NonTerm `is Rule RuleAlt `end Production|
|Rule|---|RuleItem RuleTail|---|---|---|RuleItem RuleTail|`epsilon|---|
|RuleItem|---|Term|---|---|---|NonTerm|---|---|
|RuleTail|---|RuleItem RuleTail|𝓔|𝓔|---|RuleItem RuleTail|---|---|
|RuleAlt|---|---|𝓔|`or Rule RuleAlt|---|---|---|---|
|Axiom|---|---|---|---|---|𝓔|---|`axiom|
|NonTerm|---|---|---|---|---|#Ident|---|---|
|Term|---|#QuotedStr|---|---|---|---|---|---|
|Init|Production #EOF|---|---|---|---|Production #EOF|---|Production #EOF|
