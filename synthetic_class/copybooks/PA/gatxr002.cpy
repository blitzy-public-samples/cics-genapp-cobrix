******************************************************************
*  COPYBOOK  : GATXR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : TX
******************************************************************
 01  RT-ATX-RATING.

          03 RT-ATX-TERRITORY-CODE            PIC X(3).
          03 RT-ATX-CLASS-CODE                PIC X(4).
          03 RT-ATX-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ATX-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ATX-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ATX-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ATX-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ATX-RATED-PREMIUM             PIC 9(9)V9(2).
