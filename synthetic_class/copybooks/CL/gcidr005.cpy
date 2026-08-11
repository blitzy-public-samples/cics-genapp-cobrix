******************************************************************
*  COPYBOOK  : GCIDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : ID
******************************************************************
 01  RT-CID-RATING.

          03 RT-CID-TERRITORY-CODE            PIC X(3).
          03 RT-CID-CLASS-CODE                PIC X(4).
          03 RT-CID-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CID-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CID-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CID-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CID-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CID-RATED-PREMIUM             PIC 9(9)V9(2).
