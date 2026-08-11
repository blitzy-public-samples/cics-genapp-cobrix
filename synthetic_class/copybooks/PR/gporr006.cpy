******************************************************************
*  COPYBOOK  : GPORR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : OR
******************************************************************
 01  RT-POR-RATING.

          03 RT-POR-TERRITORY-CODE            PIC X(3).
          03 RT-POR-CLASS-CODE                PIC X(4).
          03 RT-POR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-POR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-POR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-POR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-POR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-POR-RATED-PREMIUM             PIC 9(9)V9(2).
