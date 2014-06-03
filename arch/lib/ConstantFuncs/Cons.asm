/* cons function */

L_CONS:
  PUSH(FP);
  MOV(FP, SP);

  CMP(FPARG(1), 2);
  JUMP_NE(LERROR_NUM_OF_PARAMS_NO_MATCH);

  PUSH(FPARG(3));
  PUSH(FPARG(2));
  CALL(MAKE_SOB_PAIR);
  DROP(2);

  POP(FP);
  RETURN;