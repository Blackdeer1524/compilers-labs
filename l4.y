%{
#include <stdio.h>
#include "l4.h"
%}

%define api.pure
%define locations

%lex-param {yyscan_t scanner}

%parse-param {yyscan_t scanner}
%union {
    char* str;
    struct {
        char *value;
        int system;
    } number;
}

%left PLUS MINUS 
%left MULT DIV

%left KW_AND KW_OR KW_XOR
%left KW_MOD
%right UMINUS KW_NOT KW_POW

%nonassoc KW_EQ KW_GE KW_GT KW_LE KW_LT KW_NE 
%nonassoc KW_ASSIGN

%token LIT_FALSE LIT_TRUE
%token KW_NOTHING 
%token KW_NEW 

%token FUNC_END BLOCK_END KW_ELSE LEFT_ANGLE RIGHT_ANGLE LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE
%token COMMA COLON QUESTION ASSERT RETURN COMMENT AMPERSAND

%token SYMBOL 

%token <str> TYPE
%token <str> NAME
%token <str> IDENT
%token <str> STRING 
%token <str> STR_SYMBOL 

%{
int yylex(YYSTYPE *yylval_param, YYLTYPE *yylloc_param, yyscan_t scanner);
void yyerror(YYLTYPE *loc, yyscan_t scanner, const char *message);
%}

%%
PROGRAM : 
    FUNCTION PROGRAM
    | 
    ;

FUNCTION :
    FUNC_HEADER FUNC_BODY
    ;

VAR_DECL :
    LEFT_PAREN {printf("(");} 
        TYPE_DECL IDENT[N] {printf("%s", $N);} 
    RIGHT_PAREN {printf(")");}
    ;

FUNC_HEADER :
    LEFT_PAREN {printf("(");} TYPE_DECL 
        LEFT_BRACE {printf("[");} 
            NAME[N] {printf("%s", $N);} FUNC_PARAMS 
        RIGHT_BRACE {printf("]");} 
    RIGHT_PAREN {printf(")");} 
    | 
    ;

    FUNC_PARAMS:
        VAR_DECL FUNC_PARAMS
        | 
        ;

TYPE_DECL: 
    LEFT_ANGLE {printf("<"); } TYPE_DECL RIGHT_ANGLE {printf("> ");}
    | TYPE[T] {printf("%s", $T);}
    ;

FUNC_BODY : 
    STATEMENTS FUNC_END {printf("%%%%");}

ARRAY_INDEXING :
    LEFT_ANGLE {printf("<");} EXPRESSION {printf(" ");}EXPRESSION RIGHT_ANGLE {printf(">");}
    ;

STATEMENTS: 
    STATEMENT STATEMENTS
    |
    ;
        STATEMENT:
            VAR_DECL         OPTIONAL_ASSIGNMENT COMMA {printf(", ");} 
            | IDENT[N] {printf("%s", $N);} ASSIGNMENT COMMA {printf(", ");} 
            | ARRAY_INDEXING ASSIGNMENT COMMA {printf(", ");} 
            | ASSERT {printf("\\ ");} LOGIC COMMA {printf(", ");} 
            | RETURN {printf("^ ");} EXPRESSION COMMA {printf(", ");} 
            | RETURN {printf("^ ");} COMMA {printf(", ");} 
            | IF 
            | LOOP 
            ;
            

            ASSIGNMENT : 
                KW_ASSIGN {printf(" := ");} ASSIGNMENT_RHS 
                ;

                ASSIGNMENT_RHS:
                    EXPRESSION 
                    |   KW_NEW {printf("new_");} 
                            LEFT_ANGLE {printf("<");} 
                                TYPE_DECL 
                            RIGHT_ANGLE {printf(">");} 
                        EXPRESSION 
                    | STRINGS_BLOCK 
                    ;

            OPTIONAL_ASSIGNMENT :
                ASSIGNMENT
                | 
                ;  

    STRINGS_BLOCK :
        | STRING[S] {printf("%s", $S);} STRINGS_BLOCK
        | STR_SYMBOL[S] {printf("%s", $S);} STRINGS_BLOCK
        |
        ;


