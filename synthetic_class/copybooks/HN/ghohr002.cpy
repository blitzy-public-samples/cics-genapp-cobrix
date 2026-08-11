******************************************************************
*  COPYBOOK  : GHOHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : OH
******************************************************************
 01  RT-HOH-RATING.

          03 RT-HOH-TERRITORY-CODE            PIC X(3).
          03 RT-HOH-CLASS-CODE                PIC X(4).
          03 RT-HOH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HOH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HOH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HOH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HOH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HOH-RATED-PREMIUM             PIC 9(9)V9(2).
