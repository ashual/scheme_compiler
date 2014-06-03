/* string? function */

L_STRING:
  PUSH(FP);
  MOV(FP, SP);

  CMP(FPARG(1), 1);
  JUMP_NE(LERROR_NUM_OF_PARAMS_NO_MATCH);

  PUSH(FPARG(2));
  CALL(IS_SOB_STRING);
  DROP(1);

  CMP(R0,1);
  JUMP_EQ(L_STRING_TRUE);
  MOV(R0, IMM(6)); // 6 is false
  JUMP(L_STRING_END);
L_STRING_TRUE:
  MOV(R0, IMM(8)); // 8 is true
L_STRING_END:
  POP(FP);
  RETURN;