EXPRESSION :
      EXPRESSION MULT   {printf(" * ");} EXPRESSION
    | EXPRESSION DIV    {printf(" / ");} EXPRESSION
    | EXPRESSION KW_MOD {printf(" _mod_ ");} EXPRESSION
    | EXPRESSION KW_POW {printf(" _pow_ ");} EXPRESSION
    | EXPRESSION KW_XOR {printf(" _xor_ ");} EXPRESSION
    | EXPRESSION PLUS   {printf(" + ");} EXPRESSION
    | EXPRESSION MINUS  {printf(" - ");} EXPRESSION
    | MINUS {printf("-");} EXPRESSION %prec UMINUS
    | LEFT_PAREN {printf("(");} EXPRESSION RIGHT_PAREN {printf(")");}
    | FUNC_CALL
    | ARRAY_INDEXING
    | NAME[N]  {printf("%s", $N);}
    | IDENT[N] {printf("%s", $N);}
    | KW_NOTHING {printf("nothing");}
    ;

FUNC_CALL : 
    LEFT_BRACE {printf("[");} NAME[N] {printf("%s", $N);} ARGS RIGHT_BRACE {printf("]");}
    ;

    ARGS : 
        {printf(" ");} EXPRESSION ARGS
        |
        ;

LOGIC :
    LOGIC KW_OR    {printf(" _or_ ");} LOGIC
    | LOGIC KW_AND {printf(" _and_ ");} LOGIC
    | KW_NOT       {printf(" _not_ ");} LOGIC
    | LEFT_PAREN   {printf("(");} LOGIC RIGHT_PAREN {printf(")");}
    | COMPARISON
    | LIT_TRUE {printf("true");}
    | LIT_FALSE {printf("false");}
    | IDENT[N] {printf("%s", $N);}
    ;

IF: 
    LEFT_PAREN {printf("(");} QUESTION {printf("?");} LOGIC RIGHT_PAREN {printf(")");} STATEMENTS OPTIONAL_ELSE_BRANCH BLOCK_END {printf("%%");}
    ;

    OPTIONAL_ELSE_BRANCH :
        KW_ELSE {printf("+++");} STATEMENTS
        |
        ;
    
    COMPARISON :
        EXPRESSION KW_LT {  printf(" _lt_ ");}EXPRESSION
        | EXPRESSION KW_LE {printf(" _le_ ");}EXPRESSION
        | EXPRESSION KW_GT {printf(" _gt_ ");}EXPRESSION
        | EXPRESSION KW_GE {printf(" _ge_ ");}EXPRESSION
        | EXPRESSION KW_EQ {printf(" _eq_ ");}EXPRESSION
        | EXPRESSION KW_NE {printf(" _ne_ ");}EXPRESSION
        ;

LOOP : 
     LOOP_HEADER STATEMENTS  BLOCK_END {printf("%%");}
     ;

    LOOP_HEADER : 
        LOOP_PREFIX LOGIC RIGHT_PAREN {printf(")");}
        | LOOP_PREFIX 
            IDENT[N] {printf("%s", $N);} 
            COLON {printf(" : ");} EXPRESSION 
            COMMA {printf(", ");} EXPRESSION 
          RIGHT_PAREN {printf(")");}
        | LOOP_PREFIX 
            IDENT[N] {printf("%s", $N);} 
            COLON {printf(" : ");} EXPRESSION 
            COMMA {printf(", ");} EXPRESSION 
            COMMA {printf(", ");} EXPRESSION
          RIGHT_PAREN {printf(")");}
        ;

        LOOP_PREFIX: 
            LEFT_PAREN {printf("(");} AMPERSAND {printf("&");}
            ;

%%

int main(int argc, char *argv[]) {
    FILE *input = 0;
    yyscan_t scanner;
    struct Extra extra;

    input = fopen("./input.txt", "r");
    // if (argc > 1) {
    //     printf("Read file %s\n", argv[1]);
    //     input = fopen(argv[1], "r");
    // } else {
    //     printf("No file in command line, use stdin\n");
    //     input = stdin;
    // }

    init_scanner(input, &scanner, &extra);

    // int tag;
    // YYSTYPE value;
    // YYLTYPE coords;
    // 
    // tag = yylex(&value, &coords, &scanner);

    yyparse(scanner);
    destroy_scanner(scanner);

    if (input != stdin) {
        fclose(input);
    }

    return 0;
}

