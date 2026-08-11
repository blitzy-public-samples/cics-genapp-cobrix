******************************************************************
*  COPYBOOK  : GBCTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : CT
******************************************************************
 01  RT-BCT-RATING.

          03 RT-BCT-TERRITORY-CODE            PIC X(3).
          03 RT-BCT-CLASS-CODE                PIC X(4).
          03 RT-BCT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BCT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BCT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BCT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BCT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BCT-RATED-PREMIUM             PIC 9(9)V9(2).
