******************************************************************
*  COPYBOOK  : GAPAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : PA
******************************************************************
 01  RT-APA-RATING.

          03 RT-APA-TERRITORY-CODE            PIC X(3).
          03 RT-APA-CLASS-CODE                PIC X(4).
          03 RT-APA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-APA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-APA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-APA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-APA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-APA-RATED-PREMIUM             PIC 9(9)V9(2).
