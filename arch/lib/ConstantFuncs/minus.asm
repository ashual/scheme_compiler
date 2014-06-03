/* - function */

L_MINUS:
  PUSH(FP);
  MOV(FP, SP);

  PUSH(R1); // R1 will be the mone of the sum
  PUSH(R2); // R2 will be the base of the sum
  PUSH(R3); // R3 will be the mone of the current number
  PUSH(R4); // R4 will be the base of the current number
  PUSH(R5); // R4 will be the pointer for the next number

  CALL(VariadicStart);

	MOV(R5,FPARG(2));
	PUSH(R5);
	CALL(IS_SOB_NIL);
	DROP(1);
	CMP(R0, 1);
	JUMP_EQ(LERROR_TYPE_MISMATCH);
	
	
	
	PUSH(INDD(R5,1));
	CALL(IS_SOB_INTEGER);
	DROP(1);
	CMP(R0, 1);
	JUMP_NE(L_MINUS_NOT_INTEGER2);

	MOV(R2, 1);
	MOV(R1, INDD(R5,1)); // Go to integer object
	MOV(R1, INDD(R1,1)); // Go to integer value
	
	MOV(R5, INDD(R5,2));
	JUMP(L_MINUS_CONT);

L_MINUS_NOT_INTEGER2:
	PUSH(INDD(R5,1));
	CALL(IS_SOB_FRACTION);
	DROP(1);
	CMP(R0, 1);
	JUMP_NE(LERROR_TYPE_MISMATCH); // Must to be integer or fraction

	MOV(R1, INDD(R5,1)) // Go to fraction object
	MOV(R1, INDD(R1,1)) // Go to fraction mone value
	MOV(R2, INDD(R5,1)) // Go to fraction object
	MOV(R2, INDD(R2,2)) // Go to fraction base value
	
	MOV(R5, INDD(R5,2));
	JUMP(L_MINUS_CONT);
	
L_MINUS_CONT:
	PUSH(R5);
	CALL(IS_SOB_NIL);
	DROP(1);
	CMP(R0, 1);
	JUMP_NE(L_MINUS_LOOP);
	

  // Set the sum to zero
  
  MOV(R3,IMM(0));
  SUB(R3, R1);
  MOV(R1,R3);
  JUMP(L_MINUS_END);
  

L_MINUS_LOOP:
  // Check if reach the null
  PUSH(R5);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_MINUS_END);

  PUSH(INDD(R5,1));
  CALL(IS_SOB_INTEGER);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(L_MINUS_NOT_INTEGER);

  MOV(R4, 1);
  MOV(R3, INDD(R5,1)); // Go to integer object
  MOV(R3, INDD(R3,1)); // Go to integer value

  JUMP(L_MINUS_CALC);

L_MINUS_NOT_INTEGER:
  PUSH(INDD(R5,1));
  CALL(IS_SOB_FRACTION);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(LERROR_TYPE_MISMATCH); // Must to be integer or fraction

  MOV(R3, INDD(R5,1)) // Go to fraction object
  MOV(R3, INDD(R3,1)) // Go to fraction mone value
  MOV(R4, INDD(R5,1)) // Go to fraction object
  MOV(R4, INDD(R4,2)) // Go to fraction base value

L_MINUS_CALC:
  MUL(R1, R4);
  MUL(R3, R2);
  SUB(R1, R3);
  MUL(R2, R4);

  MOV(R5, INDD(R5,2)); // Go to next number pos
  JUMP(L_MINUS_LOOP);

L_MINUS_END:
  PUSH(R2);
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