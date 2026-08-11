******************************************************************
*  COPYBOOK  : GMORR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : OR
******************************************************************
 01  RT-MOR-RATING.

          03 RT-MOR-TERRITORY-CODE            PIC X(3).
          03 RT-MOR-CLASS-CODE                PIC X(4).
          03 RT-MOR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MOR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MOR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MOR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MOR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MOR-RATED-PREMIUM             PIC 9(9)V9(2).
