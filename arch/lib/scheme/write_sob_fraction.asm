/* scheme/write_sob_fraction */
 WRITE_SOB_FRACTION:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1);

  MOV(R1, FPARG(0));

  PUSH(INDD(R1, 1));
  CALL(WRITE_INTEGER);
  DROP(1);

  PUSH(IMM('/'));
  CALL(PUTCHAR);
  DROP(1);

  PUSH(INDD(R1, 2));
  CALL(WRITE_INTEGER);
  DROP(1);

  POP(R1);
  POP(FP);
  RETURN;
