%{
#include <stdio.h>
#include <string.h>
#include "l4.h"

#define LINE_LIMIT 40
#define INDENT_SIZE 4

int indent(const int level) {
    printf("\n");
    for (int i = 0; i < level; ++i) {
        for (int j = 0; j < INDENT_SIZE; ++j) {
            printf(" ");
        }
    }
    return level * INDENT_SIZE;
}

int limited_print(
    const char *str,
    const int line_len,
    const int current_level
) {
    int res = 0;
    const size_t str_len = strlen(str);
    if (str_len + line_len > LINE_LIMIT) {
        res = indent(current_level + 1) + str_len; 
        printf("%s", str);
        return res;
    }
    res = str_len + line_len;
    printf("%s", str);
    return res;
}
%}

%define api.pure
%define locations

%lex-param {yyscan_t scanner}

%parse-param {yyscan_t scanner}
%parse-param {int indent_level}
%parse-param {int line_len}

%union {
    char* str;
    struct {
        char *value;
        int system;
    } number;
}

%left PLUS MINUS 
%left MULT DIV

%left KW_OR KW_XOR
%left KW_AND 
%left KW_MOD
%right UMINUS KW_NOT KW_POW

%nonassoc KW_EQ KW_GE KW_GT KW_LE KW_LT KW_NE 
%nonassoc KW_ASSIGN

%token LIT_FALSE LIT_TRUE
%token KW_NOTHING 
%token KW_NEW 

%token FUNC_END BLOCK_END KW_ELSE LEFT_ANGLE RIGHT_ANGLE LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE
%token COMMA COLON QUESTION ASSERT RETURN COMMENT AMPERSAND NEW_LINE

%token <str> SYMBOL 
%token <str> TYPE
%token <str> NAME
%token <str> IDENT
%token <str> STRING 
%token <str> STR_SYMBOL 

%{
int yylex(YYSTYPE *yylval_param, YYLTYPE *yylloc_param, yyscan_t scanner);
void yyerror(YYLTYPE *loc, yyscan_t scanner, int indent_level, int line_len, const char *message);
%}

%%
PROGRAM : 
    FUNCTION PROGRAM
    | 
    ;

FUNCTION:
    FUNC_HEADER FUNC_BODY 
    ;

VAR_DECL :
    LEFT_PAREN {line_len = limited_print("(", line_len, indent_level);} 
        TYPE_DECL IDENT[N] {line_len = limited_print($N, line_len, indent_level);} 
    RIGHT_PAREN {line_len = limited_print(")", line_len, indent_level);} 
    ;

FUNC_HEADER :
    LEFT_PAREN {line_len = limited_print("(", line_len, indent_level);} 
        TYPE_DECL {line_len = limited_print(" ", line_len, indent_level);} 
        LEFT_BRACE {line_len = limited_print("[", line_len, indent_level);} 
            NAME[N] {line_len = limited_print($N, line_len, indent_level);}  FUNC_PARAMS 
        RIGHT_BRACE {line_len = limited_print("]", line_len, indent_level);} 
    RIGHT_PAREN {
                    line_len = limited_print(")", line_len, indent_level);
                    ++indent_level;
                } 
    |   
        LEFT_BRACE {line_len = limited_print("[", line_len, indent_level);} 
            NAME[N] {line_len = limited_print($N, line_len, indent_level);}  FUNC_PARAMS 
        RIGHT_BRACE {
                        line_len = limited_print("]", line_len, indent_level);
                        ++indent_level;
                    } 
    ;

    FUNC_PARAMS:
        {line_len = limited_print(" ", line_len, indent_level);} VAR_DECL FUNC_PARAMS
        | 
        ;

TYPE_DECL: 
    LEFT_ANGLE {line_len = limited_print("<", line_len, indent_level); }  
        TYPE_DECL  
    RIGHT_ANGLE {line_len = limited_print(">", line_len, indent_level);} 
    | TYPE[T] {line_len = limited_print($T, line_len, indent_level);} 
    ;

FUNC_BODY : 
    STATEMENTS FUNC_END {
                            line_len = indent(--indent_level);
                            line_len = limited_print("%%", line_len, indent_level);
                            printf("\n\n");
                        } 

