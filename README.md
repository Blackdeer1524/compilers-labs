`python parser.py < test.txt | xclip -selection clipboard`

|   |#Ident|`is|`axiom|`end|#QuotedStr|`epsilon|#EOF|`or|
|---|---|---|---|---|---|---|---|---|
|Production|Axiom NonTerm `is Rule RuleAlt `end Production|---|Axiom NonTerm `is Rule RuleAlt `end Production|---|---|---|𝓔|---|
|Rule|RuleItem RuleTail|---|---|---|RuleItem RuleTail|`epsilon|---|---|
|RuleItem|NonTerm|---|---|---|Term|---|---|---|
|RuleTail|NonTerm RuleTail|---|---|𝓔|Term RuleTail|---|---|𝓔|
|RuleAlt|---|---|---|𝓔|---|---|---|`or Rule RuleAlt|
|Axiom|𝓔|---|`axiom|---|---|---|---|---|
|NonTerm|#Ident|---|---|---|---|---|---|---|
|Term|---|---|---|---|#QuotedStr|---|---|---|
|Init|Production #EOF|---|Production #EOF|---|---|---|Production #EOF|---|
