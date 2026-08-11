******************************************************************
*  COPYBOOK  : GPMTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : MT
******************************************************************
 01  RT-PMT-RATING.

          03 RT-PMT-TERRITORY-CODE            PIC X(3).
          03 RT-PMT-CLASS-CODE                PIC X(4).
          03 RT-PMT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PMT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PMT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PMT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PMT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PMT-RATED-PREMIUM             PIC 9(9)V9(2).
