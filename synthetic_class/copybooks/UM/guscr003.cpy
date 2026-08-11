******************************************************************
*  COPYBOOK  : GUSCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : SC
******************************************************************
 01  RT-USC-RATING.

          03 RT-USC-TERRITORY-CODE            PIC X(3).
          03 RT-USC-CLASS-CODE                PIC X(4).
          03 RT-USC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-USC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-USC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-USC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-USC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-USC-RATED-PREMIUM             PIC 9(9)V9(2).
