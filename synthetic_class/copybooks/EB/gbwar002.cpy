******************************************************************
*  COPYBOOK  : GBWAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : WA
******************************************************************
 01  RT-BWA-RATING.

          03 RT-BWA-TERRITORY-CODE            PIC X(3).
          03 RT-BWA-CLASS-CODE                PIC X(4).
          03 RT-BWA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BWA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BWA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BWA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BWA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BWA-RATED-PREMIUM             PIC 9(9)V9(2).
