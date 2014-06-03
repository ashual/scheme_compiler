/* list->vector function */

L_LISTTOVECTOR:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1);
  PUSH(R2);
  PUSH(R3);

  MOV(R1,FPARG(2));
  MOV(R2, 0);

  // Create the entry for the temp array
  PUSH(1);
  CALL(MALLOC);
  DROP(1);
  MOV(R3, R0);

L_LISTTOVECTOR_LOOP:
  // Check if reach the null
  PUSH(R1);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_LISTTOVECTOR_END);

  // Update the temp array  result on memory
  PUSH(1);
  CALL(MALLOC);
  DROP(1);
  INCR(R2);
  MOV(INDD(R3,R2),INDD(R1,1));

  MOV(R1, INDD(R1,2));
  JUMP(L_LISTTOVECTOR_LOOP);
L_LISTTOVECTOR_END:

  MOV(IND(R3), R2);

L_LISTTOVECTOR_PUSH_VECTOR_ARG:
    CMP(R2,0);
    JUMP_EQ(L_LISTTOVECTOR_PUSH_VECTOR_ARG_END);

    PUSH(INDD(R3,R2));

    DECR(R2);
    JUMP(L_LISTTOVECTOR_PUSH_VECTOR_ARG);
L_LISTTOVECTOR_PUSH_VECTOR_ARG_END:

  MOV(R2, IND(R3));


  PUSH(R2);      // number of args
  PUSH(FPARG(0)); // env
  CALL(L_VECTOR);
  DROP(3);

  POP(R3);
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;


