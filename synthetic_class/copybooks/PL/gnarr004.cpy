******************************************************************
*  COPYBOOK  : GNARR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : AR
******************************************************************
 01  RT-NAR-RATING.

          03 RT-NAR-TERRITORY-CODE            PIC X(3).
          03 RT-NAR-CLASS-CODE                PIC X(4).
          03 RT-NAR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NAR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NAR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NAR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NAR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NAR-RATED-PREMIUM             PIC 9(9)V9(2).
