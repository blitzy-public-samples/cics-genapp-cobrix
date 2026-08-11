******************************************************************
*  COPYBOOK  : GBILR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : IL
******************************************************************
 01  RT-BIL-RATING.

          03 RT-BIL-TERRITORY-CODE            PIC X(3).
          03 RT-BIL-CLASS-CODE                PIC X(4).
          03 RT-BIL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BIL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BIL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BIL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BIL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BIL-RATED-PREMIUM             PIC 9(9)V9(2).
