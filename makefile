.SUFIXES: .asm
%: %.asm
	gcc -x c -Iarch -o $@ $<
