******************************************************************
*  COPYBOOK  : GAALR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : AL
******************************************************************
 01  RT-AAL-RATING.

          03 RT-AAL-TERRITORY-CODE            PIC X(3).
          03 RT-AAL-CLASS-CODE                PIC X(4).
          03 RT-AAL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AAL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AAL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AAL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AAL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AAL-RATED-PREMIUM             PIC 9(9)V9(2).
