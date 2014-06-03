/* * function */

L_MULT:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1); // R1 will be the mone of the sum
  PUSH(R2); // R2 will be the base of the sum
  PUSH(R3); // R3 will be the mone of the current number
  PUSH(R4); // R4 will be the base of the current number
  PUSH(R5); // R4 will be the pointer for the next number

  CALL(VariadicStart);

  // Set the sum to 1
  MOV(R1, 1);
  MOV(R2, 1);

  MOV(R5, FPARG(2));

L_MULT_LOOP:
  // Check if reach the null
  PUSH(R5);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_MULT_END);

  PUSH(INDD(R5,1));
  CALL(IS_SOB_INTEGER);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(L_MULT_NOT_INTEGER);

  MOV(R4, 1);
  MOV(R3, INDD(R5,1)); // Go to integer object
  MOV(R3, INDD(R3,1)); // Go to integer value

  JUMP(L_MULT_CALC);

L_MULT_NOT_INTEGER:
  PUSH(INDD(R5,1));
  CALL(IS_SOB_FRACTION);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(LERROR_TYPE_MISMATCH); // Must to be integer or fraction

  MOV(R3, INDD(R5,1)) // Go to fraction object
  MOV(R3, INDD(R3,1)) // Go to fraction mone value
  MOV(R4, INDD(R5,1)) // Go to fraction object
  MOV(R4, INDD(R4,2)) // Go to fraction base value

L_MULT_CALC:
  MUL(R1, R3);
  MUL(R2, R4);

  MOV(R5, INDD(R5,2)); // Go to next number pos
  JUMP(L_MULT_LOOP);

L_MULT_END:
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