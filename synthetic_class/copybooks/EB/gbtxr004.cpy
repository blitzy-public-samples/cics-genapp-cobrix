******************************************************************
*  COPYBOOK  : GBTXR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : TX
******************************************************************
 01  RT-BTX-RATING.

          03 RT-BTX-TERRITORY-CODE            PIC X(3).
          03 RT-BTX-CLASS-CODE                PIC X(4).
          03 RT-BTX-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BTX-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BTX-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BTX-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BTX-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BTX-RATED-PREMIUM             PIC 9(9)V9(2).
