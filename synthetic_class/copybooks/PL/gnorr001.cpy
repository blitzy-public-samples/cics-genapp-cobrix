******************************************************************
*  COPYBOOK  : GNORR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : OR
******************************************************************
 01  RT-NOR-RATING.

          03 RT-NOR-TERRITORY-CODE            PIC X(3).
          03 RT-NOR-CLASS-CODE                PIC X(4).
          03 RT-NOR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NOR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NOR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NOR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NOR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NOR-RATED-PREMIUM             PIC 9(9)V9(2).
