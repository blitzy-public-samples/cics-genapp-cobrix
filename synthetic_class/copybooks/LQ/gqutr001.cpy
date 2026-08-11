******************************************************************
*  COPYBOOK  : GQUTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : UT
******************************************************************
 01  RT-QUT-RATING.

          03 RT-QUT-TERRITORY-CODE            PIC X(3).
          03 RT-QUT-CLASS-CODE                PIC X(4).
          03 RT-QUT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QUT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QUT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QUT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QUT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QUT-RATED-PREMIUM             PIC 9(9)V9(2).
