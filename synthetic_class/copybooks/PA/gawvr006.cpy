******************************************************************
*  COPYBOOK  : GAWVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : WV
******************************************************************
 01  RT-AWV-RATING.

          03 RT-AWV-TERRITORY-CODE            PIC X(3).
          03 RT-AWV-CLASS-CODE                PIC X(4).
          03 RT-AWV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AWV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AWV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AWV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AWV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AWV-RATED-PREMIUM             PIC 9(9)V9(2).
