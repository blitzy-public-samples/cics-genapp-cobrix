******************************************************************
*  COPYBOOK  : GCORR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : OR
******************************************************************
 01  RT-COR-RATING.

          03 RT-COR-TERRITORY-CODE            PIC X(3).
          03 RT-COR-CLASS-CODE                PIC X(4).
          03 RT-COR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-COR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-COR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-COR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-COR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-COR-RATED-PREMIUM             PIC 9(9)V9(2).
