******************************************************************
*  COPYBOOK  : GBORR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : OR
******************************************************************
 01  RT-BOR-RATING.

          03 RT-BOR-TERRITORY-CODE            PIC X(3).
          03 RT-BOR-CLASS-CODE                PIC X(4).
          03 RT-BOR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BOR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BOR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BOR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BOR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BOR-RATED-PREMIUM             PIC 9(9)V9(2).
