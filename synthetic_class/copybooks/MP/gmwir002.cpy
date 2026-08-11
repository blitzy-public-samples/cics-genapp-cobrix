******************************************************************
*  COPYBOOK  : GMWIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : WI
******************************************************************
 01  RT-MWI-RATING.

          03 RT-MWI-TERRITORY-CODE            PIC X(3).
          03 RT-MWI-CLASS-CODE                PIC X(4).
          03 RT-MWI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MWI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MWI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MWI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MWI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MWI-RATED-PREMIUM             PIC 9(9)V9(2).
