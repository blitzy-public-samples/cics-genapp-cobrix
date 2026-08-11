******************************************************************
*  COPYBOOK  : GPNMR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : NM
******************************************************************
 01  RT-PNM-RATING.

          03 RT-PNM-TERRITORY-CODE            PIC X(3).
          03 RT-PNM-CLASS-CODE                PIC X(4).
          03 RT-PNM-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PNM-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PNM-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PNM-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PNM-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PNM-RATED-PREMIUM             PIC 9(9)V9(2).
