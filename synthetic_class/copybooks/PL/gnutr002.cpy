******************************************************************
*  COPYBOOK  : GNUTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : UT
******************************************************************
 01  RT-NUT-RATING.

          03 RT-NUT-TERRITORY-CODE            PIC X(3).
          03 RT-NUT-CLASS-CODE                PIC X(4).
          03 RT-NUT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NUT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NUT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NUT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NUT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NUT-RATED-PREMIUM             PIC 9(9)V9(2).
