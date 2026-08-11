******************************************************************
*  COPYBOOK  : GAVTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : VT
******************************************************************
 01  RT-AVT-RATING.

          03 RT-AVT-TERRITORY-CODE            PIC X(3).
          03 RT-AVT-CLASS-CODE                PIC X(4).
          03 RT-AVT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AVT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AVT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AVT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AVT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AVT-RATED-PREMIUM             PIC 9(9)V9(2).
