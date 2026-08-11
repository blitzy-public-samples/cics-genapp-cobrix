******************************************************************
*  COPYBOOK  : GBTNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : TN
******************************************************************
 01  RT-BTN-RATING.

          03 RT-BTN-TERRITORY-CODE            PIC X(3).
          03 RT-BTN-CLASS-CODE                PIC X(4).
          03 RT-BTN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BTN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BTN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BTN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BTN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BTN-RATED-PREMIUM             PIC 9(9)V9(2).
