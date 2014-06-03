/* append function */

L_APPEND:
  PUSH(FP);
  MOV(FP, SP);

  PUSH(R1); // pointer to the next item in current list
  PUSH(R2); // Count the item in the result list
  PUSH(R3);
  PUSH(R4); // pointer to the temp array on the memory
  PUSH(R5); // Pointer for the next arg

  CALL(VariadicStart);

  MOV(R5,FPARG(2));
  MOV(R2, 0);

  // Check if get no paramters:
  PUSH(R5);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_APPEND_NO_PARAMS);


  // Create the entry for the temp array
  PUSH(1);
  CALL(MALLOC);
  DROP(1);
  MOV(R4, R0);

L_APPEND_LOOP:
  // Check if reach the null
  PUSH(R5);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_APPEND_END);

  // Check if next is null (we want to handle the last one in speical form)
  PUSH(INDD(R5,2));
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_APPEND_END);

  // if current item is nill - skip it!
  PUSH(INDD(R5,1));
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(L_APPEND_LOOP_NOT_NIL);

  MOV(R5, INDD(R5,2)); // Go to next item pointer
  JUMP(L_APPEND_LOOP); // skip the nil
L_APPEND_LOOP_NOT_NIL:
  // must be pair
  PUSH(INDD(R5,1));
  CALL(IS_SOB_PAIR);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(LERROR_TYPE_MISMATCH);

  MOV(R1, INDD(R5,1));
L_APPEND_FLAT_CURRENT_LIST_LOOP:
  // Check if reach the null
  PUSH(R1);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_APPEND_FLAT_CURRENT_LIST_LOOP_END);

  // Update the temp array  result on memory
  PUSH(1);
  CALL(MALLOC);
  DROP(1);
  INCR(R2);
  MOV(INDD(R4,R2),INDD(R1,1));

  MOV(R1, INDD(R1,2)); // Go to next number pos
  JUMP(L_APPEND_FLAT_CURRENT_LIST_LOOP);
L_APPEND_FLAT_CURRENT_LIST_LOOP_END:

  MOV(R5, INDD(R5,2)); // Go to next number pos
  JUMP(L_APPEND_LOOP);
L_APPEND_END:

CMP(R2, 0);
JUMP_NE(L_APPEND_MORE_THEN_ONE_ITEM);

MOV(R0, INDD(R5,1)); // Set the result to be the one only item
JUMP(L_APPEND_EXIT); // Exit

L_APPEND_MORE_THEN_ONE_ITEM:

// Save R2
PUSH(1);
CALL(MALLOC);
DROP(1);
MOV(IND(R0), R2);

// Create list
L_APPEND_CREATE_LIST:
    CMP(R2,0);
    JUMP_EQ(L_APPEND_CREATE_LIST_END);

    PUSH(INDD(R4,R2));

    DECR(R2);
    JUMP(L_APPEND_CREATE_LIST);
L_APPEND_CREATE_LIST_END:
// Recover R2
MOV(R2, IND(R0));
  PUSH(R2);      // number of args
  PUSH(FPARG(0)); // env
  CALL(L_LIST);
  DROP(3);         // Suppose to drop 3 , fix it after oron fix l_List

  MOV(R1, R0); // R4 will be the pointer to next irem
  MOV(R2, R0); // Pointer to where to add the last item
  MOV(R3, R0); // Save the entry for the list result
// Go to the last item in the new list and push there the last item
L_APPEND_ADD_LAST_ITEM:
  // Check if reach the null
  PUSH(R1);
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_APPEND_ADD_LAST_ITEM_END);

  MOV(R2, R1);
  ADD(R2,2);

  MOV(R1, INDD(R1,2)); // Go to next number pos
  JUMP(L_APPEND_ADD_LAST_ITEM);
L_APPEND_ADD_LAST_ITEM_END:

  // Set the last item
  MOV(IND(R2), INDD(R5,1));

  // Recover R0
  MOV(R0, R3);

  JUMP(L_APPEND_EXIT);
L_APPEND_NO_PARAMS:
   MOV(R0, 5);

L_APPEND_EXIT:

  POP(R5);
  POP(R4);
  POP(R3);
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;