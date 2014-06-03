// This is special Function for = <> and similar
// Pay attention using this function is risky because you pass parameters and return value by registries!
// Get integer or fraction and put the number in R3 and R4
// Assume that it have the pointer to the integer\fraction in R5
L_MAKE_IT_FRACTION:
  PUSH(FP);
  MOV(FP, SP);

  PUSH(INDD(R5,1));
  CALL(IS_SOB_INTEGER);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(L_MAKE_IT_FRACTION_NOT_INTEGER);

  MOV(R4, 1);
  MOV(R3, INDD(R5,1)); // Go to integer object
  MOV(R3, INDD(R3,1)); // Go to integer value

  JUMP(L_MAKE_IT_FRACTION_EXIT);

L_MAKE_IT_FRACTION_NOT_INTEGER:
  PUSH(INDD(R5,1));
  CALL(IS_SOB_FRACTION);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(LERROR_TYPE_MISMATCH); // Must to be integer or fraction

  MOV(R3, INDD(R5,1)) // Go to fraction object
  MOV(R3, INDD(R3,1)) // Go to fraction mone value
  MOV(R4, INDD(R5,1)) // Go to fraction object
  MOV(R4, INDD(R4,2)) // Go to fraction base value

L_MAKE_IT_FRACTION_EXIT:
  POP(FP);
  RETURN;