******************************************************************
*  COPYBOOK  : GPKSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : KS
******************************************************************
 01  RT-PKS-RATING.

          03 RT-PKS-TERRITORY-CODE            PIC X(3).
          03 RT-PKS-CLASS-CODE                PIC X(4).
          03 RT-PKS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PKS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PKS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PKS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PKS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PKS-RATED-PREMIUM             PIC 9(9)V9(2).
