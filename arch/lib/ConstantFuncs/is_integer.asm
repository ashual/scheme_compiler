/* Integer? function */

L_INTEGER:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1);
  PUSH(R2);

  MOV(R1, FPARG(2));

  CMP(FPARG(1), 1);
  JUMP_NE(LERROR_NUM_OF_PARAMS_NO_MATCH);

  PUSH(FPARG(2));
  CALL(IS_SOB_INTEGER);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_INTEGER_TRUE);

  PUSH(FPARG(2));
  CALL(IS_SOB_FRACTION);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(L_INTEGER_FALSE);

  MOV(R2, INDD(R1, 1)); /* Mone */
  MOV(R1, INDD(R1, 2)); /* Base */
  REM(R2, R1);
  CMP(R2, 0);
  JUMP_EQ(L_INTEGER_TRUE);

L_INTEGER_FALSE:
  MOV(R0, IMM(6));
  JUMP(L_INTEGER_EXIT);

L_INTEGER_TRUE:
  MOV(R0, IMM(8));

L_INTEGER_EXIT:
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;