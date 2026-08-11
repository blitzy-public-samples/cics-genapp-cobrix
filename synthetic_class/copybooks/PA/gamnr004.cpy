******************************************************************
*  COPYBOOK  : GAMNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : MN
******************************************************************
 01  RT-AMN-RATING.

          03 RT-AMN-TERRITORY-CODE            PIC X(3).
          03 RT-AMN-CLASS-CODE                PIC X(4).
          03 RT-AMN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AMN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AMN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AMN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AMN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AMN-RATED-PREMIUM             PIC 9(9)V9(2).
