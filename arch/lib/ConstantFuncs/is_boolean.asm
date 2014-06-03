/* Boolean? function */

L_BOOLEAN:
  PUSH(FP);
  MOV(FP, SP);

  CMP(FPARG(1), 1);
  JUMP_NE(LERROR_NUM_OF_PARAMS_NO_MATCH);

  PUSH(FPARG(2));
  CALL(IS_SOB_BOOL);
  DROP(1);

  CMP(R0,1);
  JUMP_EQ(L_BOOLEAN_TRUE);
  MOV(R0, 6); // 6 is false
  JUMP(L_BOOLEAN_END);
L_BOOLEAN_TRUE:
  MOV(R0, 8); // 8 is true
L_BOOLEAN_END:
  POP(FP);
  RETURN;