build: parser.lex
	flex parser.lex
	gcc lex.yy.c -o parser
	