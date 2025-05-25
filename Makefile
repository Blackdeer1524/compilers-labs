debug: l4.l l4.h l4.y
	flex l4.l
	bison -g -d l4.y
	gcc -g -o calc *.c
	gdb ./calc

test: l4.l l4.h l4.y
	flex l4.l
	bison -g -d l4.y
	gcc -g -o calc *.c
	rm -f lex.yy.c l4.tab.?
	./calc input.txt