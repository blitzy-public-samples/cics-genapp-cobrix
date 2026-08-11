******************************************************************
*  COPYBOOK  : GCIAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : IA
******************************************************************
 01  RT-CIA-RATING.

          03 RT-CIA-TERRITORY-CODE            PIC X(3).
          03 RT-CIA-CLASS-CODE                PIC X(4).
          03 RT-CIA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CIA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CIA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CIA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CIA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CIA-RATED-PREMIUM             PIC 9(9)V9(2).
