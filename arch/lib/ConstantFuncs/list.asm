/* LIST function */

L_LIST:
  PUSH(FP);
  MOV(FP, SP);

  PUSH(R1);
  PUSH(R2);
  PUSH(R3);
  PUSH(R4);
  PUSH(R5);

  CALL(VariadicStart);

  MOV(R0,FPARG(2));
	

  POP(R5);
  POP(R4);
  POP(R3);
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;