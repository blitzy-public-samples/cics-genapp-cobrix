******************************************************************
*  COPYBOOK  : GNAZR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : AZ
******************************************************************
 01  RT-NAZ-RATING.

          03 RT-NAZ-TERRITORY-CODE            PIC X(3).
          03 RT-NAZ-CLASS-CODE                PIC X(4).
          03 RT-NAZ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NAZ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NAZ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NAZ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NAZ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NAZ-RATED-PREMIUM             PIC 9(9)V9(2).
