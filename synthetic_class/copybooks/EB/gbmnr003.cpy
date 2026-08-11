******************************************************************
*  COPYBOOK  : GBMNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : MN
******************************************************************
 01  RT-BMN-RATING.

          03 RT-BMN-TERRITORY-CODE            PIC X(3).
          03 RT-BMN-CLASS-CODE                PIC X(4).
          03 RT-BMN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BMN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BMN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BMN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BMN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BMN-RATED-PREMIUM             PIC 9(9)V9(2).
