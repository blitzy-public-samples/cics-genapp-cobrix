******************************************************************
*  COPYBOOK  : GCMSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : MS
******************************************************************
 01  RT-CMS-RATING.

          03 RT-CMS-TERRITORY-CODE            PIC X(3).
          03 RT-CMS-CLASS-CODE                PIC X(4).
          03 RT-CMS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CMS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CMS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CMS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CMS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CMS-RATED-PREMIUM             PIC 9(9)V9(2).