ARRAY_INDEXING :
    LEFT_ANGLE {line_len = limited_print("<", line_len, indent_level);} 
        EXPRESSION {line_len = limited_print(" ", line_len, indent_level);} 
        EXPRESSION 
    RIGHT_ANGLE {line_len = limited_print(">", line_len, indent_level);} 
    ;

STATEMENTS: 
    { line_len = indent(indent_level); } STATEMENT STATEMENTS
    |
    ;

    STATEMENT:
        VAR_DECL OPTIONAL_ASSIGNMENT COMMA {line_len = limited_print(", ", line_len, indent_level);} 
        | IDENT[N] {line_len = limited_print($N, line_len, indent_level);} ASSIGNMENT COMMA {line_len = limited_print(", ", line_len, indent_level);} 
        | ARRAY_INDEXING ASSIGNMENT COMMA {line_len = limited_print(", ", line_len, indent_level);} 
        | ASSERT {line_len = limited_print("\\ ", line_len, indent_level);} LOGIC COMMA {line_len = limited_print(", ", line_len, indent_level);} 
        | RETURN {line_len = limited_print("^ ", line_len, indent_level);} EXPRESSION COMMA {line_len = limited_print(", ", line_len, indent_level);} 
        | RETURN {line_len = limited_print("^ ", line_len, indent_level);} COMMA {line_len = limited_print(", ", line_len, indent_level);} 
        | IF 
        | LOOP 
        ;
        
        ASSIGNMENT : 
            KW_ASSIGN {line_len = limited_print(" := ", line_len, indent_level);}  ASSIGNMENT_RHS 
            ;

            ASSIGNMENT_RHS:
                EXPRESSION 
                |   KW_NEW {line_len = limited_print("new_", line_len, indent_level);}        
                        LEFT_ANGLE {line_len = limited_print("<", line_len, indent_level);}   
                            TYPE_DECL               
                        RIGHT_ANGLE {line_len = limited_print(">", line_len, indent_level);}  
                    EXPRESSION 
                | STRINGS_BLOCK 
                | SYMBOL[S] {line_len = limited_print($S, line_len, indent_level);}
                ;
                
                STRINGS_BLOCK :
                    | STRING[S]     {line_len = limited_print($S, line_len, indent_level);}  STRINGS_BLOCK
                    | STR_SYMBOL[S] {line_len = limited_print($S, line_len, indent_level);}  STRINGS_BLOCK
                    |
                    ;

        OPTIONAL_ASSIGNMENT :
            ASSIGNMENT
            | 
            ;  


EXPRESSION :
      EXPRESSION  MULT   {line_len = limited_print(" * ", line_len, indent_level);}      EXPRESSION 
    | EXPRESSION  DIV    {line_len = limited_print(" / ", line_len, indent_level);}      EXPRESSION 
    | EXPRESSION  KW_MOD {line_len = limited_print(" _mod_ ", line_len, indent_level);}  EXPRESSION 
    | EXPRESSION  KW_POW {line_len = limited_print(" _pow_ ", line_len, indent_level);}  EXPRESSION 
    | EXPRESSION  KW_XOR {line_len = limited_print(" _xor_ ", line_len, indent_level);}  EXPRESSION 
    | EXPRESSION  PLUS   {line_len = limited_print(" + ", line_len, indent_level);}      EXPRESSION 
    | EXPRESSION  MINUS  {line_len = limited_print(" - ", line_len, indent_level);}      EXPRESSION 
    | MINUS {line_len = limited_print("-", line_len, indent_level);} EXPRESSION %prec UMINUS
    | LEFT_PAREN {line_len = limited_print("(", line_len, indent_level);}  
        EXPRESSION  
      RIGHT_PAREN {line_len = limited_print(")", line_len, indent_level);}
    | FUNC_CALL 
    | ARRAY_INDEXING 
    | NAME[N]  {line_len = limited_print($N, line_len, indent_level);} 
    | IDENT[N] {line_len = limited_print($N, line_len, indent_level);}
    | KW_NOTHING {line_len = limited_print("nothing", line_len, indent_level);}
    ;

FUNC_CALL : 
    LEFT_BRACE {line_len = limited_print("[", line_len, indent_level);}  
        NAME[N] {line_len = limited_print($N, line_len, indent_level);}  ARGS 
    RIGHT_BRACE {line_len = limited_print("]", line_len, indent_level);} 
    ;

    ARGS : 
        {line_len = limited_print(" ", line_len, indent_level);} EXPRESSION  ARGS
        | {line_len = limited_print(" ", line_len, indent_level);} SYMBOL[N] {line_len = limited_print($N, line_len, indent_level);}  ARGS
        | 
        ;

