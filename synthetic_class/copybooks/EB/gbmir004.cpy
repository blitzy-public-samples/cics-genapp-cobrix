******************************************************************
*  COPYBOOK  : GBMIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : MI
******************************************************************
 01  RT-BMI-RATING.

          03 RT-BMI-TERRITORY-CODE            PIC X(3).
          03 RT-BMI-CLASS-CODE                PIC X(4).
          03 RT-BMI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BMI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BMI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BMI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BMI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BMI-RATED-PREMIUM             PIC 9(9)V9(2).
