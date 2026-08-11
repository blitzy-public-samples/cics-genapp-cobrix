******************************************************************
*  COPYBOOK  : GMILR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : IL
******************************************************************
 01  RT-MIL-RATING.

          03 RT-MIL-TERRITORY-CODE            PIC X(3).
          03 RT-MIL-CLASS-CODE                PIC X(4).
          03 RT-MIL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MIL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MIL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MIL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MIL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MIL-RATED-PREMIUM             PIC 9(9)V9(2).
