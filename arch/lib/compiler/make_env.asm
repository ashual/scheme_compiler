/*
* Get in Paramter the numbers of levels to create
* Create new empty env with X empty levels.
* Env Look like thie: [T_ENV] [Num of leveles] [level 1 address] ..... [level x address]
*/


MAKE_ENV:
  PUSH(FP);
  MOV(FP, SP);
  PUSH(R1);

  MOV(R1, FPARG(0));
  ADD(R1, 2);
  PUSH(R1);
  CALL(MALLOC);
  DROP(1);

  MOV(IND(R0), T_ENV);
  MOV(INDD(R0, 1), FPARG(0));

  POP(R1);
  POP(FP);
  RETURN;