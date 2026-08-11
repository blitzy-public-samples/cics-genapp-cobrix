******************************************************************
*  COPYBOOK  : GPOHM001
*  KIND      : ERROR-MSG
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : OH
*  Pattern derived from GenApp's ERROR-MSG structure.
******************************************************************
 01  ERROR-MSG.
     03 EM-DATE                  PIC X(8)  VALUE SPACES.
     03 FILLER                   PIC X     VALUE SPACES.
     03 EM-TIME                  PIC X(6)  VALUE SPACES.
     03 FILLER                   PIC X(9)  VALUE ' GPOHAL01'.
     03 EM-VARIABLE              PIC X(21) VALUE SPACES.
