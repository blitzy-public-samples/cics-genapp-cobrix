******************************************************************
*  COPYBOOK  : GBWVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : WV
******************************************************************
 01  RT-BWV-RATING.

          03 RT-BWV-TERRITORY-CODE            PIC X(3).
          03 RT-BWV-CLASS-CODE                PIC X(4).
          03 RT-BWV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BWV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BWV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BWV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BWV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BWV-RATED-PREMIUM             PIC 9(9)V9(2).
