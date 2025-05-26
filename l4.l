%option reentrant noyywrap bison-bridge bison-locations
%option extra-type="struct Extra *"

/* Подавление предупреждений для -Wall */
%option noinput nounput

%{
#include <stdio.h>
#include <stdlib.h>
#include "l4.h"
#include "l4.tab.h"  /* файл генерируется Bison’ом с опцией -d */

#define YY_USER_ACTION                                                         \
    {                                                                          \
        int i;                                                                 \
        struct Extra *extra = yyextra;                                         \
        if (!extra->continued) {                                               \
            yylloc->first_line = extra->cur_line;                              \
            yylloc->first_column = extra->cur_column;                          \
        }                                                                      \
        extra->continued = false;                                              \
        for (i = 0; i < yyleng; ++i) {                                         \
            if (yytext[i] == '\n') {                                           \
                extra->cur_line += 1;                                          \
                extra->cur_column = 1;                                         \
            } else {                                                           \
                extra->cur_column += 1;                                        \
            }                                                                  \
        }                                                                      \
        yylloc->last_line = extra->cur_line;                                   \
        yylloc->last_column = extra->cur_column;                               \
    }

void yyerror(YYLTYPE *loc,
             yyscan_t scanner,
             const char *message) {
    printf("Error (%d,%d): %s\n", loc->first_line, loc->first_column, message);
}

%}

IDENT_PREF [_!@\.#]
DIGIT [0-9]
LETTER [a-zA-Z]

IDENT {IDENT_PREF}({LETTER}|{DIGIT})+

%x NUMBER NUMBER_SYSTEM_START NUMBER_SYSTEM_END 

%%

\r\n {/*printf("\n"); return NEW_LINE;*/}
\r   {/*printf("\n"); return NEW_LINE;*/}
\n   {/*printf("\n"); return NEW_LINE;*/}

[\t ]+

:= return KW_ASSIGN;
\+\+\+ return KW_ELSE;

\< return LEFT_ANGLE;
\> return RIGHT_ANGLE;
\( return LEFT_PAREN;
\) return RIGHT_PAREN;
\[ return LEFT_BRACE;
\] return RIGHT_BRACE;

\, return COMMA;
\: return COLON;
\? return QUESTION;
\& return AMPERSAND;
\\ return ASSERT;
\^ return RETURN;

\+ return PLUS;
\- return MINUS;
\* return MULT;
\/ return DIV;


_and_ return KW_AND;
_or_ return KW_OR;
_xor_ return KW_XOR;

_mod_ return KW_MOD;

not_ return KW_NOT;
_pow_ return KW_POW;

_eq_ return KW_EQ;
_ge_ return KW_GE;
_gt_ return KW_GT;
_le_ return KW_LE;
_lt_ return KW_LT;
_ne_ return KW_NE;

false return LIT_FALSE;
true return LIT_TRUE;

nothing return KW_NOTHING;
new_ return KW_NEW;

(int|char|bool) {
                    yylval->str = strdup(yytext);
                    return TYPE;
                }

{IDENT}         {
                    yylval->str = strdup(yytext);
                    return IDENT;
                }

([a-zA-Z0-9]+)\{([0-9]+)\} {
    // yytext contains the whole match, but you can use yymore() or sscanf, or manually extract
    // For example, using sscanf:
    char value[256];
    int system;
    sscanf(yytext, "%[^{}]{%d}", value, &system);
    yylval->number.value = strdup(value);
    yylval->number.system = system;
    return NAME;
}

[a-zA-Z0-9]+ {
    yylval->number.value = strdup(yytext);
    yylval->number.system = 10; // or some default
    return NAME;
}

\".\"   {
            yylval->str = strdup(yytext);
            return SYMBOL;
        }

\$.+\$  {
            yylval->str = strdup(yytext);
            return SYMBOL;
        }

\%.+\%  {
            yylval->str = strdup(yytext);
            return STR_SYMBOL;
        }

\%\%    {
            return FUNC_END;
        }

\%  {
        return BLOCK_END;
    }
 
 
\'.*\'  {
            yylval->str = strdup(yytext);
            return STRING;
        }

\{.*\}  {
            // yylval->str = strdup(yytext);
            printf("%s", yytext);
            // return STRING;
        }


%%

void init_scanner(FILE *input, yyscan_t *scanner, struct Extra *extra) {
    extra->continued = false;
    extra->cur_line = 1;
    extra->cur_column = 1;

    yylex_init(scanner);
    yylex_init_extra(extra, scanner);
    yyset_in(input, *scanner);
}

void destroy_scanner(yyscan_t scanner) {
    yylex_destroy(scanner);
}
