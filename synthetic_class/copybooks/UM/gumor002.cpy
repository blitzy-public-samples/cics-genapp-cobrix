******************************************************************
*  COPYBOOK  : GUMOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MO
******************************************************************
 01  RT-UMO-RATING.

          03 RT-UMO-TERRITORY-CODE            PIC X(3).
          03 RT-UMO-CLASS-CODE                PIC X(4).
          03 RT-UMO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UMO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UMO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UMO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UMO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UMO-RATED-PREMIUM             PIC 9(9)V9(2).
