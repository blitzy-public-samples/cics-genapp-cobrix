******************************************************************
*  COPYBOOK  : GQILR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : IL
******************************************************************
 01  RT-QIL-RATING.

          03 RT-QIL-TERRITORY-CODE            PIC X(3).
          03 RT-QIL-CLASS-CODE                PIC X(4).
          03 RT-QIL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QIL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QIL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QIL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QIL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QIL-RATED-PREMIUM             PIC 9(9)V9(2).
