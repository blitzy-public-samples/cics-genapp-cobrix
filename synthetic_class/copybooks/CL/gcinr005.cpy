******************************************************************
*  COPYBOOK  : GCINR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : IN
******************************************************************
 01  RT-CIN-RATING.

          03 RT-CIN-TERRITORY-CODE            PIC X(3).
          03 RT-CIN-CLASS-CODE                PIC X(4).
          03 RT-CIN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CIN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CIN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CIN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CIN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CIN-RATED-PREMIUM             PIC 9(9)V9(2).
