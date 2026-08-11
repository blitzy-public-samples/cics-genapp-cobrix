******************************************************************
*  COPYBOOK  : GNRIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : RI
******************************************************************
 01  RT-NRI-RATING.

          03 RT-NRI-TERRITORY-CODE            PIC X(3).
          03 RT-NRI-CLASS-CODE                PIC X(4).
          03 RT-NRI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NRI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NRI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NRI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NRI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NRI-RATED-PREMIUM             PIC 9(9)V9(2).
