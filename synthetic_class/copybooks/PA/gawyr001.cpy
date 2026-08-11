******************************************************************
*  COPYBOOK  : GAWYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : WY
******************************************************************
 01  RT-AWY-RATING.

          03 RT-AWY-TERRITORY-CODE            PIC X(3).
          03 RT-AWY-CLASS-CODE                PIC X(4).
          03 RT-AWY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AWY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AWY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AWY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AWY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AWY-RATED-PREMIUM             PIC 9(9)V9(2).
