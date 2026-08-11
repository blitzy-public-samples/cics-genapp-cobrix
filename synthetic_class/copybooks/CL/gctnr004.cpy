******************************************************************
*  COPYBOOK  : GCTNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : TN
******************************************************************
 01  RT-CTN-RATING.

          03 RT-CTN-TERRITORY-CODE            PIC X(3).
          03 RT-CTN-CLASS-CODE                PIC X(4).
          03 RT-CTN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CTN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CTN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CTN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CTN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CTN-RATED-PREMIUM             PIC 9(9)V9(2).
