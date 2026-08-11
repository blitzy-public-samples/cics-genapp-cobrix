******************************************************************
*  COPYBOOK  : GPMIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : MI
******************************************************************
 01  RT-PMI-RATING.

          03 RT-PMI-TERRITORY-CODE            PIC X(3).
          03 RT-PMI-CLASS-CODE                PIC X(4).
          03 RT-PMI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PMI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PMI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PMI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PMI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PMI-RATED-PREMIUM             PIC 9(9)V9(2).
