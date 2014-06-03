// get fraction(Mone + base) and change it to integer if possible otherwise - fraction

NUMBER_BUTIFER:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1);
  PUSH(R2);
  PUSH(R3);

  MOV(R1, FPARG(0)); // Mone
  MOV(R2, FPARG(1)); // Base

  MOV(R3, R1);
  REM(R3, R2);
  CMP(R3, 0);
  JUMP_EQ(L_NUMBER_BUTIFER_INTEGER);
	
	CMP(R2,0);
	JUMP_GT(L_NEGATIVE_END_FIX);
	MOV(R3,IMM(0));
	SUB(R3,R2);
	MOV(R2,R3);
	MOV(R3,IMM(0));
	SUB(R3,R1);
	MOV(R1,R3);

L_NEGATIVE_END_FIX:
  PUSH(R2);
  PUSH(R1);
  CALL(MAKE_SOB_FRACTION);
  DROP(2);
  JUMP(L_NUMBER_BUTIFER_END);

L_NUMBER_BUTIFER_INTEGER:
  DIV(R1, R2);
  PUSH(R1);
  CALL(MAKE_SOB_INTEGER);
  DROP(1);

	
  
L_NUMBER_BUTIFER_END:
  POP(R3);
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;
