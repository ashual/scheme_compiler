/* REMAINDER function */

L_REMAINDER:
  PUSH(FP);
  MOV(FP, SP);

  PUSH(R1); // R1 will be the mone of the sum
  PUSH(R2); // R2 will be the base of the sum
  PUSH(R3); // R3 will be the mone of the current number
  PUSH(R4); // R4 will be the base of the current number
  PUSH(R5); // R4 will be the pointer for the next number

	
	MOV(R1,FPARG(2));
	MOV(R1,INDD(R1,IMM(1)));
	MOV(R2,FPARG(3));
	MOV(R2,INDD(R2,IMM(1)));
	MOV(R3,R1);
	DIV(R3,R2);
	MUL(R3,R2);
	SUB(R1,R3);
	PUSH(IMM(1));
    PUSH(R1);
    CALL(NUMBER_BUTIFER);
    DROP(2);




  POP(R5);
  POP(R4);
  POP(R3);
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;