/*
* Take the current env and enlarge it with 1 more level
* This function just:
*    1) Create New env object on the memory
*    2) Allcoate memory for all the levels
*    3) Copy the old levels for the new object
*
* Pay attention the function do not copy the args from the stack to the new level(zero level).
*/

ENLARGE_ENV:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1);
  PUSH(R2);
  PUSH(R3);

  // R1 Get the env, R2 the number of levels of env
  MOV(R1, FPARG(0));
  MOV(R2, INDD(R1,1));


  // Make new env with one more level
  ADD(R2, 1);
  PUSH(R2);
  CALL(MAKE_ENV);
  DROP(1);
  // Now R0 save the adress of the new env

  MOV(R3,R2);  //R3 is (R2+1)
  INCR(R3);

  // Copy levels from old env
ENLARGE_ENV_LOOP:
  CMP(R2,1); // Until 1 Becuase the meta-data: t_env and num of levels
  JUMP_EQ(EXIT_ENLARGE_ENV_LOOP);

  MOV(INDD(R0, R3), INDD(R1, R2));
  DECR(R2);
  DECR(R3);
  JUMP(ENLARGE_ENV_LOOP);
EXIT_ENLARGE_ENV_LOOP:

  POP(R3);
  POP(R2);
  POP(R1);
  POP(FP);
  RETURN;