

L_DELETE_MAGIC:

    PUSH(R1);
	PUSH(R2);
	
    MOV(R1,SP);
    SUB(R1,4);
	MOV(R1,STACK(R1));
	CMP(R1,IMM(123456));

	JUMP_NE(L_DELETE_MAGIC_END);
	MOV(R1,SP);
	SUB(R1,3);
	MOV(R2,R1);
	DECR(R2);
	MOV(STACK(R2),STACK(R1));
	POP(R2);
	POP(R1);
	DROP(1);
	RETURN;

L_DELETE_MAGIC_END:
  POP(R2);
  POP(R1);
  RETURN;