******************************************************************
*  COPYBOOK  : GPNYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : NY
******************************************************************
 01  RT-PNY-RATING.

          03 RT-PNY-TERRITORY-CODE            PIC X(3).
          03 RT-PNY-CLASS-CODE                PIC X(4).
          03 RT-PNY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PNY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PNY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PNY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PNY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PNY-RATED-PREMIUM             PIC 9(9)V9(2).
