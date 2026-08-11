******************************************************************
*  COPYBOOK  : GQOHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : OH
******************************************************************
 01  RT-QOH-RATING.

          03 RT-QOH-TERRITORY-CODE            PIC X(3).
          03 RT-QOH-CLASS-CODE                PIC X(4).
          03 RT-QOH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QOH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QOH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QOH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QOH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QOH-RATED-PREMIUM             PIC 9(9)V9(2).
