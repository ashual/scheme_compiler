/* vector function */

L_VECTOR:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1); // save the size of the future vector
  PUSH(R2);
  PUSH(R3);
  PUSH(R4);
  PUSH(R5); // Pointer to paramter list

  CALL(VariadicStart);

  MOV(R5, FPARG(2));
  MOV(R1, 0);

L_VECTOR_LOOP:
  // Check if the current is null
  PUSH(R5);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_VECTOR_END);

  PUSH(INDD(R5,1));
  INCR(R1);
  MOV(R5, INDD(R5,2)); // Go to next number pos

  JUMP(L_VECTOR_LOOP);

L_VECTOR_END:

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