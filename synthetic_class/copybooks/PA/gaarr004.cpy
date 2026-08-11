******************************************************************
*  COPYBOOK  : GAARR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : AR
******************************************************************
 01  RT-AAR-RATING.

          03 RT-AAR-TERRITORY-CODE            PIC X(3).
          03 RT-AAR-CLASS-CODE                PIC X(4).
          03 RT-AAR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AAR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AAR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AAR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AAR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AAR-RATED-PREMIUM             PIC 9(9)V9(2).
