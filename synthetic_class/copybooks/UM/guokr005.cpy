******************************************************************
*  COPYBOOK  : GUOKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : OK
******************************************************************
 01  RT-UOK-RATING.

          03 RT-UOK-TERRITORY-CODE            PIC X(3).
          03 RT-UOK-CLASS-CODE                PIC X(4).
          03 RT-UOK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UOK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UOK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UOK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UOK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UOK-RATED-PREMIUM             PIC 9(9)V9(2).
