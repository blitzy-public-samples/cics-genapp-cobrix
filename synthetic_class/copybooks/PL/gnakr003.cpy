******************************************************************
*  COPYBOOK  : GNAKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : AK
******************************************************************
 01  RT-NAK-RATING.

          03 RT-NAK-TERRITORY-CODE            PIC X(3).
          03 RT-NAK-CLASS-CODE                PIC X(4).
          03 RT-NAK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NAK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NAK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NAK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NAK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NAK-RATED-PREMIUM             PIC 9(9)V9(2).
