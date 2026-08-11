******************************************************************
*  COPYBOOK  : GNOKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : OK
******************************************************************
 01  RT-NOK-RATING.

          03 RT-NOK-TERRITORY-CODE            PIC X(3).
          03 RT-NOK-CLASS-CODE                PIC X(4).
          03 RT-NOK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NOK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NOK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NOK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NOK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NOK-RATED-PREMIUM             PIC 9(9)V9(2).
