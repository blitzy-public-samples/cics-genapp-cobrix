******************************************************************
*  COPYBOOK  : GNSCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : SC
******************************************************************
 01  RT-NSC-RATING.

          03 RT-NSC-TERRITORY-CODE            PIC X(3).
          03 RT-NSC-CLASS-CODE                PIC X(4).
          03 RT-NSC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NSC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NSC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NSC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NSC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NSC-RATED-PREMIUM             PIC 9(9)V9(2).
