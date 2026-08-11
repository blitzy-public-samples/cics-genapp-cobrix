******************************************************************
*  COPYBOOK  : GMSCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : SC
******************************************************************
 01  RT-MSC-RATING.

          03 RT-MSC-TERRITORY-CODE            PIC X(3).
          03 RT-MSC-CLASS-CODE                PIC X(4).
          03 RT-MSC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MSC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MSC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MSC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MSC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MSC-RATED-PREMIUM             PIC 9(9)V9(2).
