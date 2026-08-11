******************************************************************
*  COPYBOOK  : GAUTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : UT
******************************************************************
 01  RT-AUT-RATING.

          03 RT-AUT-TERRITORY-CODE            PIC X(3).
          03 RT-AUT-CLASS-CODE                PIC X(4).
          03 RT-AUT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AUT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AUT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AUT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AUT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AUT-RATED-PREMIUM             PIC 9(9)V9(2).