LOGIC :
      LOGIC  KW_OR  {line_len = limited_print(" _or_ ", line_len, indent_level);}  LOGIC
    | LOGIC  KW_AND {line_len = limited_print(" _and_ ", line_len, indent_level);} LOGIC
    | KW_NOT       {line_len = limited_print(" _not_ ", line_len, indent_level);}  LOGIC
    | LEFT_PAREN   {line_len = limited_print("(", line_len, indent_level);} 
        LOGIC 
      RIGHT_PAREN {line_len = limited_print(")", line_len, indent_level);}
    | LIT_TRUE {line_len = limited_print("true", line_len, indent_level);}
    | LIT_FALSE {line_len = limited_print("false", line_len, indent_level);}
    | IDENT[N] {line_len = limited_print($N, line_len, indent_level);}
    | COMPARISON
    ;

IF: 
    LEFT_PAREN {line_len = limited_print("(", line_len, indent_level);} 
        QUESTION {line_len = limited_print("?", line_len, indent_level);} 
        LOGIC 
    RIGHT_PAREN {line_len = limited_print(")", line_len, indent_level); ++indent_level;} 
        STATEMENTS 
    OPTIONAL_ELSE_BRANCH 
    BLOCK_END {--indent_level; line_len = indent(indent_level); line_len = limited_print("%", line_len, indent_level);}
    ;

    OPTIONAL_ELSE_BRANCH :
        KW_ELSE {
                    --indent_level; 
                    indent(indent_level);
                    line_len = limited_print("+++", line_len, indent_level); 
                    ++indent_level;
                }
        STATEMENTS
        |
        ;
    
    COMPARISON :
          EXPRESSION KW_LT {line_len = limited_print(" _lt_ ", line_len, indent_level);} EXPRESSION
        | EXPRESSION KW_LE {line_len = limited_print(" _le_ ", line_len, indent_level);} EXPRESSION
        | EXPRESSION KW_GT {line_len = limited_print(" _gt_ ", line_len, indent_level);} EXPRESSION
        | EXPRESSION KW_GE {line_len = limited_print(" _ge_ ", line_len, indent_level);} EXPRESSION
        | EXPRESSION KW_EQ {line_len = limited_print(" _eq_ ", line_len, indent_level);} EXPRESSION
        | EXPRESSION KW_NE {line_len = limited_print(" _ne_ ", line_len, indent_level);} EXPRESSION
        ;

LOOP : 
     LOOP_HEADER {++indent_level;} STATEMENTS BLOCK_END {
                                                            --indent_level; 
                                                            line_len = indent(indent_level); 
                                                            line_len = limited_print("%", line_len, indent_level);
                                                        }
     ;

    LOOP_HEADER : 
        LOOP_PREFIX LOGIC RIGHT_PAREN {line_len = limited_print(")", line_len, indent_level);}
        | LOOP_PREFIX 
            IDENT[N] {line_len = limited_print($N, line_len, indent_level);} 
            COLON {line_len = limited_print(" : ", line_len, indent_level);} EXPRESSION 
            COMMA {line_len = limited_print(", ", line_len, indent_level);} EXPRESSION 
          RIGHT_PAREN {line_len = limited_print(")", line_len, indent_level);}
        | LOOP_PREFIX 
            IDENT[N] {line_len = limited_print($N, line_len, indent_level);} 
            COLON {line_len = limited_print(" : ", line_len, indent_level);} EXPRESSION 
            COMMA {line_len = limited_print(", ", line_len, indent_level);} EXPRESSION 
            COMMA {line_len = limited_print(", ", line_len, indent_level);} EXPRESSION
          RIGHT_PAREN {line_len = limited_print(")", line_len, indent_level);}
        ;

        LOOP_PREFIX: 
            LEFT_PAREN {line_len = limited_print("(", line_len, indent_level);} AMPERSAND {line_len = limited_print("& ", line_len, indent_level);}
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
    int indent_level = 0;
    int line_len = 0;
    yyparse(scanner, indent_level, line_len);
    destroy_scanner(scanner);

    if (input != stdin) {
        fclose(input);
    }

    return 0;
}

