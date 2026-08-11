******************************************************************
*  COPYBOOK  : GBDER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : DE
******************************************************************
 01  RT-BDE-RATING.

          03 RT-BDE-TERRITORY-CODE            PIC X(3).
          03 RT-BDE-CLASS-CODE                PIC X(4).
          03 RT-BDE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BDE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BDE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BDE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BDE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BDE-RATED-PREMIUM             PIC 9(9)V9(2).
