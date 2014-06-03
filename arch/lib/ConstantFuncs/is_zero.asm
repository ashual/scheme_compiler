/* ZERO? function */

L_ZERO:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1);

  CMP(FPARG(1), 1);
  JUMP_NE(LERROR_NUM_OF_PARAMS_NO_MATCH);

  MOV(R1, FPARG(2));

  PUSH(R1);
  PUSH(1); /* num of args */
  PUSH(1); /* env */
  CALL(L_NUMBER);
  DROP(3);
  CMP(R0, 8);
  JUMP_NE(L_ZERO_FALSE);

  CMP(INDD(R1, 1), 0);
  JUMP_NE(L_ZERO_FALSE);

  MOV(R0, IMM(8));
  JUMP(L_ZERO_EXIT);

L_ZERO_FALSE:
    MOV(R0, IMM(6));

L_ZERO_EXIT:
  POP(R1);
  POP(FP);
  RETURN;