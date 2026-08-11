******************************************************************
*  COPYBOOK  : GPLAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : LA
******************************************************************
 01  RT-PLA-RATING.

          03 RT-PLA-TERRITORY-CODE            PIC X(3).
          03 RT-PLA-CLASS-CODE                PIC X(4).
          03 RT-PLA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PLA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PLA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PLA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PLA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PLA-RATED-PREMIUM             PIC 9(9)V9(2).
