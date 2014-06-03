/* make-vector function */

L_MAKEVECTOR:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1); // save the size of the future vector
  PUSH(R2); // Save the default char of the future vector
  PUSH(R3); // Loop Counter
  PUSH(R4);
  PUSH(R5); // Pointer to paramter list

  CALL(VariadicStart);


L_MAKEVECTOR_EXTRACT_PARAMS:
  MOV(R5, FPARG(2))

  // Check if the first is null
  PUSH(R5);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(LERROR_NUM_OF_PARAMS_NO_MATCH);

  MOV(R1, INDD(R5,1));

  // Check if R1 is integer
  PUSH(R1);
  CALL(IS_SOB_INTEGER);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(LERROR_TYPE_MISMATCH);

  MOV(R1, INDD(R1,1)); // Set in R1 the content of the integer

  // Check if R1 is positive or zero
  PUSH(R1);
  CALL(IS_NEGATIVE);
  DROP(1);
  CMP(R0, IMM(1));
  JUMP_EQ(LERROR_TYPE_MISMATCH);

  MOV(R5, INDD(R5,2)); // Go to next number pos

  // Check if the Second is null
  PUSH(R5);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_MAKEVECTOR_SET_DEFAULT);

  MOV(R2, INDD(R5,1));

  // Check if there are more paramteres - if yes error!
  MOV(R5, INDD(R5,2)); // Go to next number pos
  PUSH(R5);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(LERROR_NUM_OF_PARAMS_NO_MATCH);

  JUMP(L_MAKEVECTOR_BODY);

L_MAKEVECTOR_SET_DEFAULT:
  PUSH(0);
  CALL(MAKE_SOB_INTEGER);
  DROP(1);
  MOV(R2, R0);
L_MAKEVECTOR_BODY:

  MOV(R3, R1); // Set loop index
  // Enter the defult  to all the vector
L_MAKEVECTOR_LOOP:
  CMP(R3, 0);
  JUMP_EQ(L_MAKEVECTOR_END);
  PUSH(R2);
  DECR(R3);
  JUMP(L_MAKEVECTOR_LOOP);
L_MAKEVECTOR_END:

  // Create the vector
  PUSH(R1);
  CALL(MAKE_SOB_VECTOR);
  INCR(R1);
  DROP(R1);

  POP(R5);
  POP(R4);
  POP(R3);
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;