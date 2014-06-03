/* comapre 2 strings return 1 or 0 */

IS_STRING_EQUAL:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1);
  PUSH(R2);
  PUSH(R3);

  MOV(R1, FPARG(0)); // First string
  MOV(R2, FPARG(1)); // Second string

  // Go to string len position
  INCR(R1);
  INCR(R2);

  // Compare strings size
  CMP(IND(R1), IND(R2));
  JUMP_NE(IS_STRING_EQUAL_FALSE);
  MOV(R3, IND(R1)); // Save the strings size

// Compare strings content
IS_STRING_EQUAL_LOOP:
  CMP(R3, 0);
  JUMP_EQ(IS_STRING_EQUAL_TRUE);
  CMP(INDD(R1,R3), INDD(R2,R3));
  JUMP_NE(IS_STRING_EQUAL_FALSE);
  DECR(R3);
  JUMP(IS_STRING_EQUAL_LOOP);

IS_STRING_EQUAL_TRUE:
  MOV(R0, 1);
  JUMP(IS_STRING_EQUAL_END);
IS_STRING_EQUAL_FALSE:
  MOV(R0, 0);
IS_STRING_EQUAL_END:
  POP(R3);
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;