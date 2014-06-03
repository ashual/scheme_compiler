/* Char? function */

L_CHAR:
  PUSH(FP);
  MOV(FP, SP);

  CMP(FPARG(1), 1);
  JUMP_NE(LERROR_NUM_OF_PARAMS_NO_MATCH);

  PUSH(FPARG(2));
  CALL(IS_SOB_CHAR);
  DROP(1);

  CMP(R0,1);
  JUMP_EQ(L_CHAR_TRUE);
  MOV(R0, IMM(6)); // 6 is false
  JUMP(L_CHAR_END);
L_CHAR_TRUE:
  MOV(R0, IMM(8)); // 8 is true
L_CHAR_END:
  POP(FP);
  RETURN;