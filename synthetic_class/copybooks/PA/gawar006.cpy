******************************************************************
*  COPYBOOK  : GAWAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : WA
******************************************************************
 01  RT-AWA-RATING.

          03 RT-AWA-TERRITORY-CODE            PIC X(3).
          03 RT-AWA-CLASS-CODE                PIC X(4).
          03 RT-AWA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AWA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AWA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AWA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AWA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AWA-RATED-PREMIUM             PIC 9(9)V9(2).
