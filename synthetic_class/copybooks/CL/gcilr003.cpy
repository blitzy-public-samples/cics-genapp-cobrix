******************************************************************
*  COPYBOOK  : GCILR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : IL
******************************************************************
 01  RT-CIL-RATING.

          03 RT-CIL-TERRITORY-CODE            PIC X(3).
          03 RT-CIL-CLASS-CODE                PIC X(4).
          03 RT-CIL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CIL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CIL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CIL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CIL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CIL-RATED-PREMIUM             PIC 9(9)V9(2).
