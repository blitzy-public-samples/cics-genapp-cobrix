******************************************************************
*  COPYBOOK  : GCVAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : VA
******************************************************************
 01  RT-CVA-RATING.

          03 RT-CVA-TERRITORY-CODE            PIC X(3).
          03 RT-CVA-CLASS-CODE                PIC X(4).
          03 RT-CVA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CVA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CVA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CVA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CVA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CVA-RATED-PREMIUM             PIC 9(9)V9(2).
