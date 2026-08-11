******************************************************************
*  COPYBOOK  : GMWVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : WV
******************************************************************
 01  RT-MWV-RATING.

          03 RT-MWV-TERRITORY-CODE            PIC X(3).
          03 RT-MWV-CLASS-CODE                PIC X(4).
          03 RT-MWV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MWV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MWV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MWV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MWV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MWV-RATED-PREMIUM             PIC 9(9)V9(2).
