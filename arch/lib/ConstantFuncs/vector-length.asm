/* vector-length function */

L_VECTORLENGTH:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1);

  CMP(FPARG(1), 1);
  JUMP_NE(LERROR_NUM_OF_PARAMS_NO_MATCH);

  MOV(R1,FPARG(2));
  PUSH(R1);
  CALL(IS_SOB_VECTOR);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(LERROR_TYPE_MISMATCH);

  PUSH(INDD(R1,1));
  CALL(MAKE_SOB_INTEGER);
  DROP(1);

  POP(R1);
  POP(FP);
  RETURN;