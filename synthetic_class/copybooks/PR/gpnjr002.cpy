******************************************************************
*  COPYBOOK  : GPNJR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : NJ
******************************************************************
 01  RT-PNJ-RATING.

          03 RT-PNJ-TERRITORY-CODE            PIC X(3).
          03 RT-PNJ-CLASS-CODE                PIC X(4).
          03 RT-PNJ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PNJ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PNJ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PNJ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PNJ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PNJ-RATED-PREMIUM             PIC 9(9)V9(2).
