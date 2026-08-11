******************************************************************
*  COPYBOOK  : GAIDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : ID
******************************************************************
 01  RT-AID-RATING.

          03 RT-AID-TERRITORY-CODE            PIC X(3).
          03 RT-AID-CLASS-CODE                PIC X(4).
          03 RT-AID-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AID-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AID-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AID-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AID-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AID-RATED-PREMIUM             PIC 9(9)V9(2).
