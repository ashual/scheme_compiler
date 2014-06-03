/* APPLY function */

L_APPLY:
  PUSH(FP);
  MOV(FP, SP);

  PUSH(R1); // R1 will be the offset of the list
  PUSH(R2); // R2 will be the counter of the list
  PUSH(R3); // R3 will be the closure
  PUSH(R4); // R4 will be the
  PUSH(R5); // R5 will be the

		
  MOV(R3,FPARG(IMM(2)));	
  PUSH(R3);
  CALL(IS_SOB_CLOSURE);
  DROP(1);
  CMP(IMM(0),R0);
  JUMP_EQ(LERROR_NOT_CLOSURE);
  

  MOV(R1,FPARG(IMM(1)));
  ADD(R1,1);//R1 is containing the offset of the list (ONE FOR THE ENV AND ONE FOR THE NUMBER OF VARIABLES)
  
  PUSH(IMM(123456));
  
  MOV(R2,IMM(0));//COUNTER OF THE LIST
  MOV(R3,FPARG(R1));//THE LIST
L_APPLY_COUNTER_LOOP:
	PUSH(R3);
	CALL(IS_SOB_NIL);
	DROP(1);
	CMP(R0,IMM(1));
	JUMP_EQ(L_APPLY_COUNTER_END);
	INCR(R2);
	MOV(R3,INDD(R3,IMM(2)));
	PUSH(0);
	JUMP(L_APPLY_COUNTER_LOOP);
L_APPLY_COUNTER_END: 
	
	MOV(R4,IMM(-8));
	SUB(R4,R2);
	MOV(R3,FPARG(R1));//THE LIST
	MOV(R1,R2);//SAVING THE NUMBER OF PARAMETERS

L_APPLY_MOVE_LIST: //insert the list
	CMP(R2,IMM(0));
	JUMP_EQ(L_APPLY_MOVE_LIST_END);
	MOV(FPARG(R4),INDD(R3,IMM(1)));
	INCR(R4);
	DECR(R2);
	MOV(R3,INDD(R3,IMM(2)));
	JUMP(L_APPLY_MOVE_LIST);
L_APPLY_MOVE_LIST_END:

//insert the other parameters
	MOV(R3,FPARG(1));//number of parameters without the list AND THE OFFSET
	
L_APPLY_MOVE_PARAMETERS:
	CMP(R3,IMM(2));
	JUMP_EQ(L_APPLY_MOVE_PARAMETERS_END);
	PUSH(FPARG(R3));
	DECR(R3);
	JUMP(L_APPLY_MOVE_PARAMETERS);
L_APPLY_MOVE_PARAMETERS_END:
	
	
	SUB(R1,IMM(2));
	ADD(R1,FPARG(1));
//insert the number of parameters
	PUSH(R1);
//insert the enviroment
	MOV(R3,FPARG(2));
	PUSH(INDD(R3,1));
//CALL the function
	MOV(R3,INDD(R3,2));
	CALLA(R3);
  
  //CLEAN THE STACK
	DROP(1);
	POP(R1);
	DROP(R1);
	POP(R1);
	CMP(R1,IMM(123456));
	JUMP_EQ(L_APPLY_END);
	PUSH(R1);

L_APPLY_END:
  POP(R5);
  POP(R4);
  POP(R3);
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;
  