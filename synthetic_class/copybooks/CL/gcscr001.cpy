******************************************************************
*  COPYBOOK  : GCSCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : SC
******************************************************************
 01  RT-CSC-RATING.

          03 RT-CSC-TERRITORY-CODE            PIC X(3).
          03 RT-CSC-CLASS-CODE                PIC X(4).
          03 RT-CSC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CSC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CSC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CSC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CSC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CSC-RATED-PREMIUM             PIC 9(9)V9(2).
