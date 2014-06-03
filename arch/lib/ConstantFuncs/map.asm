/* map function */

L_MAP:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1); // save the procedure
  PUSH(R2); // Help Registry, First Loop -Save the Current list, Middle loop - Save the size of list , Last Loop - loop index
  PUSH(R3); // Begin - number of lists, End - size of list
  PUSH(R4); // Array of list location, in the end it convert to pointer to reuslt list
  PUSH(R5); // Pointer to paramter list, after it save temp

  CALL(VariadicStart);

  MOV(R5, FPARG(2));

  // Check if the first is null
  PUSH(R5);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(LERROR_NUM_OF_PARAMS_NO_MATCH);

  MOV(R1, INDD(R5,1));

  // Check if R1 is closure
  PUSH(R1);
  CALL(IS_SOB_CLOSURE);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(LERROR_TYPE_MISMATCH);

  MOV(R5, INDD(R5,2)); // Go to next number pos

  MOV(R3, 0);

  // Build array of lists = Save the entry
  PUSH(1);
  CALL(MALLOC);
  DROP(1);
  MOV(R4, R0);

// This loop save in R3 the number of lists is get in paramters, and build an array on the memory.
// Every cell in the array is the first item of each list.
// R4 is the entry point for the array
L_MAP_LOOP_COUNT_LISTS:
  // Check if the Current is null
  PUSH(R5);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_MAP_LOOP_COUNT_LISTS_END);

  MOV(R2, INDD(R5,1));

  // Check if R2 is pair
  PUSH(R2);
  CALL(IS_SOB_PAIR);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(LERROR_TYPE_MISMATCH);

  // Build array of lists = Enlarge it by 1
  PUSH(1);
  CALL(MALLOC);
  DROP(1);
  MOV(IND(R0), R2);

  INCR(R3); // Update the counter of lists

  MOV(R5, INDD(R5,2)); // Go to next number pos
  JUMP(L_MAP_LOOP_COUNT_LISTS);
L_MAP_LOOP_COUNT_LISTS_END:

MOV(R2,0); // Save the size of the list

L_MAP_LOOP_CALC:
  // Check if we reach the end of list
  // We check only the first list because the input is valid!
  PUSH(INDD(R4, 1));
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_MAP_LOOP_CALC_END);

PUSH(IMM(123456));
MOV(IND(R4), R3); // Save R3
L_MAP_LOOP_PUSH_ARG_FROM_EVERY_LIST:
  CMP(R3, 0);
  JUMP_EQ(L_MAP_LOOP_PUSH_ARG_FROM_EVERY_LIST_END);

  MOV(R5, INDD(R4, R3)); // Jump to relevant list
 // MOV(R5, IND(R5)); // Jump acctuly to the list
  PUSH(INDD(R5,1)); // Push the content of the current item
  MOV(INDD(R4,R3), INDD(R5,2)); // Set to next item in the list

  DECR(R3);
  JUMP(L_MAP_LOOP_PUSH_ARG_FROM_EVERY_LIST);
L_MAP_LOOP_PUSH_ARG_FROM_EVERY_LIST_END:
  MOV(R3, IND(R4)); // Recover R3

  PUSH(R3); // Push the number of args
  PUSH(INDD(R1, 1)); // Push the env
  CALLA(INDD(R1,2)); // Applic the procedure
  DROP(1);
  POP(R15);
  DROP(R15);

  POP(R15);
  CMP(R15,IMM(123456));
  JUMP_EQ(L_MAP_DELETE_MAGIC);
  PUSH(R15);
L_MAP_DELETE_MAGIC:


  PUSH(R0); // Save the result to later

  INCR(R2);
  JUMP(L_MAP_LOOP_CALC);
L_MAP_LOOP_CALC_END:

  MOV(R3, R2);  // R3 - Size of result list

  // Reverse the list we create that sit on the stack, we need to do it for sending it to list function
  PUSH(R3);
  CALL(MALLOC);
  DROP(1);
  MOV(R4, R0); // Now R4 will be pointer to the result list
  MOV(R2, 0);  // R2 - loop index

L_MAP_LOOP_REVERSE_RESULT:
  CMP(R2, R3);
  JUMP_EQ(L_MAP_LOOP_REVERSE_RESULT_END);

  POP(R5);
  MOV(INDD(R4, R2), R5);

  INCR(R2);
JUMP(L_MAP_LOOP_REVERSE_RESULT);
L_MAP_LOOP_REVERSE_RESULT_END:

  MOV(R2, 0);  // R2 - loop index
L_MAP_LOOP_READY_FOR_MAKE_LIST:
  CMP(R2, R3);
  JUMP_EQ(L_MAP_LOOP_READY_FOR_MAKE_LIST_END);

  MOV(R5, INDD(R4, R2));
  PUSH(R5);

  INCR(R2);
JUMP(L_MAP_LOOP_READY_FOR_MAKE_LIST);
L_MAP_LOOP_READY_FOR_MAKE_LIST_END:

  PUSH(R3); // push number of args
  PUSH(FPARG(0)); // push the env
  CALL(L_LIST);

  DROP(3);  // 1 - is the number of args, 2 - the env, 3 - the paramter (I send many but the list function change it)

  POP(R5);
  POP(R4);
  POP(R3);
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;