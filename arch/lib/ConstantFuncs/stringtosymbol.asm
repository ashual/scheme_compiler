/* string->symbol function */

L_STRINGTOSYMBOL:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1); // Save the string I get in param
  PUSH(R2); // Save the pointer to the symbol table
  PUSH(R3); // Save the string of the Current symbol
  PUSH(R4); // Save pointer to the nil constant

  // Validy check 1 - number of args
  CMP(FPARG(1), 1);
  JUMP_NE(LERROR_NUM_OF_PARAMS_NO_MATCH);

  // Validy check 2 - type of arg
  MOV(R1,FPARG(2));
  PUSH(R1);
  CALL(IS_SOB_STRING);
  DROP(1);
  CMP(R0, 1);
  JUMP_NE(LERROR_TYPE_MISMATCH);

  // The entry point of the symbol table always will be in the first place on the mem
  MOV(R2, IMM(1));

  // Loop over all the symbols in the table
L_STRINGTOSYMBOL_RUN_ALL_SYMBOL:
  // Check if reach the end of table(mark with nil)
  PUSH(IND(R2));
  CALL(IS_SOB_NIL);
  DROP(1);
  CMP(R0, 1);
  JUMP_EQ(L_STRINGTOSYMBOL_CREATE_NEW);

  // Move to the next symbol
  MOV(R2, IND(R2));

  // Set R3 to the symbol
  MOV(R3, IND(R2));
  // Set R3 to the string of the symbol
  MOV(R3, INDD(R3,1));

  // Set R2 to the next symbol pos
  INCR(R2);

  // Check if the current symbol match the string in arg
  PUSH(R1);
  PUSH(R3);
  CALL(IS_STRING_EQUAL);
  DROP(2);
  CMP(R0,0);
  JUMP_EQ(L_STRINGTOSYMBOL_RUN_ALL_SYMBOL);

  // We Find the Symbol!
  // Set R2 to the Curr symbol pos
  DECR(R2);
  MOV(R0, IND(R2));
  JUMP(L_STRINGTOSYMBOL_END);

L_STRINGTOSYMBOL_CREATE_NEW:
  // Save the nil constant pointer
  MOV(R4, IND(R2));

  // Create the new symbol
  PUSH(R1);
  CALL(MAKE_SOB_SYMBOL);
  DROP(1);
  MOV(R1, R0); // R1 save the pointer for the new symbol

  // Create new item in the symbol table
  PUSH(IMM(2));
  CALL(MALLOC);
  DROP(1);

  // Set the new item
  MOV(IND(R2), R0); // Connect the new item to the link list
  MOV(IND(R0), R1); // Save the content of the item
  MOV(INDD(R0,1), R4); // Point to nill

  MOV(R0, IND(R0)); // Return the new symbol
L_STRINGTOSYMBOL_END:
  POP(R4);
  POP(R3);
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;