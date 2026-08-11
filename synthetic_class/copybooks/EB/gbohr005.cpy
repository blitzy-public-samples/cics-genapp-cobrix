******************************************************************
*  COPYBOOK  : GBOHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : OH
******************************************************************
 01  RT-BOH-RATING.

          03 RT-BOH-TERRITORY-CODE            PIC X(3).
          03 RT-BOH-CLASS-CODE                PIC X(4).
          03 RT-BOH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BOH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BOH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BOH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BOH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BOH-RATED-PREMIUM             PIC 9(9)V9(2).
