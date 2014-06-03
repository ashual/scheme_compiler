/* < function */

L_LOWER:
  PUSH(FP);
  MOV(FP, SP);

  PUSH(R1); // R1 will be the mone of the previus number
  PUSH(R2); // R2 will be the base of the previus number
  PUSH(R3); // R3 will be the mone of the current number
  PUSH(R4); // R4 will be the base of the current number
  PUSH(R5); // R5 will be the pointer for the next number

  CALL(VariadicStart);

  MOV(R5, FPARG(2))

  // Check if the first is null
  PUSH(R5);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(LERROR_NUM_OF_PARAMS_NO_MATCH);

  // Put the number in R5 into R3 and R4
  CALL(L_MAKE_IT_FRACTION);
  // Set the fisrt number
  MOV(R1, R3);
  MOV(R2, R4);

  MOV(R5, INDD(R5,2)); // Go to next number pos

L_LOWER_LOOP:
  // Check if reach the null
  PUSH(R5);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_LOWER_END_TRUE);

  // Put the number in R5 into R3 and R4
  CALL(L_MAKE_IT_FRACTION);

  // Move to Mutal base
  MUL(R1, R4);
  MUL(R2, R3);

  // Calc the < operation
  CMP(R1, R2);
  JUMP_GE(L_LOWER_END_FALSE);

  // Set R3, R4 to be the prev number
  MOV(R1, R3);
  MOV(R2, R4);

  MOV(R5, INDD(R5,2)); // Go to next number pos
  JUMP(L_LOWER_LOOP);

L_LOWER_END_FALSE:
  MOV(R0, IMM(6)); // 6 is false
  JUMP(L_LOWER_END);
L_LOWER_END_TRUE:
  MOV(R0, IMM(8)); // 8 is true
L_LOWER_END:
  POP(R5);
  POP(R4);
  POP(R3);
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;

