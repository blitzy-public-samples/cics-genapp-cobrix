******************************************************************
*  COPYBOOK  : GPMAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : MA
******************************************************************
 01  RT-PMA-RATING.

          03 RT-PMA-TERRITORY-CODE            PIC X(3).
          03 RT-PMA-CLASS-CODE                PIC X(4).
          03 RT-PMA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PMA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PMA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PMA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PMA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PMA-RATED-PREMIUM             PIC 9(9)V9(2).
