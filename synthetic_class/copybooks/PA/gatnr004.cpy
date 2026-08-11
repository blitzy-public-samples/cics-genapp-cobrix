******************************************************************
*  COPYBOOK  : GATNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : TN
******************************************************************
 01  RT-ATN-RATING.

          03 RT-ATN-TERRITORY-CODE            PIC X(3).
          03 RT-ATN-CLASS-CODE                PIC X(4).
          03 RT-ATN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ATN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ATN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ATN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ATN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ATN-RATED-PREMIUM             PIC 9(9)V9(2).
