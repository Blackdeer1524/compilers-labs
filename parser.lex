%option noyywrap bison-bridge bison-locations

%{

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define TAG_IDENT    1
#define TAG_NUMBER   2
#define TAG_CHAR     3
#define TAG_LPAREN   4
#define TAG_RPAREN   5
#define TAG_LT       6
#define TAG_GT       7
char *tag_names[] = {"END_OF_PROGRAM",
                     "IDENT",
                     "NUMBER",
                     "CHAR",
                     "LPAREN",
                     "RPAREN",
                     "LT",
                     "GT"};

struct Position {
    int line, pos, index;
};

void print_pos(struct Position *p) {
    printf("(%d, %d)", p->line, p->pos);
}

struct Fragment {
    struct Position starting, following;
};
typedef struct Fragment YYLTYPE;

void print_frag(struct Fragment *f) {
    print_pos(&(f->starting));
    printf("-");
    print_pos(&(f->following));
}

struct Node{
    struct Position pos;
    char* message;
    struct Node* next;
};

static struct Node* ERRORS = NULL;

union Token {
    unsigned long long code;
    long long int num;
    char ch;
};


typedef struct DictNode {
    char *key;
    unsigned long long value;
    struct DictNode *next;
} DictNode;

typedef struct Dictionary {
    DictNode *head;
    int size;
} Dictionary;

Dictionary *dict_create() {
    Dictionary *dict = (Dictionary *)malloc(sizeof(Dictionary));
    if (dict) {
        dict->head = NULL;
        dict->size = 0;
    }
    return dict;
}

static Dictionary* IDENT_DICT = NULL;
static unsigned long long IDENT_COUNTER = 0;

int dict_set(Dictionary *dict, const char *key, unsigned long long value) {
    if (!dict || !key) {
        return 0;
    }

    DictNode *current = dict->head;
    while (current) {
        if (strcmp(current->key, key) == 0) {
            return 1;
        }
        current = current->next;
    }

    DictNode *new_node = (DictNode *)malloc(sizeof(DictNode));
    if (!new_node) {
        return 0;
    }

    new_node->key = (char *)malloc(strlen(key) + 1);
    if (!new_node->key) {
        free(new_node);
        return 0;
    }
    strcpy(new_node->key, key);
    new_node->value = value;

    new_node->next = dict->head;
    dict->head = new_node;
    dict->size++;
    return 1;
}

unsigned long long dict_get(Dictionary *dict, const char *key) {
    if (!dict || !key) { 
        return -1; 
    }

    DictNode *current = dict->head;
    while (current) {
        if (strcmp(current->key, key) == 0) {
            return current->value;
        }
        current = current->next;
    }
    return -1;
}

void dict_free(Dictionary *dict) {
    if (!dict) return;

    DictNode *current = dict->head;
    while (current) {
        DictNode *next = current->next;
        free(current->key);
        free(current);
        current = next;
    }
    free(dict);
}

typedef union Token YYSTYPE;

int continued;
struct Position cur;
#define YY_USER_ACTION                                                         \
    {                                                                          \
        int i;                                                                 \
        if (!continued)                                                        \
            yylloc->starting = cur;                                         \
        continued = 0;                                                         \
                                                                               \
        for (i = 0; i < yyleng; i++) {                                         \
            if (yytext[i] == '\n') {                                           \
                cur.line++;                                                    \
                cur.pos = 1;                                                   \
            } else                                                             \
                cur.pos++;                                                     \
            cur.index++;                                                       \
        }                                                                      \
                                                                               \
        yylloc->following = cur;                                            \
    }

void init_scanner(char *program) {
    continued = 0;
    cur.line = 1;
    cur.pos = 1;
    cur.index = 0;
    // yy_scan_string(program);
}

void err(char *msg) {
    struct Node* node = malloc(sizeof(struct Node));
    node->pos = cur;
    node->message = msg;
    node->next = ERRORS;
    ERRORS = node;
}

void free_errors() {
    struct Node* cur = ERRORS;
    while (cur != NULL) {
        struct Node *next = cur->next;
        free(cur);
        cur = next;
    }
}

%}

LETTER [_a-zA-Z]
DIGIT [0-9]
IDENT {LETTER}({LETTER}|{DIGIT}|\-)*
NUMBER {DIGIT}+

%x CHAR 

%%
[\n\t ]+

\(                  return TAG_LPAREN;
\)                  return TAG_RPAREN;
\<                  return TAG_LT;
\>                  return TAG_GT;

{IDENT}             {
                        unsigned long long v = dict_get(IDENT_DICT, yytext);
                        if (v == -1) {
                            dict_set(IDENT_DICT, yytext, IDENT_COUNTER);
                            v = IDENT_COUNTER;
                            ++IDENT_COUNTER;
                        }

                        yylval->code = v;
                        return TAG_IDENT ;
                    }
{NUMBER}            {
                        yylval->num = atoi(yytext);
                        return TAG_NUMBER ;
                    }

\'                  BEGIN(CHAR);
.                   err("unexpected character"); 


<CHAR>\n            {
                        err("newline in constant");
                        BEGIN(0);
                        yylval->ch=0;
                    }
<CHAR>\\n           yylval->ch = '\n'; return TAG_CHAR;
<CHAR>\\\'          yylval->ch = '\''; return TAG_CHAR;
<CHAR>\\\\          yylval->ch = '\\'; return TAG_CHAR;
<CHAR>\\.           {
                       err(" unrecognized Escape sequence ");
                       yylval->ch = 0;
                    }
<CHAR>\'            BEGIN(0);
<CHAR>.             yylval->ch = yytext[0]; return TAG_CHAR;
<CHAR><<EOF>>       err("expected ', eof found"); return 0; 

%%

#define PROGRAM "123"

int main(int argc, char **argv) {
    int tag ;
    YYSTYPE value;
    YYLTYPE coords;
    
    if (argc > 1) {
        yyin = fopen(argv[1], "r");
    } else {
        yyin = stdin;
    }

    IDENT_DICT = dict_create(IDENT_DICT);
    
    init_scanner(PROGRAM);

    do {
        tag = yylex(&value, &coords);
        if (tag == 0) {
            break;
        }
        printf("%s ", tag_names[tag]);
        print_frag(&coords);
        printf(":");
        
        if (tag == TAG_IDENT) {
            printf(" %d", value.code);
        } else if (tag == TAG_NUMBER) {
            printf(" %d", value.num);
        } else if (tag == TAG_CHAR) {
            printf(" %c", value.ch);
        }
        printf("\n");
    } while (tag != 0);
    
    struct Node *cur = ERRORS;
    while (cur != NULL) {
        printf("%s", cur->message);
        print_pos(&(cur->pos));
        printf("\n");
        cur = cur->next;
    }

    free_errors();
    dict_free(IDENT_DICT);
    return 0;
}
